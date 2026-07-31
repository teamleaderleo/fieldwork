#!/usr/bin/env python3
"""Exact-source controls for the malformed authority timestamp repair."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "reconcile.py"
DECISION_SOURCE = HERE / "decision_currentness.py"
PATCH = HERE / "repairs" / "0001-fail-closed-malformed-authority-time.patch"
FIXTURE = HERE / "fixtures" / "cross-repository.json"
OBSERVED_AT = "2026-07-31T02:30:00Z"
EXPECTED_SOURCE_BLOB = "9e664220b3b024b92cbbc4444c15e87545cbd3cd"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def authorized(
    *, expires_at: object, revocation_record: str | None = None
) -> dict[str, object]:
    return {
        "state": "authorized",
        "expires_at": expires_at,
        "revocation_record": revocation_record,
    }


def live_facts(record: dict[str, object]) -> dict[str, object]:
    source = record["canonical_source"]
    carrier = record["active_carriers"][0]
    return {
        "generation": "live-facts-malformed-authority-time-v1",
        "source_heads": {
            f"{source['repository']}:{source['branch']}": source["head"],
        },
        "alternative_heads": {},
        "carrier_facts": {
            carrier["id"]: {
                "generation": "carrier-fact-malformed-authority-time-v1",
                "repository": carrier["repository"],
                "pull_request": carrier["pull_request"],
                "head": carrier["head"],
                "state": "open",
                "accessible": True,
                "checks_generation": carrier["checks_generation"],
            }
        },
        "authority_revocations": {},
    }


def authority_condition(
    projection: dict[str, object], action: str
) -> dict[str, object]:
    return next(
        condition
        for condition in projection["conditions"]
        if condition["type"] == "AuthorityUsable"
        and condition["inputs"]["action"] == action
    )


@contextmanager
def patched_modules():
    with TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        target = root / "playgrounds" / "EXP-20260731-observed-generation"
        target.mkdir(parents=True)
        shutil.copy2(SOURCE, target / "reconcile.py")
        shutil.copy2(DECISION_SOURCE, target / "decision_currentness.py")
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(root), "apply", "--check", str(PATCH)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(root), "apply", str(PATCH)],
            check=True,
        )

        patched_reconcile = load_module(
            "fieldwork_patched_reconcile",
            target / "reconcile.py",
        )
        previous = sys.modules.get("reconcile")
        sys.modules["reconcile"] = patched_reconcile
        try:
            patched_decision = load_module(
                "fieldwork_patched_decision_currentness",
                target / "decision_currentness.py",
            )
        finally:
            if previous is None:
                del sys.modules["reconcile"]
            else:
                sys.modules["reconcile"] = previous
        yield patched_reconcile, patched_decision


class MalformedAuthorityTimePatchTests(unittest.TestCase):
    def test_exact_source_blob_and_zero_fuzz_patch_application(self) -> None:
        observed_blob = subprocess.run(
            ["git", "hash-object", str(SOURCE)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(EXPECTED_SOURCE_BLOB, observed_blob)
        with patched_modules() as (patched, _):
            self.assertTrue(callable(patched.reconcile))

    def test_baseline_aborts_complete_reconciliation(self) -> None:
        baseline = load_module("fieldwork_baseline_reconcile", SOURCE)
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at="not-a-time")
        with self.assertRaises(ValueError):
            baseline.reconcile(record, live_facts(record), OBSERVED_AT)

    def test_malformed_expiry_denies_only_the_affected_action(self) -> None:
        invalid_values: tuple[object, ...] = (
            "not-a-time",
            "2026-08-01T02:30:00",
            123,
        )
        with patched_modules() as (patched, decision):
            for invalid in invalid_values:
                with self.subTest(invalid=invalid):
                    record = fixture()
                    record["authority"] = {
                        "merge": authorized(expires_at=invalid),
                        "deploy": authorized(expires_at="2026-08-01T02:30:00Z"),
                    }
                    facts = live_facts(record)
                    projection = patched.reconcile(record, facts, OBSERVED_AT)

                    merge = authority_condition(projection, "merge")
                    deploy = authority_condition(projection, "deploy")
                    self.assertEqual(
                        ("Unknown", "InvalidAuthorityTime"),
                        (merge["status"], merge["reason"]),
                    )
                    self.assertEqual(
                        ("True", "AuthorityCurrent"),
                        (deploy["status"], deploy["reason"]),
                    )
                    self.assertEqual("denied", projection["effective_authority"]["merge"])
                    self.assertEqual(
                        "authorized",
                        projection["effective_authority"]["deploy"],
                    )

                    currentness = decision.authorization_currentness(
                        projection,
                        OBSERVED_AT,
                        record,
                        facts,
                    )
                    self.assertEqual(
                        "True",
                        currentness["projection_authority_integrity"]["merge"]["status"],
                    )
                    self.assertEqual(
                        "denied",
                        currentness["actions"]["merge"]["effective"],
                    )
                    self.assertEqual(
                        "authorized",
                        currentness["actions"]["deploy"]["effective"],
                    )

    def test_revocation_bounded_authority_remains_independent(self) -> None:
        with patched_modules() as (patched, _):
            record = fixture()
            record["authority"] = {
                "merge": authorized(expires_at="bad"),
                "release": authorized(
                    expires_at=None,
                    revocation_record="authority/release@v1",
                ),
            }
            facts = live_facts(record)
            facts["authority_revocations"] = {"authority/release@v1": False}
            projection = patched.reconcile(record, facts, OBSERVED_AT)

            self.assertEqual("denied", projection["effective_authority"]["merge"])
            self.assertEqual(
                "authorized",
                projection["effective_authority"]["release"],
            )
            self.assertEqual(
                "AuthorityCurrent",
                authority_condition(projection, "release")["reason"],
            )

    def test_repair_does_not_mutate_canonical_inputs(self) -> None:
        with patched_modules() as (patched, _):
            record = fixture()
            record["authority"]["merge"] = authorized(expires_at="bad")
            facts = live_facts(record)
            record_before = json.dumps(record, sort_keys=True)
            facts_before = json.dumps(facts, sort_keys=True)

            patched.reconcile(record, facts, OBSERVED_AT)

            self.assertEqual(record_before, json.dumps(record, sort_keys=True))
            self.assertEqual(facts_before, json.dumps(facts, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
