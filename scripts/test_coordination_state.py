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


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPOSITORY_ROOT / "templates" / "coordination-state.json"


def template_state() -> dict[str, object]:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


class CoordinationStateTests(unittest.TestCase):
    def test_template_is_valid(self) -> None:
        state = template_state()
        self.assertEqual([], validator.validate_state(TEMPLATE_PATH, state))

    def test_land_ready_requires_matching_accepted_head(self) -> None:
        state = template_state()
        state["phase"] = "land-ready"
        state["review"] = {
            "disposition": "ACCEPT",
            "exact_head": "1111111111111111111111111111111111111111",
            "reviewed_inputs": ["finding@one"],
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("review head must match canonical source head" in error for error in errors),
            errors,
        )

    def test_enabled_authority_requires_record(self) -> None:
        state = template_state()
        state["authority"]["merge"] = True
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("enabled authority requires authority_record" in error for error in errors),
            errors,
        )

    def test_stopped_requires_terminal_record(self) -> None:
        state = template_state()
        state["phase"] = "stopped"
        state["next_transition"] = ""
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("stopped or closed phase requires terminal_record" in error for error in errors),
            errors,
        )

    def test_active_carrier_requires_canonical_source(self) -> None:
        state = template_state()
        state["canonical_source"] = None
        state["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 1,
            "head": "2222222222222222222222222222222222222222",
            "purpose": "Run the exact target gate.",
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(
            any("active_carrier requires canonical_source" in error for error in errors),
            errors,
        )

    def test_duplicate_active_lease_and_carrier_fail_collection(self) -> None:
        first = template_state()
        first["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 1,
            "head": "3333333333333333333333333333333333333333",
            "purpose": "Run the exact target gate.",
        }
        second = copy.deepcopy(first)
        second["id"] = "F001-second"
        second["canonical_finding"] = "findings/F001-second/finding.md"
        second["canonical_source"]["branch"] = "fieldwork/example-second"
        second["active_carrier"]["pull_request"] = 2
        second["active_carrier"]["head"] = "4444444444444444444444444444444444444444"

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, state in (("F000-example", first), ("F001-second", second)):
                path = root / "findings" / name
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

        self.assertEqual(1, result)
        text = output.getvalue()
        self.assertIn("active writer lease duplicates", text)
        self.assertIn("active carrier duplicates invariant", text)


if __name__ == "__main__":
    unittest.main()
