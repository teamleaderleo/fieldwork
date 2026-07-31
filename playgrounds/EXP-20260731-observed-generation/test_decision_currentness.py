#!/usr/bin/env python3
"""Reversing controls for exact-input and per-action authority currentness."""

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
    authorization_currentness,
    decision_currentness,
    effective_authority_at,
)
from reconcile import projection_is_current, reconcile  # noqa: E402


T0 = "2026-07-31T02:30:00Z"
EXPIRY = "2026-07-31T03:00:00Z"
T1 = "2026-07-31T03:00:00Z"
AFTER_EXPIRY = "2026-07-31T03:30:00Z"
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


def authority_condition(
    projection: dict[str, object], action: str
) -> dict[str, object]:
    return next(
        condition
        for condition in projection["conditions"]
        if condition["type"] == "AuthorityUsable"
        and condition["inputs"]["action"] == action
    )


def authority_reason(projection: dict[str, object], action: str) -> str:
    return str(authority_condition(projection, action)["reason"])


def authorized(
    *, expires_at: str | None, revocation_record: str | None = None
) -> dict[str, object]:
    return {
        "state": "authorized",
        "expires_at": expires_at,
        "revocation_record": revocation_record,
    }


def effective(
    projection: dict[str, object],
    current_at: str,
    record: dict[str, object],
    facts: dict[str, object],
) -> dict[str, str]:
    return effective_authority_at(projection, current_at, record, facts)


class DecisionCurrentnessTests(unittest.TestCase):
    def test_expired_action_invalidates_its_decision_without_input_movement(self) -> None:
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at=EXPIRY)
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)

        self.assertTrue(projection_is_current(projection, record, facts))
        self.assertEqual("AuthorityCurrent", authority_reason(projection, "merge"))
        at_observation = decision_currentness(projection, T0)
        self.assertEqual(
            ("True", "DecisionCurrent"),
            (at_observation["status"], at_observation["reason"]),
        )
        self.assertEqual(EXPIRY, at_observation["valid_until"])
        self.assertEqual("True", at_observation["actions"]["merge"]["status"])

        authorization = authorization_currentness(projection, T0, record, facts)
        self.assertEqual(
            ("True", "ExactInputsCurrent"),
            (
                authorization["inputs_current"]["status"],
                authorization["inputs_current"]["reason"],
            ),
        )
        self.assertEqual(
            ("True", "ExactProjectedAuthority"),
            (
                authorization["projection_authority_integrity"]["merge"]["status"],
                authorization["projection_authority_integrity"]["merge"]["reason"],
            ),
        )
        self.assertEqual("authorized", authorization["actions"]["merge"]["effective"])

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
        self.assertEqual("denied", effective(projection, T1, record, facts)["merge"])

        fresh = reconcile(record, facts, T1)
        self.assertEqual("AuthorityExpired", authority_reason(fresh, "merge"))
        self.assertEqual("denied", fresh["effective_authority"]["merge"])

    def test_one_expired_action_does_not_revoke_another_current_action(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(expires_at=LATER_EXPIRY),
            "deploy": authorized(expires_at=EXPIRY),
        }
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)
        self.assertEqual(EXPIRY, decision_currentness(projection, T0)["valid_until"])

        at_first_horizon = decision_currentness(projection, T1)
        self.assertEqual("DecisionRefreshRequired", at_first_horizon["reason"])
        self.assertEqual(LATER_EXPIRY, at_first_horizon["valid_until"])
        self.assertEqual("True", at_first_horizon["actions"]["merge"]["status"])
        self.assertEqual("False", at_first_horizon["actions"]["deploy"]["status"])

        current = effective(projection, T1, record, facts)
        self.assertEqual("authorized", current["merge"])
        self.assertEqual("denied", current["deploy"])

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
        self.assertEqual(
            "GenerationBoundCurrent", at_horizon["actions"]["merge"]["reason"]
        )
        self.assertEqual(
            "AuthorityHorizonElapsed", at_horizon["actions"]["deploy"]["reason"]
        )
        current = effective(projection, T1, record, facts)
        self.assertEqual("authorized", current["merge"])
        self.assertEqual("denied", current["deploy"])

    def test_malformed_one_action_time_denies_only_that_action(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(expires_at=LATER_EXPIRY),
            "deploy": authorized(expires_at=EXPIRY),
        }
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)
        malformed = deepcopy(projection)
        authority_condition(malformed, "deploy")["inputs"]["expires_at"] = "not-a-time"

        currentness = decision_currentness(malformed, T0)
        self.assertEqual("DecisionRefreshRequired", currentness["reason"])
        self.assertEqual("True", currentness["actions"]["merge"]["status"])
        self.assertEqual(
            "InvalidAuthorityTime", currentness["actions"]["deploy"]["reason"]
        )
        authorization = authorization_currentness(malformed, T0, record, facts)
        self.assertEqual(
            "True",
            authorization["projection_authority_integrity"]["merge"]["status"],
        )
        self.assertEqual(
            ("False", "ProjectionAuthorityMismatch"),
            (
                authorization["projection_authority_integrity"]["deploy"]["status"],
                authorization["projection_authority_integrity"]["deploy"]["reason"],
            ),
        )
        self.assertEqual("authorized", authorization["actions"]["merge"]["effective"])
        self.assertEqual("denied", authorization["actions"]["deploy"]["effective"])

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
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)
        currentness = decision_currentness(projection, T0)
        self.assertEqual("DecisionCurrent", currentness["reason"])
        self.assertEqual(
            "NotAuthorized", currentness["actions"]["deploy"]["reason"]
        )
        current = effective(projection, T0, record, facts)
        self.assertEqual("authorized", current["merge"])
        self.assertEqual("denied", current["deploy"])

    def test_future_or_malformed_projection_boundary_denies_all_actions(self) -> None:
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at=LATER_EXPIRY)
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)

        future_time = "2026-07-31T02:00:00Z"
        future = decision_currentness(projection, future_time)
        self.assertEqual(
            ("False", "ProjectionObservedInFuture"),
            (future["status"], future["reason"]),
        )
        self.assertTrue(
            all(
                state == "denied"
                for state in effective(projection, future_time, record, facts).values()
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
            all(
                state == "denied"
                for state in effective(malformed, T1, record, facts).values()
            )
        )

    def test_stale_inputs_deny_unexpired_authority_while_time_dimension_stays_current(self) -> None:
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at=LATER_EXPIRY)
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)

        moved_record = deepcopy(record)
        moved_record["finding_generation"] = "finding-cross-repository-v2"
        self.assertFalse(projection_is_current(projection, moved_record, facts))
        currentness = authorization_currentness(
            projection,
            T0,
            moved_record,
            facts,
        )
        self.assertEqual(
            ("False", "InputsMovedOrIncomplete"),
            (
                currentness["inputs_current"]["status"],
                currentness["inputs_current"]["reason"],
            ),
        )
        self.assertEqual(
            "True",
            currentness["decision_currentness"]["actions"]["merge"]["status"],
        )
        self.assertEqual("denied", currentness["actions"]["merge"]["effective"])
        self.assertEqual(
            "denied",
            effective(projection, T0, moved_record, facts)["merge"],
        )

        moved_facts = deepcopy(facts)
        moved_facts["generation"] = "live-facts-decision-horizon-v2"
        self.assertFalse(projection_is_current(projection, record, moved_facts))
        self.assertEqual(
            "denied",
            effective(projection, T0, record, moved_facts)["merge"],
        )

        missing_inputs = authorization_currentness(projection, T0, None, None)
        self.assertEqual(
            ("Unknown", "MissingCurrentInputs"),
            (
                missing_inputs["inputs_current"]["status"],
                missing_inputs["inputs_current"]["reason"],
            ),
        )
        self.assertEqual("denied", missing_inputs["actions"]["merge"]["effective"])

    def test_extended_projected_expiry_cannot_outlive_durable_grant(self) -> None:
        record = fixture()
        record["authority"]["merge"] = authorized(expires_at=EXPIRY)
        facts = live_facts(record)
        projection = reconcile(record, facts, T0)
        extended = deepcopy(projection)
        authority_condition(extended, "merge")["inputs"]["expires_at"] = LATER_EXPIRY

        self.assertTrue(projection_is_current(extended, record, facts))
        self.assertEqual(
            "True",
            decision_currentness(extended, AFTER_EXPIRY)["actions"]["merge"]["status"],
        )
        currentness = authorization_currentness(
            extended,
            AFTER_EXPIRY,
            record,
            facts,
        )
        self.assertEqual("True", currentness["inputs_current"]["status"])
        self.assertEqual(
            ("False", "ProjectionAuthorityMismatch"),
            (
                currentness["projection_authority_integrity"]["merge"]["status"],
                currentness["projection_authority_integrity"]["merge"]["reason"],
            ),
        )
        self.assertEqual("True", currentness["actions"]["merge"]["decision_current"])
        self.assertEqual("denied", currentness["actions"]["merge"]["effective"])

    def test_flipped_projected_revocation_cannot_restore_authority(self) -> None:
        record = fixture()
        record["authority"] = {
            "merge": authorized(
                expires_at=None,
                revocation_record="authority/merge@v1",
            ),
            "deploy": authorized(expires_at=LATER_EXPIRY),
        }
        facts = live_facts(record)
        facts["authority_revocations"] = {"authority/merge@v1": True}
        projection = reconcile(record, facts, T0)
        self.assertEqual("denied", projection["effective_authority"]["merge"])
        self.assertEqual("AuthorityRevoked", authority_reason(projection, "merge"))

        flipped = deepcopy(projection)
        flipped["effective_authority"]["merge"] = "authorized"
        merge_condition = authority_condition(flipped, "merge")
        merge_condition["status"] = "True"
        merge_condition["reason"] = "AuthorityCurrent"

        self.assertTrue(projection_is_current(flipped, record, facts))
        self.assertEqual(
            "True",
            decision_currentness(flipped, T0)["actions"]["merge"]["status"],
        )
        currentness = authorization_currentness(flipped, T0, record, facts)
        self.assertEqual(
            "False",
            currentness["projection_authority_integrity"]["merge"]["status"],
        )
        self.assertEqual("denied", currentness["actions"]["merge"]["effective"])
        self.assertEqual("authorized", currentness["actions"]["deploy"]["effective"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
