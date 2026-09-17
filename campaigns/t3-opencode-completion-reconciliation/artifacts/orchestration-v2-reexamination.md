# Orchestration V2 re-examination

Date: `2026-07-30`

State: `ready-for-review`

Campaign: `#71`

Review decision: `#234`

Prior legacy disposition: `#178`

Upstream contact authorized: `false`

## Purpose

Later T3 source movement changes the likely landing architecture for the lifecycle contracts developed by Campaign #71. This note compares the legacy adapter findings with the open Orchestration V2 stack. It does not treat any open upstream pull request as merged behavior and does not approve a production implementation.

The bounded decision is whether to:

1. transfer the accepted contracts to Orchestration V2 and hold legacy production work;
2. retain a narrowly justified legacy compatibility slice; or
3. repair missing V2 controls before either path proceeds.

## Pinned source inputs

- Orchestration V2: [`pingdotgg/t3code#2829`](https://redirect.github.com/pingdotgg/t3code/pull/2829) at `1c24c650c74c813d07209a25f1384890d22e315d`.
- Interrupted tool-item finalization: [`pingdotgg/t3code#4759`](https://redirect.github.com/pingdotgg/t3code/pull/4759) at `1e994fdcbe155999574a5f3c4ae964a2c8118e39`.
- OpenCode error cleanup drain: [`pingdotgg/t3code#4786`](https://redirect.github.com/pingdotgg/t3code/pull/4786) at `a3b3a5d5af53850f74ef7d6741f6ef07b368cfdc`.
- Owned legacy test carrier: `teamleaderleo/t3code#1` at `cae5d869f3ca441b4117197e34796a7d8b9466af`.

All three upstream pull requests are open. Their source is evidence about the proposed architecture, not a claim about released T3 behavior.

## Executive comparison

| Slice | Legacy campaign result | Source-confirmed V2 boundary | Current recommendation |
| --- | --- | --- | --- |
| A — interrupt ownership | Exact generation/session/turn ownership required; one canonical interrupted terminal result | Durable per-thread effect records exact provider session, thread, and turn; worker owns execution independently of the command caller | Re-examine at #234; likely move ownership to the V2 outbox/manager layer rather than add a second legacy adapter state machine |
| B — pending requests | Local expiry must not impersonate user decline or submission | Runtime requests have typed `pending`, `resolved`, `expired`, and `cancelled` states and exact provider-turn affinity | V2 materially supersedes the legacy compatibility shape; require execution controls before promotion |
| C — restart correlation | Status/history cannot safely reconstruct an exact old run | Process recovery fail-closes by cancelling nonterminal runs, attempts, nodes, provider turns, and process-bound effects | Decide whether explicit cancel-on-restart is the supported policy instead of resumed-run reconstruction |
| D — idle release | Projection check-then-stop is a TOCTOU race | Live session manager uses busy count, idle generation, runtime identity, and atomic entry removal before scope close | V2 supplies the missing ownership boundary; legacy reaper production work should remain held pending #234 |

## A — interruption ownership

### Durable effect identity

The V2 outbox represents an interrupt as a `provider-turn.interrupt` effect containing:

- `providerSessionId`;
- `providerThreadId`;
- `providerTurnId`;
- the owning app `threadId` and command receipt.

Claim selection excludes a pending effect whenever another effect for the same app thread is already `running`. Later same-thread work therefore cannot execute concurrently with the claimed interrupt.

The effect worker owns execution after command commit. Cancellation of the UI or request caller does not cancel the durable row. The worker claims, executes, retries or terminalizes, and settles the row under a lease.

### Exact target validation

`ProviderTurnControlServiceV2` reloads the current projection before invoking the adapter and validates:

- the recorded provider thread still exists;
- the recorded provider turn still exists;
- the provider turn still belongs to that thread;
- the provider thread still targets the captured provider session, or the exact replacement session captured by a restart effect.

A terminal provider turn or missing live session is treated as already stopped for interrupt/restart rather than issuing a stale provider call.

### Adapter-local limitation

`OpenCodeAdapterV2.interruptTurn` itself remains simple:

1. validate the active `providerTurnId`;
2. mark the active turn interrupted;
3. await `session.abort`.

It does not contain an adapter-local Deferred or duplicate-operation table. The decision for #234 is whether durable per-thread effect ownership is the correct single owner, making a second adapter-local coalescer redundant, or whether an adapter-local guard remains necessary for non-outbox callers.

### Process-loss ambiguity

`provider-turn.interrupt` is process-bound and intentionally not replayed after process loss. Startup recovery instead:

- cancels every nonterminal run;
- cancels pending/running attempts;
- cancels pending/running/waiting nodes and turn items;
- cancels pending/running provider turns;
- marks active provider threads idle;
- marks live provider sessions stopped;
- retires process-bound effects.

This removes stale working state. The unresolved semantic question is whether an abort accepted by OpenCode immediately before T3 process loss may be recorded as `cancelled` rather than `interrupted`. That uncertainty must be explicit; recovery must not invent a stronger outcome than the durable receipt proves.

## B — pending interactive requests

V2 runtime requests are durable records with:

- exact `providerTurnId` affinity;
- exact native request reference when available;
- typed kind, including `dynamic_tool_call` and `user_input`;
- typed status: `pending`, `resolved`, `expired`, or `cancelled`;
- response capability identifying the live provider session or a `not_resumable` reason.

OpenCode turn finalization closes matching pending requests as `cancelled`. Startup process recovery marks pending requests `expired`; shutdown uses `cancelled`. Session release also closes pending requests and terminalizes their request nodes/items without manufacturing a user decision.

This is a stronger contract than the legacy candidate's generic resolution metadata. The remaining work is executable ordering evidence:

- request cleanup precedes final visible run settlement where required;
- late responses cannot reach a detached/replaced session;
- provider error cleanup drains all ordered native cleanup events before turn finalization;
- multiple pending requests on one turn close exactly once.

## C — restart and delayed-event correlation

The legacy campaign attempted to distinguish completed, failed, and interrupted old work after adapter reconstruction. That required exact affinity unavailable from session status and raised bounded-history, acceptance/persistence, and delayed-event problems.

V2 chooses a different policy:

- while live, app run, run attempt, provider thread, provider turn, execution node, and runtime request identity are durable and explicit;
- after process loss, provider-bound nonterminal work is cancelled rather than reconstructed from weak status/history evidence;
- process-bound effects are retired instead of replayed into a possibly different provider generation.

This policy is conservative and removes false success. Review #234 must decide whether continuity across a T3 process restart is a product requirement strong enough to justify a supported resume protocol, or whether explicit cancelled recovery is the intended contract.

## D — idle session release

The V2 session manager owns live residency rather than consulting a stale projected shell and later stopping by thread ID.

Each live entry carries:

- `busyCount`;
- `idleGeneration`;
- runtime object identity;
- idle-release fiber;
- last-activity and background-work pin state.

Idle release captures the generation and runtime identity. After any asynchronous pending-work probe, it revalidates both. `releaseEntry` then atomically removes the exact live entry only when `busyCount === 0` and `idleGeneration` still matches. New activity or replacement invalidates the claim before external scope close.

This directly supplies the ownership boundary missing from the legacy reaper. It is not read-twice projection logic.

## Related open source movement

### Mid-flight tool terminalization

PR #4759 closes provider turn items that remain pending/running when a V2 turn terminalizes. This matters because a run can be correctly marked interrupted while a command/tool card remains visibly running.

### Ordered OpenCode cleanup drain

PR #4786 keeps an errored OpenCode turn available long enough to ingest later ordered cleanup events, then finalizes the turn after a subsequent stable event or stream end. It adds fixtures for:

- cleanup after session error;
- interrupt-error cleanup;
- aborted tool cleanup;
- multiple assistant messages;
- no pre-idle cleanup;
- unscoped error handling.

This supports B's ordering requirements but remains open source, not merged evidence.

## Exact controls required before transfer

The V2 transfer should not be accepted from source review alone. At minimum, execute deterministic controls for:

1. two distinct `run.interrupt` commands for one active run cause one provider abort and one durable terminal result;
2. cancellation of the command/request caller after commit does not abandon the interrupt effect;
3. a later prompt, detach, or restart effect cannot overtake the claimed interrupt for the same app thread;
4. an old interrupt cannot target a replacement provider session sharing the app thread;
5. process loss after provider abort acceptance but before outbox success produces no stale running run, request, node, provider turn, or effect;
6. the previous case records only the strongest justified outcome (`cancelled` unless an interrupted receipt was already durable);
7. all pending approval/question requests for the exact provider turn close once on interruption, error, release, and process recovery;
8. late runtime-response effects are cancelled or rejected after request expiry/session replacement;
9. idle release cannot remove a session after its busy count/generation/runtime identity changes during the pending-work probe;
10. cleanup-drain fixtures leave no running tool/request nodes after terminal run projection.

## Legacy execution status

The unpatched legacy controls execute and fail on the intended current boundaries.

The first A, B, and composed candidate runs did not test behavior because malformed stored unified-diff hunk metadata stopped `git apply`. The carriers were repaired at Fieldwork commits:

- A: `8e2cc0053aaf653b069a08349557c3268c795d08`;
- B: `8df686d9616281083d276af50f9ae72277a73070`;
- A+B overlay: `03ad4d94c8ed13d9b1d16673affc5863853452f2`.

Fieldwork integrity now validates candidate patch hunk metadata and runs negative controls. Repaired A and B workflows passed their input-filter stages and have real focused, existing-suite, ingestion, and typecheck jobs queued. No candidate result is currently green.

These runs remain useful legacy evidence. They must not automatically trigger a legacy production branch while #234 is open.

## Decision boundary

Pending review #234:

- retain the owned legacy branch as test/evidence only;
- do not create a new legacy production branch;
- do not assume open V2 PRs will merge unchanged;
- keep legacy restart/reaper production work held;
- require exact pinned V2 tests before transferring or promoting the contract;
- preserve the process-loss outcome uncertainty rather than relabel it as proven interruption.

No upstream interaction occurred.