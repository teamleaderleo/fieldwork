#!/usr/bin/env python3
"""Deterministic controls for the issue #325 reconciliation pilot."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
sys.path.insert(0, str(HERE))

from lease_checks import evaluate_writer_leases  # noqa: E402
from reconcile import projection_is_current, reconcile, render_compact  # noqa: E402


OBSERVED_AT = "2026-07-31T02:30:00Z"


def load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def source_key(record: dict[str, object]) -> str:
    source = record["canonical_source"]
    return f"{source['repository']}:{source['branch']}"


def authorized(*, expires_at: str | None, revocation_record: str | None = None) -> dict[str, object]:
    return {
        "state": "authorized",
        "expires_at": expires_at,
        "revocation_record": revocation_record,
    }


class ObservedGenerationPilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.terminal = load_fixture("terminal-continuity.json")
        self.comparative = load_fixture("comparative-alternatives.json")
        self.cross_repository = load_fixture("cross-repository.json")

    def comparative_live_facts(self) -> dict[str, object]:
        return {
            "source_heads": {
                source_key(self.comparative): self.comparative["canonical_source"]["head"]
            },
            "alternative_heads": {
                alternative["id"]: alternative["head"]
                for alternative in self.comparative["alternatives"]
            },
            "authority_revocations": {},
        }

    def test_01_current_exact_source_and_review_are_current(self) -> None:
        projection = reconcile(
            self.comparative,
            self.comparative_live_facts(),
            OBSERVED_AT,
        )
        condition = projection["conditions"][0]
        self.assertEqual("SourceReviewCurrent", condition["type"])
        self.assertEqual("True", condition["status"])
        self.assertEqual("ExactHeadsMatch", condition["reason"])

    def test_02_moved_source_expires_the_recorded_review(self) -> None:
        facts = self.comparative_live_facts()
        facts["source_heads"][source_key(self.comparative)] = "9" * 40
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        condition = projection["conditions"][0]
        self.assertEqual("False", condition["status"])
        self.assertEqual("SourceHeadMoved", condition["reason"])
        self.assertIn("SourceReviewCurrent: SourceHeadMoved", projection["proposed_repairs"])

    def test_03_projection_from_generation_n_is_rejected_after_n_plus_one(self) -> None:
        projection = reconcile(
            self.comparative,
            self.comparative_live_facts(),
            OBSERVED_AT,
        )
        self.assertTrue(
            projection_is_current(projection, self.comparative["spec_generation"])
        )
        moved = deepcopy(self.comparative)
        moved["spec_generation"] = "comparison-spec-v2"
        self.assertFalse(projection_is_current(projection, moved["spec_generation"]))

    def test_04_moving_one_alternative_expires_only_that_alternative(self) -> None:
        facts = self.comparative_live_facts()
        facts["alternative_heads"]["staged-ownership"] = "8" * 40
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        by_id = {
            condition["inputs"]["alternative_id"]: condition
            for condition in projection["alternative_conditions"]
        }
        self.assertEqual("False", by_id["staged-ownership"]["status"])
        self.assertEqual("AlternativeHeadMoved", by_id["staged-ownership"]["reason"])
        self.assertEqual("True", by_id["bounded-repair"]["status"])
        self.assertEqual("True", by_id["automatic-rollback"]["status"])

    def test_05_missing_live_fact_is_unknown_not_negative(self) -> None:
        projection = reconcile(
            self.comparative,
            {"source_heads": {}, "alternative_heads": {}, "authority_revocations": {}},
            OBSERVED_AT,
        )
        source_condition = projection["conditions"][0]
        self.assertEqual("Unknown", source_condition["status"])
        self.assertEqual("MissingLiveSourceFact", source_condition["reason"])
        self.assertTrue(
            all(
                condition["status"] == "Unknown"
                for condition in projection["alternative_conditions"]
            )
        )

    def test_06_authority_is_fail_closed_for_absent_expired_revoked_and_unresolved(self) -> None:
        record = deepcopy(self.cross_repository)
        record["authority"] = {
            "merge": authorized(expires_at="2026-07-30T02:30:00Z"),
            "release": authorized(
                expires_at=None,
                revocation_record="authority/release@v1",
            ),
            "deploy": authorized(
                expires_at=None,
                revocation_record="authority/deploy@v1",
            ),
            "upstream_contact": authorized(expires_at="2026-08-01T02:30:00Z"),
        }
        facts = {
            "source_heads": {source_key(record): record["canonical_source"]["head"]},
            "alternative_heads": {},
            "authority_revocations": {
                "authority/release@v1": True,
            },
        }
        projection = reconcile(record, facts, OBSERVED_AT)
        effective = projection["effective_authority"]
        self.assertEqual("denied", effective["merge"])
        self.assertEqual("denied", effective["release"])
        self.assertEqual("denied", effective["deploy"])
        self.assertEqual("authorized", effective["upstream_contact"])
        self.assertEqual("denied", effective["private_or_production_data"])
        self.assertEqual("denied", effective["material_spending"])
        reasons = {
            condition["inputs"]["action"]: condition["reason"]
            for condition in projection["conditions"]
            if condition["type"] == "AuthorityUsable"
        }
        self.assertEqual("AuthorityExpired", reasons["merge"])
        self.assertEqual("AuthorityRevoked", reasons["release"])
        self.assertEqual("RevocationUnresolved", reasons["deploy"])
        self.assertEqual("MissingAuthorityRecord", reasons["material_spending"])

    def test_07_duplicate_carriers_report_conflict_without_selection(self) -> None:
        record = deepcopy(self.cross_repository)
        duplicate = deepcopy(record["active_carriers"][0])
        duplicate["id"] = "second-carrier"
        duplicate["pull_request"] = 902
        record["active_carriers"].append(duplicate)
        facts = {
            "source_heads": {source_key(record): record["canonical_source"]["head"]},
            "alternative_heads": {},
            "authority_revocations": {},
        }
        projection = reconcile(record, facts, OBSERVED_AT)
        condition = next(
            item for item in projection["conditions"] if item["type"] == "CarrierWipValid"
        )
        self.assertEqual("False", condition["status"])
        self.assertEqual("DuplicateActiveCarriers", condition["reason"])
        self.assertEqual(
            ["external-execution-carrier", "second-carrier"],
            condition["inputs"]["active_carriers"],
        )
        self.assertNotIn("selected_carrier", projection)

    def test_08_identical_paths_in_different_repositories_do_not_collide(self) -> None:
        leases = [
            {
                "state": "active",
                "holder": "worker-a",
                "repository": "teamleaderleo/one",
                "resource_kind": "path",
                "resource": "findings/shared/state.json",
            },
            {
                "state": "active",
                "holder": "worker-b",
                "repository": "teamleaderleo/two",
                "resource_kind": "path",
                "resource": "findings/shared/state.json",
            },
        ]
        result = evaluate_writer_leases(leases)
        self.assertEqual("True", result["status"])
        self.assertEqual([], result["collisions"])

        duplicate = deepcopy(leases[1])
        duplicate["repository"] = "teamleaderleo/one"
        result = evaluate_writer_leases([leases[0], duplicate])
        self.assertEqual("False", result["status"])
        self.assertEqual("DuplicateActiveLease", result["reason"])

    def test_09_stopped_path_retains_research_continuity(self) -> None:
        facts = {
            "source_heads": {
                source_key(self.terminal): self.terminal["canonical_source"]["head"]
            },
            "alternative_heads": {},
            "authority_revocations": {},
        }
        projection = reconcile(self.terminal, facts, OBSERVED_AT)
        condition = next(
            item
            for item in projection["conditions"]
            if item["type"] == "TerminalContinuityVisible"
        )
        self.assertEqual("True", condition["status"])
        self.assertEqual("ContinuityRetained", condition["reason"])

        hidden = deepcopy(self.terminal)
        hidden["terminal"]["avenues"] = []
        projection = reconcile(hidden, facts, OBSERVED_AT)
        condition = next(
            item
            for item in projection["conditions"]
            if item["type"] == "TerminalContinuityVisible"
        )
        self.assertEqual("False", condition["status"])
        self.assertIn("avenues", condition["inputs"]["missing"])

    def test_10_success_and_failure_leave_inputs_byte_for_byte_unchanged(self) -> None:
        record = deepcopy(self.cross_repository)
        facts = {
            "source_heads": {source_key(record): record["canonical_source"]["head"]},
            "alternative_heads": {},
            "authority_revocations": {},
        }
        record_before = json.dumps(record, sort_keys=True)
        facts_before = json.dumps(facts, sort_keys=True)
        projection = reconcile(record, facts, OBSERVED_AT)
        self.assertEqual(record_before, json.dumps(record, sort_keys=True))
        self.assertEqual(facts_before, json.dumps(facts, sort_keys=True))
        self.assertIn("OBSERVED GENERATION", render_compact(projection))

        broken = deepcopy(record)
        broken["authority"]["merge"] = authorized(expires_at="not-a-time")
        broken_before = json.dumps(broken, sort_keys=True)
        with self.assertRaises(ValueError):
            reconcile(broken, facts, OBSERVED_AT)
        self.assertEqual(broken_before, json.dumps(broken, sort_keys=True))
        self.assertEqual(facts_before, json.dumps(facts, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
