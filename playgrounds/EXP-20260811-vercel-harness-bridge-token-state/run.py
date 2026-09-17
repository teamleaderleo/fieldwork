#!/usr/bin/env python3
"""Dependency-free model of the Vercel AI SDK bridge-token resume contract.

This models only the source-level lifecycle properties under test: custom token
minting on spawn, token serialization on detach, attach reuse, and bridge
coordinate validation. It is not target-native execution.
"""

from __future__ import annotations

import hashlib
import hmac
import json

SANDBOX_ID = "sandbox-1"
SECRET = b"fieldwork-synthetic-secret"

mint_calls: list[str] = []


def mint_bridge_token(sandbox_id: str) -> str:
    mint_calls.append(sandbox_id)
    return hmac.new(SECRET, sandbox_id.encode(), hashlib.sha256).hexdigest()


def start(lifecycle_state: dict | None = None) -> dict:
    coords = None if lifecycle_state is None else lifecycle_state["data"].get("bridge")
    if coords is not None:
        # Current attach path uses the serialized coordinate token directly.
        return {"mode": "attach", "bridgeToken": coords["token"]}

    return {"mode": "spawn", "bridgeToken": mint_bridge_token(SANDBOX_ID)}


def detach(session: dict) -> dict:
    return {
        "type": "resume-session",
        "harnessId": "claude-code",
        "specificationVersion": "harness-v1",
        "data": {
            "bridge": {
                "port": 4000,
                "token": session["bridgeToken"],
                "lastSeenEventId": 7,
                "sandboxId": SANDBOX_ID,
            }
        },
    }


def validate_bridge_coords(state: dict) -> None:
    bridge = state.get("data", {}).get("bridge")
    if bridge is None:
        return
    missing = [
        field
        for field in ("port", "token", "lastSeenEventId")
        if field not in bridge
    ]
    if missing:
        raise ValueError(
            "missing required bridge coordinate field(s): " + ", ".join(missing)
        )


def main() -> None:
    spawned = start()
    resume_state = detach(spawned)
    serialized = json.dumps(resume_state, sort_keys=True)
    attached = start(resume_state)

    scrubbed = json.loads(serialized)
    del scrubbed["data"]["bridge"]["token"]
    try:
        validate_bridge_coords(scrubbed)
        scrubbed_state_validation = "accepted"
    except ValueError as error:
        scrubbed_state_validation = f"rejected: {error}"

    result = {
        "mint_calls_after_spawn_and_attach": len(mint_calls),
        "token_present_in_serialized_resume_state": spawned["bridgeToken"]
        in serialized,
        "attach_reused_serialized_token": attached["bridgeToken"]
        == spawned["bridgeToken"],
        "scrubbed_resume_state_validation": scrubbed_state_validation,
    }

    assert result["mint_calls_after_spawn_and_attach"] == 1
    assert result["token_present_in_serialized_resume_state"] is True
    assert result["attach_reused_serialized_token"] is True
    assert result["scrubbed_resume_state_validation"].startswith("rejected:")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
