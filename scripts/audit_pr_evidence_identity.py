#!/usr/bin/env python3
"""Classify the commit identity exercised by a workflow checkout."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PULL_REQUEST_REF_RE = re.compile(r"^refs/pull/[1-9][0-9]*/merge$")
PUSH_REF_RE = re.compile(r"^refs/heads/[^\s]+$")
CLASSIFICATIONS = {"exact-head", "synthetic-merge-ref", "other-checkout"}
TECHNICAL_GATE_OUTCOMES = {"success", "failure", "cancelled", "skipped"}
ZERO_SHA = "0" * 40

INPUT_KEYS = {
    "checkout_sha",
    "head_sha",
    "event_base_sha",
    "observed_base_sha",
    "event_before_sha",
    "push_forced",
    "event_sha",
    "parents",
    "event_name",
    "ref",
    "head_ref",
    "base_ref",
    "run_id",
    "run_attempt",
    "expected",
    "technical_gate_name",
    "technical_gate_commands",
}


class IdentityError(ValueError):
    """Raised when an identity receipt is malformed or contradictory."""


@dataclass(frozen=True)
class TechnicalCommandReceipt:
    command: str
    outcome: str


@dataclass(frozen=True)
class IdentityReceipt:
    schema_version: int
    classification: str
    checkout_sha: str
    head_sha: str
    event_base_sha: str | None
    observed_base_sha: str | None
    merge_base_sha: str | None
    event_base_current: bool | None
    merge_base_current: bool | None
    event_merge_base_match: bool | None
    event_before_sha: str | None
    push_update_kind: str | None
    event_sha: str
    parents: tuple[str, ...]
    event_name: str
    ref: str
    head_ref: str
    base_ref: str
    run_id: str
    run_attempt: str
    technical_gate_name: str
    technical_gate_commands: tuple[TechnicalCommandReceipt, ...]
    technical_gate_outcome: str
    reusable_evidence: bool
    current_integration_evidence: bool | None


def _require_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str:
        raise IdentityError(f"{field} must be an exact string")
    if not allow_empty and not value:
        raise IdentityError(f"{field} must be nonempty")
    return value


def _require_sha(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if SHA_RE.fullmatch(text) is None:
        raise IdentityError(f"{field} must be a lowercase 40-hex commit SHA")
    return text


def _require_branch_name(value: str, field: str) -> None:
    if not value or any(character.isspace() for character in value):
        raise IdentityError(f"{field} must be a nonempty Git branch name")


def _require_null(value: Any, field: str) -> None:
    if value is not None:
        raise IdentityError(f"{field} must be null for this event")


def _require_commands(value: Any) -> tuple[TechnicalCommandReceipt, ...]:
    if type(value) is not list or not value:
        raise IdentityError("technical_gate_commands must be a nonempty exact list")
    commands: list[TechnicalCommandReceipt] = []
    for index, item in enumerate(value):
        if type(item) is not dict or set(item) != {"command", "outcome"}:
            raise IdentityError(
                f"technical_gate_commands[{index}] must contain command and outcome"
            )
        command = _require_string(
            item["command"], f"technical_gate_commands[{index}].command"
        )
        outcome = _require_string(
            item["outcome"], f"technical_gate_commands[{index}].outcome"
        )
        if outcome not in TECHNICAL_GATE_OUTCOMES:
            raise IdentityError(f"unsupported technical command outcome: {outcome}")
        commands.append(TechnicalCommandReceipt(command, outcome))
    command_names = [item.command for item in commands]
    if len(command_names) != len(set(command_names)):
        raise IdentityError("technical_gate_commands must be unique")
    return tuple(commands)


def _gate_outcome(commands: tuple[TechnicalCommandReceipt, ...]) -> str:
    outcomes = {command.outcome for command in commands}
    if "failure" in outcomes:
        return "failure"
    if "cancelled" in outcomes:
        return "cancelled"
    if outcomes == {"success"}:
        return "success"
    return "skipped"


def _reject_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IdentityError(f"duplicate JSON object member: {key!r}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> None:
    raise IdentityError(f"non-standard JSON constant: {value}")


def _strict_json_loads(text: str) -> Any:
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_nonstandard_constant,
    )


def classify_identity(
    *,
    checkout_sha: Any,
    head_sha: Any,
    event_base_sha: Any,
    event_sha: Any,
    parents: Any,
) -> str:
    checkout = _require_sha(checkout_sha, "checkout_sha")
    head = _require_sha(head_sha, "head_sha")
    event = _require_sha(event_sha, "event_sha")
    if event_base_sha is not None:
        _require_sha(event_base_sha, "event_base_sha")
    if type(parents) not in {list, tuple}:
        raise IdentityError("parents must be an exact list or tuple")
    parent_values = tuple(
        _require_sha(parent, f"parents[{index}]")
        for index, parent in enumerate(parents)
    )
    if len(parent_values) != len(set(parent_values)):
        raise IdentityError("parents must be unique")
    if checkout in parent_values:
        raise IdentityError("checkout commit cannot be its own parent")

    if checkout == head:
        return "exact-head"
    if checkout == event and len(parent_values) == 2 and parent_values[1] == head:
        return "synthetic-merge-ref"
    return "other-checkout"


def build_receipt(data: Any) -> IdentityReceipt:
    if type(data) is not dict:
        raise IdentityError("receipt input must be an exact object")
    unknown = sorted(set(data) - INPUT_KEYS)
    if unknown:
        raise IdentityError(f"receipt input has unknown field {unknown[0]!r}")
    missing = sorted(INPUT_KEYS - set(data))
    if missing:
        raise IdentityError(f"receipt input is missing field {missing[0]!r}")

    checkout_sha = _require_sha(data["checkout_sha"], "checkout_sha")
    head_sha = _require_sha(data["head_sha"], "head_sha")
    event_sha = _require_sha(data["event_sha"], "event_sha")
    event_name = _require_string(data["event_name"], "event_name")
    ref = _require_string(data["ref"], "ref")
    head_ref = _require_string(data["head_ref"], "head_ref", allow_empty=True)
    base_ref = _require_string(data["base_ref"], "base_ref", allow_empty=True)

    event_base_sha: str | None
    observed_base_sha: str | None
    merge_base_sha: str | None
    event_base_current: bool | None
    merge_base_current: bool | None
    event_merge_base_match: bool | None
    event_before_sha: str | None
    push_update_kind: str | None

    if event_name == "pull_request":
        if PULL_REQUEST_REF_RE.fullmatch(ref) is None:
            raise IdentityError(
                "pull_request ref must be refs/pull/<positive-number>/merge"
            )
        _require_branch_name(head_ref, "head_ref")
        _require_branch_name(base_ref, "base_ref")
        event_base_sha = _require_sha(data["event_base_sha"], "event_base_sha")
        observed_base_sha = _require_sha(
            data["observed_base_sha"], "observed_base_sha"
        )
        _require_null(data["event_before_sha"], "event_before_sha")
        _require_null(data["push_forced"], "push_forced")
        event_before_sha = None
        push_update_kind = None
        event_base_current = event_base_sha == observed_base_sha
        if head_sha == event_base_sha:
            raise IdentityError(
                "pull_request head_sha and event_base_sha must differ"
            )
        if event_sha in {head_sha, event_base_sha}:
            raise IdentityError(
                "pull_request event_sha must identify a generated object, not a parent"
            )
    elif event_name == "push":
        if PUSH_REF_RE.fullmatch(ref) is None:
            raise IdentityError("push ref must be a refs/heads/<branch> ref")
        if head_ref or base_ref:
            raise IdentityError("push receipts require empty head_ref and base_ref")
        if event_sha != head_sha:
            raise IdentityError("push event_sha must equal head_sha")
        _require_null(data["event_base_sha"], "event_base_sha")
        _require_null(data["observed_base_sha"], "observed_base_sha")
        event_base_sha = None
        observed_base_sha = None
        event_base_current = None
        event_before_sha = _require_sha(
            data["event_before_sha"], "event_before_sha"
        )
        if type(data["push_forced"]) is not bool:
            raise IdentityError("push_forced must be an exact boolean")
        push_forced = data["push_forced"]
        if event_before_sha == ZERO_SHA:
            if push_forced:
                raise IdentityError(
                    "branch-creation push cannot also be marked forced"
                )
            push_update_kind = "branch-created"
        elif push_forced:
            push_update_kind = "forced-update"
        else:
            push_update_kind = "ordinary-update"
    else:
        raise IdentityError(f"unsupported event_name: {event_name}")

    parents_value = data["parents"]
    classification = classify_identity(
        checkout_sha=checkout_sha,
        head_sha=head_sha,
        event_base_sha=event_base_sha,
        event_sha=event_sha,
        parents=parents_value,
    )
    parents = tuple(parents_value)

    if classification == "synthetic-merge-ref":
        if event_name != "pull_request":
            raise IdentityError("synthetic merge classification requires pull_request")
        merge_base_sha = parents[0]
        merge_base_current = merge_base_sha == observed_base_sha
        event_merge_base_match = merge_base_sha == event_base_sha
    else:
        merge_base_sha = None
        merge_base_current = None
        event_merge_base_match = None

    run_id = _require_string(data["run_id"], "run_id")
    run_attempt = _require_string(data["run_attempt"], "run_attempt")
    if not run_id.isdecimal() or int(run_id) <= 0:
        raise IdentityError("run_id must be a positive decimal string")
    if not run_attempt.isdecimal() or int(run_attempt) <= 0:
        raise IdentityError("run_attempt must be a positive decimal string")

    expected = _require_string(data["expected"], "expected")
    if expected not in CLASSIFICATIONS:
        raise IdentityError(f"unsupported expected classification: {expected}")
    if classification != expected:
        raise IdentityError(f"expected {expected}, observed {classification}")

    technical_gate_name = _require_string(
        data["technical_gate_name"], "technical_gate_name"
    )
    technical_gate_commands = _require_commands(data["technical_gate_commands"])
    technical_gate_outcome = _gate_outcome(technical_gate_commands)
    reusable_evidence = (
        technical_gate_outcome == "success"
        and classification in {"exact-head", "synthetic-merge-ref"}
    )
    current_integration_evidence = (
        reusable_evidence and bool(merge_base_current)
        if classification == "synthetic-merge-ref"
        else None
    )

    return IdentityReceipt(
        schema_version=3,
        classification=classification,
        checkout_sha=checkout_sha,
        head_sha=head_sha,
        event_base_sha=event_base_sha,
        observed_base_sha=observed_base_sha,
        merge_base_sha=merge_base_sha,
        event_base_current=event_base_current,
        merge_base_current=merge_base_current,
        event_merge_base_match=event_merge_base_match,
        event_before_sha=event_before_sha,
        push_update_kind=push_update_kind,
        event_sha=event_sha,
        parents=parents,
        event_name=event_name,
        ref=ref,
        head_ref=head_ref,
        base_ref=base_ref,
        run_id=run_id,
        run_attempt=run_attempt,
        technical_gate_name=technical_gate_name,
        technical_gate_commands=technical_gate_commands,
        technical_gate_outcome=technical_gate_outcome,
        reusable_evidence=reusable_evidence,
        current_integration_evidence=current_integration_evidence,
    )


def _read_input(path: str) -> Any:
    if path == "-":
        return _strict_json_loads(sys.stdin.read())
    return _strict_json_loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify a GitHub workflow checkout identity receipt."
    )
    parser.add_argument("input", help="JSON input path, or - for stdin")
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        receipt = build_receipt(_read_input(args.input))
    except (OSError, UnicodeError, json.JSONDecodeError, IdentityError) as error:
        print(f"PR evidence identity error: {error}", file=sys.stderr)
        return 2

    encoded = json.dumps(asdict(receipt), indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
