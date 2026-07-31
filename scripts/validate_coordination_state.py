#!/usr/bin/env python3
"""Validate Fieldwork structured coordination state records."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

PHASES = {
    "research-active",
    "comparative-evaluation-active",
    "review-ready",
    "design-decision-ready",
    "delivery-gate-ready",
    "land-ready",
    "stopped",
    "closed",
}
ACTIVE_PHASES = PHASES - {"stopped", "closed"}
REVIEWED_PHASES = {
    "review-ready",
    "design-decision-ready",
    "delivery-gate-ready",
    "land-ready",
}
WORK_CLASSES = {
    "owned-product-delivery",
    "upstream-fork-research",
    "execution-carrier",
    "evidence-documentation",
    "blocked-sensitive",
}
PRIORITIES = {"P0", "P1", "P2", "P3", "none"}
DISPOSITIONS = {"ACCEPT", "REPAIR", "HOLD", "EXECUTE", "REJECT", "none"}
EVIDENCE_LEVELS = {
    "source-read",
    "model-executed",
    "target-test-prepared",
    "target-executed",
    "integration-executed",
    "full-gate",
}
LEASE_STATES = {"active", "released", "stale", "superseded", "none"}
AUTHORITY_KEYS = {
    "merge",
    "release",
    "deploy",
    "upstream_contact",
    "private_or_production_data",
    "material_spending",
}
SCOPE_KEYS = {"programme", "target", "workstream", "parent_issue"}
TOP_LEVEL_KEYS = {
    "schema_version",
    "id",
    "title",
    "summary",
    "impact",
    "priority",
    "scope",
    "state_updated_at",
    "invariant_id",
    "canonical_finding",
    "phase",
    "work_class",
    "review",
    "evidence",
    "canonical_source",
    "active_carrier",
    "writer_lease",
    "freshness",
    "authority",
    "authority_record",
    "blocker",
    "next_transition",
    "terminal_record",
}


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nullable_string(value: object) -> bool:
    return value is None or isinstance(value, str)


def positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def safe_relative_path(value: object) -> bool:
    if not non_empty_string(value):
        return False
    path = Path(str(value))
    return not path.is_absolute() and ".." not in path.parts


def parse_timestamp(value: object) -> bool:
    if not non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def exact_keys(value: object, expected: set[str], location: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{location}: must be an object"]
    keys = set(value)
    errors: list[str] = []
    missing = expected - keys
    extra = keys - expected
    if missing:
        errors.append(f"{location}: missing keys: {sorted(missing)}")
    if extra:
        errors.append(f"{location}: unsupported keys: {sorted(extra)}")
    return errors


def validate_scope(path: Path, value: object) -> list[str]:
    location = f"{path}: scope"
    errors = exact_keys(value, SCOPE_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    for key in ("programme", "target", "workstream"):
        if not nullable_string(value[key]):
            errors.append(f"{location}: {key} must be a string or null")
    parent = value["parent_issue"]
    if parent is not None and not positive_integer(parent):
        errors.append(f"{location}: parent_issue must be a positive integer or null")
    return errors


def validate_review(path: Path, value: object) -> list[str]:
    location = f"{path}: review"
    errors = exact_keys(value, {"disposition", "exact_head", "reviewed_inputs"}, location)
    if errors or not isinstance(value, dict):
        return errors
    if value["disposition"] not in DISPOSITIONS:
        errors.append(f"{location}: unsupported disposition {value['disposition']!r}")
    if not nullable_string(value["exact_head"]):
        errors.append(f"{location}: exact_head must be a string or null")
    inputs = value["reviewed_inputs"]
    if not isinstance(inputs, list) or any(not non_empty_string(item) for item in inputs):
        errors.append(f"{location}: reviewed_inputs must contain non-empty strings")
    elif len(inputs) != len(set(inputs)):
        errors.append(f"{location}: reviewed_inputs must be unique")
    if value["disposition"] == "ACCEPT" and not non_empty_string(value["exact_head"]):
        errors.append(f"{location}: ACCEPT requires exact_head")
    return errors


def validate_evidence(path: Path, value: object) -> list[str]:
    location = f"{path}: evidence"
    if not isinstance(value, list):
        return [f"{location}: must be an array"]
    errors: list[str] = []
    for index, item in enumerate(value):
        item_location = f"{location}[{index}]"
        item_errors = exact_keys(item, {"claim", "level", "receipt", "limit"}, item_location)
        errors.extend(item_errors)
        if item_errors or not isinstance(item, dict):
            continue
        if not non_empty_string(item["claim"]):
            errors.append(f"{item_location}: claim must be non-empty")
        if item["level"] not in EVIDENCE_LEVELS:
            errors.append(f"{item_location}: unsupported evidence level {item['level']!r}")
        if not non_empty_string(item["receipt"]):
            errors.append(f"{item_location}: receipt must be non-empty")
        if not non_empty_string(item["limit"]):
            errors.append(f"{item_location}: limit must be non-empty")
    return errors


def validate_source(path: Path, value: object) -> list[str]:
    location = f"{path}: canonical_source"
    if value is None:
        return []
    errors = exact_keys(value, {"repository", "branch", "head"}, location)
    if errors or not isinstance(value, dict):
        return errors
    if not non_empty_string(value["repository"]) or "/" not in value["repository"]:
        errors.append(f"{location}: repository must be owner/name")
    if not non_empty_string(value["branch"]):
        errors.append(f"{location}: branch must be non-empty")
    if not non_empty_string(value["head"]) or len(value["head"]) < 7:
        errors.append(f"{location}: head must identify an exact revision")
    return errors


def validate_carrier(path: Path, value: object) -> list[str]:
    location = f"{path}: active_carrier"
    if value is None:
        return []
    errors = exact_keys(value, {"repository", "pull_request", "head", "purpose"}, location)
    if errors or not isinstance(value, dict):
        return errors
    if not non_empty_string(value["repository"]) or "/" not in value["repository"]:
        errors.append(f"{location}: repository must be owner/name")
    if not positive_integer(value["pull_request"]):
        errors.append(f"{location}: pull_request must be a positive integer")
    if not non_empty_string(value["head"]) or len(value["head"]) < 7:
        errors.append(f"{location}: head must identify an exact revision")
    if not non_empty_string(value["purpose"]):
        errors.append(f"{location}: purpose must be non-empty")
    return errors


def validate_lease(path: Path, value: object) -> list[str]:
    location = f"{path}: writer_lease"
    errors = exact_keys(value, {"worker", "artifact", "state", "transfer_record"}, location)
    if errors or not isinstance(value, dict):
        return errors
    if value["state"] not in LEASE_STATES:
        errors.append(f"{location}: unsupported lease state {value['state']!r}")
    for key in ("worker", "artifact", "transfer_record"):
        if not nullable_string(value[key]):
            errors.append(f"{location}: {key} must be a string or null")
    if value["state"] == "active":
        if not non_empty_string(value["worker"]):
            errors.append(f"{location}: active lease requires worker")
        if not safe_relative_path(value["artifact"]):
            errors.append(f"{location}: active lease requires a safe relative artifact")
    return errors


def validate_freshness(path: Path, value: object) -> list[str]:
    location = f"{path}: freshness"
    errors = exact_keys(value, {"base_head", "upstream_valid_through", "checked_at"}, location)
    if errors or not isinstance(value, dict):
        return errors
    for key in ("base_head", "upstream_valid_through"):
        if not nullable_string(value[key]):
            errors.append(f"{location}: {key} must be a string or null")
    if not parse_timestamp(value["checked_at"]):
        errors.append(f"{location}: checked_at must be a timezone-aware ISO-8601 timestamp")
    return errors


def validate_authority(path: Path, value: object, record: object) -> list[str]:
    location = f"{path}: authority"
    errors = exact_keys(value, AUTHORITY_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    for key in sorted(AUTHORITY_KEYS):
        if not isinstance(value[key], bool):
            errors.append(f"{location}: {key} must be boolean")
    if any(value.get(key) is True for key in AUTHORITY_KEYS) and not non_empty_string(record):
        errors.append(f"{path}: enabled authority requires authority_record")
    return errors


def validate_state(path: Path, data: object) -> list[str]:
    errors = exact_keys(data, TOP_LEVEL_KEYS, str(path))
    if errors or not isinstance(data, dict):
        return errors

    if data["schema_version"] != 1:
        errors.append(f"{path}: schema_version must be 1")
    for key in ("id", "title", "summary", "impact", "invariant_id"):
        if not non_empty_string(data[key]):
            errors.append(f"{path}: {key} must be non-empty")
    if data["priority"] not in PRIORITIES:
        errors.append(f"{path}: unsupported priority {data['priority']!r}")
    errors.extend(validate_scope(path, data["scope"]))
    if not parse_timestamp(data["state_updated_at"]):
        errors.append(f"{path}: state_updated_at must be a timezone-aware ISO-8601 timestamp")
    if not safe_relative_path(data["canonical_finding"]):
        errors.append(f"{path}: canonical_finding must be a safe relative path")
    if data["phase"] not in PHASES:
        errors.append(f"{path}: unsupported phase {data['phase']!r}")
    if data["work_class"] not in WORK_CLASSES:
        errors.append(f"{path}: unsupported work_class {data['work_class']!r}")

    errors.extend(validate_review(path, data["review"]))
    errors.extend(validate_evidence(path, data["evidence"]))
    errors.extend(validate_source(path, data["canonical_source"]))
    errors.extend(validate_carrier(path, data["active_carrier"]))
    errors.extend(validate_lease(path, data["writer_lease"]))
    errors.extend(validate_freshness(path, data["freshness"]))
    errors.extend(validate_authority(path, data["authority"], data["authority_record"]))

    for key in ("authority_record", "blocker", "terminal_record"):
        if not nullable_string(data[key]):
            errors.append(f"{path}: {key} must be a string or null")
    if not isinstance(data["next_transition"], str):
        errors.append(f"{path}: next_transition must be a string")

    phase = data["phase"]
    review = data["review"] if isinstance(data["review"], dict) else {}
    source = data["canonical_source"]
    carrier = data["active_carrier"]
    if phase in ACTIVE_PHASES and not non_empty_string(data["next_transition"]):
        errors.append(f"{path}: active phase requires next_transition")
    if phase == "land-ready":
        if source is None:
            errors.append(f"{path}: land-ready requires canonical_source")
        if review.get("disposition") != "ACCEPT":
            errors.append(f"{path}: land-ready requires ACCEPT disposition")
        if isinstance(source, dict) and review.get("exact_head") != source.get("head"):
            errors.append(f"{path}: land-ready review head must match canonical source head")
    if carrier is not None and source is None:
        errors.append(f"{path}: active_carrier requires canonical_source")
    if phase in {"stopped", "closed"} and not non_empty_string(data["terminal_record"]):
        errors.append(f"{path}: stopped or closed phase requires terminal_record")
    return errors


def load_state(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{path}: invalid JSON: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{path}: root must be an object"]
    return value, []


def discover_paths() -> list[Path]:
    paths = sorted(Path("findings").glob("**/state.json"))
    template = Path("templates/coordination-state.json")
    if template.exists():
        paths.append(template)
    return paths


def main() -> int:
    errors: list[str] = []
    ids: dict[str, Path] = {}
    findings: dict[str, Path] = {}
    active_leases: dict[str, Path] = {}
    active_carriers: dict[str, Path] = {}

    for path in discover_paths():
        state, load_errors = load_state(path)
        errors.extend(load_errors)
        if state is None:
            continue
        state_errors = validate_state(path, state)
        errors.extend(state_errors)
        if state_errors:
            continue

        for value, index, label in (
            (state["id"], ids, "state id"),
            (state["canonical_finding"], findings, "canonical finding"),
        ):
            previous = index.get(value)
            if previous is not None:
                errors.append(f"{path}: duplicate {label} {value!r} from {previous}")
            else:
                index[value] = path

        lease = state["writer_lease"]
        if lease["state"] == "active":
            artifact = lease["artifact"]
            previous = active_leases.get(artifact)
            if previous is not None:
                errors.append(f"{path}: active writer lease duplicates {artifact!r} from {previous}")
            else:
                active_leases[artifact] = path

        if state["active_carrier"] is not None:
            invariant = state["invariant_id"]
            previous = active_carriers.get(invariant)
            if previous is not None:
                errors.append(f"{path}: active carrier duplicates invariant {invariant!r} from {previous}")
            else:
                active_carriers[invariant] = path

    if errors:
        print("Coordination state violations:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("Coordination state validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
