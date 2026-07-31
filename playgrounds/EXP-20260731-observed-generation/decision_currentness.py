#!/usr/bin/env python3
"""Time-bound decision currentness for the issue #325 mechanism pilot.

Exact input identity and present decision usability are separate. A historically
exact projection may remain useful evidence after its time-sensitive authority
conclusions have expired, but it must not continue granting effective authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DecisionCurrentness = dict[str, Any]


def _parse_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("decision time must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("decision time must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _valid_until(projection: dict[str, Any]) -> str | None:
    """Return the earliest expiry supporting a currently authorized decision."""

    candidates: list[tuple[datetime, str]] = []
    for condition in projection.get("conditions", []):
        if not isinstance(condition, dict):
            raise ValueError("projection condition must be a record")
        if (
            condition.get("type") != "AuthorityUsable"
            or condition.get("status") != "True"
            or condition.get("reason") != "AuthorityCurrent"
        ):
            continue
        inputs = condition.get("inputs")
        if not isinstance(inputs, dict):
            raise ValueError("authority condition inputs must be a record")
        expires_at = inputs.get("expires_at")
        if expires_at is None:
            continue
        candidates.append((_parse_time(expires_at), expires_at))
    return min(candidates, key=lambda candidate: candidate[0])[1] if candidates else None


def decision_currentness(
    projection: dict[str, Any], current_at: str
) -> DecisionCurrentness:
    """Evaluate whether time-dependent conclusions remain usable now.

    Invalid timestamps or malformed authority conditions fail closed. This result
    does not replace the existing exact input-generation comparison.
    """

    observed_value = projection.get("observed_at")
    try:
        observed_at = _parse_time(observed_value)
        current = _parse_time(current_at)
        valid_until_value = _valid_until(projection)
        valid_until = (
            _parse_time(valid_until_value) if valid_until_value is not None else None
        )
    except (TypeError, ValueError):
        return {
            "status": "False",
            "reason": "InvalidDecisionTime",
            "observed_at": observed_value,
            "current_at": current_at,
            "valid_until": None,
        }

    if current < observed_at:
        return {
            "status": "False",
            "reason": "ProjectionObservedInFuture",
            "observed_at": observed_value,
            "current_at": current_at,
            "valid_until": valid_until_value,
        }
    if valid_until is not None and current >= valid_until:
        return {
            "status": "False",
            "reason": "DecisionHorizonElapsed",
            "observed_at": observed_value,
            "current_at": current_at,
            "valid_until": valid_until_value,
        }
    return {
        "status": "True",
        "reason": "DecisionCurrent",
        "observed_at": observed_value,
        "current_at": current_at,
        "valid_until": valid_until_value,
    }


def effective_authority_at(
    projection: dict[str, Any], current_at: str
) -> dict[str, str]:
    """Return effective authority only while the projection decision is current."""

    authority = projection.get("effective_authority")
    if not isinstance(authority, dict):
        return {}
    currentness = decision_currentness(projection, current_at)
    if currentness["status"] != "True":
        return {str(action): "denied" for action in authority}
    return {
        str(action): state if state == "authorized" else "denied"
        for action, state in authority.items()
    }
