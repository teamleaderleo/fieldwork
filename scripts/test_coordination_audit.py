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


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
STATE_TEMPLATE = REPOSITORY_ROOT / "templates" / "coordination-state.json"
FACT_TEMPLATE = REPOSITORY_ROOT / "templates" / "coordination-live-facts.json"


def base_state() -> dict[str, object]:
    return json.loads(STATE_TEMPLATE.read_text(encoding="utf-8"))


def base_facts() -> dict[str, object]:
    return json.loads(FACT_TEMPLATE.read_text(encoding="utf-8"))


def running_state() -> dict[str, object]:
    state = base_state()
    state.update(
        {
            "id": "F200-running",
            "title": "Run one exact carrier",
            "summary": "One canonical source has one active execution carrier.",
            "impact": "Duplicate carriers would consume runner capacity without adding evidence.",
            "priority": "P0",
            "state_updated_at": "2026-07-31T01:00:00Z",
            "invariant_id": "carrier-invariant",
            "canonical_finding": "findings/F200-running/finding.md",
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
        "branch": "fieldwork/source",
        "head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    }
    state["active_carrier"] = {
        "repository": "teamleaderleo/example",
        "pull_request": 10,
        "head": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "purpose": "Run four exact controls and publish a receipt.",
    }
    state["writer_lease"] = {
        "worker": "worker-200",
        "artifact": "findings/F200-running/finding.md",
        "state": "active",
        "transfer_record": None,
    }
    state["freshness"] = {
        "base_head": "9999999999999999999999999999999999999999",
        "upstream_valid_through": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "checked_at": "2026-07-31T01:00:00Z",
    }
    return state


def matching_facts() -> dict[str, object]:
    facts = base_facts()
    facts["generated_at"] = "2026-07-31T01:01:00Z"
    facts["refs"] = [
        {
            "repository": "teamleaderleo/example",
            "branch": "fieldwork/source",
            "head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "observed_at": "2026-07-31T01:01:00Z",
        }
    ]
    facts["pull_requests"] = [
        {
            "repository": "teamleaderleo/example",
            "number": 10,
            "state": "open",
            "draft": True,
            "head_branch": "fieldwork/carrier",
            "head": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "base_branch": "fieldwork/source",
            "base_head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "updated_at": "2026-07-31T01:01:00Z",
            "checks": [
                {
                    "name": "exact-review",
                    "status": "queued",
                    "conclusion": None,
                    "run_id": 10,
                    "job_id": 20,
                }
            ],
        }
    ]
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


def codes(findings: list[audit.Finding]) -> set[str]:
    return {item.code for item in findings}


def write_state(root: Path, state: dict[str, object]) -> None:
    directory = root / "findings" / state["id"]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "state.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )


class CoordinationAuditTests(unittest.TestCase):
    def test_matching_queued_carrier_reports_backpressure_not_error(self) -> None:
        findings = audit.audit(
            [running_state()],
            matching_facts(),
            "teamleaderleo/fieldwork",
            queued_carrier_threshold=3,
            review_pressure_threshold=8,
        )
        self.assertEqual({"carrier-queued"}, codes(findings))
        self.assertEqual("info", findings[0].severity)

    def test_source_and_review_movement_expire_currentness(self) -> None:
        state = running_state()
        state["phase"] = "review-ready"
        state["review"] = {
            "disposition": "ACCEPT",
            "exact_head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "reviewed_inputs": ["finding@old"],
        }
        facts = matching_facts()
        facts["refs"][0]["head"] = "cccccccccccccccccccccccccccccccccccccccc"
        findings = audit.audit(
            [state], facts, "teamleaderleo/fieldwork", 3, 8
        )
        self.assertIn("source-head-mismatch", codes(findings))
        mismatch = next(item for item in findings if item.code == "source-head-mismatch")
        self.assertEqual("error", mismatch.severity)

    def test_review_head_mismatch_is_error(self) -> None:
        state = running_state()
        state["phase"] = "review-ready"
        state["review"] = {
            "disposition": "ACCEPT",
            "exact_head": "dddddddddddddddddddddddddddddddddddddddd",
            "reviewed_inputs": ["finding@different"],
        }
        findings = audit.audit(
            [state], matching_facts(), "teamleaderleo/fieldwork", 3, 8
        )
        self.assertIn("review-head-mismatch", codes(findings))

    def test_closed_or_moved_carrier_is_error(self) -> None:
        facts = matching_facts()
        facts["pull_requests"][0]["state"] = "closed"
        facts["pull_requests"][0]["head"] = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        findings = audit.audit(
            [running_state()], facts, "teamleaderleo/fieldwork", 3, 8
        )
        self.assertIn("carrier-closed", codes(findings))
        self.assertIn("carrier-head-mismatch", codes(findings))

    def test_failed_check_is_classified_without_product_claim(self) -> None:
        facts = matching_facts()
        facts["pull_requests"][0]["checks"][0].update(
            {"status": "completed", "conclusion": "failure"}
        )
        findings = audit.audit(
            [running_state()], facts, "teamleaderleo/fieldwork", 3, 8
        )
        failed = next(item for item in findings if item.code == "carrier-check-failed")
        self.assertEqual("warning", failed.severity)
        self.assertIn("first failing phase", failed.next_action)

    def test_issue_body_and_label_mismatch_is_reported(self) -> None:
        facts = matching_facts()
        facts["issues"][0]["state_text"] = "ready"
        findings = audit.audit(
            [running_state()], facts, "teamleaderleo/fieldwork", 3, 8
        )
        self.assertIn("issue-state-mismatch", codes(findings))

    def test_queue_and_review_pressure_are_global_findings(self) -> None:
        states: list[dict[str, object]] = []
        facts = matching_facts()
        facts["refs"] = []
        facts["pull_requests"] = []
        facts["issues"] = []
        for index in range(3):
            state = running_state()
            state["id"] = f"F20{index}-running"
            state["invariant_id"] = f"carrier-{index}"
            state["canonical_finding"] = f"findings/F20{index}-running/finding.md"
            state["canonical_source"]["branch"] = f"fieldwork/source-{index}"
            state["canonical_source"]["head"] = f"{index + 1}" * 40
            state["active_carrier"]["pull_request"] = 10 + index
            state["active_carrier"]["head"] = f"{index + 4}" * 40
            state["writer_lease"]["artifact"] = state["canonical_finding"]
            state["phase"] = "review-ready"
            state["review"] = {
                "disposition": "EXECUTE",
                "exact_head": state["canonical_source"]["head"],
                "reviewed_inputs": [f"finding@{index}"],
            }
            states.append(state)
            facts["refs"].append(
                {
                    "repository": "teamleaderleo/example",
                    "branch": state["canonical_source"]["branch"],
                    "head": state["canonical_source"]["head"],
                    "observed_at": "2026-07-31T01:01:00Z",
                }
            )
            facts["pull_requests"].append(
                {
                    "repository": "teamleaderleo/example",
                    "number": 10 + index,
                    "state": "open",
                    "draft": True,
                    "head_branch": f"fieldwork/carrier-{index}",
                    "head": state["active_carrier"]["head"],
                    "base_branch": state["canonical_source"]["branch"],
                    "base_head": state["canonical_source"]["head"],
                    "updated_at": "2026-07-31T01:01:00Z",
                    "checks": [
                        {
                            "name": "exact-review",
                            "status": "queued",
                            "conclusion": None,
                            "run_id": 100 + index,
                            "job_id": 200 + index,
                        }
                    ],
                }
            )
            facts["issues"].append(
                {
                    "repository": "teamleaderleo/fieldwork",
                    "number": 300,
                    "state": "open",
                    "state_text": "claimed",
                    "labels": ["state:claimed"],
                    "updated_at": "2026-07-31T01:01:00Z",
                }
            )
        # Deduplicate the shared parent issue fact.
        facts["issues"] = [facts["issues"][0]]
        findings = audit.audit(
            states, facts, "teamleaderleo/fieldwork", 3, 3
        )
        self.assertIn("runner-queue-pressure", codes(findings))
        self.assertIn("review-pressure", codes(findings))

    def test_audit_output_is_deterministic(self) -> None:
        state = running_state()
        facts = matching_facts()
        findings = audit.audit(
            [state], facts, "teamleaderleo/fieldwork", 3, 8
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            audit.write_output([state], facts, findings, first)
            audit.write_output([state], facts, findings, second)
            for path in first.iterdir():
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())

    def test_invalid_live_facts_are_rejected(self) -> None:
        facts = matching_facts()
        facts["pull_requests"][0]["checks"][0]["status"] = "completed"
        # A completed check without a conclusion is not a usable fact.
        errors = audit.validate_facts(facts, "facts")
        self.assertTrue(any("unsupported" not in error for error in errors), errors)

    def test_end_to_end_load_and_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = running_state()
            write_state(root, state)
            facts_path = root / "facts.json"
            facts_path.write_text(
                json.dumps(matching_facts(), indent=2) + "\n", encoding="utf-8"
            )
            states = views.load_states(root)
            facts = audit.load_facts(facts_path)
            findings = audit.audit(
                states, facts, "teamleaderleo/fieldwork", 3, 8
            )
            output = root / "audit"
            audit.write_output(states, facts, findings, output)
            self.assertTrue((output / "audit.json").exists())
            self.assertIn("carrier-queued", (output / "RISKS.md").read_text())


if __name__ == "__main__":
    unittest.main()
