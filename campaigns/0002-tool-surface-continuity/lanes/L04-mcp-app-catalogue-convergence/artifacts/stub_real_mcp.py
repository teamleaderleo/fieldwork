#!/usr/bin/env python3
"""Tiny MCP-shaped JSON-RPC stdio server for catalogue transition tests.

This is deliberately dependency-free and limited to initialize, tools/list,
tools/call, and shutdown. It reads a mutable state file for every request so a
single live connection can observe a server-side catalogue transition.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def response(request_id: Any, result: Any = None, error: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is None:
        payload["result"] = result
    else:
        payload["error"] = error
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    args = parser.parse_args()
    state_path = Path(args.state)

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        request = json.loads(line)
        request_id = request.get("id")
        method = request.get("method")
        state = load_state(state_path)

        if method == "initialize":
            result = {
                "protocolVersion": "2025-06-18",
                "serverInfo": state["server_info"],
                "capabilities": {"tools": {}},
            }
            out = response(request_id, result=result)
        elif method == "tools/list":
            out = response(request_id, result={"tools": state["tools"]})
        elif method == "tools/call":
            params = request.get("params") or {}
            name = params.get("name")
            known = {tool["name"] for tool in state["tools"]}
            if name not in known:
                out = response(
                    request_id,
                    error={"code": -32601, "message": f"unknown tool: {name}"},
                )
            else:
                out = response(
                    request_id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"{state['server_info']['version']}:{name}:ok",
                            }
                        ],
                        "isError": False,
                    },
                )
        elif method == "shutdown":
            out = response(request_id, result={})
            print(json.dumps(out, sort_keys=True), flush=True)
            return 0
        else:
            out = response(
                request_id,
                error={"code": -32601, "message": f"unknown method: {method}"},
            )

        print(json.dumps(out, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
