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
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

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

DOCUMENT_KEYS = {"schema_version", "source_boundary", "receipts"}
SOURCE_BOUNDARY_KEYS = {
    "public_codex_revision",
    "campaign_issue",
    "fixture_sources",
}
RECEIPT_KEYS = {
    "schema_version",
    "receipt_id",
    "source_lane",
    "transition",
    "request_kind",
    "operation_kind",
    "prior_receipt_digest",
    "views",
    "expected",
}
REQUIRED_RECEIPT_KEYS = {
    "schema_version",
    "receipt_id",
    "transition",
    "request_kind",
    "operation_kind",
    "views",
}
EXPECTED_KEYS = {"first_divergent_layer", "typed_reason"}
VIEW_NAMES = frozenset(VIEW_ORDER)
VIEW_KEYS = {
    "state",
    "count",
    "digest",
    "identity_digest",
    "provenance",
    "required",
    "executable",
    "previous_response",
    "deferred_family_count",
    "identity_state",
    "decision",
    "delta_count",
}
VIEW_STATES = {"present", "absent", "unavailable"}
IDENTITY_STATES = {"complete", "missing", "duplicated", "reordered", "orphaned"}
AUTHORITY_DECISIONS = {
    "allow_equivalent",
    "require_explicit_approval",
    "fail_closed",
}
OPERATION_KINDS = {"read", "mutation", "mixed"}
NONNEGATIVE_INTEGER_VIEW_FIELDS = {"count", "deferred_family_count", "delta_count"}
BOOLEAN_VIEW_FIELDS = {"required", "executable", "previous_response"}
STRING_VIEW_FIELDS = {"digest", "identity_digest", "provenance"}

FORBIDDEN_PRIVACY_KEYS = {
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

RECOVERY_BY_REASON = {
    "saved_host_state_wins": "require an explicit preserve/replace/clear/reject host policy before continuation",
    "wire_manifest_omitted": "discard incompatible incremental reuse and send a full first generated request",
    "stale_binding": "relist or reconnect, validate remote identity and catalogue digest, then capture a new binding",
    "deferred_without_loader": "direct-expose the family or reject the request with a typed planner error",
    "required_capability_absent": "stop the intended action and compare any fallback authority before rerouting",
    "result_identity_ambiguous": "pause mutation continuation and reconcile the prior operation before retry",
    "display_underreports_execution": "treat display as stale and refresh its projection without changing execution",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def canonical_digest(value: Any) -> str:
    return canonical_sha256(value)[:16]


def _reject_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object member {key!r}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_strict_json(path: Path) -> tuple[Any, str]:
    raw_bytes = path.read_bytes()
    text = raw_bytes.decode("utf-8")
    document = json.loads(
        text,
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_nonstandard_constant,
    )
    return document, hashlib.sha256(raw_bytes).hexdigest()


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ValueError(f"{label} must be an object")
    return value


def _reject_unknown_keys(
    value: dict[str, Any], allowed: set[str] | frozenset[str], label: str
) -> None:
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        raise ValueError(f"{label} has unknown field {unknown[0]!r}")


def _require_string(value: Any, label: str, *, nonempty: bool = False) -> str:
    if type(value) is not str:
        raise ValueError(f"{label} must be a string")
    if nonempty and not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _require_positive_integer(value: Any, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def validate_source_boundary(value: Any) -> dict[str, Any]:
    boundary = _require_object(value, "document.source_boundary")
    _reject_unknown_keys(boundary, SOURCE_BOUNDARY_KEYS, "document.source_boundary")
    if "public_codex_revision" in boundary:
        revision = _require_string(
            boundary["public_codex_revision"],
            "document.source_boundary.public_codex_revision",
            nonempty=True,
        )
        if SHA_RE.fullmatch(revision) is None:
            raise ValueError(
                "document.source_boundary.public_codex_revision must be "
                "a lowercase 40-hex commit SHA"
            )
    if "campaign_issue" in boundary:
        _require_positive_integer(
            boundary["campaign_issue"], "document.source_boundary.campaign_issue"
        )
    if "fixture_sources" in boundary:
        sources = boundary["fixture_sources"]
        if type(sources) is not list:
            raise ValueError(
                "document.source_boundary.fixture_sources must be an array"
            )
        validated = [
            _require_positive_integer(
                item, f"document.source_boundary.fixture_sources[{index}]"
            )
            for index, item in enumerate(sources)
        ]
        if len(validated) != len(set(validated)):
            raise ValueError(
                "document.source_boundary.fixture_sources must be unique"
            )
    return boundary


def validate_document(document: Any) -> dict[str, Any]:
    document = _require_object(document, "document")
    _reject_unknown_keys(document, DOCUMENT_KEYS, "document")
    document_schema_version = document.get("schema_version")
    if (
        type(document_schema_version) is not int
        or document_schema_version != SCHEMA_VERSION
    ):
        raise ValueError(
            f"document schema_version must be {SCHEMA_VERSION}, got "
            f"{document_schema_version!r}"
        )
    receipts = document.get("receipts")
    if type(receipts) is not list:
        raise ValueError("document.receipts must be an array")
    if "source_boundary" in document:
        validate_source_boundary(document["source_boundary"])

    seen_receipt_ids: set[str] = set()
    for receipt in receipts:
        validated_receipt = validate_receipt_schema(receipt)
        receipt_id = validated_receipt["receipt_id"]
        if receipt_id in seen_receipt_ids:
            raise ValueError(f"document has duplicate receipt_id {receipt_id!r}")
        seen_receipt_ids.add(receipt_id)
    return document


def validate_receipt_schema(receipt: Any) -> dict[str, Any]:
    receipt = _require_object(receipt, "receipt")
    _reject_unknown_keys(receipt, RECEIPT_KEYS, "receipt")
    missing = sorted(REQUIRED_RECEIPT_KEYS - set(receipt))
    if missing:
        raise ValueError(f"receipt is missing required field {missing[0]!r}")
    receipt_schema_version = receipt["schema_version"]
    if (
        type(receipt_schema_version) is not int
        or receipt_schema_version != SCHEMA_VERSION
    ):
        raise ValueError(f"unsupported schema_version: {receipt_schema_version!r}")

    receipt_id = _require_string(
        receipt["receipt_id"], "receipt.receipt_id", nonempty=True
    )
    _require_string(receipt["transition"], f"receipt {receipt_id!r} transition")
    _require_string(receipt["request_kind"], f"receipt {receipt_id!r} request_kind")
    if receipt["operation_kind"] not in OPERATION_KINDS:
        raise ValueError(
            f"receipt {receipt_id!r} operation_kind must be one of "
            f"{sorted(OPERATION_KINDS)!r}"
        )
    if "source_lane" in receipt:
        _require_string(receipt["source_lane"], f"receipt {receipt_id!r} source_lane")
    if (
        "prior_receipt_digest" in receipt
        and receipt["prior_receipt_digest"] is not None
    ):
        _require_string(
            receipt["prior_receipt_digest"],
            f"receipt {receipt_id!r} prior_receipt_digest",
        )

    views = _require_object(receipt["views"], f"receipt {receipt_id!r} views")
    if not views:
        raise ValueError(f"receipt {receipt_id!r} views must contain an observation")
    unknown_views = sorted(set(views) - VIEW_NAMES)
    if unknown_views:
        raise ValueError(
            f"receipt {receipt_id!r} has unknown view {unknown_views[0]!r}"
        )

    for name, raw_view in views.items():
        label = f"receipt {receipt_id!r} view {name!r}"
        view = _require_object(raw_view, label)
        _reject_unknown_keys(view, VIEW_KEYS, label)
        if "state" not in view:
            raise ValueError(f"{label} is missing required field 'state'")
        if view["state"] not in VIEW_STATES:
            raise ValueError(f"{label}.state must be one of {sorted(VIEW_STATES)!r}")
        for field in NONNEGATIVE_INTEGER_VIEW_FIELDS & set(view):
            value = view[field]
            if type(value) is not int or value < 0:
                raise ValueError(f"{label}.{field} must be a nonnegative integer")
        for field in BOOLEAN_VIEW_FIELDS & set(view):
            if type(view[field]) is not bool:
                raise ValueError(f"{label}.{field} must be boolean")
        for field in STRING_VIEW_FIELDS & set(view):
            _require_string(view[field], f"{label}.{field}")
        if (
            "identity_state" in view
            and view["identity_state"] not in IDENTITY_STATES
        ):
            raise ValueError(
                f"{label}.identity_state must be one of {sorted(IDENTITY_STATES)!r}"
            )
        if "decision" in view and view["decision"] not in AUTHORITY_DECISIONS:
            raise ValueError(
                f"{label}.decision must be one of {sorted(AUTHORITY_DECISIONS)!r}"
            )

    if "expected" in receipt:
        expected = _require_object(
            receipt["expected"], f"receipt {receipt_id!r} expected"
        )
        _reject_unknown_keys(
            expected, EXPECTED_KEYS, f"receipt {receipt_id!r} expected"
        )
        for field in EXPECTED_KEYS:
            if field in expected and expected[field] is not None:
                _require_string(
                    expected[field],
                    f"receipt {receipt_id!r} expected.{field}",
                )
    return receipt


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
    validate_receipt_schema(receipt)

    views = receipt.get("views", {})
    unavailable = [
        name
        for name in VIEW_ORDER
        if _view(receipt, name).get("state") == "unavailable"
    ]

    saved = views.get("saved_host")
    current = views.get("current_host")
    effective = views.get("effective_host")
    if saved and current and effective and _different(saved, current):
        winner = effective.get("provenance")
        if winner == "saved_thread":
            return _result(
                receipt, "host_reconciliation", "saved_host_state_wins", unavailable
            )

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
        if discovery.get("state") in {"absent", "unavailable"} or not discovery.get(
            "executable", False
        ):
            return _result(
                receipt, "discovery", "deferred_without_loader", unavailable
            )

    executable = _view(receipt, "executable")
    if executable.get("required") is True and executable.get("state") == "absent":
        return _result(
            receipt, "executable", "required_capability_absent", unavailable
        )

    completion = _view(receipt, "server_completion")
    persistence = _view(receipt, "result_persistence")
    if completion.get("state") == "present" and persistence.get(
        "identity_state"
    ) in {"missing", "duplicated", "reordered", "orphaned"}:
        return _result(
            receipt, "result_persistence", "result_identity_ambiguous", unavailable
        )

    execution = _view(receipt, "executable")
    display = _view(receipt, "display")
    if execution.get("state") == "present" and display.get("state") == "absent":
        return _result(
            receipt, "display", "display_underreports_execution", unavailable
        )

    return {
        "receipt_id": receipt["receipt_id"],
        "classification": "no_observed_divergence",
        "first_divergent_layer": None,
        "typed_reason": None,
        "recovery": None,
        "unavailable_views": unavailable,
    }


def _result(
    receipt: dict[str, Any], layer: str, reason: str, unavailable: list[str]
) -> dict[str, Any]:
    return {
        "receipt_id": receipt["receipt_id"],
        "classification": "divergence",
        "first_divergent_layer": layer,
        "typed_reason": reason,
        "recovery": RECOVERY_BY_REASON[reason],
        "unavailable_views": unavailable,
    }


def validate_privacy(value: Any) -> list[str]:
    """Reject obvious sensitive or high-cardinality retained fields."""
    violations: list[str] = []

    def walk(child: Any, path: str) -> None:
        if type(child) is dict:
            for key, nested in child.items():
                child_path = f"{path}.{key}" if path else key
                if key.lower() in FORBIDDEN_PRIVACY_KEYS:
                    violations.append(child_path)
                walk(nested, child_path)
        elif type(child) is list:
            for index, nested in enumerate(child):
                walk(nested, f"{path}[{index}]")

    walk(value, "")
    return violations


def run(input_path: Path, output_path: Path) -> dict[str, Any]:
    document, raw_input_sha256 = load_strict_json(input_path)
    violations = validate_privacy(document)
    if violations:
        raise ValueError(f"document privacy violations: {violations}")
    validate_document(document)

    receipts = document["receipts"]
    results = []
    for receipt in receipts:
        result = classify(receipt)
        expected = receipt.get("expected")
        result["expected_match"] = expected is None or (
            result["first_divergent_layer"] == expected.get("first_divergent_layer")
            and result["typed_reason"] == expected.get("typed_reason")
        )
        results.append(result)

    summary = {
        "schema_version": SCHEMA_VERSION,
        # Retained compatibility field.
        "input_digest": canonical_digest(document),
        # Exact byte identity and full semantic identity are separate facts.
        "raw_input_sha256": raw_input_sha256,
        "canonical_input_sha256": canonical_sha256(document),
        "receipt_count": len(receipts),
        "divergence_count": sum(
            result["classification"] == "divergence" for result in results
        ),
        "healthy_count": sum(
            result["classification"] == "no_observed_divergence"
            for result in results
        ),
        "expectation_mismatches": [
            result["receipt_id"] for result in results if not result["expected_match"]
        ],
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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
        f"{summary['divergence_count']} divergences, "
        f"{summary['healthy_count']} healthy, 0 mismatches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
