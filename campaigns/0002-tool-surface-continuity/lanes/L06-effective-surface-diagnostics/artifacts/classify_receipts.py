#!/usr/bin/env python3
"""Classify the earliest observable effective-tool-surface divergence.

The input is intentionally privacy-safe: counts, stable digests, typed states,
lifecycle metadata, and operation-state enums only. Tool names, schemas,
arguments, prompts, credentials, and provider payloads are outside the model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

# Ordered by causal position, not UI presentation order.
LAYER_ORDER = (
    "host_reconciliation",
    "logical_request",
    "wire_request",
    "global_catalogue",
    "binding",
    "router",
    "model_exposure",
    "discovery",
    "executable",
    "server_completion",
    "result_persistence",
    "client_delivery",
    "display",
    "fallback_authority",
)

VIEW_ORDER = (
    "saved_host",
    "current_host",
    "effective_host",
    "logical_request",
    "wire_request",
    "global_catalogue",
    "binding",
    "router",
    "model_exposure",
    "discovery",
    "executable",
    "server_completion",
    "result_persistence",
    "client_delivery",
    "display",
    "fallback_authority",
)

RECOVERY_BY_REASON = {
    "saved_host_state_wins": "require an explicit preserve/replace/clear/reject host policy before continuation",
    "wire_manifest_omitted": "discard incompatible incremental reuse and send a full first generated request",
    "stale_binding": "relist or reconnect, validate remote identity and catalogue digest, then capture a new binding",
    "deferred_without_loader": "direct-expose the family or reject the request with a typed planner error",
    "required_capability_absent": "stop the intended action and compare any fallback authority before rerouting",
    "result_identity_ambiguous": "pause mutation continuation and reconcile the prior operation before retry",
    "display_underreports_execution": "treat display as stale and refresh its projection without changing execution",
}


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _view(receipt: dict[str, Any], name: str) -> dict[str, Any]:
    return receipt.get("views", {}).get(name, {"state": "unavailable"})


def _is_available(view: dict[str, Any]) -> bool:
    return view.get("state") in {"present", "absent"}


def _different(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if not (_is_available(left) and _is_available(right)):
        return False
    comparable = ("digest", "count", "identity_digest")
    for key in comparable:
        if key in left and key in right and left[key] != right[key]:
            return True
    return left.get("state") != right.get("state")


def classify(receipt: dict[str, Any]) -> dict[str, Any]:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {receipt.get('schema_version')!r}")

    views = receipt.get("views", {})
    unavailable = [name for name in VIEW_ORDER if _view(receipt, name).get("state") == "unavailable"]

    saved = views.get("saved_host")
    current = views.get("current_host")
    effective = views.get("effective_host")
    if saved and current and effective and _different(saved, current):
        winner = effective.get("provenance")
        if winner == "saved_thread":
            return _result(receipt, "host_reconciliation", "saved_host_state_wins", unavailable)

    logical = _view(receipt, "logical_request")
    wire = _view(receipt, "wire_request")
    if _different(logical, wire):
        return _result(receipt, "wire_request", "wire_manifest_omitted", unavailable)

    global_catalogue = _view(receipt, "global_catalogue")
    binding = _view(receipt, "binding")
    if _different(global_catalogue, binding):
        return _result(receipt, "binding", "stale_binding", unavailable)

    exposure = _view(receipt, "model_exposure")
    discovery = _view(receipt, "discovery")
    if exposure.get("deferred_family_count", 0) > 0:
        if discovery.get("state") in {"absent", "unavailable"} or not discovery.get("executable", False):
            return _result(receipt, "discovery", "deferred_without_loader", unavailable)

    executable = _view(receipt, "executable")
    if executable.get("required") is True and executable.get("state") == "absent":
        return _result(receipt, "executable", "required_capability_absent", unavailable)

    completion = _view(receipt, "server_completion")
    persistence = _view(receipt, "result_persistence")
    if completion.get("state") == "present" and persistence.get("identity_state") in {
        "missing",
        "duplicated",
        "reordered",
        "orphaned",
    }:
        return _result(receipt, "result_persistence", "result_identity_ambiguous", unavailable)

    execution = _view(receipt, "executable")
    display = _view(receipt, "display")
    if execution.get("state") == "present" and display.get("state") == "absent":
        return _result(receipt, "display", "display_underreports_execution", unavailable)

    return {
        "receipt_id": receipt["receipt_id"],
        "classification": "no_observed_divergence",
        "first_divergent_layer": None,
        "typed_reason": None,
        "recovery": None,
        "unavailable_views": unavailable,
    }


def _result(receipt: dict[str, Any], layer: str, reason: str, unavailable: list[str]) -> dict[str, Any]:
    return {
        "receipt_id": receipt["receipt_id"],
        "classification": "divergence",
        "first_divergent_layer": layer,
        "typed_reason": reason,
        "recovery": RECOVERY_BY_REASON[reason],
        "unavailable_views": unavailable,
    }


def validate_privacy(receipt: dict[str, Any]) -> list[str]:
    """Reject obvious sensitive or high-cardinality retained fields."""
    forbidden_keys = {
        "prompt",
        "arguments",
        "args",
        "credentials",
        "credential",
        "schema",
        "tool_names",
        "provider_payload",
        "account_id",
        "access_token",
        "secret",
    }
    violations: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else key
                if key.lower() in forbidden_keys:
                    violations.append(child_path)
                walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(receipt, "")
    return violations


def run(input_path: Path, output_path: Path) -> dict[str, Any]:
    document = json.loads(input_path.read_text(encoding="utf-8"))
    receipts = document["receipts"]
    results = []
    for receipt in receipts:
        violations = validate_privacy(receipt)
        if violations:
            raise ValueError(f"privacy violations in {receipt.get('receipt_id')}: {violations}")
        result = classify(receipt)
        expected = receipt.get("expected")
        result["expected_match"] = expected is None or (
            result["first_divergent_layer"] == expected.get("first_divergent_layer")
            and result["typed_reason"] == expected.get("typed_reason")
        )
        results.append(result)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "input_digest": canonical_digest(document),
        "receipt_count": len(receipts),
        "divergence_count": sum(r["classification"] == "divergence" for r in results),
        "healthy_count": sum(r["classification"] == "no_observed_divergence" for r in results),
        "expectation_mismatches": [r["receipt_id"] for r in results if not r["expected_match"]],
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args.input, args.output)
    if summary["expectation_mismatches"]:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(
        f"classified {summary['receipt_count']} receipts: "
        f"{summary['divergence_count']} divergences, {summary['healthy_count']} healthy, 0 mismatches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
