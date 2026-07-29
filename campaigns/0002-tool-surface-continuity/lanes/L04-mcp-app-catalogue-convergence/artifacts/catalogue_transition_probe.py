#!/usr/bin/env python3
"""Model the public Codex MCP refresh seam with a live local stdio fixture.

The probe preserves these public-source properties:
- a thread owns one mutable MCP runtime;
- normal refresh may reuse a ready client when connection config matches;
- a managed client captures server info and tools during startup;
- a sampling-step binding freezes model-visible tools and prepared handlers;
- a direct control-plane call can use the latest live client independently.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "stub_real_mcp.py"
SOURCE_REVISION = "3725f02cf38d856bc82bb46dd68ab61bb96ec6fc"

STUB = {
    "server_info": {"name": "bridge", "version": "stub-1"},
    "tools": [
        {
            "name": "offline_status",
            "description": "Report that the bridge is still using its offline stub.",
            "inputSchema": {"type": "object", "properties": {}},
        }
    ],
}
REAL = {
    "server_info": {"name": "bridge", "version": "real-2"},
    "tools": [
        {
            "name": "catalogue_version",
            "description": "Return the active catalogue version.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "echo",
            "description": "Echo a harmless value.",
            "inputSchema": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
            },
        },
        {
            "name": "health",
            "description": "Return a harmless health result.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ],
}


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def tool_names(tools: Iterable[dict[str, Any]]) -> list[str]:
    return sorted(tool["name"] for tool in tools)


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class RpcError(RuntimeError):
    pass


class McpClient:
    def __init__(self, state_path: Path, connection_identity: str) -> None:
        self.state_path = state_path
        self.connection_identity = connection_identity
        self.process = subprocess.Popen(
            [sys.executable, str(SERVER), "--state", str(state_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._next_id = 1
        initialized = self.request("initialize", {})
        self.server_info = initialized["serverInfo"]
        self.tools = self.request("tools/list", {})["tools"]

    def request(self, method: str, params: dict[str, Any]) -> Any:
        if self.process.stdin is None or self.process.stdout is None:
            raise RpcError("stdio unavailable")
        request_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self.process.stdin.write(json.dumps(request, sort_keys=True) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RpcError(f"server closed: {stderr}")
        response = json.loads(line)
        if "error" in response:
            raise RpcError(response["error"]["message"])
        return response["result"]

    def raw_call(self, name: str) -> str:
        result = self.request("tools/call", {"name": name, "arguments": {}})
        return result["content"][0]["text"]

    def close(self) -> None:
        if self.process.poll() is None:
            try:
                self.request("shutdown", {})
            except Exception:
                self.process.terminate()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=2)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            if stream is not None and not stream.closed:
                stream.close()


@dataclass
class StepBinding:
    client: McpClient
    runtime_generation: int
    tools: list[dict[str, Any]]

    @property
    def registered(self) -> list[str]:
        return tool_names(self.tools)

    @property
    def advertised(self) -> list[str]:
        return tool_names(self.tools)

    def call(self, name: str) -> str:
        if name not in self.registered:
            raise RpcError(f"handler missing: {name}")
        return self.client.raw_call(name)


class ThreadRuntime:
    def __init__(self, state_path: Path, connection_identity: str = "stdio:bridge") -> None:
        self.state_path = state_path
        self.connection_identity = connection_identity
        self.generation = 1
        self.client = McpClient(state_path, connection_identity)
        self.reuse_count = 0
        self.retired_clients: list[McpClient] = []

    def refresh(self, connection_identity: str | None = None, force_reconnect: bool = False) -> str:
        desired = connection_identity or self.connection_identity
        if force_reconnect or desired != self.connection_identity:
            old = self.client
            self.retired_clients.append(old)
            self.connection_identity = desired
            self.generation += 1
            self.client = McpClient(self.state_path, desired)
            # Existing StepBinding values retain `old`, mirroring source-held Arc ownership.
            return "reconnected"
        self.reuse_count += 1
        return "reused"

    def capture_step(self) -> StepBinding:
        return StepBinding(self.client, self.generation, list(self.client.tools))

    def raw_call(self, name: str) -> str:
        return self.client.raw_call(name)

    def close(self) -> None:
        self.client.close()
        for client in self.retired_clients:
            client.close()
        self.retired_clients.clear()


@dataclass
class Snapshot:
    label: str
    global_server_info: dict[str, Any]
    global_tools: list[str]
    bound_server_info: dict[str, Any]
    bound_tools: list[str]
    registered_tools: list[str]
    advertised_tools: list[str]
    executable_smoke: dict[str, str]
    raw_control_plane_smoke: dict[str, str]
    runtime_generation: int
    refresh_action: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "label": self.label,
            "global": {
                "server_info": self.global_server_info,
                "server_identity_digest": canonical_digest(self.global_server_info),
                "tools": self.global_tools,
                "catalogue_digest": canonical_digest(self.global_tools),
            },
            "binding": {
                "server_info": self.bound_server_info,
                "server_identity_digest": canonical_digest(self.bound_server_info),
                "tools": self.bound_tools,
                "catalogue_digest": canonical_digest(self.bound_tools),
                "runtime_generation": self.runtime_generation,
            },
            "router": {
                "registered": self.registered_tools,
                "catalogue_digest": canonical_digest(self.registered_tools),
            },
            "model": {
                "advertised": self.advertised_tools,
                "catalogue_digest": canonical_digest(self.advertised_tools),
            },
            "execution": {
                "router_smoke": self.executable_smoke,
                "raw_control_plane_smoke": self.raw_control_plane_smoke,
            },
        }
        if self.refresh_action is not None:
            payload["refresh_action"] = self.refresh_action
        return payload


def smoke(step: StepBinding, names: Iterable[str]) -> dict[str, str]:
    results: dict[str, str] = {}
    for name in names:
        try:
            results[name] = step.call(name)
        except RpcError as exc:
            results[name] = f"ERROR:{exc}"
    return results


def raw_smoke(runtime: ThreadRuntime, names: Iterable[str]) -> dict[str, str]:
    results: dict[str, str] = {}
    for name in names:
        try:
            results[name] = runtime.raw_call(name)
        except RpcError as exc:
            results[name] = f"ERROR:{exc}"
    return results


def global_probe(state_path: Path) -> tuple[dict[str, Any], list[str]]:
    client = McpClient(state_path, "global-probe")
    try:
        return client.server_info, tool_names(client.tools)
    finally:
        client.close()


def capture(label: str, runtime: ThreadRuntime, refresh_action: str | None = None) -> Snapshot:
    global_info, global_tools = global_probe(runtime.state_path)
    step = runtime.capture_step()
    candidates = sorted(set(global_tools) | set(step.registered))
    return Snapshot(
        label=label,
        global_server_info=global_info,
        global_tools=global_tools,
        bound_server_info=runtime.client.server_info,
        bound_tools=tool_names(runtime.client.tools),
        registered_tools=step.registered,
        advertised_tools=step.advertised,
        executable_smoke=smoke(step, candidates),
        raw_control_plane_smoke=raw_smoke(runtime, candidates),
        runtime_generation=runtime.generation,
        refresh_action=refresh_action,
    )


def run_probe(output: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="fieldwork-l04-") as temp:
        state_path = Path(temp) / "server-state.json"
        write_state(state_path, STUB)
        runtime = ThreadRuntime(state_path)
        fresh_thread: ThreadRuntime | None = None
        restarted: ThreadRuntime | None = None
        try:
            checkpoints: list[Snapshot] = []
            checkpoints.append(capture("01-stub-baseline", runtime))

            write_state(state_path, REAL)
            checkpoints.append(capture("02-server-became-real-before-refresh", runtime))

            action = runtime.refresh()
            checkpoints.append(capture("03-ordinary-refresh-same-config", runtime, action))

            fresh_thread = ThreadRuntime(state_path)
            checkpoints.append(capture("04-fresh-thread", fresh_thread, "new-thread-runtime"))

            action = runtime.refresh(force_reconnect=True)
            checkpoints.append(capture("05-explicit-reconnect", runtime, action))

            runtime.close()
            restarted = ThreadRuntime(state_path)
            checkpoints.append(capture("06-full-restart", restarted, "new-process-runtime"))

            # Server-identity-only change under the same endpoint and catalogue.
            identity_only = json.loads(json.dumps(REAL))
            identity_only["server_info"]["version"] = "real-3-identity-only"
            write_state(state_path, identity_only)
            action = restarted.refresh()
            checkpoints.append(capture("07-identity-only-ordinary-refresh", restarted, action))

            action = restarted.refresh(force_reconnect=True)
            checkpoints.append(capture("07b-identity-reconnect-control", restarted, action))

            # Catalogue-only change while server identity remains stable.
            catalogue_only = json.loads(json.dumps(identity_only))
            catalogue_only["tools"].append(
                {
                    "name": "new_read_only_tool",
                    "description": "A harmless catalogue-only addition.",
                    "inputSchema": {"type": "object", "properties": {}},
                }
            )
            write_state(state_path, catalogue_only)
            action = restarted.refresh()
            checkpoints.append(capture("08-catalogue-only-ordinary-refresh", restarted, action))

            # A connection-config identity change forces a fresh startup/list.
            action = restarted.refresh(connection_identity="stdio:bridge:config-v2")
            checkpoints.append(capture("09-connection-config-change", restarted, action))

            payload = {
                "experiment": "L04-mcp-app-catalogue-convergence",
                "source_revision": SOURCE_REVISION,
                "environment": {
                    "python": sys.version.split()[0],
                    "platform": sys.platform,
                },
                "checkpoints": [checkpoint.as_dict() for checkpoint in checkpoints],
                "assertions": {
                    "ordinary_refresh_reused_client": checkpoints[2].refresh_action == "reused",
                    "first_stale_layer_after_transition": "binding",
                    "fresh_thread_converged": checkpoints[3].global_tools == checkpoints[3].bound_tools,
                    "explicit_reconnect_converged": checkpoints[4].global_tools == checkpoints[4].bound_tools,
                    "full_restart_converged": checkpoints[5].global_tools == checkpoints[5].bound_tools,
                    "identity_change_ignored_by_ordinary_refresh": (
                        checkpoints[6].global_server_info != checkpoints[6].bound_server_info
                    ),
                    "identity_reconnect_converged": (
                        checkpoints[7].global_server_info == checkpoints[7].bound_server_info
                    ),
                    "catalogue_change_ignored_by_ordinary_refresh": (
                        checkpoints[8].global_tools != checkpoints[8].bound_tools
                    ),
                    "config_identity_change_converged": checkpoints[9].global_tools == checkpoints[9].bound_tools,
                    "router_and_model_agree_each_step": all(
                        checkpoint.registered_tools == checkpoint.advertised_tools
                        for checkpoint in checkpoints
                    ),
                },
            }
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return payload
        finally:
            for candidate in (fresh_thread, restarted):
                if candidate is not None:
                    try:
                        candidate.close()
                    except Exception:
                        pass
            try:
                runtime.close()
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "results" / "latest.json"))
    args = parser.parse_args()
    payload = run_probe(Path(args.output))
    failed = [name for name, ok in payload["assertions"].items() if isinstance(ok, bool) and not ok]
    if failed:
        print(json.dumps({"failed": failed}, indent=2))
        return 1
    print(json.dumps(payload["assertions"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
