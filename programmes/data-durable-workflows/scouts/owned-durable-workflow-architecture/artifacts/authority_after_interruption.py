#!/usr/bin/env python3
"""Portfolio interruption-disposition model for Fieldwork issue #29.

The model compares what durable evidence survives an interruption across owned
systems. It does not execute the applications or claim deployed behaviour.
Profiles are derived from pinned source, tests, and repository documentation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Literal

Recommendation = Literal["baseline", "campaign", "retain"]
Disposition = Literal[
    "read_local_receipt",
    "reconcile_external_owner",
    "fresh_observation_then_receipt",
    "rebuild_projection_from_ledger",
    "full_sync_then_reconcile_outbox",
    "read_terminal_receipt_or_mark_interrupted",
    "inspect_run_directory_and_finalize",
    "discard_derived_cache_and_refetch",
    "serve_stale_and_backoff",
    "revalidate_ref_then_delete_or_undo",
    "advance_from_absolute_time",
    "replay_applied_actions",
    "rebuild_state_from_audit_chain",
]


@dataclass(frozen=True)
class BoundaryProfile:
    name: str
    system: str
    family: str
    logical_identity: str
    state_owner: str
    effect_owner: str
    surviving_evidence: tuple[str, ...]
    interruption_gap: str | None
    disposition: Disposition
    recommendation: Recommendation


@dataclass(frozen=True)
class BoundaryResult:
    name: str
    system: str
    disposition: Disposition
    recommendation: Recommendation
    decisive_evidence: tuple[str, ...]
    missing_or_deferred_evidence: tuple[str, ...]


def evaluate(profile: BoundaryProfile) -> BoundaryResult:
    if not profile.logical_identity.strip():
        raise AssertionError(f"{profile.name}: logical identity is required")
    if not profile.state_owner.strip() or not profile.effect_owner.strip():
        raise AssertionError(f"{profile.name}: state and effect owners are required")
    if not profile.surviving_evidence:
        raise AssertionError(f"{profile.name}: surviving evidence is required")

    missing: tuple[str, ...] = ()
    if profile.interruption_gap:
        missing = (profile.interruption_gap,)

    return BoundaryResult(
        name=profile.name,
        system=profile.system,
        disposition=profile.disposition,
        recommendation=profile.recommendation,
        decisive_evidence=profile.surviving_evidence,
        missing_or_deferred_evidence=missing,
    )


def profiles() -> tuple[BoundaryProfile, ...]:
    return (
        BoundaryProfile(
            name="stensibly-local-ledger",
            system="stensibly",
            family="coordination ledger",
            logical_identity="item, run, operation, and idempotency key",
            state_owner="stensibly ledger",
            effect_owner="stensibly ledger",
            surviving_evidence=("operation receipt", "run generation", "event history"),
            interruption_gap=None,
            disposition="read_local_receipt",
            recommendation="baseline",
        ),
        BoundaryProfile(
            name="stensibly-external-runner",
            system="stensibly",
            family="coordination ledger plus external executor",
            logical_identity="run ID plus external run ID",
            state_owner="stensibly ledger",
            effect_owner="external runner system",
            surviving_evidence=("run identity", "lease generation", "external operation reference"),
            interruption_gap="external terminal read-back and replacement gate",
            disposition="reconcile_external_owner",
            recommendation="campaign",
        ),
        BoundaryProfile(
            name="smolrunner-host-execution",
            system="smolrunner",
            family="local execution steward",
            logical_identity="request, reservation, action, and execution IDs",
            state_owner="smolrunner durable store",
            effect_owner="observed host or worker",
            surviving_evidence=("pre-call journal checkpoint", "attempt state", "fresh-observation rule"),
            interruption_gap="live attempt-to-receipt publication and read-back",
            disposition="fresh_observation_then_receipt",
            recommendation="campaign",
        ),
        BoundaryProfile(
            name="proofwake-observation-ledger",
            system="proofwake",
            family="append-only evidence index",
            logical_identity="provider delivery, receipt ID, or canonical observation digest",
            state_owner="proofwake observation ledger",
            effect_owner="source producer",
            surviving_evidence=("immutable observation", "request fingerprint", "rebuildable projection"),
            interruption_gap=None,
            disposition="rebuild_projection_from_ledger",
            recommendation="baseline",
        ),
        BoundaryProfile(
            name="days-upon-google-sync",
            system="days-upon",
            family="local-first provider synchronization",
            logical_identity="calendar ID, remote event ID, sync token, and local event ID",
            state_owner="browser workspace and sync storage",
            effect_owner="Google Calendar",
            surviving_evidence=("sync cursor", "remote baseline fingerprint", "local event state"),
            interruption_gap="durable idempotent mutation outbox and terminal provider disposition",
            disposition="full_sync_then_reconcile_outbox",
            recommendation="campaign",
        ),
        BoundaryProfile(
            name="renderprove-browser-review",
            system="renderprove",
            family="bounded verifier and receipt producer",
            logical_identity="manifest project plus stable route and viewport case IDs",
            state_owner="renderprove output directory",
            effect_owner="local runtime and browser",
            surviving_evidence=("screenshots", "case diagnostics", "runtime summary when completion reaches receipt write"),
            interruption_gap="pre-start run identity and atomic interrupted or terminal receipt publication",
            disposition="read_terminal_receipt_or_mark_interrupted",
            recommendation="campaign",
        ),
        BoundaryProfile(
            name="starsector-preflight-run",
            system="starsector-preflight",
            family="run wrapper, profiler, and cache pipeline",
            logical_identity="run directory, profile fingerprint, and benchmark cohort identity",
            state_owner="preflight run directory and cache stores",
            effect_owner="child launcher, game process, and local filesystem",
            surviving_evidence=("run directory", "profile census", "JFR recording", "final run status"),
            interruption_gap=None,
            disposition="inspect_run_directory_and_finalize",
            recommendation="retain",
        ),
        BoundaryProfile(
            name="elatura-derived-cache",
            system="elatura",
            family="observe-only sidecar and derived cache",
            logical_identity="origin, browser profile, adapter, namespace, resource, and content identity",
            state_owner="derived synthetic cache",
            effect_owner="authenticated application",
            surviving_evidence=("versioned cache envelope", "provenance", "freshness and corruption disposition"),
            interruption_gap="persistent private-content storage remains intentionally gated",
            disposition="discard_derived_cache_and_refetch",
            recommendation="retain",
        ),
        BoundaryProfile(
            name="scrapbook-github-activity-cache",
            system="scrapbook",
            family="stale-while-error cache coordinator",
            logical_identity="generated snapshot plus request ID",
            state_owner="Next.js data cache and instance coordinator",
            effect_owner="GitHub contribution source",
            surviving_evidence=("last successful snapshot", "failure count", "next retry time", "source diagnostics"),
            interruption_gap=None,
            disposition="serve_stale_and_backoff",
            recommendation="baseline",
        ),
        BoundaryProfile(
            name="gh-tidy-branches-delete",
            system="gh-tidy-branches",
            family="bounded destructive command with undo receipt",
            logical_identity="repository, branch, merged PR, and exact head SHA",
            state_owner="GitHub refs plus local undo receipt",
            effect_owner="GitHub ref service",
            surviving_evidence=("fresh ref SHA", "merged PR head SHA", "atomic local undo receipt"),
            interruption_gap="GitHub delete-ref lacks an expected-SHA precondition",
            disposition="revalidate_ref_then_delete_or_undo",
            recommendation="retain",
        ),
        BoundaryProfile(
            name="botany-sim-garden-calendar",
            system="botany-sim",
            family="deterministic offline simulation",
            logical_identity="calendar, generator version, mode, event, and garden year",
            state_owner="garden save",
            effect_owner="deterministic simulation",
            surviving_evidence=("last evaluated day", "pending events", "history", "absolute elapsed time"),
            interruption_gap="explicit migration across calendar versions or time modes",
            disposition="advance_from_absolute_time",
            recommendation="retain",
        ),
        BoundaryProfile(
            name="make-good-tv-agent-session",
            system="make-good-tv",
            family="deterministic simulation and controller audit",
            logical_identity="session ID, seed, seat, controller, and decision number",
            state_owner="game host and applied-action trace",
            effect_owner="game host",
            surviving_evidence=("untouched observation snapshot", "applied action trace", "terminal outcome"),
            interruption_gap="persistent worker or MCP remains gated on live evidence",
            disposition="replay_applied_actions",
            recommendation="retain",
        ),
        BoundaryProfile(
            name="quarry-paper-and-verification",
            system="quarry",
            family="research pipeline and resumable paper execution",
            logical_identity="paper session, audit sequence, execution attempt, state, verification request, and receipt IDs",
            state_owner="hash-chained audit ledger and immutable attempt artifacts",
            effect_owner="simulated execution engine and verification runner",
            surviving_evidence=("verified event chain", "rebuildable state", "content-addressed request", "terminal verification receipt"),
            interruption_gap=None,
            disposition="rebuild_state_from_audit_chain",
            recommendation="baseline",
        ),
    )


def main() -> None:
    boundary_profiles = profiles()
    results = tuple(evaluate(profile) for profile in boundary_profiles)

    names = [profile.name for profile in boundary_profiles]
    assert len(names) == len(set(names))
    assert {profile.system for profile in boundary_profiles} == {
        "stensibly",
        "smolrunner",
        "proofwake",
        "days-upon",
        "renderprove",
        "starsector-preflight",
        "elatura",
        "scrapbook",
        "gh-tidy-branches",
        "botany-sim",
        "make-good-tv",
        "quarry",
    }
    assert sum(result.recommendation == "campaign" for result in results) == 4
    assert sum(result.recommendation == "baseline" for result in results) == 4
    assert sum(result.recommendation == "retain" for result in results) == 5

    output = {
        "experiment": {
            "id": "portfolio-authority-after-interruption",
            "question": (
                "After an interruption, what identity and durable evidence survive, "
                "who still owns the effect, and what recovery action is authorized?"
            ),
            "selected_after_maps": True,
            "input_kind": "synthetic profiles derived from pinned owned-system source",
            "limitations": [
                "does not execute the owned applications",
                "does not prove deployed behaviour",
                "does not attribute a dependency or runtime defect without a direct reproduction",
                "does not authorize live trading, destructive operations, or private-data use",
            ],
        },
        "profiles": [asdict(profile) for profile in boundary_profiles],
        "results": [asdict(result) for result in results],
        "branch_decisions": {
            "campaigns": [
                "stensibly-external-runner-reconciliation",
                "smolrunner-attempt-journal-receipt-integration",
                "days-upon-durable-provider-mutation-outbox",
                "renderprove-interruption-safe-terminal-receipts",
            ],
            "baselines": [
                "stensibly-local-ledger-receipts",
                "proofwake-append-only-observation-recovery",
                "scrapbook-stale-while-error-coordinator",
                "quarry-audit-chain-and-attempt-receipts",
            ],
            "retained_patterns": [
                "starsector-preflight-run-directory-finalization",
                "elatura-authoritative-fallback-cache-contract",
                "gh-tidy-branches-live-revalidation-and-undo",
                "botany-sim-deterministic-offline-catch-up",
                "make-good-tv-deterministic-session-replay",
                "shared-correlation-envelope",
            ],
            "stops": [
                "one-universal-durable-workflow-library",
                "treating-caches-or-simulations-as-background-workers",
                "dependency-or-runtime-attribution-without-reproduction",
                "elatura-private-content-persistence-before-product-gate",
                "make-good-tv-persistent-worker-before-live-evidence",
                "quarry-live-trading-or-order-authority",
            ],
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
