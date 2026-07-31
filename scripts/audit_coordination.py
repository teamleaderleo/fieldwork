#!/usr/bin/env python3
"""Reconcile tracked Fieldwork coordination state with versioned live facts."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable

import render_coordination_views as views
import validate_coordination_state as state_validator

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
FACT_KEYS = {"schema_version", "generated_at", "refs", "pull_requests", "issues"}
REF_KEYS = {"repository", "branch", "head", "observed_at"}
PR_KEYS = {
    "repository",
    "number",
    "state",
    "draft",
    "head_branch",
    "head",
    "base_branch",
    "base_head",
    "updated_at",
    "checks",
}
CHECK_KEYS = {"name", "status", "conclusion", "run_id", "job_id"}
ISSUE_KEYS = {"repository", "number", "state", "state_text", "labels", "updated_at"}
CHECK_STATUSES = {"queued", "in_progress", "completed"}
CHECK_CONCLUSIONS = {
    "success",
    "failure",
    "cancelled",
    "timed_out",
    "skipped",
    "neutral",
    "action_required",
    None,
}

State = dict[str, Any]
Facts = dict[str, Any]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    state_id: str | None
    message: str
    next_action: str
    evidence: tuple[str, ...]


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


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive_integer_or_null(value: object) -> bool:
    return value is None or (
        isinstance(value, int) and not isinstance(value, bool) and value >= 1
    )


def validate_ref(value: object, location: str) -> list[str]:
    errors = exact_keys(value, REF_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not non_empty_string(value["repository"]) or "/" not in value["repository"]:
        errors.append(f"{location}: repository must be owner/name")
    if not non_empty_string(value["branch"]):
        errors.append(f"{location}: branch must be non-empty")
    if not non_empty_string(value["head"]) or len(value["head"]) < 7:
        errors.append(f"{location}: head must identify an exact revision")
    if not state_validator.parse_timestamp(value["observed_at"]):
        errors.append(f"{location}: observed_at must be an ISO-8601 timestamp")
    return errors


def validate_check(value: object, location: str) -> list[str]:
    errors = exact_keys(value, CHECK_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not non_empty_string(value["name"]):
        errors.append(f"{location}: name must be non-empty")
    if value["status"] not in CHECK_STATUSES:
        errors.append(f"{location}: unsupported status {value['status']!r}")
    if value["conclusion"] not in CHECK_CONCLUSIONS:
        errors.append(f"{location}: unsupported conclusion {value['conclusion']!r}")
    if value["status"] != "completed" and value["conclusion"] is not None:
        errors.append(f"{location}: incomplete checks must have null conclusion")
    if not positive_integer_or_null(value["run_id"]):
        errors.append(f"{location}: run_id must be a positive integer or null")
    if not positive_integer_or_null(value["job_id"]):
        errors.append(f"{location}: job_id must be a positive integer or null")
    return errors


def validate_pr(value: object, location: str) -> list[str]:
    errors = exact_keys(value, PR_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not non_empty_string(value["repository"]) or "/" not in value["repository"]:
        errors.append(f"{location}: repository must be owner/name")
    if not isinstance(value["number"], int) or isinstance(value["number"], bool) or value["number"] < 1:
        errors.append(f"{location}: number must be a positive integer")
    if value["state"] not in {"open", "closed"}:
        errors.append(f"{location}: state must be open or closed")
    if not isinstance(value["draft"], bool):
        errors.append(f"{location}: draft must be boolean")
    for key in ("head_branch", "head", "base_branch"):
        if not non_empty_string(value[key]):
            errors.append(f"{location}: {key} must be non-empty")
    if not isinstance(value["base_head"], (str, type(None))):
        errors.append(f"{location}: base_head must be a string or null")
    if not state_validator.parse_timestamp(value["updated_at"]):
        errors.append(f"{location}: updated_at must be an ISO-8601 timestamp")
    checks = value["checks"]
    if not isinstance(checks, list):
        errors.append(f"{location}: checks must be an array")
    else:
        for index, check in enumerate(checks):
            errors.extend(validate_check(check, f"{location}.checks[{index}]"))
    return errors


def validate_issue(value: object, location: str) -> list[str]:
    errors = exact_keys(value, ISSUE_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if not non_empty_string(value["repository"]) or "/" not in value["repository"]:
        errors.append(f"{location}: repository must be owner/name")
    if not isinstance(value["number"], int) or isinstance(value["number"], bool) or value["number"] < 1:
        errors.append(f"{location}: number must be a positive integer")
    if value["state"] not in {"open", "closed"}:
        errors.append(f"{location}: state must be open or closed")
    if value["state_text"] is not None and not isinstance(value["state_text"], str):
        errors.append(f"{location}: state_text must be a string or null")
    labels = value["labels"]
    if not isinstance(labels, list) or any(not non_empty_string(label) for label in labels):
        errors.append(f"{location}: labels must contain non-empty strings")
    elif len(labels) != len(set(labels)):
        errors.append(f"{location}: labels must be unique")
    if not state_validator.parse_timestamp(value["updated_at"]):
        errors.append(f"{location}: updated_at must be an ISO-8601 timestamp")
    return errors


def validate_facts(value: object, location: str) -> list[str]:
    errors = exact_keys(value, FACT_KEYS, location)
    if errors or not isinstance(value, dict):
        return errors
    if value["schema_version"] != 1:
        errors.append(f"{location}: schema_version must be 1")
    if not state_validator.parse_timestamp(value["generated_at"]):
        errors.append(f"{location}: generated_at must be an ISO-8601 timestamp")

    collections = (
        ("refs", validate_ref),
        ("pull_requests", validate_pr),
        ("issues", validate_issue),
    )
    for key, item_validator in collections:
        items = value[key]
        if not isinstance(items, list):
            errors.append(f"{location}: {key} must be an array")
            continue
        for index, item in enumerate(items):
            errors.extend(item_validator(item, f"{location}.{key}[{index}]"))
    return errors


def load_facts(path: Path) -> Facts:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid facts JSON: {exc}") from exc
    errors = validate_facts(value, str(path))
    if errors:
        raise ValueError("\n".join(errors))
    return value


def normalize_state_token(value: str | None) -> str | None:
    if value is None:
        return None
    token = value.strip().strip("`").lower()
    token = re.split(r"\s+[—–-]\s+", token, maxsplit=1)[0]
    return token.strip() or None


def check_summary(checks: list[dict[str, Any]]) -> str:
    if not checks:
        return "missing"
    if all(check["status"] == "queued" for check in checks):
        return "queued"
    if any(check["status"] == "in_progress" for check in checks):
        return "in_progress"
    failing = {
        "failure",
        "cancelled",
        "timed_out",
        "action_required",
    }
    if any(check["conclusion"] in failing for check in checks):
        return "failed"
    if all(
        check["status"] == "completed"
        and check["conclusion"] in {"success", "skipped", "neutral"}
        for check in checks
    ):
        return "completed"
    return "mixed"


def evidence_for_check(check: dict[str, Any]) -> str:
    identity: list[str] = [check["name"], check["status"]]
    if check["conclusion"] is not None:
        identity.append(check["conclusion"])
    if check["run_id"] is not None:
        identity.append(f"run {check['run_id']}")
    if check["job_id"] is not None:
        identity.append(f"job {check['job_id']}")
    return " / ".join(identity)


def finding(
    code: str,
    severity: str,
    state: State | None,
    message: str,
    next_action: str,
    *evidence: str,
) -> Finding:
    return Finding(
        code=code,
        severity=severity,
        state_id=state["id"] if state else None,
        message=message,
        next_action=next_action,
        evidence=tuple(evidence),
    )


def audit(
    states: list[State],
    facts: Facts,
    coordination_repository: str,
    queued_carrier_threshold: int,
    review_pressure_threshold: int,
) -> list[Finding]:
    findings: list[Finding] = []
    refs = {(item["repository"], item["branch"]): item for item in facts["refs"]}
    prs = {
        (item["repository"], item["number"]): item
        for item in facts["pull_requests"]
    }
    issues = {
        (item["repository"], item["number"]): item for item in facts["issues"]
    }
    queued_states: list[State] = []

    for state in states:
        source = state["canonical_source"]
        review = state["review"]
        carrier = state["active_carrier"]

        if source is not None:
            live_ref = refs.get((source["repository"], source["branch"]))
            if live_ref is None:
                findings.append(
                    finding(
                        "source-fact-missing",
                        "warning",
                        state,
                        "No live ref fact exists for the tracked canonical source branch.",
                        "Collect the exact branch ref before claiming currentness.",
                        f"tracked {source['repository']}:{source['branch']}@{source['head']}",
                    )
                )
            elif live_ref["head"] != source["head"]:
                findings.append(
                    finding(
                        "source-head-mismatch",
                        "error",
                        state,
                        "The live canonical branch head differs from tracked structured state.",
                        "Expire current review/promotion claims, inspect the complete new diff, and update state only after reconciliation.",
                        f"tracked {source['head']}",
                        f"live {live_ref['head']} observed {live_ref['observed_at']}",
                    )
                )

        if (
            source is not None
            and review["exact_head"] is not None
            and review["exact_head"] != source["head"]
        ):
            findings.append(
                finding(
                    "review-head-mismatch",
                    "error",
                    state,
                    "The review receipt is anchored to a different head than canonical source state.",
                    "Expire the disposition or prove semantic identity within the reviewed fence.",
                    f"reviewed {review['exact_head']}",
                    f"source {source['head']}",
                )
            )

        if carrier is not None:
            live_pr = prs.get((carrier["repository"], carrier["pull_request"]))
            if live_pr is None:
                findings.append(
                    finding(
                        "carrier-fact-missing",
                        "warning",
                        state,
                        "No live pull-request fact exists for the tracked active carrier.",
                        "Collect the carrier PR and checks before claiming execution state.",
                        f"tracked {carrier['repository']}#{carrier['pull_request']}@{carrier['head']}",
                    )
                )
            else:
                if live_pr["state"] != "open":
                    findings.append(
                        finding(
                            "carrier-closed",
                            "error",
                            state,
                            "Structured state names a closed pull request as the active carrier.",
                            "Transfer any retained receipt and clear or replace the carrier through an explicit state transition.",
                            f"{carrier['repository']}#{carrier['pull_request']} is {live_pr['state']}",
                        )
                    )
                if live_pr["head"] != carrier["head"]:
                    findings.append(
                        finding(
                            "carrier-head-mismatch",
                            "error",
                            state,
                            "The live execution carrier head differs from tracked state.",
                            "Inspect the complete carrier diff and update or expire its execution claim.",
                            f"tracked {carrier['head']}",
                            f"live {live_pr['head']}",
                        )
                    )
                if (
                    source is not None
                    and carrier["repository"] == source["repository"]
                    and live_pr["base_branch"] != source["branch"]
                ):
                    findings.append(
                        finding(
                            "carrier-base-mismatch",
                            "warning",
                            state,
                            "The live carrier targets a different branch than canonical source state.",
                            "Confirm the carrier applies the exact source intentionally or repair its base relationship.",
                            f"carrier base {live_pr['base_branch']}",
                            f"source branch {source['branch']}",
                        )
                    )

                summary = check_summary(live_pr["checks"])
                check_evidence = tuple(evidence_for_check(check) for check in live_pr["checks"])
                if summary == "missing":
                    findings.append(
                        finding(
                            "carrier-checks-missing",
                            "warning",
                            state,
                            "The active carrier has no observed check facts.",
                            "Collect exact workflow/job state before claiming execution progress.",
                            f"{carrier['repository']}#{carrier['pull_request']}",
                        )
                    )
                elif summary == "queued":
                    queued_states.append(state)
                    findings.append(
                        finding(
                            "carrier-queued",
                            "info",
                            state,
                            "The active carrier is runner-queued; no product evidence has executed yet.",
                            "Preserve the queued run and use the blocked time for review, drift, finding, or retirement work rather than an equivalent carrier.",
                            *check_evidence,
                        )
                    )
                elif summary == "in_progress":
                    findings.append(
                        finding(
                            "carrier-running",
                            "info",
                            state,
                            "The active carrier has an in-progress check.",
                            "Wait for the first material phase result and classify it exactly.",
                            *check_evidence,
                        )
                    )
                elif summary == "failed":
                    findings.append(
                        finding(
                            "carrier-check-failed",
                            "warning",
                            state,
                            "At least one active-carrier check failed, timed out, required action, or was cancelled.",
                            "Inspect the first failing phase and classify queue, harness, setup, patch, target, gate, or publication failure before changing source.",
                            *check_evidence,
                        )
                    )
                elif summary == "completed":
                    findings.append(
                        finding(
                            "carrier-checks-completed",
                            "info",
                            state,
                            "All observed carrier checks completed without a failing conclusion.",
                            "Verify intended tests and counts, transfer the exact receipt, review the published source, and retire temporary machinery.",
                            *check_evidence,
                        )
                    )
                else:
                    findings.append(
                        finding(
                            "carrier-checks-mixed",
                            "warning",
                            state,
                            "The active carrier has mixed or incomplete observed check state.",
                            "Resolve the exact run/job outcomes before promotion or replacement.",
                            *check_evidence,
                        )
                    )

        parent_issue = state["scope"]["parent_issue"]
        if parent_issue is not None:
            live_issue = issues.get((coordination_repository, parent_issue))
            if live_issue is None:
                findings.append(
                    finding(
                        "issue-fact-missing",
                        "warning",
                        state,
                        "No live fact exists for the tracked parent coordination issue.",
                        "Collect the issue state, State token, labels, and update boundary.",
                        f"{coordination_repository}#{parent_issue}",
                    )
                )
            else:
                if (
                    live_issue["state"] == "closed"
                    and state["phase"] in state_validator.ACTIVE_PHASES
                ):
                    findings.append(
                        finding(
                            "active-finding-closed-parent",
                            "error",
                            state,
                            "An active finding points to a closed parent coordination issue.",
                            "Reopen or replace the parent record, or move the finding to a terminal phase.",
                            f"{coordination_repository}#{parent_issue} is closed",
                        )
                    )

                state_labels = sorted(
                    label.split(":", 1)[1]
                    for label in live_issue["labels"]
                    if label.startswith("state:") and ":" in label
                )
                state_text = normalize_state_token(live_issue["state_text"])
                if state_text is None:
                    findings.append(
                        finding(
                            "issue-state-text-missing",
                            "warning",
                            state,
                            "The parent issue has no observable body State token.",
                            "Add or collect one current coordination-state token.",
                            f"{coordination_repository}#{parent_issue}",
                        )
                    )
                if not state_labels:
                    findings.append(
                        finding(
                            "issue-state-label-missing",
                            "warning",
                            state,
                            "The parent issue has no live state:* label.",
                            "Synchronize issue coordination metadata before promotion.",
                            f"{coordination_repository}#{parent_issue}",
                        )
                    )
                elif len(state_labels) > 1:
                    findings.append(
                        finding(
                            "issue-state-label-ambiguous",
                            "error",
                            state,
                            "The parent issue has more than one live state:* label.",
                            "Retain one current coordination label and preserve state history elsewhere.",
                            ", ".join(state_labels),
                        )
                    )
                elif state_text is not None and state_labels[0] != state_text:
                    findings.append(
                        finding(
                            "issue-state-mismatch",
                            "warning",
                            state,
                            "The parent issue body State token and live state label disagree.",
                            "Reconcile the issue body and label without changing finding phase implicitly.",
                            f"body {state_text}",
                            f"label {state_labels[0]}",
                        )
                    )

    if queued_carrier_threshold > 0 and len(queued_states) >= queued_carrier_threshold:
        findings.append(
            finding(
                "runner-queue-pressure",
                "info",
                None,
                f"{len(queued_states)} active carriers are entirely runner-queued.",
                "Pause equivalent carrier creation; prioritize source review, drift classification, finding reconciliation, and stale-carrier retirement.",
                *(state["id"] for state in queued_states),
            )
        )

    review_states = [
        state
        for state in states
        if state["phase"] in {"review-ready", "land-ready"}
    ]
    if review_pressure_threshold > 0 and len(review_states) >= review_pressure_threshold:
        findings.append(
            finding(
                "review-pressure",
                "info",
                None,
                f"{len(review_states)} findings are review-ready or land-ready.",
                "Finish, repair, supersede, explicitly hold, or close current review surfaces before opening equivalent promotion work.",
                *(state["id"] for state in review_states),
            )
        )

    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            item.state_id or "",
            item.code,
            item.message,
        ),
    )


def markdown_findings(title: str, findings: Iterable[Finding], generated_at: str) -> str:
    lines = [f"# {title}", "", f"Live-facts boundary: `{generated_at}`", ""]
    findings = list(findings)
    if not findings:
        lines.extend(["No findings.", ""])
        return "\n".join(lines)

    for item in findings:
        state = f" `{item.state_id}`" if item.state_id else ""
        lines.extend(
            [
                f"## {item.severity.upper()} — `{item.code}`{state}",
                "",
                item.message,
                "",
                f"**Next action:** {item.next_action}",
                "",
            ]
        )
        if item.evidence:
            lines.append("**Evidence:**")
            lines.append("")
            lines.extend(f"- {value}" for value in item.evidence)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def running_markdown(states: list[State], facts: Facts) -> str:
    prs = {
        (item["repository"], item["number"]): item
        for item in facts["pull_requests"]
    }
    lines = [
        "# RUNNING — live carrier reconciliation",
        "",
        f"Live-facts boundary: `{facts['generated_at']}`",
        "",
    ]
    active = [state for state in states if state["active_carrier"] is not None]
    if not active:
        lines.extend(["No active carriers in tracked state.", ""])
        return "\n".join(lines)
    for state in active:
        carrier = state["active_carrier"]
        live = prs.get((carrier["repository"], carrier["pull_request"]))
        if live is None:
            observed = "live facts missing"
        else:
            observed = check_summary(live["checks"])
        source = state["canonical_source"]
        source_identity = (
            f"{source['repository']}:{source['branch']}@{source['head'][:12]}"
            if source
            else "none"
        )
        lines.extend(
            [
                f"## `{state['id']}` — {state['title']}",
                "",
                f"- source: `{source_identity}`",
                f"- carrier: `{carrier['repository']}#{carrier['pull_request']}@{carrier['head'][:12]}`",
                f"- observed checks: `{observed}`",
                f"- purpose: {carrier['purpose']}",
                f"- next: {state['next_transition']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_output(
    states: list[State], facts: Facts, findings: list[Finding], output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": facts["generated_at"],
        "summary": {
            severity: sum(item.severity == severity for item in findings)
            for severity in ("error", "warning", "info")
        },
        "findings": [asdict(item) for item in findings],
    }
    (output_dir / "audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "RISKS.md").write_text(
        markdown_findings("RISKS — live coordination reconciliation", findings, facts["generated_at"]),
        encoding="utf-8",
    )
    (output_dir / "RUNNING.md").write_text(
        running_markdown(states, facts), encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("generated/coordination-audit")
    )
    parser.add_argument(
        "--coordination-repository", default="teamleaderleo/fieldwork"
    )
    parser.add_argument("--queued-carrier-threshold", type=int, default=3)
    parser.add_argument("--review-pressure-threshold", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        states = views.load_states(args.root)
        facts = load_facts(args.facts)
        findings = audit(
            states,
            facts,
            args.coordination_repository,
            args.queued_carrier_threshold,
            args.review_pressure_threshold,
        )
        write_output(states, facts, findings, args.output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Coordination audit failed:\n{exc}", file=sys.stderr)
        return 1
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    print(
        f"Coordination audit generated {errors} error(s), {warnings} warning(s), "
        f"and {len(findings) - errors - warnings} info item(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
