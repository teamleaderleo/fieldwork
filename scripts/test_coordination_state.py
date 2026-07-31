#!/usr/bin/env python3
"""Regression tests for structured Fieldwork coordination state."""

from __future__ import annotations

import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

import validate_coordination_state as validator


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "coordination-state.json"


def state_fixture() -> dict[str, object]:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def run_collection(states: list[dict[str, object]]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for index, state in enumerate(states):
            path = root / "findings" / f"item-{index}"
            path.mkdir(parents=True)
            (path / "state.json").write_text(json.dumps(state), encoding="utf-8")
        old_cwd = Path.cwd()
        try:
            os.chdir(root)
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                result = validator.main()
        finally:
            os.chdir(old_cwd)
    return result, output.getvalue()


class CoordinationStateTests(unittest.TestCase):
    def test_template_is_valid(self) -> None:
        self.assertEqual([], validator.validate_state(TEMPLATE, state_fixture()))

    def test_placeholder_or_naive_timestamp_is_rejected(self) -> None:
        state = state_fixture()
        state["state_updated_at"] = "YYYY-MM-DDTHH:MM:SSZ"
        state["freshness"]["checked_at"] = "2026-07-31T01:00:00"
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(any("state_updated_at" in error for error in errors), errors)
        self.assertTrue(any("checked_at" in error for error in errors), errors)

    def test_land_ready_requires_matching_accepted_head(self) -> None:
        state = state_fixture()
        state["phase"] = "land-ready"
        state["review"] = {
            "disposition": "ACCEPT",
            "exact_head": "1" * 40,
            "reviewed_inputs": ["finding@one"],
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("review head must match canonical source head" in error for error in errors),
            errors,
        )

    def test_enabled_authority_requires_record(self) -> None:
        state = state_fixture()
        state["authority"]["merge"] = True
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("enabled authority requires authority_record" in error for error in errors),
            errors,
        )

    def test_stopped_requires_terminal_record(self) -> None:
        state = state_fixture()
        state["phase"] = "stopped"
        state["next_transition"] = ""
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("stopped or closed phase requires terminal_record" in error for error in errors),
            errors,
        )

    def test_active_carrier_requires_canonical_source(self) -> None:
        state = state_fixture()
        state["canonical_source"] = None
        state["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 1,
            "head": "2" * 40,
            "purpose": "Run the exact target gate.",
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("active_carrier requires canonical_source" in error for error in errors),
            errors,
        )

    def test_duplicate_lease_carrier_id_and_finding_fail_collection(self) -> None:
        first = state_fixture()
        first["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 1,
            "head": "3" * 40,
            "purpose": "Run the exact target gate.",
        }
        second = copy.deepcopy(first)
        second["canonical_source"]["branch"] = "fieldwork/example-second"
        second["active_carrier"]["pull_request"] = 2
        second["active_carrier"]["head"] = "4" * 40

        result, text = run_collection([first, second])
        self.assertEqual(1, result)
        self.assertIn("duplicate state id", text)
        self.assertIn("duplicate canonical finding", text)
        self.assertIn("active writer lease duplicates", text)
        self.assertIn("active carrier duplicates invariant", text)


if __name__ == "__main__":
    unittest.main()
