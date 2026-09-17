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
SCHEMA = ROOT / "schemas" / "coordination-state.schema.json"


def state_fixture() -> dict[str, object]:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def active_lease(
    *,
    repository: str = "teamleaderleo/example",
    resource: str = "findings/F000-example/finding.md",
    generation: str = "1" * 64,
    transition: int = 0,
    previous_generation: str | None = None,
    transfer_record: str | None = None,
) -> dict[str, object]:
    return {
        "state": "active",
        "holder": "worker-id",
        "repository": repository,
        "resource_kind": "path",
        "resource": resource,
        "generation_type": "sha256",
        "generation": generation,
        "acquired_at": "2026-07-31T01:00:00Z",
        "renewed_at": "2026-07-31T01:05:00Z",
        "duration_seconds": 3600,
        "transition": transition,
        "previous_generation": previous_generation,
        "transfer_record": transfer_record,
    }


def authorized_merge() -> dict[str, object]:
    return {
        "state": "authorized",
        "action": "merge",
        "target": {
            "kind": "pull-request",
            "location": "teamleaderleo/fieldwork#306",
            "operation_id": "merge-pr-306",
            "data_class": "public",
        },
        "source": {
            "kind": "user-instruction",
            "record": "conversation/turn-authorization",
            "generation": "message-1",
        },
        "issued_at": "2026-07-31T01:00:00Z",
        "expires_at": "2026-08-01T01:00:00Z",
        "revocation_record": None,
    }


def review_ready_state() -> dict[str, object]:
    state = state_fixture()
    source_head = state["canonical_source"]["head"]
    state["phase"] = "review-ready"
    state["review"] = {
        "disposition": "EXECUTE",
        "exact_head": source_head,
        "reviewed_inputs": ["finding@sha256:one"],
    }
    return state


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
    def test_template_and_schema_parse(self) -> None:
        self.assertEqual([], validator.validate_state(TEMPLATE, state_fixture()))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(1, schema["properties"]["schema_version"]["const"])
        self.assertIn("authority", schema["$defs"])
        self.assertIn("lease", schema["$defs"])

    def test_boolean_schema_and_integer_fields_are_rejected(self) -> None:
        state = state_fixture()
        state["schema_version"] = True
        state["scope"]["parent_issue"] = True
        state["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": True,
            "head": "2" * 40,
            "purpose": "Run the exact target gate.",
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(any("schema_version" in error for error in errors), errors)
        self.assertTrue(any("parent_issue" in error for error in errors), errors)
        self.assertTrue(any("pull_request" in error for error in errors), errors)

    def test_placeholder_naive_and_weak_revision_values_are_rejected(self) -> None:
        state = state_fixture()
        state["state_updated_at"] = "YYYY-MM-DDTHH:MM:SSZ"
        state["freshness"]["checked_at"] = "2026-07-31T01:00:00"
        state["freshness"]["base_head"] = "main"
        state["freshness"]["external_boundary"]["value"] = "deadbeef"
        state["canonical_source"]["head"] = "deadbeef"
        state["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 2,
            "head": "cafebabe",
            "purpose": "Run an exact gate.",
        }
        state["review"]["exact_head"] = "HEAD"
        errors = validator.validate_state(Path("state.json"), state)
        for field in (
            "state_updated_at",
            "checked_at",
            "base_head",
            "boundary",
            "canonical_source",
            "active_carrier",
            "exact_head",
        ):
            self.assertTrue(any(field in error for error in errors), (field, errors))

    def test_review_facing_phase_requires_identity_inputs_evidence_and_source(self) -> None:
        state = state_fixture()
        state["phase"] = "review-ready"
        state["review"] = {
            "disposition": "EXECUTE",
            "exact_head": None,
            "reviewed_inputs": [],
        }
        state["evidence"] = []
        state["canonical_source"] = None
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(any("exact reviewed head" in error for error in errors), errors)
        self.assertTrue(any("versioned reviewed_inputs" in error for error in errors), errors)
        self.assertTrue(any("claim-scoped evidence" in error for error in errors), errors)
        self.assertTrue(any("canonical_source" in error for error in errors), errors)

    def test_reviewed_and_accepted_head_must_match_source_in_any_phase(self) -> None:
        state = review_ready_state()
        state["review"] = {
            "disposition": "ACCEPT",
            "exact_head": "1" * 40,
            "reviewed_inputs": ["finding@sha256:one"],
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(any("reviewed head must match" in error for error in errors), errors)
        self.assertTrue(any("ACCEPT head must match" in error for error in errors), errors)

    def test_terminal_phase_requires_quiescence_and_terminal_record(self) -> None:
        state = state_fixture()
        state["phase"] = "stopped"
        state["next_transition"] = ""
        state["terminal_record"] = None
        state["writer_lease"] = active_lease()
        state["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 2,
            "head": "2" * 40,
            "purpose": "Obsolete carrier.",
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(any("terminal_record" in error for error in errors), errors)
        self.assertTrue(any("active_carrier" in error for error in errors), errors)
        self.assertTrue(any("active writer lease" in error for error in errors), errors)

    def test_active_carrier_requires_canonical_source(self) -> None:
        state = state_fixture()
        state["canonical_source"] = None
        state["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 2,
            "head": "2" * 40,
            "purpose": "Run the exact target gate.",
        }
        errors = validator.validate_state(Path("state.json"), state)
        self.assertTrue(any("active_carrier requires" in error for error in errors), errors)

    def test_active_lease_requires_exact_identity_renewal_and_takeover_record(self) -> None:
        state = state_fixture()
        lease = active_lease(
            transition=1,
            previous_generation=None,
            transfer_record=None,
        )
        lease["repository"] = "example"
        lease["generation"] = "short"
        lease["renewed_at"] = "2026-07-31T00:59:00Z"
        lease["duration_seconds"] = True
        state["writer_lease"] = lease
        errors = validator.validate_state(Path("state.json"), state)
        for phrase in (
            "repository owner/name",
            "sha256 generation",
            "renewed_at cannot precede",
            "duration_seconds",
            "previous_generation",
            "transfer_record",
        ):
            self.assertTrue(any(phrase in error for error in errors), (phrase, errors))

    def test_authority_is_fail_closed_and_conditionally_complete(self) -> None:
        state = state_fixture()
        state["authority"]["merge"] = authorized_merge()
        self.assertEqual([], validator.validate_state(Path("state.json"), state))

        incomplete = copy.deepcopy(state)
        incomplete["authority"]["merge"]["target"]["operation_id"] = None
        incomplete["authority"]["merge"]["source"]["generation"] = None
        incomplete["authority"]["merge"]["issued_at"] = None
        incomplete["authority"]["merge"]["expires_at"] = None
        errors = validator.validate_state(Path("state.json"), incomplete)
        self.assertTrue(any("operation_id" in error for error in errors), errors)
        self.assertTrue(any("versioned source" in error for error in errors), errors)
        self.assertTrue(any("issued_at" in error for error in errors), errors)
        self.assertTrue(any("expires_at or versioned revocation_record" in error for error in errors), errors)

    def test_duplicate_identity_carrier_and_same_repository_lease_fail_collection(self) -> None:
        first = state_fixture()
        first["writer_lease"] = active_lease()
        first["active_carrier"] = {
            "repository": "teamleaderleo/example",
            "pull_request": 2,
            "head": "2" * 40,
            "purpose": "Run the exact target gate.",
        }
        second = copy.deepcopy(first)
        second["canonical_source"]["branch"] = "fieldwork/example-second"
        second["active_carrier"]["pull_request"] = 3
        second["active_carrier"]["head"] = "3" * 40

        result, text = run_collection([first, second])
        self.assertEqual(1, result)
        self.assertIn("duplicate state id", text)
        self.assertIn("duplicate canonical finding", text)
        self.assertIn("active writer lease duplicates", text)
        self.assertIn("active carrier duplicates invariant", text)

    def test_identical_path_in_different_repositories_does_not_collide(self) -> None:
        first = state_fixture()
        first["id"] = "F001-first"
        first["invariant_id"] = "first-invariant"
        first["canonical_finding"] = "findings/F001-first/finding.md"
        first["writer_lease"] = active_lease(
            repository="teamleaderleo/one",
            resource="shared/path.md",
        )
        second = copy.deepcopy(first)
        second["id"] = "F002-second"
        second["invariant_id"] = "second-invariant"
        second["canonical_finding"] = "findings/F002-second/finding.md"
        second["canonical_source"]["repository"] = "teamleaderleo/two"
        second["writer_lease"] = active_lease(
            repository="teamleaderleo/two",
            resource="shared/path.md",
        )

        result, text = run_collection([first, second])
        self.assertEqual(0, result, text)


if __name__ == "__main__":
    unittest.main()
