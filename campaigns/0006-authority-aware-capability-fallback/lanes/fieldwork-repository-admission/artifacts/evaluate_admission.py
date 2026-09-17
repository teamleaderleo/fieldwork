#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Final

DECISION_READY: Final = "ready"
DECISION_DEGRADED: Final = "degraded_read_only"
DECISION_APPROVAL: Final = "require_explicit_approval"
DECISION_BLOCKED: Final = "blocked"

PHASES: Final = (
    "advertised",
    "registered",
    "discoverable",
    "callable",
    "executable",
)
PHASE_VALUES: Final = {"present", "absent", "unknown"}
INPUT_KEYS: Final = {
    "version",
    "request_id",
    "operation_kind",
    "required_capabilities",
    "observations",
    "fallbacks",
}
CAPABILITY_KEYS: Final = {"id", "capability_kind"}
OBSERVATION_KEYS: Final = {"id", "route_provenance", "phases"}
FALLBACK_KEYS: Final = {"capability_id", "classifier_input"}
FALLBACK_INPUT_KEYS: Final = {
    "operation_kind",
    "logical_operation_id",
    "original_call_id",
    "typed_absence_reason",
    "original_execution_certainty",
    "captured_binding_generation",
    "proposed_binding_generation",
    "proposed_route_provenance",
    "preserves_logical_operation_identity",
    "reversible",
    "authority_deltas",
}
FALLBACK_STRING_KEYS: Final = {
    "logical_operation_id",
    "original_call_id",
    "typed_absence_reason",
    "original_execution_certainty",
    "captured_binding_generation",
    "proposed_binding_generation",
    "proposed_route_provenance",
}
AUTHORITY_DELTA_KEYS: Final = {"field", "relation"}
AUTHORITY_RELATIONS: Final = {"equal", "narrower", "changed", "broader", "weaker"}
REQUIRED_AUTHORITY_FIELDS: Final = {
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


def repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def load_fallback_classifier() -> Callable[[dict[str, Any]], Any]:
    path = (
        repository_root()
        / "campaigns"
        / "0006-authority-aware-capability-fallback"
        / "artifacts"
        / "classify_fallback.py"
    )
    spec = importlib.util.spec_from_file_location(
        "fieldwork_authority_fallback_classifier",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load fallback classifier from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    classify = getattr(module, "classify", None)
    if not callable(classify):
        raise RuntimeError("fallback classifier does not export classify")
    return classify


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(
            f"{label} keys differ; missing={missing}, unknown={unknown}"
        )


def nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def parse_capabilities(raw: Any) -> dict[str, str]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("required_capabilities must be a non-empty list")
    capabilities: dict[str, str] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"required_capabilities[{index}] must be an object")
        exact_keys(item, CAPABILITY_KEYS, f"required_capabilities[{index}]")
        capability_id = nonempty_string(item["id"], "capability id")
        kind = item["capability_kind"]
        if kind not in {"read", "potential_mutation"}:
            raise ValueError(
                f"capability {capability_id} has invalid capability_kind"
            )
        if capability_id in capabilities:
            raise ValueError(f"duplicate capability {capability_id}")
        capabilities[capability_id] = kind
    return capabilities


def parse_observations(raw: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("observations must be a list")
    observations: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"observations[{index}] must be an object")
        exact_keys(item, OBSERVATION_KEYS, f"observations[{index}]")
        capability_id = nonempty_string(item["id"], "observation id")
        if capability_id in observations:
            raise ValueError(f"duplicate observation {capability_id}")
        route = nonempty_string(
            item["route_provenance"],
            f"observation {capability_id} route_provenance",
        )
        phases = item["phases"]
        if not isinstance(phases, dict):
            raise ValueError(f"observation {capability_id} phases must be an object")
        exact_keys(phases, set(PHASES), f"observation {capability_id} phases")
        first_nonpresent: str | None = None
        normalized: dict[str, str] = {}
        for phase in PHASES:
            value = phases[phase]
            if value not in PHASE_VALUES:
                raise ValueError(
                    f"observation {capability_id} phase {phase} is invalid"
                )
            if first_nonpresent is not None and value == "present":
                raise ValueError(
                    f"observation {capability_id} becomes present after "
                    f"{first_nonpresent}"
                )
            if value != "present" and first_nonpresent is None:
                first_nonpresent = phase
            normalized[phase] = value
        observations[capability_id] = {
            "route_provenance": route,
            "phases": normalized,
        }
    return observations


def validate_fallback_input(
    classifier_input: dict[str, Any],
    capability_id: str,
) -> None:
    label = f"fallback {capability_id} classifier_input"
    exact_keys(classifier_input, FALLBACK_INPUT_KEYS, label)
    if classifier_input["operation_kind"] not in {"read", "potential_mutation"}:
        raise ValueError(f"{label} operation_kind is invalid")
    for key in FALLBACK_STRING_KEYS:
        nonempty_string(classifier_input[key], f"{label} {key}")
    if not isinstance(classifier_input["preserves_logical_operation_identity"], bool):
        raise ValueError(
            f"{label} preserves_logical_operation_identity must be a boolean"
        )
    if not isinstance(classifier_input["reversible"], bool):
        raise ValueError(f"{label} reversible must be a boolean")

    raw_deltas = classifier_input["authority_deltas"]
    if not isinstance(raw_deltas, list) or not raw_deltas:
        raise ValueError(f"{label} authority_deltas must be a non-empty list")
    seen_fields: set[str] = set()
    for index, item in enumerate(raw_deltas):
        if not isinstance(item, dict):
            raise ValueError(f"{label} authority_deltas[{index}] must be an object")
        exact_keys(item, AUTHORITY_DELTA_KEYS, f"{label} authority_deltas[{index}]")
        field = nonempty_string(
            item["field"],
            f"{label} authority_deltas[{index}] field",
        )
        if item["relation"] not in AUTHORITY_RELATIONS:
            raise ValueError(
                f"{label} authority_deltas[{index}] relation is invalid"
            )
        if field in seen_fields:
            raise ValueError(f"{label} duplicates authority field {field}")
        seen_fields.add(field)

    if seen_fields != REQUIRED_AUTHORITY_FIELDS:
        missing = sorted(REQUIRED_AUTHORITY_FIELDS - seen_fields)
        unknown = sorted(seen_fields - REQUIRED_AUTHORITY_FIELDS)
        raise ValueError(
            f"fallback {capability_id} authority comparison differs; "
            f"missing={missing}, unknown={unknown}"
        )


def parse_fallbacks(raw: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("fallbacks must be a list")
    fallbacks: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"fallbacks[{index}] must be an object")
        exact_keys(item, FALLBACK_KEYS, f"fallbacks[{index}]")
        capability_id = nonempty_string(item["capability_id"], "fallback capability")
        classifier_input = item["classifier_input"]
        if not isinstance(classifier_input, dict):
            raise ValueError(
                f"fallback {capability_id} classifier_input must be an object"
            )
        validate_fallback_input(classifier_input, capability_id)
        if capability_id in fallbacks:
            raise ValueError(f"duplicate fallback {capability_id}")
        fallbacks[capability_id] = classifier_input
    return fallbacks


def absence_reason(observation: dict[str, Any] | None) -> str | None:
    if observation is None:
        return "capability_observation_missing"
    phases = observation["phases"]
    for phase in PHASES:
        value = phases[phase]
        if value == "absent":
            return f"{phase}_absent"
        if value == "unknown":
            return f"{phase}_unknown"
    return None


def evaluate(request: dict[str, Any]) -> dict[str, Any]:
    exact_keys(request, INPUT_KEYS, "request")
    if type(request["version"]) is not int or request["version"] != 1:
        raise ValueError("version must be primitive integer 1")
    request_id = nonempty_string(request["request_id"], "request_id")
    operation_kind = request["operation_kind"]
    if operation_kind not in {"read", "potential_mutation"}:
        raise ValueError("operation_kind must be read or potential_mutation")

    capabilities = parse_capabilities(request["required_capabilities"])
    observations = parse_observations(request["observations"])
    fallbacks = parse_fallbacks(request["fallbacks"])
    unknown_observations = sorted(set(observations) - set(capabilities))
    unknown_fallbacks = sorted(set(fallbacks) - set(capabilities))
    if unknown_observations:
        raise ValueError(
            f"observations reference unknown capabilities {unknown_observations}"
        )
    if unknown_fallbacks:
        raise ValueError(f"fallbacks reference unknown capabilities {unknown_fallbacks}")

    classify_fallback = load_fallback_classifier()
    receipts: list[dict[str, Any]] = []
    blocked: list[str] = []
    approvals: list[str] = []
    unresolved_mutations: list[str] = []
    executable_reads: list[str] = []

    for capability_id in sorted(capabilities):
        capability_kind = capabilities[capability_id]
        observation = observations.get(capability_id)
        reason = absence_reason(observation)
        receipt: dict[str, Any] = {
            "capability_id": capability_id,
            "capability_kind": capability_kind,
            "route_provenance": (
                observation["route_provenance"] if observation else None
            ),
            "absence_reason": reason,
            "fallback_decision": None,
            "fallback_reason": None,
            "authority_delta_digest": None,
        }
        if reason is None:
            if capability_kind == "read":
                executable_reads.append(capability_id)
            receipts.append(receipt)
            continue

        fallback_input = fallbacks.get(capability_id)
        if fallback_input is not None:
            supplied_reason = fallback_input["typed_absence_reason"]
            if supplied_reason != reason:
                raise ValueError(
                    f"fallback {capability_id} typed_absence_reason "
                    f"{supplied_reason!r} does not match {reason!r}"
                )
            if fallback_input["operation_kind"] != capability_kind:
                raise ValueError(
                    f"fallback {capability_id} operation_kind must match "
                    f"{capability_kind}"
                )
            classification = classify_fallback(fallback_input)
            receipt["fallback_decision"] = classification.decision
            receipt["fallback_reason"] = classification.reason
            receipt["authority_delta_digest"] = classification.authority_delta_digest
            if classification.decision == "fail_closed":
                blocked.append(f"{capability_id}:{classification.reason}")
            elif classification.decision == "require_explicit_approval":
                approvals.append(capability_id)
            elif classification.decision == "allow_equivalent":
                if capability_kind == "read":
                    executable_reads.append(capability_id)
            else:
                raise ValueError(
                    f"fallback {capability_id} returned unknown decision "
                    f"{classification.decision!r}"
                )
            receipts.append(receipt)
            continue

        if capability_kind == "read" or operation_kind == "read":
            blocked.append(f"{capability_id}:{reason}")
        else:
            unresolved_mutations.append(capability_id)
        receipts.append(receipt)

    if unresolved_mutations and not executable_reads:
        blocked.append("read_only_recovery_capability_unavailable")

    if blocked:
        decision = DECISION_BLOCKED
        decision_reason = "required_capability_blocked"
    elif approvals:
        decision = DECISION_APPROVAL
        decision_reason = "fallback_authority_change_requires_approval"
    elif unresolved_mutations:
        decision = DECISION_DEGRADED
        decision_reason = "mutation_capability_missing_read_only_work_remains"
    else:
        decision = DECISION_READY
        decision_reason = "all_required_capabilities_executable_or_equivalent"

    return {
        "version": 1,
        "request_id": request_id,
        "operation_kind": operation_kind,
        "decision": decision,
        "reason": decision_reason,
        "blocked_reasons": sorted(blocked),
        "approval_capabilities": sorted(approvals),
        "unresolved_mutation_capabilities": sorted(unresolved_mutations),
        "capability_receipts": receipts,
    }


def run_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    counts = {
        DECISION_READY: 0,
        DECISION_DEGRADED: 0,
        DECISION_APPROVAL: 0,
        DECISION_BLOCKED: 0,
        "invalid": 0,
    }
    for item in cases:
        if not isinstance(item, dict):
            raise ValueError("each case must be an object")
        case_id = nonempty_string(item.get("id"), "case id")
        request = item.get("request")
        if not isinstance(request, dict):
            raise ValueError(f"case {case_id} request must be an object")
        expected_decision = item.get("expected_decision")
        expected_error = item.get("expected_error")
        try:
            result = evaluate(request)
            decision = result["decision"]
            counts[decision] += 1
            matched = expected_error is None and decision == expected_decision
            error = None
        except (ValueError, RuntimeError) as exc:
            decision = "invalid"
            counts["invalid"] += 1
            error = str(exc)
            matched = isinstance(expected_error, str) and expected_error in error
            result = None
        if not matched:
            failures.append(case_id)
        results.append(
            {
                "id": case_id,
                "expected_decision": expected_decision,
                "expected_error": expected_error,
                "decision": decision,
                "error": error,
                "matched": matched,
                "result": result,
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
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "case_count": output["case_count"],
                "decision_counts": output["decision_counts"],
                "failed_cases": output["failed_cases"],
            },
            sort_keys=True,
        )
    )
    if not output["all_expectations_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
