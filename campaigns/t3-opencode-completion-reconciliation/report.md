# Campaign: T3 and OpenCode completion reconciliation

State: `claimed`

## In simple words

The first apparent fix was too weak. Emitting a generic T3 `ready` event whenever a resumed OpenCode session is idle would unlock a stuck thread, but it could also clear a newer turn if an old session or replaced adapter delivers a delayed idle event.

The safer contract is turn-specific. T3 already persists the active T3 turn ID in its provider-session directory. OpenCode exposes both an authoritative session-status snapshot and caller-supplied user-message IDs. T3 can preserve a small mapping between its turn and the OpenCode user messages sent for that turn, then reconcile the exact old turn from OpenCode status and message history after restart. Existing T3 lifecycle guards already reject completion for a different newer turn.

OpenCode `idle` alone is not evidence that the old turn completed successfully. A local OpenCode process may have died with T3, an external server may have completed while T3 was disconnected, or the run may have failed or been aborted. Recovery therefore needs message evidence before choosing `completed` or `failed`; when no terminal evidence exists, `interrupted` is the conservative existing state.

Interruption is a related but distinct race. OpenCode's abort endpoint waits for runner cancellation and the provider idle transition before returning. T3 currently emits `turn.aborted`, while a concurrent OpenCode idle event can still be translated as ordinary `turn.completed: completed`. The exact turn needs one race-safe terminal settlement, classified as `interrupted`, without depending on later event delivery.

## Assignment

- Fieldwork issue: #71
- Programme: `agent-cli-execution` (#14)
- Worker: `chatgpt:gpt-5.6-thinking`
- Claim scope: `mechanism` and `interface`
- Retrieval date: `2026-07-30`
- Upstream contact authorized: `false`
- Owned Fieldwork path: `campaigns/t3-opencode-completion-reconciliation/`
- Owned target branch: `teamleaderleo/t3code:fieldwork/opencode-completion-reconciliation`

Pinned sources:

- T3 Code base: `teamleaderleo/t3code@85a89868703530e03c5e79797c7b952c684bd222`
- OpenCode reference: `teamleaderleo/opencode@7565e03536d19e850f9996c407f9bf5e932b5f7a`
- Prepared target head: `teamleaderleo/t3code@6910916928ae487b99c6204b01c84fee90207300`
- Fieldwork base: `teamleaderleo/fieldwork@ed91a4d1de9d62b3eab50d0b0188917b061746db`

Dependencies:

- scout PR #63;
- programme #14;
- completed Gemini lifecycle scout #22;
- cross-agent process comparison #24.

Stop condition:

Stop if target-native tests disprove the recovery gap, if exact outcome reconciliation cannot be bounded without a broad cross-provider redesign, or if the proposed affinity data cannot prevent an old provider result from settling a newer turn.

## Repository protocol followed

The T3 fork's `AGENTS.md`, `CONTRIBUTING.md`, vendored Effect guidance, and Effect function checklist were read before preparing tests.

Applied constraints:

- focused backend tests only;
- no repository-wide checks;
- no browser or live T3 state;
- no target pull request without a separate explicit request;
- no upstream issue or pull request;
- no production repair before the owning and safety boundaries are tested.

## Source-confirmed behavior

### T3 persists active-turn recovery metadata

`ProviderService.sendTurn` persists a provider binding containing the resume cursor and a runtime payload. That payload includes `activeTurnId`, model, working directory, and recent runtime-operation metadata.

`recoverSessionForThread` reads the persisted cursor, model selection, and working directory. It does not currently read the persisted active turn ID or pass it back to the adapter.

The inspected canonical-event path logs and publishes provider events, but does not update the provider-session directory. No other terminal-event directory update path was found in the inspected source. This means the recovery binding can retain stale active-turn metadata after normal completion unless another uninspected component updates it.

### OpenCode adapter resume

The OpenCode resume cursor stores a schema version and OpenCode session ID. `startSession` validates and re-adopts that upstream session. A newly built `OpenCodeSessionContext` initializes `activeTurnId` as undefined.

The cursor therefore restores conversation identity but not the T3 turn identity recorded by the provider-session directory.

### OpenCode idle event mapping

For OpenCode `session.status` events:

- `busy` updates the adapter-local session to running;
- `retry` emits a warning;
- `idle` clears local active state and emits canonical `turn.completed` only when the adapter still has an in-memory active turn ID.

A rebuilt adapter can therefore observe provider idle without emitting any canonical lifecycle transition for the old persisted T3 turn.

### A generic ready event is not turn-safe

T3's lifecycle projection deliberately treats `session.state.changed: ready` as session-wide truth and clears whichever active turn is currently projected.

Provider-instance identity does not fully solve stale-event ordering:

- settings replacement can reuse the same configured provider-instance ID;
- canonical events do not carry an adapter-generation ID;
- closing an adapter clears events still buffered in its queue, but an event already taken by ProviderService can finish publishing after replacement;
- replacing one OpenCode session context inside the same adapter object is not distinguishable by adapter object identity.

Therefore `idle without activeTurnId -> ready` is rejected as the preferred repair.

### Exact turn completion already has a stale-event guard

`ProviderRuntimeIngestion` rejects `turn.completed` when its turn ID conflicts with the currently active turn. The matching active turn is accepted and cleared.

This existing guard is the strongest reusable safety boundary. Recovery should produce an exact old-turn result rather than a generic session-wide ready event.

### OpenCode has an authoritative status snapshot

OpenCode exposes `GET /session/status` through `client.session.status()`. The result is a map from session ID to `busy`, `retry`, or `idle` status.

OpenCode's status service removes idle sessions from its internal active-status map and treats a missing entry as idle. A recovery path can therefore query current provider truth rather than wait indefinitely for a new SSE status event.

Status is activity truth, not outcome truth. It says whether execution is active; it does not say whether an idle historical turn completed, failed, was aborted, or lost continuity.

### OpenCode supports explicit provider message affinity

The async prompt API accepts an optional caller-supplied `messageID`. OpenCode uses that ID for the recorded user message. Assistant messages record the corresponding user message ID in `parentID` and expose completion time and structured error information.

T3 currently lets OpenCode generate the user message ID and does not retain it. Supplying and persisting that ID would let recovery connect a T3 turn to the exact OpenCode history produced for it.

Repeated steering reuses one T3 turn while sending more than one OpenCode prompt. The durable mapping therefore needs an ordered collection of provider user-message IDs, not a single field.

### OpenCode interruption reaches provider idle before the HTTP response

OpenCode's abort route calls `SessionPrompt.cancel`. The runner cancellation path interrupts active work, waits for cleanup, and runs its idle callback. That callback updates OpenCode session status to idle before the abort request returns.

T3's OpenCode adapter currently:

1. calls `session.abort`;
2. emits `turn.aborted`;
3. leaves adapter-local `activeTurnId` and session status unchanged;
4. relies on a later idle event for lifecycle settlement.

Because the idle event is published during OpenCode cancellation, the event pump can race with the adapter's interrupt method. The idle handler currently classifies any known active turn as `completed`, which can conflict with the user's interruption.

## Rejected shortcut

### Generic `idle -> ready`

Rejected as the preferred production change.

It is small, but its scope is too broad: a delayed old-session idle event can clear a newer active turn. Making it safe would require provider-session or adapter-generation affinity, at which point exact turn completion is both clearer and already protected by T3's lifecycle guard.

The original prepared generic-ready regression was replaced on the owned target branch.

## Preferred bounded contract

This is a design candidate, not an implemented patch.

### 1. Keep recovery affinity internal

Do not add recovery-only fields to the public WebSocket start-session schema.

Use an internal provider-adapter start input or equivalent server-owned context containing:

- persisted T3 `activeTurnId` when present;
- ordered OpenCode user-message IDs associated with that turn;
- the existing provider resume cursor and provider-instance identity.

### 2. Generate and retain OpenCode user-message IDs

For each OpenCode `promptAsync` call:

- generate a valid `msg...` OpenCode message ID;
- pass it in the prompt request;
- append it to the active T3 turn's provider-message list;
- return enough provider-specific recovery state for ProviderService to persist it with the turn binding.

For steering, append another message ID while retaining the same T3 turn ID.

### 3. Keep the directory lifecycle current

When canonical provider lifecycle events are accepted for routing:

- `turn.started` stores the exact active turn;
- exact `turn.completed`, terminal error, or session exit clears the recovery active-turn marker;
- stale completion for another turn must not clear the current binding;
- provider-specific message affinity is cleared or marked terminal with the same exact-turn guard.

This directory update should happen in a deterministic order relative to canonical event publication and should be covered by restart tests. A terminal event must not be published as durable truth while leaving recovery metadata indefinitely running.

### 4. Subscribe before snapshot reconciliation

On OpenCode recovery:

1. re-adopt the OpenCode session;
2. construct context with the persisted recovery turn, but do not expose it for new prompts yet;
3. start the provider event subscription;
4. query the authoritative session-status snapshot;
5. reconcile through one race-safe settlement helper;
6. only then return the recovered session to ProviderService.

Subscribing after the status query creates a lost-transition window. Querying after subscription closes that window, while a one-shot active-turn claim prevents the snapshot and an SSE event from settling the same turn twice.

### 5. Classify exact recovered outcome from history

If provider status is `busy` or `retry`:

- restore the persisted exact T3 turn ID into adapter-local state;
- keep the session active;
- let later events settle it normally.

If provider status is idle or absent:

- read OpenCode messages associated with the persisted provider user-message IDs;
- emit exact `turn.completed` for the persisted T3 turn;
- classify `completed` only when matching assistant history has terminal success evidence;
- classify `failed` when matching assistant history has a terminal non-abort error;
- classify `interrupted` when history reports abort or when no matching terminal result exists;
- include a clear reconciliation reason when the result is conservative rather than provider-confirmed.

If the upstream OpenCode session is confirmed missing while T3 retains an active turn, settle that exact turn as interrupted before creating a fresh session. A transient status/history/auth failure must fail recovery rather than silently mint a new empty session.

### 6. Settle interruption exactly once

Before calling OpenCode abort:

- validate that an explicitly requested turn ID matches the adapter's active turn;
- mark that exact turn as interruption-requested;
- call `session.abort`;
- after successful return, settle the exact turn as `interrupted` even if no SSE event was delivered;
- let the idle-event path use the same one-shot settlement helper and interruption marker;
- clear adapter-local active state and return the session to ready;
- if abort fails, preserve the active turn and clear only the interruption intent.

This separates cancellation acknowledgement from provider failure while preventing `completed` and `interrupted` from racing for the same turn.

## Prepared target specifications

Owned target head:

`6910916928ae487b99c6204b01c84fee90207300`

Prepared files:

- `apps/server/src/provider/Layers/OpenCodeAdapter.restart.test.ts`
- `apps/server/src/provider/Layers/OpenCodeAdapter.interrupt.test.ts`

Intended focused command:

```sh
vp test run \
  apps/server/src/provider/Layers/OpenCodeAdapter.restart.test.ts \
  apps/server/src/provider/Layers/OpenCodeAdapter.interrupt.test.ts
```

### Restart specification

The test provides:

- a valid resumed OpenCode session;
- persisted exact T3 turn identity;
- persisted provider user-message affinity;
- provider status idle;
- no matching terminal assistant history.

Required future result:

- exact `turn.completed` for the persisted turn;
- state `interrupted`, not generic ready and not unsupported success.

### Interruption specification

The test starts an exact turn, successfully calls OpenCode abort, and deliberately withholds a later provider status event.

Required future result:

- exact `turn.completed` for that turn;
- state `interrupted`;
- no dependence on incidental SSE delivery.

Evidence status:

- test files committed: **observed**;
- source mechanisms: **source-confirmed**;
- target execution: **not run**;
- expected current failures: **inferred from source**, not reported as executed failures;
- branch-push workflow runs: none returned.

## Required test matrix before production code

1. Idle recovery with no terminal history settles the exact old turn as interrupted.
2. Idle recovery with matching successful assistant history settles it as completed.
3. Idle recovery with matching failed assistant history settles it as failed.
4. Busy recovery restores the exact old turn and a later idle event settles it once.
5. Repeated steering retains all provider message IDs under one T3 turn and converges once.
6. Exact old-turn completion arriving after a new turn starts is rejected by the existing lifecycle guard.
7. Terminal canonical events clear provider-directory active-turn recovery metadata.
8. OpenCode abort settles interrupted when no idle event is delivered.
9. OpenCode abort racing with an idle event still emits one interrupted terminal result.
10. Interrupt with a mismatched stale turn ID does not abort the current turn.
11. Confirmed missing OpenCode session settles the old turn as interrupted before fresh creation.
12. Transient status or message-history failure does not silently create a fresh session.
13. Pending permission/question recovery remains explicitly separate; message affinity does not reconstruct request maps.
14. External OpenCode servers below the required status/message API capability fail with a clear compatibility error rather than unsafe fallback.

## Negative results and limits

- No target-native test was executed.
- No production file was changed.
- No target pull request was opened.
- The public steering reports are context, not proof that every symptom shares this root cause.
- OpenCode idle status does not prove successful completion.
- A generic idle-to-ready patch is now rejected as the preferred repair.
- Persisting only a T3 turn ID is insufficient to classify recovery outcome; provider message affinity is also needed.
- The exact location and shape of provider-specific recovery payload still need a target-native implementation spike.
- The inspected source did not reveal another terminal-event update path for ProviderSessionDirectory, but this remains a bounded negative finding rather than proof over every generated or dynamically loaded component.
- External OpenCode server version/capability negotiation needs explicit coverage.
- Pending approvals and questions remain an independent in-memory recovery problem.
- No browser, mobile, desktop, remote, or live-data trial was performed.
- No upstream contact occurred.

## Current recommendation

Do not apply a production patch yet.

Run the two prepared failing specifications in an owned worktree, then add the successful-history, failed-history, busy-recovery, stale-exact-completion, and directory-clearing cases. If those tests support the model, implement the smallest internal recovery payload and one-shot settlement helper. Keep generic ready fallback, public-schema expansion, and broad cross-provider lifecycle redesign out of the first change.

Keep the campaign claimed until target-native results establish both the owning boundary and the stale-event safety boundary.
