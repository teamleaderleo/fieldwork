#!/usr/bin/env python3
"""Deterministic authority comparison for capability-loss fallbacks.

The harness has two controllers:

* availability_first: selects the first available path with the requested verb.
  It deliberately models the unsafe baseline where capability continuity is
  treated as sufficient authority.
* authority_guarded: compares the expected and fallback authority envelopes
  before selecting a path.

The fixture uses synthetic resources only and performs no network or external
mutations.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


class Decision(str, Enum):
    ALLOW_EQUIVALENT = "allow_equivalent"
    REQUIRE_EXPLICIT_APPROVAL = "require_explicit_approval"
    FAIL_CLOSED = "fail_closed"


IDENTITY_RANK = {
    "none": 0,
    "call_only": 1,
    "logical_operation_and_call": 2,
}

RECOVERY_RANK = {
    "none": 0,
    "visual_recheck": 1,
    "read_after_write": 2,
    "authoritative_receipt_and_read_after_write": 3,
}


@dataclass(frozen=True)
class Envelope:
    path_class: str
    actor: str
    credential_binding: str
    permissions: frozenset[str]
    resource_scope: frozenset[str]
    approval_contract: str
    operation_identity: str
    logical_operation_id: str | None
    audit_evidence: frozenset[str]
    recovery: str
    provider_semantics: str
    user_visibility: str
    reversible: bool
    delegated_lineage: bool = False
    delegation_preapproved: bool = False

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> "Envelope":
        return cls(
            path_class=value["path_class"],
            actor=value["actor"],
            credential_binding=value["credential_binding"],
            permissions=frozenset(value["permissions"]),
            resource_scope=frozenset(value["resource_scope"]),
            approval_contract=value["approval_contract"],
            operation_identity=value["operation_identity"],
            logical_operation_id=value.get("logical_operation_id"),
            audit_evidence=frozenset(value["audit_evidence"]),
            recovery=value["recovery"],
            provider_semantics=value["provider_semantics"],
            user_visibility=value["user_visibility"],
            reversible=bool(value["reversible"]),
            delegated_lineage=bool(value.get("delegated_lineage", False)),
            delegation_preapproved=bool(value.get("delegation_preapproved", False)),
        )


@dataclass(frozen=True)
class Case:
    case_id: str
    description: str
    operation: str
    expected_tool_available: bool
    fallback_available: bool
    prior_result_state: str
    original: Envelope
    fallback: Envelope
    expected_guarded_decision: Decision

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> "Case":
        return cls(
            case_id=value["case_id"],
            description=value["description"],
            operation=value["operation"],
            expected_tool_available=bool(value["expected_tool_available"]),
            fallback_available=bool(value["fallback_available"]),
            prior_result_state=value["prior_result_state"],
            original=Envelope.from_json(value["original"]),
            fallback=Envelope.from_json(value["fallback"]),
            expected_guarded_decision=Decision(value["expected_guarded_decision"]),
        )


def sorted_list(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def authority_deltas(original: Envelope, fallback: Envelope) -> list[str]:
    deltas: list[str] = []
    if fallback.credential_binding != original.credential_binding:
        deltas.append("credential_binding_changed")
    if not fallback.permissions.issubset(original.permissions):
        deltas.append("permissions_broadened")
    if not fallback.resource_scope.issubset(original.resource_scope):
        deltas.append("resource_scope_broadened")
    if fallback.approval_contract != original.approval_contract:
        deltas.append("approval_contract_changed")
    if fallback.actor != original.actor:
        if not (fallback.delegated_lineage and fallback.delegation_preapproved):
            deltas.append("actor_or_delegation_changed")
    if IDENTITY_RANK[fallback.operation_identity] < IDENTITY_RANK[original.operation_identity]:
        deltas.append("operation_identity_weakened")
    if fallback.logical_operation_id != original.logical_operation_id:
        deltas.append("logical_operation_id_changed")
    if not original.audit_evidence.issubset(fallback.audit_evidence):
        deltas.append("audit_evidence_weakened")
    if RECOVERY_RANK[fallback.recovery] < RECOVERY_RANK[original.recovery]:
        deltas.append("recovery_semantics_weakened")
    if fallback.provider_semantics != original.provider_semantics:
        deltas.append("provider_semantics_changed")
    if fallback.user_visibility != original.user_visibility:
        deltas.append("user_visibility_changed")
    return sorted_list(deltas)


def mutation_has_hard_failure(case: Case, deltas: set[str]) -> bool:
    if case.prior_result_state == "ambiguous":
        return True
    if not case.fallback.reversible:
        return True
    hard = {
        "permissions_broadened",
        "resource_scope_broadened",
        "operation_identity_weakened",
        "logical_operation_id_changed",
        "audit_evidence_weakened",
        "recovery_semantics_weakened",
    }
    if deltas & hard:
        return True
    if case.fallback.credential_binding.startswith("ambient:"):
        return True
    return False


def authority_guarded(case: Case) -> tuple[Decision, list[str]]:
    if case.expected_tool_available:
        return Decision.ALLOW_EQUIVALENT, []
    if not case.fallback_available:
        return Decision.FAIL_CLOSED, ["no_executable_path"]

    deltas = authority_deltas(case.original, case.fallback)
    delta_set = set(deltas)

    if case.operation == "mutation" and mutation_has_hard_failure(case, delta_set):
        if case.prior_result_state == "ambiguous":
            deltas = sorted_list([*deltas, "prior_result_ambiguous"])
        if not case.fallback.reversible:
            deltas = sorted_list([*deltas, "fallback_irreversible"])
        return Decision.FAIL_CLOSED, deltas

    if deltas:
        return Decision.REQUIRE_EXPLICIT_APPROVAL, deltas

    return Decision.ALLOW_EQUIVALENT, []


def availability_first(case: Case) -> dict[str, Any]:
    if case.expected_tool_available:
        return {"selected": "expected", "silent_reroute": False}
    if case.fallback_available:
        return {"selected": "fallback", "silent_reroute": True}
    return {"selected": "none", "silent_reroute": False}


def run(cases: list[Case]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    failures: list[str] = []

    for case in cases:
        baseline = availability_first(case)
        guarded_decision, deltas = authority_guarded(case)
        passed = guarded_decision == case.expected_guarded_decision
        if not passed:
            failures.append(case.case_id)
        records.append(
            {
                "case_id": case.case_id,
                "description": case.description,
                "operation": case.operation,
                "expected_path": case.original.path_class,
                "fallback_path": case.fallback.path_class,
                "availability_first": baseline,
                "authority_guarded": {
                    "decision": guarded_decision.value,
                    "authority_deltas": deltas,
                },
                "expected_guarded_decision": case.expected_guarded_decision.value,
                "passed": passed,
            }
        )

    counts = {decision.value: 0 for decision in Decision}
    for record in records:
        counts[record["authority_guarded"]["decision"]] += 1

    return {
        "schema_version": 1,
        "fixture_kind": "synthetic_authority_fallback",
        "network_used": False,
        "external_mutations": False,
        "case_count": len(records),
        "availability_first_silent_reroutes": sum(
            1 for record in records if record["availability_first"]["silent_reroute"]
        ),
        "authority_guarded_counts": counts,
        "all_expectations_passed": not failures,
        "failed_cases": failures,
        "cases": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = json.loads(args.cases.read_text(encoding="utf-8"))
    cases = [Case.from_json(value) for value in raw["cases"]]
    result = run(cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_expectations_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
