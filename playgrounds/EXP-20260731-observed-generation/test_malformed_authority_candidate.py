#!/usr/bin/env python3
"""Controls for the malformed canonical authority isolation candidate."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

import reconcile as parent
import reconcile_malformed_authority_candidate as candidate
from test_reconcile import (
    OBSERVED_AT,
    ObservedGenerationPilotTests,
    authorized,
)


class MalformedAuthorityCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = ObservedGenerationPilotTests(methodName="runTest")
        self.parent.setUp()

    @staticmethod
    def authority_condition(
        projection: dict[str, object], action: str
    ) -> dict[str, object]:
        matches = [
            condition
            for condition in projection["conditions"]
            if condition["type"] == "AuthorityUsable"
            and condition["inputs"].get("action") == action
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"expected one AuthorityUsable condition for {action}, got {matches}"
            )
        return matches[0]

    def test_01_valid_record_output_is_parent_identical(self) -> None:
        record = deepcopy(self.parent.cross_repository)
        facts = self.parent.live_facts(record)

        expected = parent.reconcile(record, facts, OBSERVED_AT)
        actual = candidate.reconcile(record, facts, OBSERVED_AT)

        self.assertEqual(expected, actual)

    def test_02_malformed_canonical_time_denies_only_that_action(self) -> None:
        record = deepcopy(self.parent.cross_repository)
        record["authority"]["merge"] = authorized(expires_at="not-a-time")
        record["authority"]["upstream_contact"] = authorized(
            expires_at="2026-08-01T02:30:00Z"
        )
        facts = self.parent.live_facts(record)
        record_before = json.dumps(record, sort_keys=True)
        facts_before = json.dumps(facts, sort_keys=True)

        projection = candidate.reconcile(record, facts, OBSERVED_AT)

        malformed = self.authority_condition(projection, "merge")
        current = self.authority_condition(projection, "upstream_contact")
        self.assertEqual(
            ("Unknown", "InvalidAuthorityTime"),
            (malformed["status"], malformed["reason"]),
        )
        self.assertEqual("denied", projection["effective_authority"]["merge"])
        self.assertEqual(
            ("True", "AuthorityCurrent"),
            (current["status"], current["reason"]),
        )
        self.assertEqual(
            "authorized", projection["effective_authority"]["upstream_contact"]
        )
        self.assertIn(
            "AuthorityUsable: InvalidAuthorityTime",
            projection["proposed_repairs"],
        )

        condition_types = {condition["type"] for condition in projection["conditions"]}
        self.assertIn("SourceReviewCurrent", condition_types)
        self.assertIn("InputGenerationsComplete", condition_types)
        self.assertIn("CarrierWipValid", condition_types)
        self.assertIn("CarrierCurrent", condition_types)
        self.assertIn("CrossRepositoryIdentityComplete", condition_types)
        self.assertIn("TerminalContinuityVisible", condition_types)

        self.assertEqual(record_before, json.dumps(record, sort_keys=True))
        self.assertEqual(facts_before, json.dumps(facts, sort_keys=True))

    def test_03_timezone_naive_expiry_is_also_isolated(self) -> None:
        record = deepcopy(self.parent.cross_repository)
        record["authority"]["release"] = authorized(
            expires_at="2026-08-01T02:30:00"
        )
        record["authority"]["deploy"] = authorized(
            expires_at=None,
            revocation_record="authority/deploy@v1",
        )
        facts = self.parent.live_facts(record)
        facts["authority_revocations"] = {"authority/deploy@v1": False}

        projection = candidate.reconcile(record, facts, OBSERVED_AT)

        malformed = self.authority_condition(projection, "release")
        current = self.authority_condition(projection, "deploy")
        self.assertEqual(
            ("Unknown", "InvalidAuthorityTime"),
            (malformed["status"], malformed["reason"]),
        )
        self.assertEqual(
            ("True", "AuthorityCurrent"),
            (current["status"], current["reason"]),
        )
        self.assertEqual("denied", projection["effective_authority"]["release"])
        self.assertEqual("authorized", projection["effective_authority"]["deploy"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
