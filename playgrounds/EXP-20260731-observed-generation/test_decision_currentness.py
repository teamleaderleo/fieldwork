#!/usr/bin/env python3
"""Reversing controls for time-dependent decision currentness."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
sys.path.insert(0, str(HERE))

from decision_currentness import (  # noqa: E402
    decision_currentness,
    effective_authority_at,
)
from reconcile import projection_is_current, reconcile  # noqa: E402


T0 = "2026-07-31T02:30:00Z"
EXPIRY = "2026-07-31T03:00:00Z"
T1 = "2026-07-31T03:00:00Z"


def fixture() -> dict[str, object]:
    return json.loads(
        (FIXTURES / "cross-repository.json").read_text(encoding="utf-8")
    )


def live_facts(record: dict[str, object]) -> dict[str, object]:
    source = record["canonical_source"]
    carrier = record["active_carriers"][0]
    return {
        "generation": "live-facts-decision-horizon-v1",
        "source_heads": {
            f"{source['repository']}:{source['branch']}": source["head"],
        },
        "alternative_heads": {},
        "carrier_facts": {
            carrier["id"]: {
                "generation": "carrier-fact-decision-horizon-v1",
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


def authority_reason(projection: dict[str, object], action: str) -> str:
    return next(
        condition["reason"]
        for condition in projection["conditions"]
        if condition["type"] == "AuthorityUsable"
        and condition["inputs"]["action"] == action
    )


class DecisionCurrentnessTests(unittest.TestCase):
    def test_expired_time_horizon_invalidates_decision_without_input_movement(self) -> None:
        record = fixture()
        record["authority"]["merge"] = {
            "state": "authorized",
            "expires_at": EXPIRY,
            "revocation_record": None,
        }
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)

        self.assertTrue(projection_is_current(projection, record, facts))
        self.assertEqual("AuthorityCurrent", authority_reason(projection, "merge"))
        self.assertEqual(
            {
                "status": "True",
                "reason": "DecisionCurrent",
                "observed_at": T0,
                "current_at": T0,
                "valid_until": EXPIRY,
            },
            decision_currentness(projection, T0),
        )
        self.assertEqual("authorized", effective_authority_at(projection, T0)["merge"])

        # Only wall-clock time moves. Historical input identity remains exact, but
        # present authority must fail closed at the expiry boundary.
        self.assertTrue(projection_is_current(projection, record, facts))
        self.assertEqual(
            ("False", "DecisionHorizonElapsed"),
            (
                decision_currentness(projection, T1)["status"],
                decision_currentness(projection, T1)["reason"],
            ),
        )
        self.assertEqual("denied", effective_authority_at(projection, T1)["merge"])

        fresh = reconcile(record, facts, T1)
        self.assertEqual("AuthorityExpired", authority_reason(fresh, "merge"))
        self.assertEqual("denied", fresh["effective_authority"]["merge"])

    def test_earliest_current_authority_expiry_sets_the_horizon(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": {
                "state": "authorized",
                "expires_at": "2026-07-31T04:00:00Z",
                "revocation_record": None,
            },
            "deploy": {
                "state": "authorized",
                "expires_at": EXPIRY,
                "revocation_record": None,
            },
        }
        projection = reconcile(record, live_facts(record), T0)
        self.assertEqual(EXPIRY, decision_currentness(projection, T0)["valid_until"])
        at_horizon = effective_authority_at(projection, T1)
        self.assertEqual("denied", at_horizon["merge"])
        self.assertEqual("denied", at_horizon["deploy"])

    def test_revocation_bounded_authority_has_no_wall_clock_horizon(self) -> None:
        record = fixture()
        record["authority"]["merge"] = {
            "state": "authorized",
            "expires_at": None,
            "revocation_record": "authority/merge@v1",
        }
        facts = live_facts(record)
        facts["authority_revocations"] = {"authority/merge@v1": False}
        projection = reconcile(record, facts, T0)

        currentness = decision_currentness(projection, "2026-08-01T02:30:00Z")
        self.assertEqual(("True", None), (currentness["status"], currentness["valid_until"]))
        self.assertEqual(
            "authorized",
            effective_authority_at(projection, "2026-08-01T02:30:00Z")["merge"],
        )

    def test_future_or_malformed_decision_boundaries_fail_closed(self) -> None:
        record = fixture()
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)

        future = decision_currentness(projection, "2026-07-31T02:00:00Z")
        self.assertEqual(
            ("False", "ProjectionObservedInFuture"),
            (future["status"], future["reason"]),
        )

        malformed = deepcopy(projection)
        malformed["observed_at"] = "not-a-time"
        currentness = decision_currentness(malformed, T1)
        self.assertEqual(
            ("False", "InvalidDecisionTime"),
            (currentness["status"], currentness["reason"]),
        )
        self.assertTrue(
            all(state == "denied" for state in effective_authority_at(malformed, T1).values())
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
