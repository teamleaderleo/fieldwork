#!/usr/bin/env python3
"""Regression tests for generated Fieldwork coordination views."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

import render_coordination_views as views


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPOSITORY_ROOT / "templates" / "coordination-state.json"


def base_state() -> dict[str, object]:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def write_state(root: Path, state: dict[str, object]) -> None:
    directory = root / "findings" / state["id"]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "state.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )


def fixture_states() -> list[dict[str, object]]:
    running = base_state()
    running.update(
        {
            "id": "F100-running",
            "title": "Run exact carrier",
            "summary": "A canonical source is waiting on one active execution carrier.",
            "impact": "Duplicating the carrier would consume runner capacity without adding evidence.",
            "priority": "P0",
            "state_updated_at": "2026-07-31T00:00:00Z",
            "invariant_id": "running-invariant",
            "canonical_finding": "findings/F100-running/finding.md",
            "phase": "research-active",
            "blocker": "Hosted runner allocation is pending.",
            "next_transition": "Inspect the exact run and transfer the receipt.",
        }
    )
    running["scope"] = {
        "programme": "agent-cli-execution",
        "target": "codex",
        "workstream": "K",
        "parent_issue": 239,
    }
    running["canonical_source"] = {
        "repository": "teamleaderleo/codex",
        "branch": "fieldwork/source",
        "head": "1111111111111111111111111111111111111111",
    }
    running["active_carrier"] = {
        "repository": "teamleaderleo/codex",
        "pull_request": 100,
        "head": "2222222222222222222222222222222222222222",
        "purpose": "Run four exact controls and publish a source-only receipt.",
    }
    running["writer_lease"] = {
        "worker": "worker-running",
        "artifact": "findings/F100-running/finding.md",
        "state": "active",
        "transfer_record": None,
    }

    decision = copy.deepcopy(running)
    decision.update(
        {
            "id": "F101-decision",
            "title": "Choose a non-delegable compatibility policy",
            "summary": "Technical comparison is complete and one product policy choice remains.",
            "impact": "The selected policy changes compatibility guarantees that repository evidence does not define.",
            "priority": "P1",
            "state_updated_at": "2026-07-31T00:01:00Z",
            "invariant_id": "decision-invariant",
            "canonical_finding": "findings/F101-decision/finding.md",
            "phase": "design-decision-ready",
            "blocker": "Choose whether the compatibility break is acceptable.",
            "next_transition": "Record the selected compatibility policy.",
            "active_carrier": None,
        }
    )
    decision["review"] = {
        "disposition": "HOLD",
        "exact_head": "3333333333333333333333333333333333333333",
        "reviewed_inputs": ["finding@decision"],
    }
    decision["canonical_source"] = {
        "repository": "teamleaderleo/example",
        "branch": "fieldwork/decision",
        "head": "3333333333333333333333333333333333333333",
    }
    decision["writer_lease"] = {
        "worker": "worker-decision",
        "artifact": "findings/F101-decision/finding.md",
        "state": "active",
        "transfer_record": None,
    }

    landing = copy.deepcopy(running)
    landing.update(
        {
            "id": "F102-landing",
            "title": "Land accepted owned repair",
            "summary": "One exact owned source head has accepted review and its full gate.",
            "impact": "The repair remains unavailable until merge authority is exercised or explicitly held.",
            "priority": "P1",
            "state_updated_at": "2026-07-31T00:02:00Z",
            "invariant_id": "landing-invariant",
            "canonical_finding": "findings/F102-landing/finding.md",
            "phase": "land-ready",
            "work_class": "owned-product-delivery",
            "blocker": None,
            "next_transition": "Merge or explicitly hold the accepted exact head.",
            "active_carrier": None,
        }
    )
    landing["canonical_source"] = {
        "repository": "teamleaderleo/fieldwork",
        "branch": "repair/accepted",
        "head": "4444444444444444444444444444444444444444",
    }
    landing["review"] = {
        "disposition": "ACCEPT",
        "exact_head": "4444444444444444444444444444444444444444",
        "reviewed_inputs": ["finding@landing", "issue@landing"],
    }
    landing["evidence"] = [
        {
            "claim": "The named repository gate passed at the exact source head.",
            "level": "full-gate",
            "receipt": "workflow:123",
            "limit": "The gate does not grant merge authority.",
        }
    ]
    landing["writer_lease"] = {
        "worker": "worker-landing",
        "artifact": "findings/F102-landing/finding.md",
        "state": "active",
        "transfer_record": None,
    }

    stopped = copy.deepcopy(running)
    stopped.update(
        {
            "id": "F103-stopped",
            "title": "Retain disproved premise",
            "summary": "Execution disproved the original defect theory.",
            "impact": "The terminal record prevents future workers from repeating the same premise.",
            "priority": "none",
            "state_updated_at": "2026-07-31T00:03:00Z",
            "invariant_id": "stopped-invariant",
            "canonical_finding": "findings/F103-stopped/finding.md",
            "phase": "stopped",
            "canonical_source": None,
            "active_carrier": None,
            "blocker": None,
            "next_transition": "",
            "terminal_record": "findings/F103-stopped/finding.md#stop",
        }
    )
    stopped["writer_lease"] = {
        "worker": None,
        "artifact": None,
        "state": "released",
        "transfer_record": "finding retained",
    }

    return [running, decision, landing, stopped]


class CoordinationViewTests(unittest.TestCase):
    def test_generates_all_views_and_routes_items(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for state in fixture_states():
                write_state(root, state)
            states = views.load_states(root)
            output = root / "generated"
            views.write_views(states, output, {})

            expected = {
                "CURRENT.md",
                "NOW.md",
                "DECISIONS.md",
                "RUNNING.md",
                "REVIEW.md",
                "LANDING.md",
                "RISKS.md",
                "ARCHIVE.md",
                "state-snapshot.json",
            }
            self.assertEqual(expected, {path.name for path in output.iterdir()})

            current = (output / "CURRENT.md").read_text(encoding="utf-8")
            self.assertIn("## Priority", current)
            self.assertIn("## Needs human authority", current)
            self.assertIn("F100-running", current)

            decisions = (output / "DECISIONS.md").read_text(encoding="utf-8")
            self.assertIn("F101-decision", decisions)
            self.assertIn("F102-landing", decisions)

            running = (output / "RUNNING.md").read_text(encoding="utf-8")
            self.assertIn("teamleaderleo/codex#100", running)
            self.assertIn("111111111111", running)

            archive = (output / "ARCHIVE.md").read_text(encoding="utf-8")
            self.assertIn("F103-stopped", archive)

    def test_snapshot_drives_material_change_view(self) -> None:
        states = fixture_states()
        old = {
            state["id"]: views.normalized_state(state)
            for state in states
        }
        states[0]["phase"] = "review-ready"
        lines = views.change_lines(states, old)
        self.assertEqual(1, len(lines))
        self.assertIn("`phase`", lines[0])

    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for state in reversed(fixture_states()):
                write_state(root, state)
            states = views.load_states(root)
            first = root / "first"
            second = root / "second"
            views.write_views(states, first, {})
            views.write_views(states, second, {})
            for path in first.iterdir():
                self.assertEqual(
                    path.read_bytes(),
                    (second / path.name).read_bytes(),
                    path.name,
                )

    def test_duplicate_active_artifact_stops_generation(self) -> None:
        states = fixture_states()[:2]
        states[1]["writer_lease"]["artifact"] = states[0]["writer_lease"]["artifact"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for state in states:
                write_state(root, state)
            with self.assertRaisesRegex(ValueError, "active writer lease duplicates"):
                views.load_states(root)


if __name__ == "__main__":
    unittest.main()
