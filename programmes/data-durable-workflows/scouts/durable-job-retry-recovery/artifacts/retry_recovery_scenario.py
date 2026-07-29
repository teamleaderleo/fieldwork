#!/usr/bin/env python3
"""Deterministic model for Fieldwork issue #29.

This is a contract model derived from pinned source. It does not execute the
owned applications. It asks one shared question: after a durable effect may
have committed but the response and process disappear, what evidence controls
retry, cancellation, and recovery?
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Literal

Disposition = Literal[
    "replay_recorded_result",
    "retry_same_request_same_key",
    "fresh_observation_required",
    "unknown_manual_decision",
    "out_of_scope",
]


@dataclass(frozen=True)
class SystemProfile:
    name: str
    logical_job_identity: bool
    attempt_identity: bool
    durable_checkpoint_before_effect: bool
    durable_terminal_receipt: bool
    exact_duplicate_replay: bool
    changed_input_conflict: bool
    cancellation_is_durable: bool
    fresh_observation_before_retry: bool
    effect_receipt_scope: Literal["local_ledger", "execution_journal", "none"]
    suitable_for_durable_job_comparison: bool


@dataclass(frozen=True)
class ScenarioResult:
    system: str
    disposition: Disposition
    duplicate_effect_permitted_by_model: bool
    cancellation_result: str
    recovery_action: str
    evidence_boundary: str


def evaluate(profile: SystemProfile, receipt_recorded: bool) -> ScenarioResult:
    if not profile.suitable_for_durable_job_comparison:
        return ScenarioResult(
            system=profile.name,
            disposition="out_of_scope",
            duplicate_effect_permitted_by_model=False,
            cancellation_result="request-local UI state only",
            recovery_action="stop durable-job comparison until a durable product requirement exists",
            evidence_boundary="request/stream lifecycle; no durable worker state",
        )

    if profile.effect_receipt_scope == "local_ledger":
        if receipt_recorded:
            return ScenarioResult(
                system=profile.name,
                disposition="replay_recorded_result",
                duplicate_effect_permitted_by_model=False,
                cancellation_result="terminal run cancellation is durable; committed local mutation remains recorded",
                recovery_action="read the operation receipt and item; do not repeat the local mutation",
                evidence_boundary="safe for Stensibly ledger mutations; generic external runner effects remain separate",
            )
        return ScenarioResult(
            system=profile.name,
            disposition="retry_same_request_same_key",
            duplicate_effect_permitted_by_model=False,
            cancellation_result="terminal cancellation prevents further run transitions",
            recovery_action="retry the exact same local request and key; external effects require a target adapter",
            evidence_boundary="operation receipt covers item/event/artifact mutations, not every external runner effect",
        )

    if (
        profile.effect_receipt_scope == "execution_journal"
        and profile.durable_checkpoint_before_effect
        and profile.fresh_observation_before_retry
    ):
        return ScenarioResult(
            system=profile.name,
            disposition="fresh_observation_required",
            duplicate_effect_permitted_by_model=False,
            cancellation_result="active cancellation requires exact draining evidence",
            recovery_action="re-observe ownership and preconditions, then resume, retry, compensate, or terminate",
            evidence_boundary="journal protocol is strong; live receipt mapping and personal-worker linkage remain incomplete",
        )

    return ScenarioResult(
        system=profile.name,
        disposition="unknown_manual_decision",
        duplicate_effect_permitted_by_model=True,
        cancellation_result="cancellation intent does not establish effect outcome",
        recovery_action="inspect the external system before any retry",
        evidence_boundary="no durable evidence resolves commit-before-disconnect",
    )


def main() -> None:
    profiles = [
        SystemProfile(
            name="stensibly",
            logical_job_identity=True,
            attempt_identity=True,
            durable_checkpoint_before_effect=False,
            durable_terminal_receipt=True,
            exact_duplicate_replay=True,
            changed_input_conflict=True,
            cancellation_is_durable=True,
            fresh_observation_before_retry=False,
            effect_receipt_scope="local_ledger",
            suitable_for_durable_job_comparison=True,
        ),
        SystemProfile(
            name="smolrunner",
            logical_job_identity=True,
            attempt_identity=True,
            durable_checkpoint_before_effect=True,
            durable_terminal_receipt=True,
            exact_duplicate_replay=True,
            changed_input_conflict=True,
            cancellation_is_durable=True,
            fresh_observation_before_retry=True,
            effect_receipt_scope="execution_journal",
            suitable_for_durable_job_comparison=True,
        ),
        SystemProfile(
            name="fin-agent",
            logical_job_identity=False,
            attempt_identity=False,
            durable_checkpoint_before_effect=False,
            durable_terminal_receipt=False,
            exact_duplicate_replay=False,
            changed_input_conflict=False,
            cancellation_is_durable=False,
            fresh_observation_before_retry=False,
            effect_receipt_scope="none",
            suitable_for_durable_job_comparison=False,
        ),
    ]

    results = [
        evaluate(profiles[0], receipt_recorded=True),
        evaluate(profiles[0], receipt_recorded=False),
        evaluate(profiles[1], receipt_recorded=False),
        evaluate(profiles[2], receipt_recorded=False),
    ]

    assert results[0].disposition == "replay_recorded_result"
    assert results[1].disposition == "retry_same_request_same_key"
    assert results[2].disposition == "fresh_observation_required"
    assert results[3].disposition == "out_of_scope"
    assert all(not result.duplicate_effect_permitted_by_model for result in results)

    output = {
        "scenario": {
            "id": "commit-response-lost-cancel-restart",
            "steps": [
                "accept one logical job under an exact request identity",
                "begin one attempt",
                "commit an effect",
                "lose the response and process before terminal acknowledgement",
                "record cancellation",
                "restart and decide whether retry is safe",
            ],
            "invariants": [
                "a retry preserves logical identity",
                "changed intent cannot reuse the same identity",
                "cancellation does not erase a committed effect",
                "unknown execution requires reconciliation before repetition",
                "terminal evidence is replayable",
            ],
        },
        "profiles": [asdict(profile) for profile in profiles],
        "results": [asdict(result) for result in results],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
