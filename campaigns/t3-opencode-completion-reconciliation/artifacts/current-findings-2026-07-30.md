# T3/OpenCode lifecycle campaign — current findings

Date: 2026-07-30

## Executive conclusion

The campaign no longer supports treating the problem as one legacy OpenCode adapter bug.

The evidence separates into four lifecycle contracts:

- **A — interrupt ownership:** exact execution identity, caller-independent lifetime, one provider abort owner, and one terminal result;
- **B — pending interaction cleanup:** terminal work must cancel or expire pending permission/question requests without inventing user input, and late responses must fail before provider reply;
- **C — restart and delayed-event correlation:** session status/error events are not exact run identity;
- **D — external stop/release ordering:** a check followed by an external abort is unsafe unless one serialized or conditional authority owns the effect.

The current architectural direction is to evaluate A/D at the Orchestration V2 durable ownership layer and evaluate B/OpenCode cleanup on the exact OpenCode V2 branch. Legacy production work should remain held until review issue #234 selects the landing target.

No upstream contact is authorized or has occurred.

## Legacy exact-head evidence

### Target

- Owned T3 draft PR: `teamleaderleo/t3code#1`
- Test-only head: `cae5d869f3ca441b4117197e34796a7d8b9466af`
- Base: `85a89868703530e03c5e79797c7b952c684bd222`
- OpenCode source pin: `7565e03536d19e850f9996c407f9bf5e932b5f7a`

### Unpatched behavior

Deterministic hosted controls established the following legacy failures:

- resumed sessions do not restore or reconcile the exact active turn;
- successful abort does not canonically settle the local/persisted turn;
- stale explicit turn IDs can reach provider abort;
- duplicate interrupt callers can issue duplicate aborts;
- caller cancellation can abandon cancellation ownership;
- teardown and interrupt can overlap;
- delayed session-scoped idle/error events can settle a newer turn;
- OpenCode `skill` approvals are not represented visibly in the legacy path;
- terminal routes can leave stale permission/question handles;
- the reaper can observe idle, race with a new turn, and still stop the provider.

### Candidate carrier history

The first A/B/composed candidate matrix did not execute candidate tests. Stored unified-diff hunk metadata was malformed or stale, so jobs stopped during patch application. These were carrier failures, not product results.

Fieldwork integrity was extended to validate patch hunk structure and includes negative controls for malformed carriers.

### Candidate A

A later exact run produced real partial evidence:

- existing OpenCode adapter suite: **passed**;
- ProviderRuntimeIngestion compatibility: **passed**;
- focused interrupt candidate: **failed**;
- server typecheck: **failed**.

The candidate was revised for:

- Effect v4 APIs;
- exact session-generation/session/turn fencing;
- one adapter-owned cancellation operation;
- caller-independent provider abort lifetime;
- duplicate callers and `stopSession` joining one operation;
- prompt rejection while cancellation owns the turn;
- one canonical completed-interrupt receipt;
- preservation of the active turn after abort transport failure;
- exclusion of delayed session-event tests that require provider/run affinity.

The revised exact run remains queued. No green claim exists.

### Candidate B

The legacy B carrier was rebuilt from the exact target after a stale-context apply failure.

Its intended contract is:

- visible mapping for OpenCode `skill` approval;
- terminal cleanup of pending permission/question handles;
- machine-readable expiry/cancellation instead of fabricated decline/answers;
- stale response rejection before SDK reply.

The exact behavioral run remains queued. No green claim exists.

## Rejected message-ID experiment

A caller-generated OpenCode message ID made the focused steering test pass, but primary source review showed this was unsafe.

OpenCode's own IDs are monotonic and lexically ordered. Its session loop uses user/assistant ID ordering to determine whether work is complete. The public SDK accepts an ID string but does not expose the official generator.

An arbitrary `msg_t3_<uuid>` could sort after assistant IDs and recreate an infinite-loop condition. The experiment was deleted and recorded as rejected.

Provider-message affinity remains necessary, but it must use a supported provider-generated identity or equivalent durable correlation.

## Orchestration V2 core ownership evaluation

### Exact target

- Upstream-derived V2 head: `1c24c650c74c813d07209a25f1384890d22e315d`
- Owned branch: `fieldwork/orchestration-v2-lifecycle-evaluation`
- Owned test head: `0d61f31820f8254338571ac3049e7dc0ac621f7c`
- Hosted run: `30556506779`
- Durable detail: `artifacts/v2-lifecycle-evaluation-01.md`

### Added controls

A real in-memory SQLite outbox test requires:

1. two `provider-turn.interrupt` effects for the same app thread serialize;
2. unrelated work on another thread remains claimable;
3. the second same-thread interrupt becomes claimable only after the first settles;
4. process recovery cancels a running process-bound interrupt;
5. process recovery requeues a running replay-safe cleanup effect.

The hosted lane also includes:

- existing EffectWorker process-loss, cancellation-registration, retry, and liveness controls;
- ProviderSessionManager busy-during-idle-probe, stale-generation, and active-turn release controls;
- server typecheck.

### Interpretation

A green result would support the claim that A/D ownership belongs at the durable orchestration/session-manager layer rather than in a second legacy adapter-local ownership system.

It would not establish OpenCode cleanup behavior, B, or release readiness for Orchestration V2 as a whole.

The run is queued. No execution result exists yet.

## Orchestration V2 OpenCode evaluation

### Branch ancestry finding

The newer V2 core head does **not** include the current OpenCode cleanup branches.

Both OpenCode branches diverge from merge base:

`a73a9ffc6de60a5b0ad93affda69c3850b6f47e6`

Relevant upstream heads:

- PR #4759: `1e994fdcbe155999574a5f3c4ae964a2c8118e39` — close mid-flight tool items when a turn terminalizes;
- PR #4786: `a3b3a5d5af53850f74ef7d6741f6ef07b368cfdc` — includes #4759 and drains ordered OpenCode cleanup after scoped session errors.

Results from the newer V2 core branch and #4786 must remain branch-specific. They are not one tested product tree.

### Exact OpenCode evaluation target

- Owned branch: `fieldwork/orchestration-v2-opencode-lifecycle-evaluation`
- Exact source: upstream PR #4786 head `a3b3a5d5af53850f74ef7d6741f6ef07b368cfdc`
- Owned test head: `4f94ecabee645bafeffcc6d620905bd0b7ad6d13`
- Hosted run: `30557111582`
- Durable detail: `artifacts/v2-opencode-lifecycle-evaluation-01.md`

The owned commit adds only the same outbox test file; Fieldwork changed no production source.

### Hosted gates

- durable outbox ownership controls;
- full `OpenCodeAdapterV2.test.ts`;
- deterministic replay fixtures for:
  - scoped cleanup drain and fallback;
  - multiple cleanup messages;
  - no-pre-idle cleanup;
  - unscoped errors;
  - interrupt/error cleanup overlap;
  - aborted cleanup tools;
  - mid-tool interruption;
- server typecheck.

The run is queued. No execution result exists yet.

## B-specific V2 source finding

Source inspection found that OpenCode V2 already contains the essential adapter-side B behavior:

- pending permission/question events create typed runtime requests bound to the exact provider turn;
- turn finalization finds requests for that provider turn;
- it updates them to `cancelled`;
- it emits request, node, and turn-item terminal events;
- it removes both the app request-ID index and native request-ID index;
- a later direct adapter response fails because no pending request remains.

The orchestration `RuntimeRequestServiceV2` adds another guard:

- only `resolved` requests are dispatchable;
- `cancelled` or `expired` requests fail as not ready before looking up or calling the live provider session.

### Remaining B evidence gap

The #4786 unit file tests permission mapping and terminal tool behavior, but does not directly test terminal cancellation of a pending request or a late-response rejection.

A deterministic fixture/test was being designed to prove:

1. a question/permission remains pending when the turn terminalizes;
2. the projected request, node, and turn item become `cancelled`;
3. no `permission.reply` or `question.reply` frame is emitted;
4. a later response is rejected by `RuntimeRequestServiceV2` before adapter invocation.

That additional test was not committed or executed before this recap. It remains an explicit next control, not completed evidence.

## C — restart policy finding

Legacy resumed-run reconstruction remains blocked because OpenCode session status and session errors are session-scoped, not run-scoped.

A busy/idle latch cannot prove which turn a delayed event belongs to.

V2 currently takes a different policy:

- exact run/attempt/provider-turn identity while the process is live;
- fail-closed cancellation of nonterminal work during process recovery;
- process-bound interrupt effects are not replayed.

This avoids stale `working`, but an abort accepted immediately before process death may be classified as `cancelled` rather than preserving `interrupted`.

Review #234 must decide whether explicit cancel-on-restart supersedes the original resumed-run reconstruction goal.

## D — external effect ordering finding

The legacy reaper race cannot be repaired safely by a second read.

A projection revision check cannot revoke an external provider abort already sent. Safe ownership needs one of:

- per-thread operation serialization;
- a durable stop-effect outbox;
- an expected-revision lease/CAS that owns the external effect before it is sent.

V2's session manager uses runtime identity, generation, busy count, and serialized residency ownership before closing the external scope. This is the candidate replacement for legacy D and is covered by the queued core lane.

## Current decision gate

Review issue #234 should choose one bounded disposition:

1. `TRANSFER A/D OWNERSHIP TO V2; HOLD LEGACY`;
2. `TRANSFER B AFTER EXACT OPENCODE LANE`;
3. `KEEP BOUNDED LEGACY COMPATIBILITY SLICE` with a concrete migration or release-window dependency;
4. `REPAIR V2 FIRST` with exact missing controls.

A green V2 core lane is not proof that the OpenCode cleanup branch ran.

A green OpenCode lane is not proof that it composes cleanly with the newer V2 core head.

## Current run status

At the time of this recap:

- revised legacy A: queued after its input-filter job passed;
- rebuilt legacy B: queued after its input-filter job passed;
- V2 core run `30556506779`: queued at the `changes` job;
- V2 OpenCode run `30557111582`: queued at the `changes` job.

No pending run is represented as passed or failed.

## Repository coordination state

- Campaign issue #71 contains the two-layer legacy/V2 model.
- Draft Fieldwork PR #75 contains the exact two-lane evidence model and ancestry warning.
- Review issue #234 owns the landing-target decision.
- Review queue #213 was corrected to make #234 active.
- Delivery Desk #160 D2 contains exact heads, run IDs, and clearing conditions.
- Fieldwork PR #75 remains substantially behind `main` and must be restacked before promotion or merge.

## Boundaries

- No production V2 source was committed by Fieldwork.
- No V2 pull request was opened in the owned T3 fork.
- The existing legacy T3 PR remains draft and test/CI-oriented.
- No upstream issue, PR, discussion, review, comment, reaction, or message was created.
- Local clean-checkout execution was unavailable because the execution container could not resolve `github.com`; this is not test evidence.
