# Orchestration V2 OpenCode lifecycle evaluation 01

Date: 2026-07-30

## Exact provenance

This is a separate test-only evaluation branch. It is not a merge of every current V2 change.

- Upstream source branch: PR #4786, `fix/opencode-session-error-cleanup-drain`
- Exact upstream head: `a3b3a5d5af53850f74ef7d6741f6ef07b368cfdc`
- Shared V2 merge base: `a73a9ffc6de60a5b0ad93affda69c3850b6f47e6`
- Owned T3 branch: `fieldwork/orchestration-v2-opencode-lifecycle-evaluation`
- Owned test commit: `4f94ecabee645bafeffcc6d620905bd0b7ad6d13`
- Fieldwork workflow commit: `4522142a7898197d5afd52d67c0c00d1463ea82c`

The owned commit adds only `EffectOutbox.lifecycle-evaluation.test.ts` on top of the exact #4786 head. No production source was changed by Fieldwork.

## Why this is a second lane

The newer V2 core head `1c24c650c74c813d07209a25f1384890d22e315d` and #4786 diverge from the same earlier merge base. The core ownership files exercised here—EffectOutbox, EffectWorker, and ProviderSessionManager—did not appear in their commit comparison, but the branches are still not represented as one merged product tree.

Accordingly:

- the core lane evaluates A/D ownership on the newer V2 head;
- this lane evaluates the #4786 OpenCode stack with the same durable outbox controls;
- neither lane alone proves that a future merged V2 head is conflict-free or release-ready.

## Hosted gates

### Durable outbox controls

Runs:

`apps/server/src/orchestration-v2/EffectOutbox.lifecycle-evaluation.test.ts`

Requires same-thread interrupt serialization and conservative process-loss handling.

### OpenCode adapter lifecycle unit suite

Runs the complete:

`apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.test.ts`

This is branch-native coverage supplied by #4786 and is treated as executable evidence only when this hosted lane completes.

### Deterministic OpenCode replay fixtures

Runs only replay cases matching:

- `opencode_error_cleanup_*`;
- `opencode_error_unscoped`;
- `opencode_interrupt_error_cleanup*`;
- `turn_interrupt_mid_tool/opencode`.

These exercise ordered cleanup after scoped errors, immediate unscoped finalization, interrupt/error overlap, interrupted cleanup-tool classification, and terminalization of tools still active at the turn boundary.

### Server typecheck

Runs:

`vp run --filter t3 typecheck`

## Interpretation boundary

A green lane would support the following bounded conclusions:

- #4786's OpenCode adapter and replay fixtures execute on its exact head;
- the same durable outbox ownership controls execute on that branch;
- the branch typechecks under its pinned dependency graph.

It would not establish:

- that #4786 is merged upstream;
- that #4786 composes cleanly with `1c24c650...`;
- that legacy compatibility is unnecessary;
- that process-loss labeling must use `cancelled` rather than `interrupted`;
- permission to open a new T3 PR or contact upstream.

## Failure classification

A failure must be recorded as one of:

1. workflow or checkout failure;
2. new outbox-test harness/type incompatibility;
3. core ownership defect on the #4786 branch;
4. OpenCode adapter unit failure;
5. replay fixture failure;
6. server typecheck failure.

## Current status

Hosted execution is pending. No green claim is made.
