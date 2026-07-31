#!/usr/bin/env python3
"""Deterministic controls for the repaired issue #325 reconciliation pilot."""

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
from reconcile import (  # noqa: E402
    input_generation_manifest,
    projection_is_current,
    reconcile,
    render_compact,
)


OBSERVED_AT = "2026-07-31T02:30:00Z"


def load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def source_key(record: dict[str, object]) -> str:
    source = record["canonical_source"]
    return f"{source['repository']}:{source['branch']}"


def authorized(
    *, expires_at: str | None, revocation_record: str | None = None
) -> dict[str, object]:
    return {
        "state": "authorized",
        "expires_at": expires_at,
        "revocation_record": revocation_record,
    }


def carrier_fact(
    carrier: dict[str, object], **overrides: object
) -> dict[str, object]:
    fact: dict[str, object] = {
        "generation": f"carrier-fact-{carrier['id']}-v1",
        "repository": carrier["repository"],
        "pull_request": carrier["pull_request"],
        "head": carrier["head"],
        "state": "open",
        "accessible": True,
        "checks_generation": carrier["checks_generation"],
    }
    fact.update(overrides)
    return fact


class ObservedGenerationPilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.terminal = load_fixture("terminal-continuity.json")
        self.comparative = load_fixture("comparative-alternatives.json")
        self.cross_repository = load_fixture("cross-repository.json")

    def live_facts(self, record: dict[str, object]) -> dict[str, object]:
        return {
            "generation": f"live-facts-{record['id']}-v1",
            "source_heads": {
                source_key(record): record["canonical_source"]["head"]
            },
            "alternative_heads": {
                alternative["id"]: alternative["head"]
                for alternative in record.get("alternatives", [])
            },
            "carrier_facts": {
                carrier["id"]: carrier_fact(carrier)
                for carrier in record.get("active_carriers", [])
                if carrier.get("state") == "active"
            },
            "authority_revocations": {},
        }

    @staticmethod
    def condition(
        projection: dict[str, object], condition_type: str, **inputs: object
    ) -> dict[str, object]:
        matches = [
            condition
            for condition in projection["conditions"]
            if condition["type"] == condition_type
            and all(condition["inputs"].get(key) == value for key, value in inputs.items())
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"expected one {condition_type} condition for {inputs}, got {matches}"
            )
        return matches[0]

    def test_01_current_exact_source_review_and_inputs_are_current(self) -> None:
        facts = self.live_facts(self.comparative)
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        source = self.condition(projection, "SourceReviewCurrent")
        generations = self.condition(projection, "InputGenerationsComplete")
        carrier = self.condition(
            projection, "CarrierCurrent", carrier_id="bounded-repair-carrier"
        )
        self.assertEqual(("True", "ExactHeadsMatch"), (source["status"], source["reason"]))
        self.assertEqual(
            ("True", "ExactInputGenerations"),
            (generations["status"], generations["reason"]),
        )
        self.assertEqual(
            ("True", "ExactCarrierFact"),
            (carrier["status"], carrier["reason"]),
        )
        self.assertTrue(projection_is_current(projection, self.comparative, facts))

    def test_02_moved_source_expires_the_recorded_review(self) -> None:
        facts = self.live_facts(self.comparative)
        facts["source_heads"][source_key(self.comparative)] = "9" * 40
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        condition = self.condition(projection, "SourceReviewCurrent")
        self.assertEqual(("False", "SourceHeadMoved"), (condition["status"], condition["reason"]))
        self.assertIn("SourceReviewCurrent: SourceHeadMoved", projection["proposed_repairs"])

    def test_03_semantic_record_change_expires_projection_without_manual_token_bump(self) -> None:
        facts = self.live_facts(self.comparative)
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        moved = deepcopy(self.comparative)
        moved["phase"] = "review-ready"
        self.assertEqual(
            self.comparative["spec_generation"], moved["spec_generation"]
        )
        self.assertFalse(projection_is_current(projection, moved, facts))
        self.assertNotEqual(
            projection["input_generations"]["record_digest"],
            input_generation_manifest(moved, facts)["record_digest"],
        )

    def test_04_finding_generation_movement_expires_projection(self) -> None:
        facts = self.live_facts(self.comparative)
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        moved = deepcopy(self.comparative)
        moved["finding_generation"] = "finding-comparison-v2"
        self.assertFalse(projection_is_current(projection, moved, facts))

    def test_05_live_fact_generation_or_content_movement_expires_projection(self) -> None:
        facts = self.live_facts(self.comparative)
        projection = reconcile(self.comparative, facts, OBSERVED_AT)

        moved_generation = deepcopy(facts)
        moved_generation["generation"] = "live-facts-comparison-v2"
        self.assertFalse(
            projection_is_current(projection, self.comparative, moved_generation)
        )

        moved_content = deepcopy(facts)
        moved_content["authority_revocations"]["authority/example@v1"] = False
        self.assertEqual(facts["generation"], moved_content["generation"])
        self.assertFalse(
            projection_is_current(projection, self.comparative, moved_content)
        )

    def test_06_moving_one_alternative_expires_only_that_alternative(self) -> None:
        facts = self.live_facts(self.comparative)
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

    def test_07_missing_live_source_and_alternative_facts_are_unknown(self) -> None:
        facts = self.live_facts(self.comparative)
        facts["source_heads"] = {}
        facts["alternative_heads"] = {}
        projection = reconcile(self.comparative, facts, OBSERVED_AT)
        source = self.condition(projection, "SourceReviewCurrent")
        self.assertEqual(("Unknown", "MissingLiveSourceFact"), (source["status"], source["reason"]))
        self.assertTrue(
            all(
                condition["status"] == "Unknown"
                for condition in projection["alternative_conditions"]
            )
        )

    def test_08_authority_is_fail_closed_for_absent_expired_revoked_and_unresolved(self) -> None:
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
        facts = self.live_facts(record)
        facts["authority_revocations"] = {"authority/release@v1": True}
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

    def test_09_permanent_unrevocable_authority_is_unusable(self) -> None:
        record = deepcopy(self.cross_repository)
        record["authority"]["merge"] = authorized(
            expires_at=None, revocation_record=None
        )
        projection = reconcile(record, self.live_facts(record), OBSERVED_AT)
        condition = next(
            condition
            for condition in projection["conditions"]
            if condition["type"] == "AuthorityUsable"
            and condition["inputs"]["action"] == "merge"
        )
        self.assertEqual(("Unknown", "UnboundedAuthority"), (condition["status"], condition["reason"]))
        self.assertEqual("denied", projection["effective_authority"]["merge"])

    def test_10_duplicate_carriers_report_conflict_without_selection(self) -> None:
        record = deepcopy(self.cross_repository)
        duplicate = deepcopy(record["active_carriers"][0])
        duplicate["id"] = "second-carrier"
        duplicate["pull_request"] = 902
        duplicate["checks_generation"] = "checks-second-v1"
        record["active_carriers"].append(duplicate)
        facts = self.live_facts(record)
        projection = reconcile(record, facts, OBSERVED_AT)
        condition = self.condition(projection, "CarrierWipValid")
        self.assertEqual(("False", "DuplicateActiveCarriers"), (condition["status"], condition["reason"]))
        self.assertEqual(
            ["external-execution-carrier", "second-carrier"],
            condition["inputs"]["active_carriers"],
        )
        self.assertNotIn("selected_carrier", projection)

    def test_11_carrier_currentness_distinguishes_moved_closed_missing_and_inaccessible(self) -> None:
        carrier_id = "external-execution-carrier"
        cases = [
            ({"head": "7" * 40}, "False", "CarrierHeadMoved"),
            ({"state": "closed"}, "False", "CarrierClosed"),
            ({"checks_generation": "checks-new"}, "False", "CarrierChecksMoved"),
            ({"accessible": False}, "Unknown", "CarrierInaccessible"),
        ]
        for overrides, expected_status, expected_reason in cases:
            with self.subTest(reason=expected_reason):
                facts = self.live_facts(self.cross_repository)
                facts["carrier_facts"][carrier_id].update(overrides)
                projection = reconcile(self.cross_repository, facts, OBSERVED_AT)
                condition = self.condition(
                    projection, "CarrierCurrent", carrier_id=carrier_id
                )
                self.assertEqual(
                    (expected_status, expected_reason),
                    (condition["status"], condition["reason"]),
                )

        facts = self.live_facts(self.cross_repository)
        del facts["carrier_facts"][carrier_id]
        projection = reconcile(self.cross_repository, facts, OBSERVED_AT)
        condition = self.condition(
            projection, "CarrierCurrent", carrier_id=carrier_id
        )
        self.assertEqual(("Unknown", "MissingCarrierFact"), (condition["status"], condition["reason"]))
        generations = self.condition(projection, "InputGenerationsComplete")
        self.assertEqual("Unknown", generations["status"])
        self.assertIn(
            f"carrier_generations.{carrier_id}", generations["inputs"]["missing"]
        )

    def test_12_identical_paths_in_different_repositories_do_not_collide(self) -> None:
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

    def test_13_stopped_path_retains_and_renders_research_continuity(self) -> None:
        facts = self.live_facts(self.terminal)
        projection = reconcile(self.terminal, facts, OBSERVED_AT)
        condition = self.condition(projection, "TerminalContinuityVisible")
        self.assertEqual(("True", "ContinuityRetained"), (condition["status"], condition["reason"]))
        rendered = render_compact(projection)
        self.assertIn("TERMINAL CONTINUITY", rendered)
        self.assertIn("test a distinct ownership boundary", rendered)
        self.assertIn("counterexample under target execution", rendered)

        hidden = deepcopy(self.terminal)
        hidden["terminal"]["avenues"] = []
        projection = reconcile(hidden, facts, OBSERVED_AT)
        condition = self.condition(projection, "TerminalContinuityVisible")
        self.assertEqual("False", condition["status"])
        self.assertIn("avenues", condition["inputs"]["missing"])

    def test_14_missing_required_generation_is_unknown_and_never_current(self) -> None:
        facts = self.live_facts(self.comparative)
        record = deepcopy(self.comparative)
        del record["finding_generation"]
        projection = reconcile(record, facts, OBSERVED_AT)
        condition = self.condition(projection, "InputGenerationsComplete")
        self.assertEqual(("Unknown", "MissingInputGeneration"), (condition["status"], condition["reason"]))
        self.assertIn("finding_generation", condition["inputs"]["missing"])
        self.assertFalse(projection_is_current(projection, record, facts))

    def test_15_success_and_failure_leave_inputs_byte_for_byte_unchanged(self) -> None:
        record = deepcopy(self.cross_repository)
        facts = self.live_facts(record)
        record_before = json.dumps(record, sort_keys=True)
        facts_before = json.dumps(facts, sort_keys=True)
        projection = reconcile(record, facts, OBSERVED_AT)
        self.assertEqual(record_before, json.dumps(record, sort_keys=True))
        self.assertEqual(facts_before, json.dumps(facts, sort_keys=True))
        self.assertIn("INPUT GENERATIONS", render_compact(projection))

        broken = deepcopy(record)
        broken["authority"]["merge"] = authorized(expires_at="not-a-time")
        broken_before = json.dumps(broken, sort_keys=True)
        with self.assertRaises(ValueError):
            reconcile(broken, facts, OBSERVED_AT)
        self.assertEqual(broken_before, json.dumps(broken, sort_keys=True))
        self.assertEqual(facts_before, json.dumps(facts, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
