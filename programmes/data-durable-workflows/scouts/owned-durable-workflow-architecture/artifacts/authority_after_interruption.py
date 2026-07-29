#!/usr/bin/env python3
"""Evidence-led interruption model for Fieldwork issue #29.

The broad repository maps identify a useful comparison: after an interruption,
which system owns enough durable evidence to decide the next action?

This model derives its profiles from pinned source. It does not execute the
owned applications or claim deployed behaviour.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Literal

Disposition = Literal[
    "read_or_replay_local_result",
    "reconcile_external_owner_before_replacement",
    "fresh_observation_required",
    "no_durable_recovery_contract",
]

Recommendation = Literal["baseline", "campaign", "stop"]


@dataclass(frozen=True)
class BoundaryProfile:
    name: str
    system: str
    work_model: str
    durable_logical_identity: bool
    coordinator_state_owner: str
    effect_owner: str
    receipt_scope: Literal["local", "external", "none"]
    durable_pre_effect_checkpoint: bool
    durable_terminal_evidence: bool
    durable_cancellation_evidence: bool
    fresh_observation_rule: bool
    correlation_fields: tuple[str, ...]


@dataclass(frozen=True)
class BoundaryResult:
    name: str
    disposition: Disposition
    recommendation: Recommendation
    next_action: str
    decisive_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]


def evaluate(profile: BoundaryProfile) -> BoundaryResult:
    if not profile.durable_logical_identity:
        return BoundaryResult(
            name=profile.name,
            disposition="no_durable_recovery_contract",
            recommendation="stop",
            next_action=(
                "treat the request as ended; introduce a durable job only after "
                "an explicit asynchronous or write-capable product requirement"
            ),
            decisive_evidence=("request lifecycle",),
            missing_evidence=(
                "durable job identity",
                "attempt identity",
                "checkpoint",
                "cancellation record",
                "terminal read-back",
            ),
        )

    if (
        profile.coordinator_state_owner == profile.effect_owner
        and profile.receipt_scope == "local"
        and profile.durable_terminal_evidence
    ):
        return BoundaryResult(
            name=profile.name,
            disposition="read_or_replay_local_result",
            recommendation="baseline",
            next_action=(
                "read the retained outcome; when unknown, replay the exact same "
                "request identity under the same key"
            ),
            decisive_evidence=(
                "logical operation identity",
                "local operation receipt",
                "changed-request conflict",
            ),
            missing_evidence=(),
        )

    if (
        profile.coordinator_state_owner != profile.effect_owner
        and profile.receipt_scope != "external"
        and not profile.fresh_observation_rule
    ):
        return BoundaryResult(
            name=profile.name,
            disposition="reconcile_external_owner_before_replacement",
            recommendation="campaign",
            next_action=(
                "query the external effect owner through a stable operation handle "
                "before retrying or creating replacement work"
            ),
            decisive_evidence=(
                "stable local run identity",
                "external operation reference",
                "lease expiry or lost acknowledgement",
            ),
            missing_evidence=(
                "external terminal receipt",
                "read-after-interruption adapter",
                "replacement gate tied to reconciliation",
            ),
        )

    if (
        profile.coordinator_state_owner != profile.effect_owner
        and profile.durable_pre_effect_checkpoint
        and profile.fresh_observation_rule
    ):
        return BoundaryResult(
            name=profile.name,
            disposition="fresh_observation_required",
            recommendation="campaign",
            next_action=(
                "observe current ownership and preconditions, then resume, retry, "
                "compensate, or terminate under the same execution identity"
            ),
            decisive_evidence=(
                "pre-call executing checkpoint",
                "immutable action or execution identity",
                "fresh-observation rule",
            ),
            missing_evidence=(
                "live attempt-to-receipt mapping",
                "durable receipt read-back",
                "cross-system receipt publication",
            ),
        )

    raise AssertionError(f"unclassified profile: {profile.name}")


def main() -> None:
    profiles = (
        BoundaryProfile(
            name="stensibly-local-ledger",
            system="stensibly",
            work_model="server-owned ledger mutation",
            durable_logical_identity=True,
            coordinator_state_owner="stensibly-ledger",
            effect_owner="stensibly-ledger",
            receipt_scope="local",
            durable_pre_effect_checkpoint=False,
            durable_terminal_evidence=True,
            durable_cancellation_evidence=True,
            fresh_observation_rule=False,
            correlation_fields=("item_id", "run_id", "idempotency_key", "event_id"),
        ),
        BoundaryProfile(
            name="stensibly-external-runner",
            system="stensibly",
            work_model="ledger-owned run coordinating an external effect",
            durable_logical_identity=True,
            coordinator_state_owner="stensibly-ledger",
            effect_owner="external-runner-system",
            receipt_scope="local",
            durable_pre_effect_checkpoint=False,
            durable_terminal_evidence=False,
            durable_cancellation_evidence=True,
            fresh_observation_rule=False,
            correlation_fields=(
                "item_id",
                "run_id",
                "retry_attempt",
                "lease_generation",
                "external_run_id",
            ),
        ),
        BoundaryProfile(
            name="smolrunner-host-execution",
            system="smolrunner",
            work_model="local durable plan and executor journal",
            durable_logical_identity=True,
            coordinator_state_owner="smolrunner-store",
            effect_owner="observed-host",
            receipt_scope="none",
            durable_pre_effect_checkpoint=True,
            durable_terminal_evidence=False,
            durable_cancellation_evidence=True,
            fresh_observation_rule=True,
            correlation_fields=(
                "request_id",
                "reservation_id",
                "reservation_generation",
                "action_id",
                "execution_id",
                "journal_revision",
            ),
        ),
        BoundaryProfile(
            name="fin-agent-chat-request",
            system="fin-agent",
            work_model="request-scoped planner, read tool, and SSE response",
            durable_logical_identity=False,
            coordinator_state_owner="browser-and-request-memory",
            effect_owner="external-read-provider",
            receipt_scope="none",
            durable_pre_effect_checkpoint=False,
            durable_terminal_evidence=False,
            durable_cancellation_evidence=False,
            fresh_observation_rule=False,
            correlation_fields=("message_array", "step_count"),
        ),
    )

    results = tuple(evaluate(profile) for profile in profiles)

    expected = {
        "stensibly-local-ledger": ("read_or_replay_local_result", "baseline"),
        "stensibly-external-runner": (
            "reconcile_external_owner_before_replacement",
            "campaign",
        ),
        "smolrunner-host-execution": ("fresh_observation_required", "campaign"),
        "fin-agent-chat-request": ("no_durable_recovery_contract", "stop"),
    }
    for result in results:
        assert (result.disposition, result.recommendation) == expected[result.name]

    assert sum(result.recommendation == "campaign" for result in results) == 2
    assert sum(result.recommendation == "stop" for result in results) == 1
    assert sum(result.recommendation == "baseline" for result in results) == 1

    output = {
        "experiment": {
            "id": "authority-after-interruption",
            "question": (
                "After an interruption, which component owns enough durable "
                "evidence to choose read-back, reconciliation, fresh observation, "
                "or termination?"
            ),
            "selected_after_maps": True,
            "input_kind": "synthetic profiles derived from pinned source",
            "limitations": [
                "does not execute the owned applications",
                "does not prove deployed behaviour",
                "does not attribute a dependency or runtime defect",
            ],
        },
        "profiles": [asdict(profile) for profile in profiles],
        "results": [asdict(result) for result in results],
        "branch_decisions": {
            "campaigns": [
                "stensibly-external-runner-reconciliation",
                "smolrunner-attempt-journal-receipt-integration",
            ],
            "baseline": ["stensibly-local-ledger-receipts"],
            "stops": [
                "fin-agent-durable-job-recovery",
                "generic-cross-system-retry-framework",
                "dependency-or-runtime-attribution",
            ],
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
