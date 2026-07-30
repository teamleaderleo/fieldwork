# Orchestration V2 lifecycle evaluation 01

Date: 2026-07-30

## Scope

This is test-only evaluation of the open Orchestration V2 stack on the owned T3 fork. It does not authorize production changes, a pull request, or upstream contact.

- Owned T3 branch: `fieldwork/orchestration-v2-lifecycle-evaluation`
- Pinned T3 commit: `0d61f31820f8254338571ac3049e7dc0ac621f7c`
- Upstream-derived base examined before the test commit: `1c24c650c74c813d07209a25f1384890d22e315d`
- Fieldwork workflow commit: `aeaa03826ec3d3821babe925c3b0be60f95b060d`

## New executable controls

File:

`apps/server/src/orchestration-v2/EffectOutbox.lifecycle-evaluation.test.ts`

### Same-thread effect ownership

The first control enqueues two `provider-turn.interrupt` effects for one app thread and one replay-safe cleanup effect for another thread. It requires:

1. the first interrupt is claimed;
2. the second interrupt for the same thread remains unclaimable while the first owns that thread;
3. unrelated work for another thread remains claimable;
4. after the first interrupt settles, the second same-thread interrupt becomes claimable.

This tests the durable outbox serialization boundary rather than adapter-local cancellation state.

### Process-loss policy

The second control claims a process-bound interrupt and a replay-safe cleanup effect, invokes `reconcileAfterProcessLoss`, and requires:

- the interrupt becomes `cancelled` and is not replayed;
- the cleanup effect returns to `pending`;
- the reconciliation receipt reports one cancellation and one requeue.

This validates the conservative distinction used by the V2 landing-target review. It does not prove that an abort accepted immediately before process death will retain the fine-grained final label `interrupted`; that ambiguity remains explicit in review issue #234.

## Existing controls included in the hosted lane

The workflow also runs:

- the full focused `EffectWorker.test.ts` file for cancellation registration, process-bound settlement, retry, and liveness behavior;
- selected `ProviderSessionManager.test.ts` cases covering busy-during-idle-probe, stale generation pinning, and active-turn release protection;
- server typecheck.

## Interpretation boundary

A green result would establish that V2 owns the relevant external-effect and release races at the durable orchestration boundary. It would not by itself establish:

- OpenCode adapter completeness;
- UI wording or compatibility behavior;
- crash-time `interrupted` versus `cancelled` labeling policy;
- readiness of upstream PR #2829 as a whole;
- permission to contact upstream or open another T3 pull request.

A failure must be classified as one of:

1. test-harness or type incompatibility;
2. workflow/checkout failure;
3. durable outbox ownership defect;
4. process-loss policy mismatch;
5. existing V2 regression outside the two new controls.

## Current status

Hosted execution is pending. No green claim is made.
