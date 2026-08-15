#!/usr/bin/env python3
"""Validate retained Fieldwork playground experiment metadata."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path("playgrounds")
ID_PATTERN = re.compile(r"EXP-[0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
STATES = {"draft", "running", "complete", "negative-result", "blocked", "promoted"}
NETWORK_POLICIES = {"disabled", "loopback-only", "public-read-only", "explicit"}
CLAIM_SCOPES = {"mechanism", "interface", "integration", "operational", "ecosystem"}
CONTEXT_REQUIRED = {"integration", "operational", "ecosystem"}
EVIDENCE_LABELS = {"Normative", "Documented", "Observed", "Inferred", "Illustrative", "Unknown"}


class ValidationError(ValueError):
    pass


def require_string(data: dict[str, Any], key: str, location: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{location}: {key} must be a non-empty string")
    return value


def validate_relative_path(value: str, location: str, *, allow_outside_experiment: bool = False) -> None:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValidationError(f"{location}: path must be repository-relative without '..'")
    if not allow_outside_experiment and path.parts and path.parts[0] in {"contexts", "campaigns", "batches"}:
        raise ValidationError(f"{location}: result path must stay inside the experiment")


def validate_experiment(directory: Path) -> None:
    metadata_path = directory / "experiment.json"
    if not metadata_path.is_file():
        raise ValidationError(f"{directory}: missing experiment.json")

    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{metadata_path}: unable to load JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"{metadata_path}: metadata must be a JSON object")
    if data.get("schema_version") != 1:
        raise ValidationError(f"{metadata_path}: schema_version must be 1")

    experiment_id = require_string(data, "id", str(metadata_path))
    if not ID_PATTERN.fullmatch(experiment_id):
        raise ValidationError(f"{metadata_path}: invalid experiment id {experiment_id!r}")
    if experiment_id != directory.name:
        raise ValidationError(
            f"{metadata_path}: id {experiment_id!r} must match directory {directory.name!r}"
        )

    require_string(data, "question", str(metadata_path))
    require_string(data, "owner", str(metadata_path))
    require_string(data, "command", str(metadata_path))
    require_string(data, "stop_condition", str(metadata_path))

    created_at = require_string(data, "created_at", str(metadata_path))
    try:
        date.fromisoformat(created_at)
    except ValueError as exc:
        raise ValidationError(f"{metadata_path}: created_at must be YYYY-MM-DD") from exc

    state = data.get("state")
    if state not in STATES:
        raise ValidationError(f"{metadata_path}: unsupported state {state!r}")

    claim_scope = data.get("claim_scope", "mechanism")
    if claim_scope not in CLAIM_SCOPES:
        raise ValidationError(f"{metadata_path}: unsupported claim_scope {claim_scope!r}")

    integration_context = data.get("integration_context")
    if integration_context is not None:
        if not isinstance(integration_context, str) or not integration_context.strip():
            raise ValidationError(
                f"{metadata_path}: integration_context must be a non-empty string or null"
            )
        validate_relative_path(
            integration_context,
            f"{metadata_path}: integration_context",
            allow_outside_experiment=True,
        )
        context_path = Path(integration_context)
        if not context_path.is_file():
            raise ValidationError(
                f"{metadata_path}: integration_context does not exist: {integration_context}"
            )
    elif claim_scope in CONTEXT_REQUIRED:
        raise ValidationError(
            f"{metadata_path}: claim_scope {claim_scope!r} requires integration_context"
        )

    network_policy = data.get("network_policy")
    if network_policy not in NETWORK_POLICIES:
        raise ValidationError(
            f"{metadata_path}: unsupported network_policy {network_policy!r}"
        )

    if data.get("upstream_contact_authorized") is not False:
        raise ValidationError(
            f"{metadata_path}: upstream_contact_authorized must remain false as a status field; "
            "live bounded upstream authority is separate under AGENTS.md"
        )

    environment = data.get("environment")
    if not isinstance(environment, dict):
        raise ValidationError(f"{metadata_path}: environment must be an object")

    sources = data.get("sources")
    if not isinstance(sources, list):
        raise ValidationError(f"{metadata_path}: sources must be an array")
    for index, source in enumerate(sources):
        location = f"{metadata_path}: sources[{index}]"
        if not isinstance(source, dict):
            raise ValidationError(f"{location}: source must be an object")
        require_string(source, "name", location)
        require_string(source, "revision", location)
        retrieved_at = require_string(source, "retrieved_at", location)
        try:
            date.fromisoformat(retrieved_at)
        except ValueError as exc:
            raise ValidationError(f"{location}: retrieved_at must be YYYY-MM-DD") from exc

        url = source.get("url")
        if url is not None and (not isinstance(url, str) or not url.strip()):
            raise ValidationError(f"{location}: url must be a non-empty string when present")
        claim = source.get("claim")
        if claim is not None and (not isinstance(claim, str) or not claim.strip()):
            raise ValidationError(f"{location}: claim must be a non-empty string when present")
        label = source.get("evidence_label")
        if label is not None and label not in EVIDENCE_LABELS:
            raise ValidationError(f"{location}: unsupported evidence_label {label!r}")

    outcomes = data.get("distinguishing_outcomes")
    if not isinstance(outcomes, list):
        raise ValidationError(
            f"{metadata_path}: distinguishing_outcomes must be an array"
        )

    result_paths = data.get("result_paths")
    if not isinstance(result_paths, list):
        raise ValidationError(f"{metadata_path}: result_paths must be an array")
    for index, result_path in enumerate(result_paths):
        if not isinstance(result_path, str) or not result_path.strip():
            raise ValidationError(
                f"{metadata_path}: result_paths[{index}] must be a non-empty string"
            )
        validate_relative_path(
            result_path,
            f"{metadata_path}: result_paths[{index}]",
        )

    promoted_to = data.get("promoted_to")
    if promoted_to is not None and not isinstance(promoted_to, str):
        raise ValidationError(f"{metadata_path}: promoted_to must be string or null")


def main() -> int:
    directories = sorted(path for path in ROOT.glob("EXP-*") if path.is_dir())

    failed = False
    for directory in directories:
        try:
            validate_experiment(directory)
        except ValidationError as exc:
            failed = True
            print(exc, file=sys.stderr)
        else:
            print(f"valid: {directory}")

    if not directories:
        print("No retained experiments found.")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())