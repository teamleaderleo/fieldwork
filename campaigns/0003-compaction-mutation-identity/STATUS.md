# Compaction Mutation Identity

## In simple words

Campaign #83 is in staged owned-fork implementation. The canonical session receipt owner now begins from the exact selected runtime effect, records certain pre-dispatch failure, and records authoritative persistence for direct tool results. Recent MCP timeout evidence adds a blocking rule: a persisted timeout output does not prove that remote execution stopped. Typed execution certainty, durable reconstruction, safe receipt retirement, source-qualified nested Code Mode delivery, and compaction enforcement remain unwired.

- Campaign issue: #83
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- State: `implementing`
- Worker: GPT-5.6 Thinking
- Fieldwork dossier: merged PR #93
- Current owned Codex main: `teamleaderleo/codex@73ae22f90300d632833f9e4a531c4dd857c5db36`
- Public source pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Upstream contact: unauthorized

## Accepted owned-fork foundations

| Slice | Owned PR | Merge commit | Validation | Behavior change |
| --- | --- | --- | --- | --- |
| operation effect and receipt contract | `teamleaderleo/codex#3` | `f84e8d6fb48917965b7dacc1b28147663a28dd84` | full `codex-tools` suite passed | none |
| raw call/result identity validator | `teamleaderleo/codex#2` | `f68ad3830bf582ebd78f046f039be08510f48a9f` | focused `codex-core compaction_identity` suite passed | none; validator has no production caller |
| exposure wrapper effect delegation | `teamleaderleo/codex#12` | `e6b3017f4c725e0e6c48fc4e7fa703e365b2be67` | focused regression passed: 1 test, 3111 skipped | none |
| canonical live owner plus lifecycle begin/terminal wiring | `teamleaderleo/codex#19` | `f9da1593f2499f6acde081d405c1a5df4ee2ea00` | focused owner and lifecycle suites, formatting, and diff hygiene passed | records live receipt state; no compaction gate |
| authoritative direct result persistence | `teamleaderleo/codex#20` | `1d9cc9709bb4c71b7b388e2baf0ab131e5585a61` | 4 direct transition tests, 1 identity-classification test, 9 owner tests, patch hygiene, and final-head V8 passed | direct results become persisted or ambiguous from authoritative append outcome; no compaction gate |
| selected-runtime effect and certain pre-dispatch closure | `teamleaderleo/codex#21` | `73ae22f90300d632833f9e4a531c4dd857c5db36` | 3 selected-runtime/pre-dispatch tests, lifecycle contributor regression, 3 lifecycle mapping tests, formatting, and diff hygiene passed | exact selected effect begins the receipt; unsupported and incompatible calls close before handler execution; no compaction gate |

## Canonical live receipt contract

The accepted owner lives on `SessionState`, not `TurnState`.

- one session-scoped map is keyed by existing call identity;
- exact registry selection begins a receipt with the selected runtime's `operation_effect()`;
- unsupported registry calls begin conservatively as `PotentialMutation`;
- certain unsupported and incompatible-payload failures close as terminal `Failed` before handler execution;
- lifecycle finish records completed, failed or blocked, and aborted terminal observations for dispatched calls;
- direct result persistence is recorded only after `record_conversation_items` reports authoritative rollout append success;
- direct append failure records an ambiguous result;
- a duplicate persistence observation becomes ambiguous;
- a result without prior begin creates conservative potential-mutation evidence and remains unreconciled because terminal coverage is missing;
- late observations default conservatively to `PotentialMutation`;
- repeated identity escalates to potentially mutating and marks terminal and result state ambiguous;
- `has_unreconciled_potential_mutation()` is available for later preflight;
- retained receipts are capped at 1,024;
- overflow sets permanent `coverage_lost`, does not silently evict evidence, and must fail closed later.

The earlier turn-scoped owner from Codex PR #9 was removed. Keeping both maps would have created competing synchronization owners, and a turn-only map would disappear before later manual compaction.

## Direct result boundary now accepted

The direct in-flight drain is the authoritative direct-result owner.

1. Extract call identity from direct function, MCP, custom-tool, and client-executed tool-search results.
2. Convert the result into a response item and append it to in-memory history.
3. Attempt authoritative rollout persistence.
4. Record `Persisted` only when that append succeeds.
5. Record `Ambiguous` when the append fails.
6. Leave server-executed tool-search results outside the client receipt path.

Handler return and terminal lifecycle completion are not persistence evidence. The merged tests currently inject synthetic append outcomes into the receipt transition helper; a controlled real `live_thread.append_items()` success/failure test remains required.

## Selected-runtime boundary now accepted

Direct model call items are recorded before their tool future is created and polled. Receipt begin now occurs inside registry dispatch after exact runtime selection and before extension start callbacks or handler side effects.

- selected read-only runtimes retain `ReadOnly` rather than being overwritten by a generic conservative begin;
- unsupported calls retain conservative mutation evidence and receive a model-visible failure result;
- incompatible payloads retain the selected runtime effect and close as certain pre-handler failure;
- one atomic terminal guard prevents pre-dispatch closure and cancellation from recording two terminal observations;
- cancellation that wins before the parallel or serial execution gate is admitted is provably pre-handler and must retain that certainty;
- malformed calls rejected before registry dispatch remain a separate coverage case;
- the owner still uses raw call ID, so this slice does not claim source-qualified nested Code Mode identity.

## Execution-certainty correction from MCP timeout evidence

Fieldwork #134 demonstrates that the legacy Codex MCP outer timeout can end the local wait without cancelling the server request. The server can later complete its mutation even though Codex already produced a timeout/failure output.

Current MCP handling can return that error as a normal `McpToolOutput`. Generic registry lifecycle then observes `Completed { success: false }`, and direct persistence can record the output as `Persisted`. That pair must not be treated as proof that remote execution reached a terminal state.

Required typed distinction before compaction, retry, fallback, refresh, or reconnect consumes receipts:

- handler execution definitively did not start, including cancellation before execution-gate admission;
- remote execution definitively completed or failed;
- remote cancellation or request-stream closure definitively settled with adequate transport semantics;
- local wait ended while remote execution may still be running.

The durable vocabulary must preserve an equivalent of `not_started`, `settled_completed_or_failed`, `confirmed_cancelled`, and `may_still_run`, preferably as an execution-certainty dimension separate from the user-visible result. `MayStillRun` must remain unreconciled even when a timeout output was persisted. Cancellation notification delivery alone is not confirmed cancellation. Campaign #133 owns protocol-specific cancellation mechanics and should expose this terminal-authority signal without requiring #83 to parse error strings.

## Revised implementation sequence

1. Add typed execution certainty that preserves pre-handler non-execution and consumes Campaign #133's legacy, native-timeout, cancellation-delivery, late-result, and modern request-stream evidence.
2. Add a controlled production-path append test for direct result persistence, including durable success, append failure after in-memory insertion, and ephemeral-session semantics.
3. Emit versioned receipt lineage into rollout state, restore it on resume and fork, and carry the minimal required evidence in compacted checkpoints.
4. Define safe retirement for reconciled receipts after durable checkpoint ownership. Unresolved, ambiguous, or may-still-run mutations must never be silently evicted.
5. Add separate source-qualified nested Code Mode result delivery; direct and nested identities must not update each other.
6. Only then enable raw-history plus receipt preflight before request construction and before replacement installation in local, remote v1, and remote v2 compaction.
7. Apply the resulting certainty and authority lineage to automatic retry and fallback.

This order is consistent with adjacent campaigns:

- #84 requires captured-call authority across MCP catalogue generations and should reuse #83 receipts rather than create another lifecycle owner;
- #85 preserves the distinction between Direct and Code Mode execution surfaces;
- #86 depends on #83 mutation certainty before allowing or rejecting fallback;
- #133 must settle or explicitly preserve uncertainty for timed-out remote operations.

## Durable checkpoint boundary

The session owner remains process-local. Resume and fork reconstruction requires:

- versioned receipt update rollout items before compaction;
- restoration into the live owner on resume or fork;
- the minimal unresolved or reconciled receipt set carried in each compacted checkpoint;
- a retirement rule proving that removed live entries remain recoverable from durable evidence;
- preservation of uncertain remote-execution state until cancellation or late completion is reconciled against the same operation identity.

Do not put receipts only in replacement history and do not leave them only in memory.

## Enforcement map

After typed execution certainty, authoritative nested result delivery, durable restoration, and safe retirement exist, one shared preflight must run twice in every compaction implementation:

1. **Before request construction**
   - local compaction: before cloned history is converted with `for_prompt`;
   - remote v1: before compact request history is built;
   - remote v2: before prompt or retained-message input is built.
2. **Before replacement installation**
   - immediately before `Session::replace_compacted_history` in local, remote v1, and remote v2.

The preflight must reject when:

- raw history has any call/result identity defect;
- the live owner reports an unreconciled potentially mutating operation;
- live or durable receipt coverage is incomplete;
- remote execution may still be running;
- a duplicate, conflicting, late, or reordered observation remains unreconciled.

The second check matters because tool futures, remote terminal authority, or persistence state can change while a compaction request is in flight.

## Remaining work

1. Add typed execution certainty for not-started, settled, confirmed-cancelled, and may-still-run outcomes, especially across MCP timeout and cancellation.
2. Add real append-boundary fault injection for direct result persistence.
3. Add versioned rollout receipt updates, checkpoint carry-forward, and resume/fork restoration.
4. Add safe retirement without silent loss of ambiguous mutation evidence.
5. Add source-qualified nested Code Mode result delivery.
6. Invoke the raw-history identity validator and receipt preflight at all six request and installation boundaries.
7. Add late-result reconciliation plus duplicate and causal-order rejection.
8. Prove complete identities continue normally and every ambiguous or may-still-run mutation fails closed without automatic replay.

## Stop rule

Do not claim a repair until compiled owned-fork tests cover complete, missing, duplicate, reordered, orphan, late, persistence-failure, cancellation-before-execution, local-timeout, cancellation-unconfirmed, coverage-loss, retirement, resume, and fork cases across local, remote v1, remote v2, continuation, retry, and fallback. No upstream interaction is authorized.
