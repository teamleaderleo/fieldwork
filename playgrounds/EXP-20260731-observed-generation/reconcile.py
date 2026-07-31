#!/usr/bin/env python3
"""Generation-bound, read-only reconciliation model for Fieldwork issue #325.

This is a mechanism probe. It intentionally does not import or claim compatibility
with the moving coordination-state implementation in PR #306.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


Condition = dict[str, Any]


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(*values: object) -> str:
    payload = "\n".join(_canonical(value) for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must be timezone-aware: {value!r}")
    return parsed.astimezone(timezone.utc)


def _condition(
    condition_type: str,
    status: str,
    reason: str,
    message: str,
    inputs: dict[str, object],
    observed_at: str,
) -> Condition:
    if status not in {"True", "False", "Unknown"}:
        raise ValueError(f"unsupported condition status: {status}")
    return {
        "type": condition_type,
        "status": status,
        "reason": reason,
        "message": message,
        "inputs": inputs,
        "observed_at": observed_at,
    }


def projection_is_current(projection: dict[str, Any], spec_generation: str) -> bool:
    """Return whether a projection was computed from the current exact spec."""

    return projection.get("observed_generation") == spec_generation


def _source_review_condition(
    record: dict[str, Any], live_facts: dict[str, Any], observed_at: str
) -> Condition:
    source = record.get("canonical_source")
    review = record.get("review")
    if not isinstance(source, dict):
        return _condition(
            "SourceReviewCurrent",
            "Unknown",
            "NoCanonicalSource",
            "The record has no canonical source to reconcile.",
            {},
            observed_at,
        )

    key = f"{source.get('repository')}:{source.get('branch')}"
    live_head = live_facts.get("source_heads", {}).get(key)
    inputs = {
        "source": key,
        "recorded_head": source.get("head"),
        "live_head": live_head,
        "reviewed_head": review.get("exact_head") if isinstance(review, dict) else None,
    }
    if live_head is None:
        return _condition(
            "SourceReviewCurrent",
            "Unknown",
            "MissingLiveSourceFact",
            "No live source head was available; currentness remains unknown.",
            inputs,
            observed_at,
        )
    if live_head != source.get("head"):
        return _condition(
            "SourceReviewCurrent",
            "False",
            "SourceHeadMoved",
            "The live source head differs from the recorded source generation.",
            inputs,
            observed_at,
        )
    if isinstance(review, dict) and review.get("disposition") not in {None, "none"}:
        if review.get("exact_head") != source.get("head"):
            return _condition(
                "SourceReviewCurrent",
                "False",
                "ReviewHeadMismatch",
                "The review does not bind the recorded canonical source head.",
                inputs,
                observed_at,
            )
    return _condition(
        "SourceReviewCurrent",
        "True",
        "ExactHeadsMatch",
        "The live source, recorded source, and applicable review head match.",
        inputs,
        observed_at,
    )


def _alternative_conditions(
    record: dict[str, Any], live_facts: dict[str, Any], observed_at: str
) -> list[Condition]:
    conditions: list[Condition] = []
    live_heads = live_facts.get("alternative_heads", {})
    for alternative in record.get("alternatives", []):
        alternative_id = alternative["id"]
        live_head = live_heads.get(alternative_id)
        inputs = {
            "alternative_id": alternative_id,
            "recorded_head": alternative.get("head"),
            "live_head": live_head,
            "reviewed_head": alternative.get("review", {}).get("exact_head"),
            "state": alternative.get("state"),
        }
        if live_head is None:
            status, reason, message = (
                "Unknown",
                "MissingAlternativeFact",
                "No live fact was available for this comparison surface.",
            )
        elif live_head != alternative.get("head"):
            status, reason, message = (
                "False",
                "AlternativeHeadMoved",
                "This comparison surface moved beyond its recorded generation.",
            )
        elif alternative.get("review", {}).get("exact_head") != alternative.get("head"):
            status, reason, message = (
                "False",
                "AlternativeReviewMismatch",
                "This comparison surface review does not bind its recorded head.",
            )
        else:
            status, reason, message = (
                "True",
                "AlternativeCurrent",
                "This comparison surface and its review remain current.",
            )
        conditions.append(
            _condition(
                "AlternativeReviewCurrent",
                status,
                reason,
                message,
                inputs,
                observed_at,
            )
        )
    return conditions


def _carrier_condition(record: dict[str, Any], observed_at: str) -> Condition:
    active = [
        carrier
        for carrier in record.get("active_carriers", [])
        if carrier.get("state") == "active"
    ]
    inputs = {
        "invariant_id": record.get("invariant_id"),
        "active_carriers": [carrier.get("id") for carrier in active],
    }
    if len(active) > 1:
        return _condition(
            "CarrierWipValid",
            "False",
            "DuplicateActiveCarriers",
            "More than one carrier is active for the invariant; no carrier was selected silently.",
            inputs,
            observed_at,
        )
    return _condition(
        "CarrierWipValid",
        "True",
        "CarrierLimitSatisfied",
        "The invariant has at most one active execution carrier.",
        inputs,
        observed_at,
    )


def _cross_repository_condition(record: dict[str, Any], observed_at: str) -> Condition:
    parent = record.get("parent_issue")
    source = record.get("canonical_source") or {}
    carriers = record.get("active_carriers", [])
    repositories = [source.get("repository")]
    repositories.extend(carrier.get("repository") for carrier in carriers)
    inputs = {"parent_issue": parent, "repositories": repositories}
    qualified = (
        isinstance(parent, dict)
        and isinstance(parent.get("repository"), str)
        and "/" in parent["repository"]
        and isinstance(parent.get("number"), int)
        and parent["number"] > 0
    )
    identified = all(isinstance(repository, str) and "/" in repository for repository in repositories)
    if qualified and identified:
        return _condition(
            "CrossRepositoryIdentityComplete",
            "True",
            "QualifiedIdentities",
            "Parent issue, source, and carriers have explicit repository identities.",
            inputs,
            observed_at,
        )
    return _condition(
        "CrossRepositoryIdentityComplete",
        "False",
        "AmbiguousRepositoryIdentity",
        "At least one issue, source, or carrier identity requires a repository guess.",
        inputs,
        observed_at,
    )


def _continuity_condition(record: dict[str, Any], observed_at: str) -> Condition:
    if record.get("phase") not in {"stopped", "closed"}:
        return _condition(
            "TerminalContinuityVisible",
            "True",
            "NotTerminal",
            "The record is active, so terminal continuity fields are not required.",
            {"phase": record.get("phase")},
            observed_at,
        )
    terminal = record.get("terminal") or {}
    required = (
        "reason",
        "evidence_boundary",
        "avenues",
        "reopening_triggers",
        "smallest_safe_next_probe",
    )
    missing = [field for field in required if not terminal.get(field)]
    inputs = {"phase": record.get("phase"), "missing": missing}
    if missing:
        return _condition(
            "TerminalContinuityVisible",
            "False",
            "MissingContinuityFields",
            "The terminal record hides retained research continuity.",
            inputs,
            observed_at,
        )
    return _condition(
        "TerminalContinuityVisible",
        "True",
        "ContinuityRetained",
        "The stopped path retains its boundary, avenues, reopening triggers, and next safe probe.",
        inputs,
        observed_at,
    )


def _authority_conditions(
    record: dict[str, Any], live_facts: dict[str, Any], observed_at: str
) -> tuple[list[Condition], dict[str, str]]:
    conditions: list[Condition] = []
    effective: dict[str, str] = {}
    now = _parse_time(observed_at)
    revocations = live_facts.get("authority_revocations", {})
    actions = {
        "merge",
        "release",
        "deploy",
        "upstream_contact",
        "private_or_production_data",
        "material_spending",
    }
    authority = record.get("authority") or {}
    for action in sorted(actions):
        entry = authority.get(action)
        inputs: dict[str, object] = {"action": action}
        if not isinstance(entry, dict):
            effective[action] = "denied"
            conditions.append(
                _condition(
                    "AuthorityUsable",
                    "Unknown",
                    "MissingAuthorityRecord",
                    "Authority is unusable because no current record exists.",
                    inputs,
                    observed_at,
                )
            )
            continue
        inputs.update(
            {
                "state": entry.get("state"),
                "expires_at": entry.get("expires_at"),
                "revocation_record": entry.get("revocation_record"),
            }
        )
        if entry.get("state") != "authorized":
            effective[action] = "denied"
            conditions.append(
                _condition(
                    "AuthorityUsable",
                    "False",
                    "ExplicitlyDenied",
                    "The action is explicitly denied.",
                    inputs,
                    observed_at,
                )
            )
            continue

        expires_at = entry.get("expires_at")
        if expires_at is not None and _parse_time(expires_at) <= now:
            effective[action] = "denied"
            conditions.append(
                _condition(
                    "AuthorityUsable",
                    "False",
                    "AuthorityExpired",
                    "The recorded authorization expired before the observation boundary.",
                    inputs,
                    observed_at,
                )
            )
            continue

        revocation_record = entry.get("revocation_record")
        if revocation_record is not None:
            revoked = revocations.get(revocation_record)
            inputs["revoked"] = revoked
            if revoked is None:
                effective[action] = "denied"
                conditions.append(
                    _condition(
                        "AuthorityUsable",
                        "Unknown",
                        "RevocationUnresolved",
                        "Revocation currentness is unresolved, so the action remains unusable.",
                        inputs,
                        observed_at,
                    )
                )
                continue
            if revoked:
                effective[action] = "denied"
                conditions.append(
                    _condition(
                        "AuthorityUsable",
                        "False",
                        "AuthorityRevoked",
                        "The versioned revocation record is effective.",
                        inputs,
                        observed_at,
                    )
                )
                continue

        effective[action] = "authorized"
        conditions.append(
            _condition(
                "AuthorityUsable",
                "True",
                "AuthorityCurrent",
                "The bounded authorization is current at the observation boundary.",
                inputs,
                observed_at,
            )
        )
    return conditions, effective


def reconcile(
    record: dict[str, Any], live_facts: dict[str, Any], observed_at: str
) -> dict[str, Any]:
    """Produce generation-bound observed conditions without mutating inputs."""

    record_before = _canonical(record)
    facts_before = _canonical(live_facts)
    record_snapshot = deepcopy(record)
    facts_snapshot = deepcopy(live_facts)

    conditions = [
        _source_review_condition(record_snapshot, facts_snapshot, observed_at),
        _carrier_condition(record_snapshot, observed_at),
        _cross_repository_condition(record_snapshot, observed_at),
        _continuity_condition(record_snapshot, observed_at),
    ]
    alternatives = _alternative_conditions(record_snapshot, facts_snapshot, observed_at)
    authority_conditions, effective_authority = _authority_conditions(
        record_snapshot, facts_snapshot, observed_at
    )
    conditions.extend(authority_conditions)

    proposed_repairs: list[str] = []
    for condition in [*conditions, *alternatives]:
        if condition["status"] == "False":
            proposed_repairs.append(f"{condition['type']}: {condition['reason']}")

    result = {
        "record_id": record_snapshot.get("id"),
        "observed_generation": record_snapshot.get("spec_generation"),
        "observed_at": observed_at,
        "input_digest": _digest(record_snapshot, facts_snapshot),
        "conditions": conditions,
        "alternative_conditions": alternatives,
        "effective_authority": effective_authority,
        "proposed_repairs": proposed_repairs,
    }

    if _canonical(record) != record_before or _canonical(live_facts) != facts_before:
        raise RuntimeError("reconciliation mutated a canonical input")
    return result


def render_compact(projection: dict[str, Any]) -> str:
    """Render one deterministic compact pilot view."""

    lines = [
        f"RECORD {projection['record_id']}",
        f"OBSERVED GENERATION {projection['observed_generation']}",
    ]
    for condition in [
        *projection["conditions"],
        *projection["alternative_conditions"],
    ]:
        lines.append(
            f"{condition['status']:7} {condition['type']}: {condition['reason']}"
        )
    denied = sorted(
        action
        for action, state in projection["effective_authority"].items()
        if state != "authorized"
    )
    lines.append("UNUSABLE AUTHORITY " + (", ".join(denied) if denied else "none"))
    return "\n".join(lines) + "\n"
