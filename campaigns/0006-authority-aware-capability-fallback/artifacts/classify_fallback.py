#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

DECISION_ALLOW: Final = "allow_equivalent"
DECISION_APPROVE: Final = "require_explicit_approval"
DECISION_FAIL: Final = "fail_closed"

OUTCOME_UNKNOWN_STATES: Final = {
    "ambiguous",
    "local_timeout_outcome_unknown",
    "may_still_run",
    "cancellation_unconfirmed",
    "transport_state_unknown",
}

MUTATION_HARD_FIELDS: Final = {
    "logical_operation_identity",
    "credential_binding",
    "permission_scope",
    "resource_scope",
    "audit_contract",
    "idempotency_contract",
    "rollback_contract",
    "recovery_contract",
}

APPROVAL_FIELDS: Final = {
    "account_binding",
    "provider",
    "approval_subject",
    "actor_delegation",
    "user_visibility",
    "credential_binding",
    "permission_scope",
    "resource_scope",
    "audit_contract",
    "idempotency_contract",
    "rollback_contract",
    "recovery_contract",
}

ALLOWED_RELATIONS: Final = {"equal", "narrower", "changed", "broader", "weaker"}


@dataclass(frozen=True)
class Classification:
    decision: str
    reason: str
    named_delta_codes: tuple[str, ...]
    authority_delta_digest: str

    def to_json(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "named_delta_codes": list(self.named_delta_codes),
            "authority_delta_digest": self.authority_delta_digest,
        }


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_deltas(case: dict[str, Any]) -> list[dict[str, str]]:
    raw = case.get("authority_deltas", [])
    if not isinstance(raw, list):
        raise ValueError("authority_deltas must be a list")

    normalized: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("each authority delta must be an object")
        field = item.get("field")
        relation = item.get("relation")
        if not isinstance(field, str) or not field:
            raise ValueError("authority delta field must be a non-empty string")
        if relation not in ALLOWED_RELATIONS:
            raise ValueError(f"unsupported relation for {field}: {relation!r}")
        normalized.append({"field": field, "relation": relation})

    normalized.sort(key=lambda item: (item["field"], item["relation"]))
    return normalized


def classify(case: dict[str, Any]) -> Classification:
    operation_kind = case.get("operation_kind")
    if operation_kind not in {"read", "potential_mutation"}:
        raise ValueError("operation_kind must be read or potential_mutation")

    logical_operation_id = case.get("logical_operation_id")
    original_call_id = case.get("original_call_id")
    proposed_route = case.get("proposed_route_provenance")
    if not isinstance(logical_operation_id, str) or not logical_operation_id:
        raise ValueError("logical_operation_id is required")
    if not isinstance(original_call_id, str) or not original_call_id:
        raise ValueError("original_call_id is required")

    deltas = normalize_deltas(case)
    delta_codes = tuple(f"{item['field']}:{item['relation']}" for item in deltas)
    digest_input = {
        "logical_operation_id": logical_operation_id,
        "original_call_id": original_call_id,
        "typed_absence_reason": case.get("typed_absence_reason"),
        "captured_binding_generation": case.get("captured_binding_generation"),
        "proposed_binding_generation": case.get("proposed_binding_generation"),
        "proposed_route_provenance": proposed_route,
        "authority_deltas": deltas,
    }
    digest = canonical_digest(digest_input)

    if not isinstance(proposed_route, str) or not proposed_route:
        return Classification(
            decision=DECISION_FAIL,
            reason="no_executable_fallback_route",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    execution_certainty = case.get("original_execution_certainty")
    if operation_kind == "potential_mutation" and execution_certainty in OUTCOME_UNKNOWN_STATES:
        return Classification(
            decision=DECISION_FAIL,
            reason="prior_mutation_reconciliation_required",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    if case.get("preserves_logical_operation_identity") is not True:
        return Classification(
            decision=DECISION_FAIL,
            reason="logical_operation_identity_not_preserved",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    hard_mutation_deltas = {
        item["field"]
        for item in deltas
        if operation_kind == "potential_mutation"
        and item["field"] in MUTATION_HARD_FIELDS
        and item["relation"] in {"broader", "weaker"}
    }
    if hard_mutation_deltas:
        return Classification(
            decision=DECISION_FAIL,
            reason="mutation_authority_or_recovery_weakened",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    if operation_kind == "potential_mutation" and case.get("reversible") is False:
        return Classification(
            decision=DECISION_FAIL,
            reason="irreversible_fallback_without_equivalent_contract",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    approval_deltas = {
        item["field"]
        for item in deltas
        if item["field"] in APPROVAL_FIELDS and item["relation"] == "changed"
    }
    read_broader_or_weaker = {
        item["field"]
        for item in deltas
        if operation_kind == "read"
        and item["field"] in APPROVAL_FIELDS
        and item["relation"] in {"broader", "weaker"}
    }
    if approval_deltas or read_broader_or_weaker:
        return Classification(
            decision=DECISION_APPROVE,
            reason="named_authority_delta_requires_approval",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    remaining_unsafe = [
        item for item in deltas if item["relation"] not in {"equal", "narrower"}
    ]
    if remaining_unsafe:
        return Classification(
            decision=DECISION_APPROVE,
            reason="unclassified_authority_delta_requires_approval",
            named_delta_codes=delta_codes,
            authority_delta_digest=digest,
        )

    return Classification(
        decision=DECISION_ALLOW,
        reason="authority_equal_or_narrower",
        named_delta_codes=delta_codes,
        authority_delta_digest=digest,
    )


def run_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    counts = {DECISION_ALLOW: 0, DECISION_APPROVE: 0, DECISION_FAIL: 0}
    failures: list[str] = []

    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("every case requires a non-empty id")
        classification = classify(case)
        counts[classification.decision] += 1
        expected = case.get("expected_decision")
        matched = classification.decision == expected
        if not matched:
            failures.append(case_id)
        results.append(
            {
                "id": case_id,
                "expected_decision": expected,
                "matched": matched,
                **classification.to_json(),
            }
        )

    return {
        "case_count": len(cases),
        "decision_counts": counts,
        "all_expectations_passed": not failures,
        "failed_cases": failures,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise SystemExit("case file must contain a JSON list")
    output = run_cases(cases)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not output["all_expectations_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
