#!/usr/bin/env python3
"""Time-bound decision currentness for the issue #325 mechanism pilot.

Exact input identity and present decision usability are separate. A historically
exact projection may remain useful evidence after one time-sensitive authority
conclusion expires, while unrelated current authority remains independently
usable. Effective authority requires both dimensions to remain current.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from reconcile import projection_is_current


DecisionCurrentness = dict[str, Any]
ActionCurrentness = dict[str, dict[str, Any]]
AuthorizationCurrentness = dict[str, Any]


def _parse_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("decision time must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("decision time must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _authority_conditions(projection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    conditions: dict[str, dict[str, Any]] = {}
    for condition in projection.get("conditions", []):
        if not isinstance(condition, dict):
            raise ValueError("projection condition must be a record")
        if condition.get("type") != "AuthorityUsable":
            continue
        inputs = condition.get("inputs")
        if not isinstance(inputs, dict):
            raise ValueError("authority condition inputs must be a record")
        action = inputs.get("action")
        if not isinstance(action, str):
            raise ValueError("authority condition action must be a string")
        if action in conditions:
            raise ValueError(f"duplicate authority condition for {action}")
        conditions[action] = condition
    return conditions


def _action_currentness(
    projection: dict[str, Any], current: datetime
) -> ActionCurrentness:
    authority = projection.get("effective_authority")
    if not isinstance(authority, dict):
        return {}

    conditions = _authority_conditions(projection)
    result: ActionCurrentness = {}
    for raw_action, raw_state in authority.items():
        action = str(raw_action)
        if raw_state != "authorized":
            result[action] = {
                "status": "False",
                "reason": "NotAuthorized",
                "valid_until": None,
            }
            continue

        condition = conditions.get(action)
        if condition is None:
            result[action] = {
                "status": "Unknown",
                "reason": "MissingAuthorityCondition",
                "valid_until": None,
            }
            continue
        if (
            condition.get("status") != "True"
            or condition.get("reason") != "AuthorityCurrent"
        ):
            result[action] = {
                "status": "False",
                "reason": "ProjectedAuthorityUnusable",
                "valid_until": None,
            }
            continue

        inputs = condition["inputs"]
        expires_at = inputs.get("expires_at")
        if expires_at is None:
            result[action] = {
                "status": "True",
                "reason": "GenerationBoundCurrent",
                "valid_until": None,
            }
            continue
        try:
            expiry = _parse_time(expires_at)
        except (TypeError, ValueError):
            result[action] = {
                "status": "False",
                "reason": "InvalidAuthorityTime",
                "valid_until": expires_at,
            }
            continue
        if current >= expiry:
            result[action] = {
                "status": "False",
                "reason": "AuthorityHorizonElapsed",
                "valid_until": expires_at,
            }
            continue
        result[action] = {
            "status": "True",
            "reason": "AuthorityCurrentUntil",
            "valid_until": expires_at,
        }
    return result


def decision_currentness(
    projection: dict[str, Any], current_at: str
) -> DecisionCurrentness:
    """Summarize whether time-dependent conclusions need fresh reconciliation.

    The projection-level status is a refresh signal. Per-action currentness remains
    available in ``actions`` and controls effective authority independently after
    exact input currentness succeeds.
    """

    observed_value = projection.get("observed_at")
    try:
        observed_at = _parse_time(observed_value)
        current = _parse_time(current_at)
    except (TypeError, ValueError):
        return {
            "status": "False",
            "reason": "InvalidDecisionTime",
            "observed_at": observed_value,
            "current_at": current_at,
            "valid_until": None,
            "actions": {},
        }

    if current < observed_at:
        return {
            "status": "False",
            "reason": "ProjectionObservedInFuture",
            "observed_at": observed_value,
            "current_at": current_at,
            "valid_until": None,
            "actions": {},
        }

    try:
        actions = _action_currentness(projection, current)
    except (TypeError, ValueError):
        return {
            "status": "False",
            "reason": "InvalidAuthorityCondition",
            "observed_at": observed_value,
            "current_at": current_at,
            "valid_until": None,
            "actions": {},
        }

    valid_expiries: list[tuple[datetime, str]] = []
    for action in actions.values():
        expires_at = action.get("valid_until")
        if action.get("status") == "True" and expires_at is not None:
            valid_expiries.append((_parse_time(expires_at), expires_at))
    valid_until = (
        min(valid_expiries, key=lambda candidate: candidate[0])[1]
        if valid_expiries
        else None
    )

    refresh_required = any(
        action.get("reason")
        in {
            "AuthorityHorizonElapsed",
            "InvalidAuthorityTime",
            "MissingAuthorityCondition",
        }
        for action in actions.values()
    )
    return {
        "status": "False" if refresh_required else "True",
        "reason": "DecisionRefreshRequired" if refresh_required else "DecisionCurrent",
        "observed_at": observed_value,
        "current_at": current_at,
        "valid_until": valid_until,
        "actions": actions,
    }


def _input_currentness(
    projection: dict[str, Any],
    current_record: dict[str, Any] | None,
    current_live_facts: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(current_record, dict) or not isinstance(current_live_facts, dict):
        return {
            "status": "Unknown",
            "reason": "MissingCurrentInputs",
        }
    if projection_is_current(projection, current_record, current_live_facts):
        return {
            "status": "True",
            "reason": "ExactInputsCurrent",
        }
    return {
        "status": "False",
        "reason": "InputsMovedOrIncomplete",
    }


def authorization_currentness(
    projection: dict[str, Any],
    current_at: str,
    current_record: dict[str, Any] | None,
    current_live_facts: dict[str, Any] | None,
) -> AuthorizationCurrentness:
    """Expose exact-input and time/revocation currentness as separate dimensions."""

    inputs_current = _input_currentness(
        projection,
        current_record,
        current_live_facts,
    )
    decision = decision_currentness(projection, current_at)
    authority = projection.get("effective_authority")
    if not isinstance(authority, dict):
        authority = {}

    actions: dict[str, dict[str, Any]] = {}
    for raw_action, raw_state in authority.items():
        action = str(raw_action)
        decision_action = decision.get("actions", {}).get(action, {})
        effective = (
            "authorized"
            if inputs_current["status"] == "True"
            and raw_state == "authorized"
            and decision_action.get("status") == "True"
            else "denied"
        )
        actions[action] = {
            "inputs_current": inputs_current["status"],
            "decision_current": decision_action.get("status", "Unknown"),
            "decision_reason": decision_action.get(
                "reason",
                decision.get("reason", "UnknownDecisionState"),
            ),
            "effective": effective,
        }

    return {
        "inputs_current": inputs_current,
        "decision_currentness": decision,
        "actions": actions,
    }


def effective_authority_at(
    projection: dict[str, Any],
    current_at: str,
    current_record: dict[str, Any] | None,
    current_live_facts: dict[str, Any] | None,
) -> dict[str, str]:
    """Return authority only when exact inputs and per-action decisions are current."""

    return {
        action: state["effective"]
        for action, state in authorization_currentness(
            projection,
            current_at,
            current_record,
            current_live_facts,
        )["actions"].items()
    }
