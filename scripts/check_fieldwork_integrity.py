#!/usr/bin/env python3
"""Validate machine-readable Fieldwork batch contracts."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ALLOWED_BATCH_STATES = {
    "observed",
    "triage",
    "ready",
    "claimed",
    "investigating",
    "blocked",
    "ready-for-synthesis",
    "synthesising",
    "complete",
    "negative-result",
    "dormant",
}

ALLOWED_ASSIGNMENT_STATES = {
    "ready",
    "claimed",
    "investigating",
    "blocked",
    "complete",
    "negative-result",
    "needs-decision",
}

REQUIRED_BATCH_KEYS = {
    "schema_version",
    "batch_id",
    "title",
    "state",
    "coordinator",
    "created_at",
    "purpose",
    "constraints",
    "assignments",
}

REQUIRED_ASSIGNMENT_KEYS = {
    "id",
    "kind",
    "target",
    "source_revision",
    "question",
    "method",
    "deliverable",
    "owned_path",
    "dependencies",
    "state",
    "stop_condition",
    "upstream_contact_authorized",
}


def safe_owned_path(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: invalid JSON: {exc}"]

    missing = REQUIRED_BATCH_KEYS - set(data)
    if missing:
        errors.append(f"{path}: missing batch keys: {sorted(missing)}")
        return errors

    if data["schema_version"] != 1:
        errors.append(f"{path}: schema_version must be 1")

    if data["state"] not in ALLOWED_BATCH_STATES:
        errors.append(f"{path}: unsupported batch state: {data['state']!r}")

    constraints = data["constraints"]
    if not isinstance(constraints, dict):
        errors.append(f"{path}: constraints must be an object")
    elif constraints.get("upstream_contact_authorized") is not False:
        errors.append(
            f"{path}: batch upstream_contact_authorized must remain false as a status field; "
            "live bounded upstream authority is separate under AGENTS.md"
        )

    assignments = data["assignments"]
    if not isinstance(assignments, list):
        errors.append(f"{path}: assignments must be an array")
        return errors

    ids: set[str] = set()
    owned_paths: set[str] = set()

    for index, assignment in enumerate(assignments):
        location = f"assignment[{index}]"
        if not isinstance(assignment, dict):
            errors.append(f"{path}: {location} must be an object")
            continue

        missing_assignment = REQUIRED_ASSIGNMENT_KEYS - set(assignment)
        if missing_assignment:
            errors.append(
                f"{path}: {location} missing keys: {sorted(missing_assignment)}"
            )
            continue

        assignment_id = assignment["id"]
        if not isinstance(assignment_id, str) or not assignment_id:
            errors.append(f"{path}: {location} id must be a non-empty string")
        elif assignment_id in ids:
            errors.append(f"{path}: duplicate assignment id: {assignment_id}")
        else:
            ids.add(assignment_id)

        owned_path = assignment["owned_path"]
        if not safe_owned_path(owned_path):
            errors.append(f"{path}: {location} owned_path is unsafe")
        elif owned_path in owned_paths:
            errors.append(f"{path}: duplicate owned_path: {owned_path}")
        else:
            owned_paths.add(owned_path)

        if assignment["state"] not in ALLOWED_ASSIGNMENT_STATES:
            errors.append(
                f"{path}: {location} unsupported state: {assignment['state']!r}"
            )

        if assignment["upstream_contact_authorized"] is not False:
            errors.append(
                f"{path}: {location} upstream_contact_authorized must remain false as a status field; "
                "live bounded upstream authority is separate under AGENTS.md"
            )

    return errors


def main() -> int:
    errors: list[str] = []
    for manifest in sorted(Path("batches").glob("*/manifest.json")):
        errors.extend(validate_manifest(manifest))

    if errors:
        print("Fieldwork integrity violations:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("Fieldwork integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())