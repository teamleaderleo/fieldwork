#!/usr/bin/env python3
"""Narrow successor for malformed canonical authority timestamps.

The parent reconciliation model remains unchanged. This candidate reuses its
exact-input and rendering helpers while isolating malformed ``expires_at``
values per action so unrelated observed conditions remain available.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import reconcile as base


Condition = dict[str, Any]


def _authority_conditions(
    record: dict[str, Any], live_facts: dict[str, Any], observed_at: str
) -> tuple[list[Condition], dict[str, str]]:
    conditions: list[Condition] = []
    effective: dict[str, str] = {}
    now = base._parse_time(observed_at)
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
                base._condition(
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
                base._condition(
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
                base._condition(
                    "AuthorityUsable",
                    "Unknown",
                    "UnboundedAuthority",
                    "Authorization has neither bounded expiry nor a versioned revocation path.",
                    inputs,
                    observed_at,
                )
            )
            continue

        if expires_at is not None:
            try:
                expires = base._parse_time(expires_at)
            except (AttributeError, TypeError, ValueError):
                effective[action] = "denied"
                conditions.append(
                    base._condition(
                        "AuthorityUsable",
                        "Unknown",
                        "InvalidAuthorityTime",
                        "Authorization expiry is malformed, so this action is unusable until the record is repaired.",
                        inputs,
                        observed_at,
                    )
                )
                continue
            if expires <= now:
                effective[action] = "denied"
                conditions.append(
                    base._condition(
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
                    base._condition(
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
                    base._condition(
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
            base._condition(
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
    """Produce parent-compatible output while isolating malformed action time."""

    record_before = base._canonical(record)
    facts_before = base._canonical(live_facts)
    record_snapshot = deepcopy(record)
    facts_snapshot = deepcopy(live_facts)
    manifest = base.input_generation_manifest(record_snapshot, facts_snapshot)

    conditions = [
        base._source_review_condition(record_snapshot, facts_snapshot, observed_at),
        base._input_generation_condition(manifest, observed_at),
        base._carrier_wip_condition(record_snapshot, observed_at),
        *base._carrier_current_conditions(record_snapshot, facts_snapshot, observed_at),
        base._cross_repository_condition(record_snapshot, observed_at),
        base._continuity_condition(record_snapshot, observed_at),
    ]
    alternatives = base._alternative_conditions(
        record_snapshot, facts_snapshot, observed_at
    )
    authority_conditions, effective_authority = _authority_conditions(
        record_snapshot, facts_snapshot, observed_at
    )
    conditions.extend(authority_conditions)

    proposed_repairs: list[str] = []
    for condition in [*conditions, *alternatives]:
        if condition["status"] == "False" or (
            condition["type"] == "AuthorityUsable"
            and condition["reason"] == "InvalidAuthorityTime"
        ):
            proposed_repairs.append(
                f"{condition['type']}: {condition['reason']}"
            )

    result = {
        "record_id": record_snapshot.get("id"),
        "observed_generation": record_snapshot.get("spec_generation"),
        "input_generations": manifest,
        "observed_at": observed_at,
        "input_digest": base._digest(record_snapshot, facts_snapshot),
        "conditions": conditions,
        "alternative_conditions": alternatives,
        "effective_authority": effective_authority,
        "proposed_repairs": proposed_repairs,
    }

    if base._canonical(record) != record_before or base._canonical(live_facts) != facts_before:
        raise RuntimeError("reconciliation mutated a canonical input")
    return result
