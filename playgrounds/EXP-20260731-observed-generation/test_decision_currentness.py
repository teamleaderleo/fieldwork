#!/usr/bin/env python3
"""Reversing controls for per-action time-dependent decision currentness."""

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
LATER_EXPIRY = "2026-07-31T04:00:00Z"


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


def authorized(
    *, expires_at: str | None, revocation_record: str | None = None
) -> dict[str, object]:
    return {
        "state": "authorized",
        "expires_at": expires_at,
        "revocation_record": revocation_record,
    }


class DecisionCurrentnessTests(unittest.TestCase):
    def test_expired_action_invalidates_its_decision_without_input_movement(self) -> None:
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at=EXPIRY)
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)

        self.assertTrue(projection_is_current(projection, record, facts))
        self.assertEqual("AuthorityCurrent", authority_reason(projection, "merge"))
        at_observation = decision_currentness(projection, T0)
        self.assertEqual(("True", "DecisionCurrent"), (at_observation["status"], at_observation["reason"]))
        self.assertEqual(EXPIRY, at_observation["valid_until"])
        self.assertEqual("True", at_observation["actions"]["merge"]["status"])
        self.assertEqual("authorized", effective_authority_at(projection, T0)["merge"])

        # Only wall-clock time moves. Historical input identity remains exact, but
        # this action's present authority fails closed at its own expiry boundary.
        self.assertTrue(projection_is_current(projection, record, facts))
        elapsed = decision_currentness(projection, T1)
        self.assertEqual(
            ("False", "DecisionRefreshRequired"),
            (elapsed["status"], elapsed["reason"]),
        )
        self.assertEqual(
            ("False", "AuthorityHorizonElapsed"),
            (
                elapsed["actions"]["merge"]["status"],
                elapsed["actions"]["merge"]["reason"],
            ),
        )
        self.assertEqual("denied", effective_authority_at(projection, T1)["merge"])

        fresh = reconcile(record, facts, T1)
        self.assertEqual("AuthorityExpired", authority_reason(fresh, "merge"))
        self.assertEqual("denied", fresh["effective_authority"]["merge"])

    def test_one_expired_action_does_not_revoke_another_current_action(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(expires_at=LATER_EXPIRY),
            "deploy": authorized(expires_at=EXPIRY),
        }
        projection = reconcile(record, live_facts(record), T0)
        self.assertEqual(EXPIRY, decision_currentness(projection, T0)["valid_until"])

        at_first_horizon = decision_currentness(projection, T1)
        self.assertEqual("DecisionRefreshRequired", at_first_horizon["reason"])
        self.assertEqual(LATER_EXPIRY, at_first_horizon["valid_until"])
        self.assertEqual("True", at_first_horizon["actions"]["merge"]["status"])
        self.assertEqual("False", at_first_horizon["actions"]["deploy"]["status"])

        effective = effective_authority_at(projection, T1)
        self.assertEqual("authorized", effective["merge"])
        self.assertEqual("denied", effective["deploy"])

    def test_expiry_does_not_revoke_generation_bounded_authority(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(
                expires_at=None,
                revocation_record="authority/merge@v1",
            ),
            "deploy": authorized(expires_at=EXPIRY),
        }
        facts = live_facts(record)
        facts["authority_revocations"] = {"authority/merge@v1": False}
        projection = reconcile(record, facts, T0)

        at_horizon = decision_currentness(projection, T1)
        self.assertEqual("GenerationBoundCurrent", at_horizon["actions"]["merge"]["reason"])
        self.assertEqual("AuthorityHorizonElapsed", at_horizon["actions"]["deploy"]["reason"])
        effective = effective_authority_at(projection, T1)
        self.assertEqual("authorized", effective["merge"])
        self.assertEqual("denied", effective["deploy"])

    def test_malformed_one_action_time_denies_only_that_action(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(expires_at=LATER_EXPIRY),
            "deploy": authorized(expires_at=EXPIRY),
        }
        projection = reconcile(record, live_facts(record), T0)
        malformed = deepcopy(projection)
        deploy_condition = next(
            condition
            for condition in malformed["conditions"]
            if condition["type"] == "AuthorityUsable"
            and condition["inputs"]["action"] == "deploy"
        )
        deploy_condition["inputs"]["expires_at"] = "not-a-time"

        currentness = decision_currentness(malformed, T0)
        self.assertEqual("DecisionRefreshRequired", currentness["reason"])
        self.assertEqual("True", currentness["actions"]["merge"]["status"])
        self.assertEqual("InvalidAuthorityTime", currentness["actions"]["deploy"]["reason"])
        effective = effective_authority_at(malformed, T0)
        self.assertEqual("authorized", effective["merge"])
        self.assertEqual("denied", effective["deploy"])

    def test_denied_action_remains_denied_while_current_action_survives(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(expires_at=LATER_EXPIRY),
            "deploy": {
                "state": "denied",
                "expires_at": None,
                "revocation_record": None,
            },
        }
        projection = reconcile(record, live_facts(record), T0)
        currentness = decision_currentness(projection, T0)
        self.assertEqual("DecisionCurrent", currentness["reason"])
        self.assertEqual("NotAuthorized", currentness["actions"]["deploy"]["reason"])
        effective = effective_authority_at(projection, T0)
        self.assertEqual("authorized", effective["merge"])
        self.assertEqual("denied", effective["deploy"])

    def test_future_or_malformed_projection_boundary_denies_all_actions(self) -> None:
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at=LATER_EXPIRY)
        projection = reconcile(record, live_facts(record), T0)

        future = decision_currentness(projection, "2026-07-31T02:00:00Z")
        self.assertEqual(
            ("False", "ProjectionObservedInFuture"),
            (future["status"], future["reason"]),
        )
        self.assertTrue(
            all(
                state == "denied"
                for state in effective_authority_at(
                    projection, "2026-07-31T02:00:00Z"
                ).values()
            )
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
