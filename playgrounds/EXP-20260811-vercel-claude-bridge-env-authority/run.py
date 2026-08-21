#!/usr/bin/env python3

"""Dependency-free discriminator for the source-derived bridge authority chain.

This model preserves only the properties under test:
- bridge transport token/port enter the bridge process environment;
- the Claude runtime inherits that environment in the reviewed configuration;
- a bridge socket is authorized by token equality;
- a new authorized socket replaces the previous active socket;
- replay exposes queued bridge events after a cursor;
- the active authorized socket may answer a pending tool approval.

It does not execute Claude Code, open a real WebSocket, or establish that a model
actually attempted this sequence in an application.
"""

from dataclasses import dataclass, field
import json


BRIDGE_PROCESS_ENV = {
    "BRIDGE_CHANNEL_TOKEN": "synthetic-secret-token",
    "BRIDGE_WS_PORT": "4319",
    "OTHER_INHERITED_VALUE": "present",
}
CALLER_ENV = {"DEPLOYMENT_ENV": "staging"}

# Mirrors `{ ...procEnv, ...start.env }` in the reviewed Claude bridge path.
CLAUDE_RUNTIME_ENV = {**BRIDGE_PROCESS_ENV, **CALLER_ENV}


@dataclass
class Bridge:
    expected_token: str
    active_socket: str | None = None
    pending_approvals: dict[str, bool | None] = field(default_factory=dict)
    event_log: list[dict[str, object]] = field(default_factory=list)

    def connect(self, socket: str, token: str) -> bool:
        if token != self.expected_token:
            return False
        # Mirrors the shared bridge's single-flight replacement rule.
        self.active_socket = socket
        return True

    def request_approval(self, approval_id: str) -> None:
        self.pending_approvals[approval_id] = None
        self.event_log.append(
            {
                "seq": len(self.event_log) + 1,
                "type": "tool-approval-request",
                "approvalId": approval_id,
            }
        )

    def resume(self, socket: str, after_seq: int) -> list[dict[str, object]]:
        if socket != self.active_socket:
            return []
        return [entry for entry in self.event_log if int(entry["seq"]) > after_seq]

    def submit_approval(self, socket: str, approval_id: str, approved: bool) -> bool:
        if socket != self.active_socket:
            return False
        if approval_id not in self.pending_approvals:
            return False
        self.pending_approvals[approval_id] = approved
        return True


def main() -> None:
    bridge = Bridge(expected_token="synthetic-secret-token")
    assert bridge.connect("host", "synthetic-secret-token")
    bridge.request_approval("approval-123")

    unauthorized_connected = bridge.connect("wrong-token-socket", "wrong-token")
    unauthorized_left_host_active = bridge.active_socket == "host"

    authorized_connected = bridge.connect(
        "second-authorized-socket",
        CLAUDE_RUNTIME_ENV["BRIDGE_CHANNEL_TOKEN"],
    )
    replayed = bridge.resume("second-authorized-socket", 0)
    approval_resolved = bridge.submit_approval(
        "second-authorized-socket",
        "approval-123",
        True,
    )

    result = {
        "child_env_contains_token": "BRIDGE_CHANNEL_TOKEN" in CLAUDE_RUNTIME_ENV,
        "child_env_contains_port": "BRIDGE_WS_PORT" in CLAUDE_RUNTIME_ENV,
        "unauthorized_socket_rejected": (
            not unauthorized_connected and unauthorized_left_host_active
        ),
        "authorized_second_socket_replaces_host": (
            authorized_connected and bridge.active_socket == "second-authorized-socket"
        ),
        "replay_exposes_pending_approval_id": any(
            entry.get("approvalId") == "approval-123" for entry in replayed
        ),
        "authorized_socket_can_resolve_pending_approval": (
            approval_resolved
            and bridge.pending_approvals.get("approval-123") is True
        ),
    }

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
