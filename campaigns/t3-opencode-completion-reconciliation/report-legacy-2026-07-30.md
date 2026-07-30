# Campaign: T3 and OpenCode completion reconciliation

State: `claimed`

## In simple words

The deeper review found that this is not one stale-state bug. It is a cluster of related ownership and ordering problems:

- T3 can remember an active turn after the rebuilt OpenCode adapter has forgotten its identity;
- OpenCode idle says that work is not active, but does not prove whether the old work completed, failed, was interrupted, or lost its process;
- abort response, idle delivery, and a later new turn can race each other;
- a delayed session-scoped idle event can accidentally close a newer turn because the provider event has no T3 turn identity;
- history can help classify recovery, but T3's existing unbounded history path has a documented large-thread hang;
- an inactivity reaper can observe no active turn and later stop the session after a new turn has already begun.

The original easy repair, `idle without activeTurnId -> session ready`, remains rejected. It can unlock the wrong turn.

The preferred direction is exact and conservative: preserve the old T3 turn ID plus ordered OpenCode user-message IDs, subscribe before taking a provider snapshot, inspect only bounded and time-limited matching history, and settle the exact turn once. Status alone must not decide success. A stale exact completion is already rejected by T3's lifecycle guard when a newer turn is active.

Four target test files now specify fourteen recovery, steering, interruption, delayed-event, and reaper cases. They are committed on the owned T3 fork but have not been run. No production repair is committed.

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
- Prepared target head: `teamleaderleo/t3code@e1108bcfaef5deacad9642ed6dcee05b889b368e`
- Fieldwork base: `teamleaderleo/fieldwork@ed91a4d1de9d62b3eab50d0b0188917b061746db`

Dependencies:

- scout PR #63;
- programme #14;
- completed Gemini lifecycle scout #22;
- cross-agent process comparison #24.

Stop condition:

Stop if target-native tests disprove the recovery gap, if exact outcome reconciliation cannot be bounded without a broad cross-provider redesign, or if the proposed affinity cannot prevent an old provider result from settling a newer turn.

## Repository protocol followed

The T3 fork's `AGENTS.md`, `CONTRIBUTING.md`, vendored Effect guidance, and Effect function checklist were read before preparing tests.

Applied constraints:

- focused backend tests only;
- no repository-wide checks;
- no browser or live T3 state;
- no target pull request without a separate explicit request;
- no upstream issue or pull request;
- no production repair before owning, ordering, and safety boundaries are tested.

## Evidence labels

- **Source-confirmed**: directly supported by pinned source.
- **Prepared**: committed as a target test specification, not executed.
- **Historical report**: public issue or merged-review evidence; useful precedent, not a fresh reproduction.
- **Inferred**: follows from source ordering but still needs target-native execution.
- **Planned**: retained as a required case, not yet implemented as a target test.

## Source-confirmed behavior

### T3 persists active-turn recovery metadata but does not restore it

`ProviderService.sendTurn` persists a provider binding containing the resume cursor and runtime payload. The payload includes `activeTurnId`, model, working directory, and recent runtime-operation metadata.

`recoverSessionForThread` reads the persisted cursor, model selection, and working directory. It does not currently read the persisted active turn ID or pass it back to the adapter.

The inspected canonical-event publication path logs and publishes provider events but does not update the provider-session directory. No other terminal-event directory update path was found in the inspected source. This is a bounded negative result, not proof over uninspected generated or dynamically loaded code.

### OpenCode resume restores conversation identity, not T3 turn identity

The OpenCode resume cursor stores a schema version and OpenCode session ID. `startSession` validates and re-adopts that session. A newly built `OpenCodeSessionContext` initializes `activeTurnId` as undefined.

The cursor therefore restores provider conversation history but not the T3 lifecycle identity that owns an outstanding turn.

### Idle is session-scoped activity state

For OpenCode `session.status` events:

- `busy` updates the adapter-local session to running;
- `retry` emits a warning;
- `idle` emits `turn.completed: completed` only when the adapter currently has an in-memory active turn ID.

The event contains the OpenCode session ID, not the owning T3 turn ID. The handler captures whichever T3 turn is active when the event is processed.

Consequences:

1. after adapter reconstruction, idle can emit no T3 lifecycle result because the old turn ID is absent;
2. after a new turn begins, a delayed or replayed old idle can be attributed to the new active turn;
3. idle alone cannot distinguish success, provider failure, user abort, lost local process, or missing terminal history.

### Generic ready is not turn-safe

T3 treats `session.state.changed: ready` as session-wide truth and clears the projected active turn.

Provider-instance identity is not sufficient generation identity:

- settings replacement can reuse the same configured instance ID;
- canonical events do not carry an adapter-generation ID;
- an event already taken by ProviderService can finish publishing after the old adapter scope closes;
- replacing one OpenCode session context inside the same adapter object is not distinguishable by adapter object identity.

Therefore generic `idle -> ready` remains rejected as the preferred repair.

### Exact turn completion already has a stale-event guard

`ProviderRuntimeIngestion` rejects a `turn.completed` event whose turn ID conflicts with the currently active turn. A matching completion is accepted and clears the turn.

This is the strongest reusable safety boundary. Recovery and interruption should produce exact turn results rather than session-wide ready transitions.

### Provider message identity can supply outcome affinity

OpenCode `promptAsync` accepts an optional caller-supplied `messageID`. OpenCode records that ID on the user message. Assistant messages retain the corresponding user message in `parentID` and expose terminal completion and structured error information.

T3 currently lets OpenCode generate the user message ID and does not retain it.

Repeated steering reuses one T3 turn while sending multiple OpenCode prompts. The recovery mapping therefore needs an ordered collection of provider user-message IDs, not one scalar field.

### History inspection must be bounded

The current `readThread` and `rollbackThread` implementations call `session.messages` without a limit, cursor, timeout, or abort budget.

A historical T3 report documents large sessions hanging indefinitely through this exact path. Recovery must not reuse it unchanged. Any recovery scan needs:

- a positive finite page limit;
- a bounded number of pages or exact-message lookup strategy;
- a documented time budget and cancellation path;
- an explicit result when matching history falls outside the budget;
- no fallback to an empty session on timeout, transport failure, or authorization failure.

### Abort and idle can race

OpenCode's abort route calls the cancellation runner and waits for cleanup. The runner's idle callback updates provider status before the abort request returns.

T3's current OpenCode adapter:

1. calls `session.abort`;
2. emits `turn.aborted` after the call returns;
3. leaves adapter-local `activeTurnId` and status unchanged;
4. lets a concurrent idle event classify the same active turn as ordinary completed.

An explicitly supplied interrupt turn ID is not validated against the adapter's active turn before the upstream abort call.

### Reaper check and stop are separate operations

`ProviderSessionReaper`:

1. reads the persisted binding and age;
2. reads the projected thread shell;
3. skips when that snapshot has an active turn;
4. otherwise calls `ProviderService.stopSession` with only the thread ID.

A turn can begin between steps 3 and 4. The safe invariant is not necessarily a second projection read; it is that a stale reaper decision cannot stop a newly active provider session. A version, last-seen token, generation, or atomic idle-stop operation could satisfy it.

### Runtime event queues are unbounded

The OpenCode adapter runtime queue and ProviderService canonical event PubSub are unbounded. Slow or absent consumers can therefore accumulate content and lifecycle events without an explicit pressure policy.

This campaign does not propose a queue redesign, but terminal-event priority, boundedness, and observability remain required regression cases.

## Historical precedent

### Steering can leave a thread permanently working

Public report:

`https://redirect.github.com/pingdotgg/t3code/issues/2173`

The reported sequence is OpenCode work, a mid-turn steering prompt, provider completion, permanent working state, disabled input, and persistence after restart.

A related repeated-comment report was closed as a duplicate:

`https://redirect.github.com/pingdotgg/t3code/issues/2886`

These reports support the symptom and ordering risk. They do not prove one shared root cause.

### Durable identity was previously missing

Public report:

`https://redirect.github.com/pingdotgg/t3code/issues/3604`

The OpenCode session ID lived only in memory, so reaping or restart could send a follow-up from one visible T3 thread to a fresh empty OpenCode session. T3's projection still showed old history, creating a confident but contextless agent.

Merged repair:

`https://redirect.github.com/pingdotgg/t3code/pull/3617`

The first implementation needed review corrections for two adjacent regressions:

- transient, authentication, and server failures during resume must not be treated as confirmed missing sessions and silently create an empty session;
- resumed sessions must reapply the current runtime-mode permissions rather than retain stale provider permissions.

This is strong precedent for structured classification and for testing every state carried across resume, not only conversation identity.

### Full-history hydration already hangs large sessions

Public report:

`https://redirect.github.com/pingdotgg/t3code/issues/3601`

The report identifies unpaginated `session.messages` with no timeout or abort signal as the cause of indefinitely pending large-thread hydration. Recovery history inspection must therefore be narrower than existing `readThread`.

### Connection and SSE failure remain recurring boundaries

Public report:

`https://redirect.github.com/pingdotgg/t3code/issues/2579`

The report describes child-process exits, fragile SSE, no automatic reconnect, and weak user-visible error reporting. Even when the exact reported details vary by revision, the recurring lesson is that event absence cannot be treated as provider success or permanent running.

## Test review of the owned branch

The original two tests were useful but incomplete.

Problems found in the first review:

- the restart test covered only idle with no terminal evidence;
- the interrupt test covered only successful abort without SSE;
- neither proved success or failure classification;
- neither tested transient recovery failures;
- neither required bounded history reads;
- neither tested stale interrupt identity;
- neither tested duplicate interruption;
- neither tested abort-idle one-shot settlement;
- neither tested delayed old idle against a newer turn;
- steering had no test requiring caller-generated provider message identity;
- no executable case crossed the ProviderSessionReaper and ProviderService boundary.

The OpenCode fakes were rebuilt so event delivery can be buffered, delayed, or injected during an in-flight abort. Each adapter test has an isolated layer and state.

The reaper test uses the real ProviderService and provider-session persistence with a fake adapter. It pauses the first projection read, starts and persists a new turn through ProviderService, then releases the stale inactive snapshot. The required behavior is only that the adapter session and running binding survive; the implementation may recheck, compare a version or last-seen token, or use an atomic stop-if-idle operation.

The reaper test harness was reviewed after creation. Its optional instance field now avoids explicit undefined under exact optional types, and its manually built layer scope is registered as an outer scoped finalizer so the expected current assertion failure cannot leak fibers or database resources.

## Prepared target specifications

Owned target head:

`e1108bcfaef5deacad9642ed6dcee05b889b368e`

Prepared files:

- `apps/server/src/provider/Layers/OpenCodeAdapter.restart.test.ts`
- `apps/server/src/provider/Layers/OpenCodeAdapter.interrupt.test.ts`
- `apps/server/src/provider/Layers/OpenCodeAdapter.steering-affinity.test.ts`
- `apps/server/src/provider/Layers/ProviderSessionReaper.race.test.ts`

Intended focused command:

```sh
vp test run \
  apps/server/src/provider/Layers/OpenCodeAdapter.restart.test.ts \
  apps/server/src/provider/Layers/OpenCodeAdapter.interrupt.test.ts \
  apps/server/src/provider/Layers/OpenCodeAdapter.steering-affinity.test.ts \
  apps/server/src/provider/Layers/ProviderSessionReaper.race.test.ts
```

### Restart and recovery cases

Six prepared test functions cover:

1. idle plus unrelated completed history settles the exact old turn as interrupted;
2. matching terminal assistant success settles the exact old turn as completed;
3. matching terminal assistant error settles the exact old turn as failed;
4. busy recovery restores the exact old turn and later idle settles it;
5. every idle-recovery history request carries a finite positive page limit;
6. status snapshot failure fails recovery and never creates an empty session;
7. bounded history failure fails recovery and never creates an empty session.

The bounded-history invariant is asserted inside the idle classification tests rather than as a separate test function. The no-evidence case deliberately includes unrelated successful history so a naive latest-message check cannot pass.

### Interruption and delayed-event cases

Six prepared test functions cover:

1. successful abort settles exact interrupted even when no later idle is delivered;
2. stale explicit turn ID is rejected before upstream abort;
3. idle published during abort and abort response share one terminal result;
4. concurrent duplicate interrupts coalesce to one abort and one terminal result;
5. abort failure preserves the active turn and emits no false terminal result;
6. delayed duplicate idle from the previous provider run cannot close a newer turn that has no matching provider evidence.

### Steering affinity case

One prepared test requires:

- initial prompt plus two steering prompts reuse one T3 turn;
- each OpenCode request carries a valid caller-generated `msg...` ID;
- all three provider message IDs are distinct.

The test intentionally does not choose whether the ordered IDs are stored in an internal runtime payload, a versioned provider cursor, or another server-private structure. That persistence shape remains an implementation decision.

### Reaper check-stop case

One integrated prepared test requires:

1. reaper begins from an inactive projected snapshot;
2. the snapshot is paused before it returns;
3. ProviderService starts a new turn and updates the durable binding;
4. the stale snapshot is released;
5. the adapter session remains alive and running;
6. the durable binding remains running with the new active turn.

Evidence status:

- four test files committed: **observed**;
- fourteen target test functions prepared: **observed**;
- source mechanisms: **source-confirmed**;
- target execution: **not run**;
- expected current failures: **inferred from source**, not reported as executed failures;
- branch-push workflow runs: none returned.

## Preferred bounded contract

This is a design candidate, not an implemented patch.

### 1. Keep recovery affinity internal

Do not add recovery-only fields to the public WebSocket start-session schema.

Use server-owned provider recovery state containing:

- persisted T3 active turn ID;
- ordered OpenCode user-message IDs for that turn;
- provider resume cursor;
- provider-instance identity;
- enough state to distinguish pending, interruption-requested, and terminal recovery.

### 2. Generate provider message identity before prompt dispatch

For every initial or steering `promptAsync` call:

- generate a valid OpenCode `msg...` ID;
- pass it to OpenCode;
- associate it with the owning T3 turn;
- define the crash boundary between provider acceptance and persistence;
- never use a failed unaccepted steer as terminal history evidence.

A pending or accepted marker, or idempotent message identity, may be needed to close the acceptance-persistence window.

### 3. Subscribe before snapshot reconciliation

On recovery:

1. re-adopt the OpenCode session;
2. construct a context with the persisted exact turn but do not admit a new prompt;
3. start the provider event subscription;
4. query the status snapshot;
5. reconcile snapshot and any queued event through one terminal-claim helper;
6. return the recovered session only after reconciliation reaches running, ready, interrupted, or explicit failure.

This closes the query-before-subscribe lost-transition window.

### 4. Treat status as liveness, not outcome

If status is busy or retry:

- restore the exact turn;
- retain running state;
- apply a user-visible liveness policy if progress and events remain absent beyond a budget.

If status is idle or absent:

- inspect only bounded matching history;
- completed requires matching terminal success;
- failed requires matching terminal non-abort error;
- abort evidence or absent matching terminal evidence yields interrupted;
- exhausted scan budget must be explicit and conservative.

### 5. Settle interruption through one atomic claim

Before awaiting OpenCode abort:

- validate explicit turn affinity;
- atomically mark the exact turn interruption-requested;
- coalesce duplicate callers;
- let idle, session error, and abort response compete through one settlement helper;
- successful abort settles interrupted even without SSE;
- abort failure restores the active state unless another terminal event already won.

### 6. Keep recovery directory state current

Accepted exact terminal lifecycle must clear or terminally mark:

- provider-directory `activeTurnId`;
- provider-message affinity;
- pending interruption state.

A stale exact completion must not clear a newer binding.

### 7. Guard reaping against stale snapshots

A reaper stop needs an expected-idle guard such as:

- binding version or last-seen compare-and-stop;
- active-turn generation token;
- adapter-side stop-if-idle operation;
- another atomic check at the owning session boundary.

A plain second read can narrow but not eliminate the race, but it is an acceptable first implementation if the integrated test and a subsequent adversarial interleaving remain green.

## Further required cases before production code

Planned but not yet prepared as executable target tests:

1. history request stalls and is cancelled within a documented recovery budget;
2. matching provider history sits just outside the newest page;
3. confirmed missing upstream session settles old turn before fresh creation;
4. local child-process restart has no terminal history;
5. prompt accepted but recovery affinity persistence crashes;
6. failed steer does not become false recovery evidence;
7. accepted terminal event clears provider-directory recovery state;
8. old adapter-generation event arrives after hot reload;
9. terminal assistant message and idle arrive in both orders;
10. session error followed by idle cannot regress failed to completed;
11. lost UI acknowledgement causes user resend without duplicate provider work;
12. pending approval or question survives, reconstructs, or explicitly expires;
13. provider remains busy without progress beyond a liveness budget;
14. runtime event consumers stall under high-volume content;
15. external OpenCode server lacks required bounded-history or status capability.

The complete case definitions are in `artifacts/test-matrix.json`.

## Rejected shortcuts

### Generic `idle -> ready`

Rejected because it clears session-wide state without exact turn affinity.

### Status-only terminal classification

Rejected because idle is not proof of success, failure, abort, or preserved execution continuity.

### Existing unbounded `readThread` for recovery

Rejected because it has a documented large-thread hang and no timeout or cancellation budget.

### Unconditional reaper stop after an inactive snapshot

Rejected because the snapshot can become stale before stop commits.

### Public start-session schema expansion

Rejected for the first change. Recovery state is server-internal.

### Broad cross-provider lifecycle redesign

Deferred. OpenCode-specific tests should first establish whether the shared lifecycle contract is actually insufficient.

## Negative results and limits

- No target-native test was executed.
- No production file was changed.
- No target pull request was opened.
- The public steering reports are context, not proof that every symptom shares one root cause.
- OpenCode idle status does not prove successful completion.
- A generic idle-to-ready patch is rejected as the preferred repair.
- Persisting only a T3 turn ID is insufficient to classify recovery outcome.
- Persisting provider message IDs alone does not solve request recovery, acceptance-persistence crashes, or reaper races.
- The exact internal recovery payload shape remains unchosen.
- The inspected source did not reveal another terminal directory-update path, but this remains a bounded negative finding.
- External server capability negotiation needs explicit coverage.
- No browser, desktop, remote, large-history, or live-provider trial was performed.
- No upstream contact occurred.

## Current recommendation

Do not apply production code yet.

Run and type-check the four focused target test files. Fix test-harness errors before interpreting lifecycle failures. Then implement only enough internal recovery, one-shot settlement, and stale-reaper guarding to make the exact-affinity cases pass.

Before calling the repair safe, also add executable history-timeout, prompt-acceptance/persistence, and terminal-directory-cleanup coverage. Those three remaining boundaries are where prior fixes and the current source are most likely to regress again.

Keep the campaign claimed until target-native results establish:

- exact old-turn recovery;
- bounded outcome classification;
- one-shot interruption;
- stale-event safety against a newer turn;
- reaper safety against a newly active session;
- durable recovery metadata cleanup.
