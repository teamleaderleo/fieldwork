#!/usr/bin/env python3
"""Focused regressions for Fieldwork playground schema primitives."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_playground_cases import PackError, check_expectations, load_pack
from scripts.validate_experiments import ValidationError, validate_experiment


class ExperimentSchemaVersionTests(unittest.TestCase):
    def metadata(self, experiment_id: str) -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": experiment_id,
            "question": "Does the validator preserve exact primitive types?",
            "owner": "fieldwork",
            "command": "python3 -c 'pass'",
            "stop_condition": "The metadata validates.",
            "created_at": "2026-07-30",
            "state": "draft",
            "claim_scope": "mechanism",
            "network_policy": "disabled",
            "upstream_contact_authorized": False,
            "environment": {},
            "sources": [],
            "distinguishing_outcomes": [],
            "result_paths": [],
            "promoted_to": None,
        }

    def write_experiment(self, root: Path, data: dict[str, object]) -> Path:
        directory = root / str(data["id"])
        directory.mkdir()
        (directory / "experiment.json").write_text(
            json.dumps(data), encoding="utf-8"
        )
        return directory

    def test_accepts_integer_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.metadata("EXP-20260730-integer-version")
            validate_experiment(self.write_experiment(root, data))

    def test_rejects_boolean_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.metadata("EXP-20260730-boolean-version")
            data["schema_version"] = True
            directory = self.write_experiment(root, data)
            with self.assertRaisesRegex(
                ValidationError, "schema_version must be integer 1"
            ):
                validate_experiment(directory)


class CasePackPrimitiveFieldTests(unittest.TestCase):
    def pack(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "name": "primitive-field-control",
            "timeout_seconds": 1.5,
            "cases": [
                {
                    "id": "control",
                    "stdin_text": "",
                    "expect": {"exit_code": 0, "timed_out": False},
                }
            ],
        }

    def write_pack(self, root: Path, data: dict[str, object]) -> Path:
        path = root / "pack.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def assert_pack_rejected(self, data: dict[str, object], pattern: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_pack(Path(tmp), data)
            with self.assertRaisesRegex(PackError, pattern):
                load_pack(path)

    def test_accepts_valid_primitive_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load_pack(self.write_pack(Path(tmp), self.pack()))
        self.assertEqual(loaded["schema_version"], 1)
        self.assertEqual(loaded["timeout_seconds"], 1.5)
        self.assertEqual(loaded["cases"][0]["expect"]["exit_code"], 0)
        self.assertIs(loaded["cases"][0]["expect"]["timed_out"], False)

    def test_accepts_null_exit_code(self) -> None:
        data = self.pack()
        data["cases"][0]["expect"]["exit_code"] = None
        with tempfile.TemporaryDirectory() as tmp:
            load_pack(self.write_pack(Path(tmp), data))

    def test_rejects_boolean_schema_version(self) -> None:
        data = self.pack()
        data["schema_version"] = True
        self.assert_pack_rejected(data, "schema_version must be integer 1")

    def test_rejects_boolean_pack_timeout(self) -> None:
        data = self.pack()
        data["timeout_seconds"] = True
        self.assert_pack_rejected(
            data, "timeout_seconds must be a finite positive number"
        )

    def test_rejects_boolean_case_timeout(self) -> None:
        data = self.pack()
        data["cases"][0]["timeout_seconds"] = False
        self.assert_pack_rejected(
            data, "timeout_seconds must be a finite positive number"
        )

    def test_rejects_non_finite_timeout(self) -> None:
        data = self.pack()
        data["timeout_seconds"] = float("inf")
        self.assert_pack_rejected(
            data, "timeout_seconds must be a finite positive number"
        )

    def test_rejects_boolean_exit_code(self) -> None:
        data = self.pack()
        data["cases"][0]["expect"]["exit_code"] = True
        self.assert_pack_rejected(
            data, "expect.exit_code must be an integer or null"
        )

    def test_rejects_non_boolean_timed_out(self) -> None:
        data = self.pack()
        data["cases"][0]["expect"]["timed_out"] = 0
        self.assert_pack_rejected(data, "expect.timed_out must be boolean")

    def test_stdout_json_does_not_conflate_boolean_and_integer(self) -> None:
        failures = check_expectations(
            {"expect": {"stdout_json": True}},
            exit_code=0,
            stdout="1",
            stderr="",
            timed_out=False,
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("stdout_json expected True, got 1", failures[0])

    def test_stdout_json_preserves_json_numeric_equivalence(self) -> None:
        failures = check_expectations(
            {"expect": {"stdout_json": {"value": 1}}},
            exit_code=0,
            stdout='{"value": 1.0}',
            stderr="",
            timed_out=False,
        )
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
