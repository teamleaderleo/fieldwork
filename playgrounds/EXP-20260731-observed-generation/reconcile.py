#!/usr/bin/env python3
"""Generation-bound, read-only reconciliation model for Fieldwork issue #325.

This remains a mechanism probe. It intentionally does not import or claim
compatibility with the moving coordination-state implementation in PR #306.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any


Condition = dict[str, Any]
GenerationManifest = dict[str, Any]


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


def _active_carriers(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        carrier
        for carrier in record.get("active_carriers", [])
        if carrier.get("state") == "active"
    ]


def input_generation_manifest(
    record: dict[str, Any], live_facts: dict[str, Any]
) -> GenerationManifest:
    """Bind projection identity to labels and canonical input bytes.

    The explicit generation labels are the integration contract. The digests
    make a forgotten label bump fail closed in this deterministic pilot.
    """

    carrier_facts = live_facts.get("carrier_facts", {})
    carrier_generations: dict[str, object] = {}
    for carrier in _active_carriers(record):
        carrier_id = str(carrier.get("id"))
        fact = carrier_facts.get(carrier_id)
        carrier_generations[carrier_id] = (
            fact.get("generation") if isinstance(fact, dict) else None
        )

    return {
        "spec_generation": record.get("spec_generation"),
        "record_digest": _digest(record),
        "finding_generation": record.get("finding_generation"),
        "live_facts_generation": live_facts.get("generation"),
        "live_facts_digest": _digest(live_facts),
        "carrier_generations": carrier_generations,
    }


def _missing_generation_paths(manifest: GenerationManifest) -> list[str]:
    missing = [
        key
        for key in (
            "spec_generation",
            "finding_generation",
            "live_facts_generation",
        )
        if not manifest.get(key)
    ]
    for carrier_id, generation in manifest.get("carrier_generations", {}).items():
        if not generation:
            missing.append(f"carrier_generations.{carrier_id}")
    return missing


def projection_is_current(
    projection: dict[str, Any],
    record_or_manifest: dict[str, Any],
    live_facts: dict[str, Any] | None = None,
) -> bool:
    """Reject movement of any required projection input.

    Callers may supply either the current record and live facts or one already
    constructed generation manifest.
    """

    current = (
        input_generation_manifest(record_or_manifest, live_facts)
        if live_facts is not None
        else record_or_manifest
    )
    return (
        not _missing_generation_paths(current)
        and projection.get("input_generations") == current
    )


def _input_generation_condition(
    manifest: GenerationManifest, observed_at: str
) -> Condition:
    missing = _missing_generation_paths(manifest)
    inputs = {"manifest": manifest, "missing": missing}
    if missing:
        return _condition(
            "InputGenerationsComplete",
            "Unknown",
            "MissingInputGeneration",
            "At least one required spec, finding, live-fact, or carrier generation is absent.",
            inputs,
            observed_at,
        )
    return _condition(
        "InputGenerationsComplete",
        "True",
        "ExactInputGenerations",
        "The projection records exact labels and canonical digests for every required input.",
        inputs,
        observed_at,
    )


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


def _carrier_wip_condition(record: dict[str, Any], observed_at: str) -> Condition:
    active = _active_carriers(record)
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


def _carrier_current_conditions(
    record: dict[str, Any], live_facts: dict[str, Any], observed_at: str
) -> list[Condition]:
    active = _active_carriers(record)
    if not active:
        return [
            _condition(
                "CarrierCurrent",
                "True",
                "NoActiveCarrier",
                "No active carrier requires live reconciliation.",
                {"carrier_id": None},
                observed_at,
            )
        ]

    live = live_facts.get("carrier_facts", {})
    conditions: list[Condition] = []
    for carrier in active:
        carrier_id = str(carrier.get("id"))
        fact = live.get(carrier_id)
        inputs: dict[str, object] = {
            "carrier_id": carrier_id,
            "recorded_repository": carrier.get("repository"),
            "recorded_pull_request": carrier.get("pull_request"),
            "recorded_head": carrier.get("head"),
            "recorded_checks_generation": carrier.get("checks_generation"),
            "live_fact": fact,
        }
        if not isinstance(fact, dict):
            status, reason, message = (
                "Unknown",
                "MissingCarrierFact",
                "No live carrier fact was available.",
            )
        elif fact.get("accessible") is not True:
            status, reason, message = (
                "Unknown",
                "CarrierInaccessible",
                "The carrier could not be observed, so currentness remains unknown.",
            )
        elif (
            fact.get("repository") != carrier.get("repository")
            or fact.get("pull_request") != carrier.get("pull_request")
        ):
            status, reason, message = (
                "False",
                "CarrierIdentityMismatch",
                "The live carrier fact does not identify the recorded repository and pull request.",
            )
        elif fact.get("state") != "open":
            status, reason, message = (
                "False",
                "CarrierClosed",
                "The recorded active carrier is not open in the live fact.",
            )
        elif fact.get("head") != carrier.get("head"):
            status, reason, message = (
                "False",
                "CarrierHeadMoved",
                "The live carrier head differs from the recorded generation.",
            )
        elif not fact.get("generation"):
            status, reason, message = (
                "Unknown",
                "MissingCarrierGeneration",
                "The carrier fact has no exact observation generation.",
            )
        elif not carrier.get("checks_generation") or not fact.get("checks_generation"):
            status, reason, message = (
                "Unknown",
                "MissingCarrierChecksGeneration",
                "The recorded or live check generation is absent.",
            )
        elif fact.get("checks_generation") != carrier.get("checks_generation"):
            status, reason, message = (
                "False",
                "CarrierChecksMoved",
                "The live carrier checks differ from the recorded check generation.",
            )
        else:
            status, reason, message = (
                "True",
                "ExactCarrierFact",
                "The carrier identity, head, open state, and check generation match.",
            )
        conditions.append(
            _condition(
                "CarrierCurrent",
                status,
                reason,
                message,
                inputs,
                observed_at,
            )
        )
    return conditions


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
    identified = all(
        isinstance(repository, str) and "/" in repository
        for repository in repositories
    )
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
            {"phase": record.get("phase"), "continuity": None},
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
    continuity = {field: deepcopy(terminal.get(field)) for field in required}
    inputs = {
        "phase": record.get("phase"),
        "missing": missing,
        "continuity": continuity,
    }
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
        revocation_record = entry.get("revocation_record")
        if expires_at is None and revocation_record is None:
            effective[action] = "denied"
            conditions.append(
                _condition(
                    "AuthorityUsable",
                    "Unknown",
                    "UnboundedAuthority",
                    "Authorization has neither bounded expiry nor a versioned revocation path.",
                    inputs,
                    observed_at,
                )
            )
            continue

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
    """Produce exact-input observed conditions without mutating inputs."""

    record_before = _canonical(record)
    facts_before = _canonical(live_facts)
    record_snapshot = deepcopy(record)
    facts_snapshot = deepcopy(live_facts)
    manifest = input_generation_manifest(record_snapshot, facts_snapshot)

    conditions = [
        _source_review_condition(record_snapshot, facts_snapshot, observed_at),
        _input_generation_condition(manifest, observed_at),
        _carrier_wip_condition(record_snapshot, observed_at),
        *_carrier_current_conditions(record_snapshot, facts_snapshot, observed_at),
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
        "input_generations": manifest,
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
    """Render one deterministic compact pilot view with retained continuity."""

    lines = [
        f"RECORD {projection['record_id']}",
        "INPUT GENERATIONS " + _canonical(projection["input_generations"]),
    ]
    for condition in [
        *projection["conditions"],
        *projection["alternative_conditions"],
    ]:
        lines.append(
            f"{condition['status']:7} {condition['type']}: {condition['reason']}"
        )
        if (
            condition["type"] == "TerminalContinuityVisible"
            and condition["reason"] == "ContinuityRetained"
        ):
            lines.append(
                "TERMINAL CONTINUITY "
                + _canonical(condition["inputs"]["continuity"])
            )
    denied = sorted(
        action
        for action, state in projection["effective_authority"].items()
        if state != "authorized"
    )
    lines.append("UNUSABLE AUTHORITY " + (", ".join(denied) if denied else "none"))
    return "\n".join(lines) + "\n"
