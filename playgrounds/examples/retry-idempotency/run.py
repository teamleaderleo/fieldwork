#!/usr/bin/env python3
"""Simulate ambiguous retries with and without retained request identity."""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any


def fingerprint(payload: Any) -> str:
    rendered = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:16]


def simulate(spec: dict[str, Any]) -> dict[str, Any]:
    mode = spec.get("mode", "idempotent")
    requests = spec.get("requests", [])
    effects: list[dict[str, Any]] = []
    remembered: dict[str, dict[str, Any]] = {}
    attempts: list[dict[str, Any]] = []

    for index, request in enumerate(requests, start=1):
        key = request.get("key")
        payload = request.get("payload")
        digest = fingerprint(payload)
        committed = False
        replayed = False

        if mode == "idempotent" and key:
            existing = remembered.get(key)
            if existing is not None:
                if existing["fingerprint"] != digest:
                    response = {
                        "status": 409,
                        "error": "idempotency-key-reused-with-different-payload",
                    }
                else:
                    response = existing["response"]
                    replayed = True
            else:
                effect = {
                    "sequence": len(effects) + 1,
                    "key": key,
                    "payload": payload,
                }
                effects.append(effect)
                response = {
                    "status": 201,
                    "effect_sequence": effect["sequence"],
                }
                remembered[key] = {
                    "fingerprint": digest,
                    "response": response,
                }
                committed = True
        else:
            effect = {
                "sequence": len(effects) + 1,
                "key": key,
                "payload": payload,
            }
            effects.append(effect)
            response = {
                "status": 201,
                "effect_sequence": effect["sequence"],
            }
            committed = True

        if request.get("response_lost", False):
            client_observation = {
                "transport_error": "response-lost-after-server-processing"
            }
        else:
            client_observation = response

        attempts.append(
            {
                "attempt": index,
                "key": key,
                "committed": committed,
                "replayed": replayed,
                "client_observation": client_observation,
            }
        )

    return {
        "mode": mode,
        "attempt_count": len(attempts),
        "effect_count": len(effects),
        "effects": effects,
        "attempts": attempts,
    }


def main() -> int:
    try:
        spec = json.load(sys.stdin)
        result = simulate(spec)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
