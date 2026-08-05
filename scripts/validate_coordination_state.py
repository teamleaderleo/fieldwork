#!/usr/bin/env python3
"""Validate Fieldwork structured coordination state records."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable

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
SOURCE_REQUIRED_PHASES = {"delivery-gate-ready", "land-ready"}
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
LEASE_RESOURCE_KINDS = {"branch", "path", "record", "none"}
GENERATION_TYPES = {"git-sha", "sha256", "record-version", "none"}
AUTHORITY_ACTIONS = {
    "merge",
    "release",
    "deploy",
    "upstream_contact",
    "private_or_production_data",
    "material_spending",
}
AUTHORITY_STATES = {"denied", "authorized"}
AUTHORITY_TARGET_KINDS = {
    "repository",
    "pull-request",
    "issue",
    "deployment",
    "data",
    "spend",
    "other",
    "none",
}
AUTHORITY_SOURCE_KINDS = {"user-instruction", "approval-record", "none"}
DATA_CLASSES = {"none", "public", "private", "production", "regulated"}
BOUNDARY_KINDS = {"git-sha", "version", "retrieval"}

SCOPE_KEYS = {"programme", "target", "workstream", "parent_issue"}
REVIEW_KEYS = {"disposition", "exact_head", "reviewed_inputs"}
EVIDENCE_KEYS = {"claim", "level", "receipt", "limit"}
SOURCE_KEYS = {"repository", "branch", "head"}
CARRIER_KEYS = {"repository", "pull_request", "head", "purpose"}
LEASE_KEYS = {
    "state",
    "holder",
    "repository",
    "resource_kind",
    "resource",
    "generation_type",
    "generation",
    "acquired_at",
    "renewed_at",
    "duration_seconds",
    "transition",
    "previous_generation",
    "transfer_record",
}
FRESHNESS_KEYS = {"base_head", "external_boundary", "checked_at"}
BOUNDARY_KEYS = {"kind", "value", "source"}
AUTHORITY_ENTRY_KEYS = {
    "state",
    "action",
    "target",
    "source",
    "issued_at",
    "expires_at",
    "revocation_record",
}
AUTHORITY_TARGET_KEYS = {"kind", "location", "operation_id", "data_class"}
AUTHORITY_SOURCE_KEYS = {"kind", "record", "generation"}
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
    "blocker",
    "next_transition",
    "terminal_record",
}

GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSIONED_INPUT = re.compile(r"^[^@\s]+@[^@\s]+$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nullable_string(value: object) -> bool:
    return value is None or isinstance(value, str)


def positive_integer(value: object) -> bool:
    return type(value) is int and value >= 1


def nonnegative_integer(value: object) -> bool:
    return type(value) is int and value >= 0


def enum_string(value: object, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def exact_git_sha(value: object) -> bool:
    return isinstance(value, str) and GIT_SHA.fullmatch(value) is not None


def exact_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def versioned_reference(value: object) -> bool:
    return isinstance(value, str) and VERSIONED_INPUT.fullmatch(value) is not None


def repository_name(value: object) -> bool:
    return isinstance(value, str) and REPOSITORY.fullmatch(value) is not None


def safe_relative_path(value: object) -> bool:
    if not non_empty_string(value):
        return False
    path = Path(str(value))
    return not path.is_absolute() and ".." not in path.parts


def parse_datetime(value: object) -> datetime | None:
    if not non_empty_string(value):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def parse_timestamp(value: object) -> bool:
    return parse_datetime(value) is not None


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
    errors = exact_keys(value, REVIEW_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    disposition = value["disposition"]
    if not enum_string(disposition, DISPOSITIONS):
        errors.append(f"{location}: unsupported disposition {disposition!r}")
    exact_head = value["exact_head"]
    if exact_head is not None and not exact_git_sha(exact_head):
        errors.append(f"{location}: exact_head must be a full lowercase Git SHA or null")
    inputs = value["reviewed_inputs"]
    if not isinstance(inputs, list) or any(not versioned_reference(item) for item in inputs):
        errors.append(f"{location}: reviewed_inputs must use unique record@generation strings")
    elif len(inputs) != len(set(inputs)):
        errors.append(f"{location}: reviewed_inputs must be unique")
    if disposition == "ACCEPT" and not exact_git_sha(exact_head):
        errors.append(f"{location}: ACCEPT requires an exact Git head")
    return errors


def validate_evidence(path: Path, value: object) -> list[str]:
    location = f"{path}: evidence"
    if not isinstance(value, list):
        return [f"{location}: must be an array"]
    errors: list[str] = []
    for index, item in enumerate(value):
        item_location = f"{location}[{index}]"
        item_errors = exact_keys(item, EVIDENCE_KEYS, item_location)
        errors.extend(item_errors)
        if item_errors or not isinstance(item, dict):
            continue
        if not non_empty_string(item["claim"]):
            errors.append(f"{item_location}: claim must be non-empty")
        if not enum_string(item["level"], EVIDENCE_LEVELS):
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
    errors = exact_keys(value, SOURCE_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not repository_name(value["repository"]):
        errors.append(f"{location}: repository must be owner/name")
    if not non_empty_string(value["branch"]):
        errors.append(f"{location}: branch must be non-empty")
    if not exact_git_sha(value["head"]):
        errors.append(f"{location}: head must be a full lowercase Git SHA")
    return errors


def validate_carrier(path: Path, value: object) -> list[str]:
    location = f"{path}: active_carrier"
    if value is None:
        return []
    errors = exact_keys(value, CARRIER_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not repository_name(value["repository"]):
        errors.append(f"{location}: repository must be owner/name")
    if not positive_integer(value["pull_request"]):
        errors.append(f"{location}: pull_request must be a positive integer")
    if not exact_git_sha(value["head"]):
        errors.append(f"{location}: head must be a full lowercase Git SHA")
    if not non_empty_string(value["purpose"]):
        errors.append(f"{location}: purpose must be non-empty")
    return errors


def validate_generation(kind: object, value: object, location: str) -> list[str]:
    if not enum_string(kind, GENERATION_TYPES):
        return [f"{location}: unsupported generation_type {kind!r}"]
    if kind == "git-sha" and not exact_git_sha(value):
        return [f"{location}: git-sha generation must be a full lowercase Git SHA"]
    if kind == "sha256" and not exact_sha256(value):
        return [f"{location}: sha256 generation must be 64 lowercase hex characters"]
    if kind == "record-version" and not non_empty_string(value):
        return [f"{location}: record-version generation must be non-empty"]
    if kind == "none" and value is not None:
        return [f"{location}: none generation_type requires null generation"]
    return []


def validate_previous_generation(kind: object, value: object, location: str) -> list[str]:
    if value is None:
        return []
    return validate_generation(kind, value, f"{location}.previous_generation")


def validate_lease(path: Path, value: object) -> list[str]:
    location = f"{path}: writer_lease"
    errors = exact_keys(value, LEASE_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    state = value["state"]
    if not enum_string(state, LEASE_STATES):
        return [f"{location}: unsupported lease state {state!r}"]
    resource_kind = value["resource_kind"]
    if not enum_string(resource_kind, LEASE_RESOURCE_KINDS):
        errors.append(f"{location}: unsupported resource_kind {resource_kind!r}")
    generation_type = value["generation_type"]
    errors.extend(validate_generation(generation_type, value["generation"], location))
    if not nonnegative_integer(value["transition"]):
        errors.append(f"{location}: transition must be a nonnegative integer")

    if state == "none":
        null_fields = (
            "holder",
            "repository",
            "resource",
            "generation",
            "acquired_at",
            "renewed_at",
            "duration_seconds",
            "previous_generation",
            "transfer_record",
        )
        if resource_kind != "none" or generation_type != "none":
            errors.append(f"{location}: none lease requires none resource/generation kinds")
        for field in null_fields:
            if value[field] is not None:
                errors.append(f"{location}: none lease requires null {field}")
        if value["transition"] != 0:
            errors.append(f"{location}: none lease requires transition 0")
        return errors

    if not non_empty_string(value["holder"]):
        errors.append(f"{location}: non-none lease requires holder")
    if not repository_name(value["repository"]):
        errors.append(f"{location}: non-none lease requires repository owner/name")
    if resource_kind == "none" or not non_empty_string(value["resource"]):
        errors.append(f"{location}: non-none lease requires typed resource identity")
    elif resource_kind == "path" and not safe_relative_path(value["resource"]):
        errors.append(f"{location}: path lease requires a safe relative resource")
    if generation_type == "none":
        errors.append(f"{location}: non-none lease requires exact generation identity")

    acquired = parse_datetime(value["acquired_at"])
    renewed = parse_datetime(value["renewed_at"])
    if acquired is None:
        errors.append(f"{location}: acquired_at must be timezone-aware ISO-8601")
    if renewed is None:
        errors.append(f"{location}: renewed_at must be timezone-aware ISO-8601")
    if acquired is not None and renewed is not None and renewed < acquired:
        errors.append(f"{location}: renewed_at cannot precede acquired_at")
    if not positive_integer(value["duration_seconds"]):
        errors.append(f"{location}: duration_seconds must be a positive integer")

    transition = value["transition"]
    previous = value["previous_generation"]
    transfer = value["transfer_record"]
    if positive_integer(transition):
        if previous is None:
            errors.append(f"{location}: takeover transition requires previous_generation")
        else:
            errors.extend(validate_previous_generation(generation_type, previous, location))
            if previous == value["generation"]:
                errors.append(f"{location}: takeover must change generation")
        if not versioned_reference(transfer):
            errors.append(f"{location}: takeover transition requires versioned transfer_record")
    else:
        if previous is not None:
            errors.append(f"{location}: initial transition requires null previous_generation")
        if transfer is not None:
            errors.append(f"{location}: initial transition requires null transfer_record")
    return errors


def validate_boundary(path: Path, value: object) -> list[str]:
    location = f"{path}: freshness.external_boundary"
    if value is None:
        return []
    errors = exact_keys(value, BOUNDARY_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    kind = value["kind"]
    if not enum_string(kind, BOUNDARY_KINDS):
        errors.append(f"{location}: unsupported boundary kind {kind!r}")
    elif kind == "git-sha" and not exact_git_sha(value["value"]):
        errors.append(f"{location}: git-sha boundary requires a full lowercase Git SHA")
    elif kind in {"version", "retrieval"} and not non_empty_string(value["value"]):
        errors.append(f"{location}: {kind} boundary requires a non-empty value")
    if not non_empty_string(value["source"]):
        errors.append(f"{location}: source must identify the observed source")
    return errors


def validate_freshness(path: Path, value: object) -> list[str]:
    location = f"{path}: freshness"
    errors = exact_keys(value, FRESHNESS_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if value["base_head"] is not None and not exact_git_sha(value["base_head"]):
        errors.append(f"{location}: base_head must be a full lowercase Git SHA or null")
    errors.extend(validate_boundary(path, value["external_boundary"]))
    if not parse_timestamp(value["checked_at"]):
        errors.append(f"{location}: checked_at must be timezone-aware ISO-8601")
    return errors


def validate_authority_target(value: object, location: str) -> list[str]:
    errors = exact_keys(value, AUTHORITY_TARGET_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not enum_string(value["kind"], AUTHORITY_TARGET_KINDS):
        errors.append(f"{location}: unsupported target kind {value['kind']!r}")
    if not enum_string(value["data_class"], DATA_CLASSES):
        errors.append(f"{location}: unsupported data_class {value['data_class']!r}")
    return errors


def validate_authority_source(value: object, location: str) -> list[str]:
    errors = exact_keys(value, AUTHORITY_SOURCE_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not enum_string(value["kind"], AUTHORITY_SOURCE_KINDS):
        errors.append(f"{location}: unsupported source kind {value['kind']!r}")
    return errors


def validate_authority_entry(path: Path, action: str, value: object) -> list[str]:
    location = f"{path}: authority.{action}"
    errors = exact_keys(value, AUTHORITY_ENTRY_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    state = value["state"]
    if not enum_string(state, AUTHORITY_STATES):
        errors.append(f"{location}: unsupported state {state!r}")
    if value["action"] != action:
        errors.append(f"{location}: action must equal {action!r}")
    errors.extend(validate_authority_target(value["target"], f"{location}.target"))
    errors.extend(validate_authority_source(value["source"], f"{location}.source"))
    target = value["target"] if isinstance(value["target"], dict) else {}
    source = value["source"] if isinstance(value["source"], dict) else {}

    if state == "denied":
        if (
            target.get("kind") != "none"
            or target.get("location") is not None
            or target.get("operation_id") is not None
            or target.get("data_class") != "none"
        ):
            errors.append(f"{location}: denied authority requires an empty target")
        if (
            source.get("kind") != "none"
            or source.get("record") is not None
            or source.get("generation") is not None
        ):
            errors.append(f"{location}: denied authority requires an empty source")
        for field in ("issued_at", "expires_at", "revocation_record"):
            if value[field] is not None:
                errors.append(f"{location}: denied authority requires null {field}")
        return errors

    if (
        target.get("kind") == "none"
        or not non_empty_string(target.get("location"))
        or not non_empty_string(target.get("operation_id"))
    ):
        errors.append(f"{location}: authorized authority requires a typed target and operation_id")
    if (
        source.get("kind") == "none"
        or not non_empty_string(source.get("record"))
        or not non_empty_string(source.get("generation"))
    ):
        errors.append(f"{location}: authorized authority requires a versioned source record")
    issued = parse_datetime(value["issued_at"])
    expires = parse_datetime(value["expires_at"]) if value["expires_at"] is not None else None
    if issued is None:
        errors.append(f"{location}: authorized authority requires issued_at")
    if value["expires_at"] is not None and expires is None:
        errors.append(f"{location}: expires_at must be timezone-aware ISO-8601 or null")
    if issued is not None and expires is not None and expires <= issued:
        errors.append(f"{location}: expires_at must follow issued_at")
    revocation = value["revocation_record"]
    if expires is None and not versioned_reference(revocation):
        errors.append(f"{location}: authorized authority requires expires_at or versioned revocation_record")
    elif revocation is not None and not versioned_reference(revocation):
        errors.append(f"{location}: revocation_record must be record@generation or null")
    if action == "private_or_production_data" and target.get("data_class") not in {
        "private",
        "production",
        "regulated",
    }:
        errors.append(f"{location}: data authority requires private, production, or regulated data_class")
    return errors


def validate_authority(path: Path, value: object) -> list[str]:
    location = f"{path}: authority"
    errors = exact_keys(value, AUTHORITY_ACTIONS, location)
    if errors or not isinstance(value, dict):
        return errors
    for action in sorted(AUTHORITY_ACTIONS):
        errors.extend(validate_authority_entry(path, action, value[action]))
    return errors


def validate_state(path: Path, data: object) -> list[str]:
    errors = exact_keys(data, TOP_LEVEL_KEYS, str(path))
    if errors or not isinstance(data, dict):
        return errors

    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        errors.append(f"{path}: schema_version must be integer 1")
    for key in ("id", "title", "summary", "impact", "invariant_id"):
        if not non_empty_string(data[key]):
            errors.append(f"{path}: {key} must be non-empty")
    if not enum_string(data["priority"], PRIORITIES):
        errors.append(f"{path}: unsupported priority {data['priority']!r}")
    errors.extend(validate_scope(path, data["scope"]))
    if not parse_timestamp(data["state_updated_at"]):
        errors.append(f"{path}: state_updated_at must be timezone-aware ISO-8601")
    if not safe_relative_path(data["canonical_finding"]):
        errors.append(f"{path}: canonical_finding must be a safe relative path")
    phase = data["phase"]
    if not enum_string(phase, PHASES):
        errors.append(f"{path}: unsupported phase {phase!r}")
    if not enum_string(data["work_class"], WORK_CLASSES):
        errors.append(f"{path}: unsupported work_class {data['work_class']!r}")

    errors.extend(validate_review(path, data["review"]))
    errors.extend(validate_evidence(path, data["evidence"]))
    errors.extend(validate_source(path, data["canonical_source"]))
    errors.extend(validate_carrier(path, data["active_carrier"]))
    errors.extend(validate_lease(path, data["writer_lease"]))
    errors.extend(validate_freshness(path, data["freshness"]))
    errors.extend(validate_authority(path, data["authority"]))

    for key in ("blocker", "terminal_record"):
        if not nullable_string(data[key]):
            errors.append(f"{path}: {key} must be a string or null")
    if not isinstance(data["next_transition"], str):
        errors.append(f"{path}: next_transition must be a string")

    review = data["review"] if isinstance(data["review"], dict) else {}
    source = data["canonical_source"]
    carrier = data["active_carrier"]
    lease = data["writer_lease"] if isinstance(data["writer_lease"], dict) else {}

    if phase in ACTIVE_PHASES and not non_empty_string(data["next_transition"]):
        errors.append(f"{path}: active phase requires next_transition")
    if phase in REVIEWED_PHASES:
        if not exact_git_sha(review.get("exact_head")):
            errors.append(f"{path}: review-facing phase requires exact reviewed head")
        if not review.get("reviewed_inputs"):
            errors.append(f"{path}: review-facing phase requires versioned reviewed_inputs")
        if not data["evidence"]:
            errors.append(f"{path}: review-facing phase requires claim-scoped evidence")
        if source is None and (
            phase in SOURCE_REQUIRED_PHASES
            or data["work_class"] not in {"evidence-documentation", "blocked-sensitive"}
        ):
            errors.append(f"{path}: review-facing technical phase requires canonical_source")
        if isinstance(source, dict) and review.get("exact_head") != source.get("head"):
            errors.append(f"{path}: reviewed head must match canonical source head")
    if (
        review.get("disposition") == "ACCEPT"
        and isinstance(source, dict)
        and review.get("exact_head") != source.get("head")
    ):
        errors.append(f"{path}: ACCEPT head must match canonical source head")
    if carrier is not None and source is None:
        errors.append(f"{path}: active_carrier requires canonical_source")
    if phase in {"stopped", "closed"}:
        if not non_empty_string(data["terminal_record"]):
            errors.append(f"{path}: stopped or closed phase requires terminal_record")
        if carrier is not None:
            errors.append(f"{path}: stopped or closed phase cannot retain active_carrier")
        if lease.get("state") == "active":
            errors.append(f"{path}: stopped or closed phase cannot retain active writer lease")
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


def lease_identity(lease: dict[str, Any]) -> tuple[str, str, str]:
    return (lease["repository"], lease["resource_kind"], lease["resource"])


def main() -> int:
    errors: list[str] = []
    ids: dict[str, Path] = {}
    findings: dict[str, Path] = {}
    active_leases: dict[tuple[str, str, str], Path] = {}
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
            identity = lease_identity(lease)
            previous = active_leases.get(identity)
            if previous is not None:
                errors.append(f"{path}: active writer lease duplicates {identity!r} from {previous}")
            else:
                active_leases[identity] = path

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
