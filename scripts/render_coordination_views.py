#!/usr/bin/env python3
"""Render deterministic human-facing views from Fieldwork coordination state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterable

import validate_coordination_state as validator

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "none": 4}
PHASE_ORDER = {
    "land-ready": 0,
    "design-decision-ready": 1,
    "delivery-gate-ready": 2,
    "review-ready": 3,
    "comparative-evaluation-active": 4,
    "research-active": 5,
    "stopped": 6,
    "closed": 7,
}
MATERIAL_FIELDS = (
    "phase",
    "priority",
    "review_disposition",
    "review_exact_head",
    "canonical_source_head",
    "active_carrier_head",
    "active_carrier_purpose",
    "blocker",
    "next_transition",
    "authority",
    "terminal_record",
)

State = dict[str, Any]


def state_sort_key(state: State) -> tuple[int, int, str]:
    return (
        PRIORITY_ORDER.get(state["priority"], 99),
        PHASE_ORDER.get(state["phase"], 99),
        state["id"],
    )


def state_link(state: State) -> str:
    title = state["title"].replace("[", "\\[").replace("]", "\\]")
    return f"[{state['id']} — {title}]({state['canonical_finding']})"


def short_head(value: object) -> str:
    if not isinstance(value, str) or not value:
        return "none"
    return value[:12]


def normalized_state(state: State) -> dict[str, Any]:
    review = state["review"]
    source = state["canonical_source"]
    carrier = state["active_carrier"]
    return {
        "title": state["title"],
        "summary": state["summary"],
        "impact": state["impact"],
        "priority": state["priority"],
        "scope": state["scope"],
        "state_updated_at": state["state_updated_at"],
        "canonical_finding": state["canonical_finding"],
        "phase": state["phase"],
        "work_class": state["work_class"],
        "review_disposition": review["disposition"],
        "review_exact_head": review["exact_head"],
        "canonical_source_head": source["head"] if source else None,
        "active_carrier_head": carrier["head"] if carrier else None,
        "active_carrier_purpose": carrier["purpose"] if carrier else None,
        "blocker": state["blocker"],
        "next_transition": state["next_transition"],
        "authority": state["authority"],
        "terminal_record": state["terminal_record"],
    }


def load_states(root: Path) -> list[State]:
    paths = sorted((root / "findings").glob("**/state.json"))
    states: list[State] = []
    errors: list[str] = []
    active_leases: dict[str, Path] = {}
    active_carriers: dict[str, Path] = {}

    for path in paths:
        state, load_errors = validator.load_state(path)
        errors.extend(load_errors)
        if state is None:
            continue
        state_errors = validator.validate_state(path, state)
        errors.extend(state_errors)
        if state_errors:
            continue

        lease = state["writer_lease"]
        if lease["state"] == "active":
            artifact = lease["artifact"]
            previous = active_leases.get(artifact)
            if previous is not None:
                errors.append(
                    f"{path}: active writer lease duplicates {artifact!r} from {previous}"
                )
            else:
                active_leases[artifact] = path

        if state["active_carrier"] is not None:
            invariant_id = state["invariant_id"]
            previous = active_carriers.get(invariant_id)
            if previous is not None:
                errors.append(
                    f"{path}: active carrier duplicates invariant {invariant_id!r} from {previous}"
                )
            else:
                active_carriers[invariant_id] = path
        states.append(state)

    if errors:
        raise ValueError("\n".join(errors))
    return sorted(states, key=state_sort_key)


def load_previous_snapshot(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    states = data.get("states")
    if not isinstance(states, dict):
        raise ValueError(f"{path}: snapshot states must be an object")
    return states


def change_lines(
    states: Iterable[State], previous: dict[str, dict[str, Any]]
) -> list[str]:
    current = {state["id"]: normalized_state(state) for state in states}
    lines: list[str] = []

    for state_id in sorted(current):
        state = current[state_id]
        old = previous.get(state_id)
        label = f"{state_id} — {state['title']}"
        if old is None:
            lines.append(f"- **New:** {label} entered as `{state['phase']}`.")
            continue
        changed = [field for field in MATERIAL_FIELDS if old.get(field) != state.get(field)]
        if changed:
            fields = ", ".join(f"`{field}`" for field in changed)
            lines.append(f"- **Changed:** {label}: {fields}.")

    for state_id in sorted(set(previous) - set(current)):
        old = previous[state_id]
        lines.append(
            f"- **Missing:** {state_id} — {old.get('title', 'unknown title')} is absent from the current tracked state; verify archive or migration."
        )
    return lines


def decision_items(states: Iterable[State]) -> list[tuple[State, str]]:
    items: list[tuple[State, str]] = []
    for state in states:
        if state["phase"] == "design-decision-ready":
            question = state["blocker"] or state["next_transition"]
            items.append((state, question))
        elif state["phase"] == "land-ready" and not state["authority"]["merge"]:
            source = state["canonical_source"]
            head = short_head(source["head"] if source else None)
            items.append((state, f"Merge or explicitly hold exact canonical head `{head}`."))
    return items


def risk_items(states: Iterable[State]) -> list[tuple[State, str]]:
    items: list[tuple[State, str]] = []
    for state in states:
        review = state["review"]
        freshness = state["freshness"]
        lease = state["writer_lease"]
        source = state["canonical_source"]

        if review["disposition"] in {"REPAIR", "HOLD"}:
            items.append((state, f"review disposition is `{review['disposition']}`"))
        if state["blocker"]:
            items.append((state, state["blocker"]))
        if state["work_class"] == "upstream-fork-research" and not freshness["upstream_valid_through"]:
            items.append((state, "external-source freshness boundary is missing"))
        if state["phase"] in validator.REVIEWED_PHASES and not review["exact_head"]:
            items.append((state, "reviewed phase lacks an exact reviewed head"))
        if state["phase"] in validator.ACTIVE_PHASES and source is None and state["work_class"] not in {"evidence-documentation", "blocked-sensitive"}:
            items.append((state, "active technical work has no canonical source head"))
        if lease["state"] in {"stale", "superseded"}:
            items.append((state, f"writer lease is `{lease['state']}`"))
    return items


def heading(title: str, boundary: str) -> list[str]:
    return [f"# {title}", "", f"Projection boundary: `{boundary}`", ""]


def section(lines: list[str], title: str, items: list[str], empty: str = "None.") -> None:
    lines.extend([f"## {title}", ""])
    lines.extend(items or [empty])
    lines.append("")


def render_now(states: list[State], previous: dict[str, dict[str, Any]], boundary: str) -> str:
    lines = heading("NOW — material coordination changes", boundary)
    section(lines, "Changed", change_lines(states, previous), "Initial projection; no previous snapshot supplied.")
    return "\n".join(lines).rstrip() + "\n"


def render_decisions(states: list[State], boundary: str) -> str:
    lines = heading("DECISIONS — human authority only", boundary)
    items = [
        f"- {state_link(state)} — {question}"
        for state, question in decision_items(states)
    ]
    section(lines, "Needs human authority", items)
    lines.extend(
        [
            "Technical alternatives that can still be distinguished through source research, prototypes, execution, or cross-review do not belong in this view.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_running(states: list[State], boundary: str) -> str:
    lines = heading("RUNNING — active execution carriers", boundary)
    items: list[str] = []
    for state in states:
        carrier = state["active_carrier"]
        if carrier is None:
            continue
        source = state["canonical_source"]
        source_head = short_head(source["head"] if source else None)
        items.append(
            f"- {state_link(state)} — carrier `{carrier['repository']}#{carrier['pull_request']}@{short_head(carrier['head'])}`; source `{source_head}`; purpose: {carrier['purpose']}"
        )
    section(lines, "Active carriers", items)
    lines.extend(
        [
            "Tracked state does not yet distinguish queued from in-progress runs; live workflow enrichment belongs to #304.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def evidence_levels(state: State) -> str:
    levels = sorted({item["level"] for item in state["evidence"]})
    return ", ".join(f"`{level}`" for level in levels) or "none"


def render_review(states: list[State], boundary: str) -> str:
    lines = heading("REVIEW — exact technical judgment", boundary)
    items: list[str] = []
    for state in states:
        review = state["review"]
        if state["phase"] != "review-ready" and review["disposition"] == "none":
            continue
        items.append(
            f"- {state_link(state)} — phase `{state['phase']}`; disposition `{review['disposition']}`; reviewed head `{short_head(review['exact_head'])}`; evidence {evidence_levels(state)}."
        )
    section(lines, "Review surfaces", items)
    return "\n".join(lines).rstrip() + "\n"


def render_landing(states: list[State], boundary: str) -> str:
    lines = heading("LANDING — selected delivery transitions", boundary)
    items: list[str] = []
    for state in states:
        if state["phase"] not in {
            "design-decision-ready",
            "delivery-gate-ready",
            "land-ready",
        }:
            continue
        source = state["canonical_source"]
        items.append(
            f"- {state_link(state)} — `{state['phase']}`; source `{short_head(source['head'] if source else None)}`; next: {state['next_transition']}"
        )
    section(lines, "Delivery transitions", items)
    return "\n".join(lines).rstrip() + "\n"


def render_risks(states: list[State], boundary: str) -> str:
    lines = heading("RISKS — coordination and evidence defects", boundary)
    items = [f"- {state_link(state)} — {risk}." for state, risk in risk_items(states)]
    section(lines, "Current risks", items)
    return "\n".join(lines).rstrip() + "\n"


def render_archive(states: list[State], boundary: str) -> str:
    lines = heading("ARCHIVE — stopped and closed findings", boundary)
    items: list[str] = []
    for state in states:
        if state["phase"] not in {"stopped", "closed"}:
            continue
        items.append(
            f"- {state_link(state)} — `{state['phase']}`; terminal record: {state['terminal_record']}"
        )
    section(lines, "Retained outcomes", items)
    return "\n".join(lines).rstrip() + "\n"


def render_current(
    states: list[State], previous: dict[str, dict[str, Any]], boundary: str
) -> str:
    lines = heading("FIELDWORK — CURRENT", boundary)
    active = [state for state in states if state["phase"] in validator.ACTIVE_PHASES]
    priorities = [state for state in active if state["priority"] in {"P0", "P1"}]
    priority_lines = [
        f"- `{state['priority']}` {state_link(state)} — {state['summary']}"
        for state in priorities[:8]
    ]
    section(lines, "Priority", priority_lines, "No active P0/P1 findings in tracked state.")

    section(lines, "Changed", change_lines(states, previous)[:10], "Initial projection; no previous snapshot supplied.")

    impact_lines = [f"- {state_link(state)} — {state['impact']}" for state in active[:6]]
    section(lines, "Why it matters", impact_lines, "No active findings.")

    waiting: list[str] = []
    for state in active:
        review = state["review"]
        if state["blocker"]:
            waiting.append(f"- {state_link(state)} — {state['blocker']}")
        elif review["disposition"] in {"EXECUTE", "HOLD", "REPAIR"}:
            waiting.append(
                f"- {state_link(state)} — review disposition `{review['disposition']}`; next: {state['next_transition']}"
            )
    section(lines, "Waiting or blocked", waiting[:10])

    decisions = [
        f"- {state_link(state)} — {question}"
        for state, question in decision_items(states)
    ]
    section(lines, "Needs human authority", decisions)

    risks = [f"- {state_link(state)} — {risk}." for state, risk in risk_items(states)]
    section(lines, "Risk", risks[:10])

    autonomous: list[str] = []
    decision_ids = {state["id"] for state, _ in decision_items(states)}
    for state in active:
        if state["id"] in decision_ids:
            continue
        autonomous.append(f"- {state_link(state)} — {state['next_transition']}")
    section(lines, "Next autonomous action", autonomous[:10])
    return "\n".join(lines).rstrip() + "\n"


def projection_boundary(states: list[State]) -> str:
    timestamps = [state["state_updated_at"] for state in states]
    return max(timestamps) if timestamps else "no tracked state"


def write_views(
    states: list[State], output_dir: Path, previous: dict[str, dict[str, Any]]
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    boundary = projection_boundary(states)
    views = {
        "CURRENT.md": render_current(states, previous, boundary),
        "NOW.md": render_now(states, previous, boundary),
        "DECISIONS.md": render_decisions(states, boundary),
        "RUNNING.md": render_running(states, boundary),
        "REVIEW.md": render_review(states, boundary),
        "LANDING.md": render_landing(states, boundary),
        "RISKS.md": render_risks(states, boundary),
        "ARCHIVE.md": render_archive(states, boundary),
    }
    for name, content in views.items():
        (output_dir / name).write_text(content, encoding="utf-8")

    snapshot = {
        "schema_version": 1,
        "generated_at": boundary,
        "states": {state["id"]: normalized_state(state) for state in states},
    }
    (output_dir / "state-snapshot.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output-dir", type=Path, default=Path("generated/coordination")
    )
    parser.add_argument("--previous-snapshot", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        states = load_states(args.root)
        previous = load_previous_snapshot(args.previous_snapshot)
        write_views(states, args.output_dir, previous)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Coordination view generation failed:\n{exc}", file=sys.stderr)
        return 1
    print(f"Generated coordination views in {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
