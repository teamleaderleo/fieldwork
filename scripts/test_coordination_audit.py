#!/usr/bin/env python3
"""Regression tests for Fieldwork coordination reconciliation controllers."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

import audit_coordination as audit
import render_coordination_views as views


ROOT = Path(__file__).resolve().parents[1]
STATE_TEMPLATE = ROOT / "templates" / "coordination-state.json"
FACT_TEMPLATE = ROOT / "templates" / "coordination-live-facts.json"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def state_fixture(index: int = 0) -> dict[str, object]:
    state = load_json(STATE_TEMPLATE)
    source_head = str(index + 1) * 40
    carrier_head = str(index + 4) * 40
    state.update(
        {
            "id": f"F20{index}-running",
            "title": "Run one exact carrier",
            "summary": "One canonical source has one active execution carrier.",
            "impact": "Duplicate carriers consume runner capacity without adding evidence.",
            "priority": "P0",
            "state_updated_at": "2026-07-31T01:00:00Z",
            "invariant_id": f"carrier-invariant-{index}",
            "canonical_finding": f"findings/F20{index}-running/finding.md",
            "phase": "research-active",
            "blocker": "Hosted runner allocation is pending.",
            "next_transition": "Inspect the first material run phase.",
        }
    )
    state["scope"] = {
        "programme": "agent-cli-execution",
        "target": "codex",
        "workstream": "K",
        "parent_issue": 300,
    }
    state["canonical_source"] = {
        "repository": "teamleaderleo/example",
        "branch": f"fieldwork/source-{index}",
        "head": source_head,
    }
    state["active_carrier"] = {
        "repository": "teamleaderleo/example",
        "pull_request": 10 + index,
        "head": carrier_head,
        "purpose": "Run four exact controls and publish a receipt.",
    }
    state["writer_lease"] = {
        "worker": f"worker-{index}",
        "artifact": state["canonical_finding"],
        "state": "active",
        "transfer_record": None,
    }
    state["freshness"] = {
        "base_head": "9" * 40,
        "upstream_valid_through": source_head,
        "checked_at": "2026-07-31T01:00:00Z",
    }
    return state


def facts_fixture(states: list[dict[str, object]]) -> dict[str, object]:
    facts = load_json(FACT_TEMPLATE)
    facts["generated_at"] = "2026-07-31T01:01:00Z"
    facts["refs"] = []
    facts["pull_requests"] = []
    for state in states:
        source = state["canonical_source"]
        carrier = state["active_carrier"]
        facts["refs"].append(
            {
                "repository": source["repository"],
                "branch": source["branch"],
                "head": source["head"],
                "observed_at": "2026-07-31T01:01:00Z",
            }
        )
        facts["pull_requests"].append(
            {
                "repository": carrier["repository"],
                "number": carrier["pull_request"],
                "state": "open",
                "draft": True,
                "head_branch": f"fieldwork/carrier-{carrier['pull_request']}",
                "head": carrier["head"],
                "base_branch": source["branch"],
                "base_head": source["head"],
                "updated_at": "2026-07-31T01:01:00Z",
                "checks": [
                    {
                        "name": "exact-review",
                        "status": "queued",
                        "conclusion": None,
                        "run_id": 100 + carrier["pull_request"],
                        "job_id": 200 + carrier["pull_request"],
                    }
                ],
            }
        )
    facts["issues"] = [
        {
            "repository": "teamleaderleo/fieldwork",
            "number": 300,
            "state": "open",
            "state_text": "claimed",
            "labels": ["state:claimed", "target:fieldwork", "type:meta"],
            "updated_at": "2026-07-31T01:01:00Z",
        }
    ]
    return facts


def finding_codes(findings: list[audit.Finding]) -> set[str]:
    return {item.code for item in findings}


def run_audit(
    states: list[dict[str, object]], facts: dict[str, object], queue: int = 3, review: int = 8
) -> list[audit.Finding]:
    return audit.audit(states, facts, "teamleaderleo/fieldwork", queue, review)


def write_state(root: Path, state: dict[str, object]) -> None:
    directory = root / "findings" / state["id"]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "state.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )


class CoordinationAuditTests(unittest.TestCase):
    def test_matching_queued_carrier_is_backpressure_not_error(self) -> None:
        state = state_fixture()
        findings = run_audit([state], facts_fixture([state]))
        self.assertEqual({"carrier-queued"}, finding_codes(findings))
        self.assertEqual("info", findings[0].severity)

    def test_source_movement_expires_currentness(self) -> None:
        state = state_fixture()
        facts = facts_fixture([state])
        facts["refs"][0]["head"] = "c" * 40
        findings = run_audit([state], facts)
        item = next(value for value in findings if value.code == "source-head-mismatch")
        self.assertEqual("error", item.severity)

    def test_review_head_mismatch_is_error(self) -> None:
        state = state_fixture()
        state["phase"] = "review-ready"
        state["review"] = {
            "disposition": "ACCEPT",
            "exact_head": "d" * 40,
            "reviewed_inputs": ["finding@different"],
        }
        self.assertIn(
            "review-head-mismatch",
            finding_codes(run_audit([state], facts_fixture([state]))),
        )

    def test_closed_moved_and_failed_carrier_are_distinct(self) -> None:
        state = state_fixture()
        facts = facts_fixture([state])
        live = facts["pull_requests"][0]
        live["state"] = "closed"
        live["head"] = "e" * 40
        live["checks"][0].update({"status": "completed", "conclusion": "failure"})
        codes = finding_codes(run_audit([state], facts))
        self.assertTrue(
            {"carrier-closed", "carrier-head-mismatch", "carrier-check-failed"} <= codes
        )

    def test_issue_body_and_label_mismatch_is_reported(self) -> None:
        state = state_fixture()
        facts = facts_fixture([state])
        facts["issues"][0]["state_text"] = "ready"
        self.assertIn(
            "issue-state-mismatch", finding_codes(run_audit([state], facts))
        )

    def test_queue_and_review_pressure_are_global(self) -> None:
        states = [state_fixture(index) for index in range(3)]
        for state in states:
            state["phase"] = "review-ready"
            state["review"] = {
                "disposition": "EXECUTE",
                "exact_head": state["canonical_source"]["head"],
                "reviewed_inputs": [f"{state['id']}@current"],
            }
        codes = finding_codes(run_audit(states, facts_fixture(states), 3, 3))
        self.assertIn("runner-queue-pressure", codes)
        self.assertIn("review-pressure", codes)

    def test_invalid_live_facts_are_rejected(self) -> None:
        state = state_fixture()
        facts = facts_fixture([state])
        # An incomplete check may not already claim a conclusion.
        facts["pull_requests"][0]["checks"][0]["conclusion"] = "success"
        errors = audit.validate_facts(facts, "facts")
        self.assertTrue(any("incomplete checks" in error for error in errors), errors)

    def test_outputs_are_deterministic(self) -> None:
        state = state_fixture()
        facts = facts_fixture([state])
        findings = run_audit([state], facts)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            audit.write_output([state], facts, findings, first)
            audit.write_output([state], facts, findings, second)
            self.assertEqual(
                {path.name: path.read_bytes() for path in first.iterdir()},
                {path.name: path.read_bytes() for path in second.iterdir()},
            )

    def test_end_to_end_load_and_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = state_fixture()
            write_state(root, state)
            facts_path = root / "facts.json"
            facts_path.write_text(
                json.dumps(facts_fixture([state]), indent=2) + "\n",
                encoding="utf-8",
            )
            states = views.load_states(root)
            facts = audit.load_facts(facts_path)
            findings = run_audit(states, facts)
            output = root / "audit"
            audit.write_output(states, facts, findings, output)
            self.assertIn("carrier-queued", (output / "RISKS.md").read_text())
            self.assertTrue((output / "audit.json").exists())


if __name__ == "__main__":
    unittest.main()
