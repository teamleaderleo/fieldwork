# Deep dive — Unit 27 cancellation-request receipt

## In simple words

The target currently combines three different facts: stopping one local reader, sending a remote cancellation request, and publishing terminal run state. Those facts can diverge. A request can fail, a reader can stop while the remote run continues, and a later server event can report natural completion.

The retained design separates request delivery from remote outcome through one immutable receipt per in-memory `Run`. Deeper source and compatibility review now identifies a narrow TypeScript repair: record the first owner of an agent-stream abort, preserve rejection control flow for current CLI consumers, classify caller-requested reader shutdown as `detached`, and leave timeout handling distinct.

## Governing invariant

> Local cancellation intent and local observer shutdown must never publish a remote terminal run outcome; only authoritative server/event data may do that.

## Current behavior

- entrypoint: TypeScript `Run.cancel()`; Python async/sync `Run.cancel()`
- state owner: each `Run` object owns cached status; TypeScript stream iterators update it through `Run._update`
- caller-visible result: legacy void/`None`; errors from the cancel endpoint are swallowed
- side effects: TypeScript agent runs may abort an attached controller, every caller sends a POST, and local status becomes `cancelled`; Python every caller sends a POST and local status becomes `cancelled`
- cleanup owner: agent stream iterator/fetch body reader in TypeScript; request coroutine/client in Python
- publication boundary: cached `Run.status`
- ordering: local observer abort can happen before remote cancellation request settlement; timeout and cancellation can race; server events can arrive before or after the request

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| TypeScript run state | [`client.ts@9f7533c`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/client.ts) `Run`, `Run._update` | cached status, run ID, attached controller, cancellation | [`run.test.ts`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/__tests__/run.test.ts) |
| TypeScript agent stream | same file, agent `_stream` iterator | timeout controller, body read, `AbortError` translation, terminal/detached updates | [`box-agent-run.test.ts`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/sdk/src/__tests__/box-agent-run.test.ts) plus required reversing controls |
| TypeScript command/code streams | same file, `_execStream` and `_execStreamCode` | stream parsing without an attached `Run` abort controller | explicit boundary controls required if widened |
| Python async source | [`_async/client.py@9f7533c`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/upstash_box/_async/client.py) `AsyncRun` | request and cached status | [`tests/_async/test_run.py`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_async/test_run.py) |
| Python sync generation | [`generate_sync.py@9f7533c`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/scripts/generate_sync.py) | maps async source into sync client | [`tests/_sync/test_sync_client.py`](https://github.com/upstash/box/blob/9f7533c645f6b519f612aa977f6f4acf86655db7/packages/python-sdk/tests/_sync/test_sync_client.py) |
| Retained transformation | [`apply_target_repair.py@ccaa28e`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_target_repair.py) | adds receipt API and coordinators | retained controls beside it |
| Follow-up transformation | [`apply_sync_test_repair.py@ccaa28e`](https://github.com/teamleaderleo/fieldwork/blob/ccaa28e40c5689aec7ad78c7f18c354e9966d7fd/programmes/high-leverage-open-source/scouts/upstash-box-cancel-receipts/target-materialization/apply_sync_test_repair.py) | aborts an attached TS observer on every call and updates sync test/typing | isolated late-controller test |
| Related context | [`RELATED_CONTEXT.md`](./RELATED_CONTEXT.md) | same-organization, HTTP, and long-running-operation comparisons | source-read only |

## Reproduction or characterization

### Setup

- exact upstream revision: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`
- environment: Ubuntu 24.04, Node 22, Python 3.12 in GitHub Actions
- fixture: repository-native mocked requests; no hosted Box call
- workflows: baseline `30622339900`; selected candidate `30642924979`

### Baseline result

Both SDK families suppress cancellation HTTP failure and publish `cancelled`. Concurrent callers issue independent POSTs. TypeScript agent cancellation aborts the attached controller before request settlement. A later internal authoritative update can replace the local status.

### Candidate result

The retained patch shares an immutable accepted/failed receipt per in-memory run object, preserves legacy return contracts, isolates Python waiters, avoids replay, and stops direct status assignment in the new cancellation methods. All named package gates passed at the executed base.

The real TypeScript agent-stream path remained outside the focused test. Existing source catches the request-triggered `AbortError`, assigns terminal `cancelled`, and reports `Stream timed out`. The broad status claim is false for that composed path until repaired.

## Failure model

1. `box.agent.stream()` creates a `StreamRun` and one `AbortController`.
2. The same controller backs optional timeout and local stream reading.
3. The retained `requestCancel()` aborts that controller before sharing or returning the cancellation POST result.
4. The iterator catches `AbortError` without an ownership record.
5. The catch assigns `status: "cancelled"` and throws `BoxError("Stream timed out")`.
6. Local cancellation intent becomes indistinguishable from timeout and remote terminal cancellation.

Steps 1–5 are source-confirmed. Hosted remote outcome after step 3 remains unknown.

## Deeper target findings

### `detached` already expresses the local boundary

Current agent-stream early termination stores partial output and changes a still-running run to `detached`; the source explicitly says server execution may continue. This is the closest target-native classification for cancellation-request observer shutdown.

### Iterator rejection is a compatibility requirement

Open upstream CLI PR #82 at `fce8c8cfc269bc09d07eb991ee39d0433029027e` records caller intent separately, calls `run.cancel()`, and expects the iterator to reject so its catch path can print `Cancelled.` Silently ending the iterator would let that flow publish ordinary command completion.

The repair should therefore keep rejection while correcting its meaning:

- status: `detached`;
- error: cancellation-request-specific, not `Stream timed out`;
- remote outcome: unknown until authoritative data arrives.

### Local observer shutdown is not uniform across stream types

Current agent stream attaches an abort controller to `Run`. Current command and code streams do not. The candidate may truthfully claim local observer shutdown only where a controller is attached. Widening command/code stream cancellation is adjacent work unless maintainers require one uniform `StreamRun` guarantee.

### Receipt naming remains unsettled

A successful HTTP response proves at least local request completion. It may not prove provider acceptance in the stronger operational sense. `requestState: "accepted"` remains a candidate name; `sent`, `delivered`, or `acknowledged` may be more precise depending on endpoint semantics.

## Selected implementation repair

Keep the receipt family and add first-owner abort classification for the TypeScript agent stream.

### Module-local ownership map

Use a private module-local map:

```ts
type RunAbortOwner = "cancel-request" | "timeout";
const runAbortOwners = new WeakMap<AbortController, RunAbortOwner>();

function abortRunObserver(controller: AbortController, owner: RunAbortOwner): void {
  if (controller.signal.aborted) return;
  runAbortOwners.set(controller, owner);
  controller.abort();
}
```

Route both timeout callbacks and `Run.requestCancel()` through this helper.

Properties:

- first abort wins and cannot be relabeled by a later race;
- a replacement controller receives a fresh ownership entry;
- completed controllers can be garbage-collected;
- runtime behavior stays on ordinary `AbortError` rather than relying on arbitrary abort-reason propagation;
- the cause remains private and adds no public API.

### Agent-stream catch

In the real iterator:

```ts
if (e instanceof Error && e.name === "AbortError") {
  if (runAbortOwners.get(abortController) === "cancel-request") {
    throw new BoxError("Run cancellation requested");
  }
  Run._update(run, { status: "cancelled", computeMs: Date.now() - start });
  throw new BoxError("Stream timed out");
}
```

The existing `finally` then stores partial output and publishes `detached` for the cancellation-request branch because the status remains `running`. Timeout behavior stays unchanged during this bounded repair.

Exact public error prose should be settled with target style; the required property is cancellation-specific rejection without terminal remote state.

### Receipt coordinator

- One per-`Run` Promise/Task/Future owns request execution and settlement.
- The receipt reports bounded request state and keeps remote outcome `unknown`.
- Legacy `cancel()` delegates and discards the receipt.
- A failed receipt remains cached; hidden replay stays absent.
- Claims explicitly say “per in-memory `Run` instance.”

## Compatibility analysis

- public API: additive receipt method and type; legacy `cancel()` signature retained
- source compatibility: callers ignoring `cancel()` result remain unchanged; new method is additive
- iterator behavior: cancellation still rejects, preserving catch-based consumers; error prose becomes truthful
- status behavior: caller-requested local reader shutdown becomes `detached` rather than terminal `cancelled`
- binary or wire compatibility: no wire change; same POST endpoint
- persistence or format compatibility: no persisted state
- platform behavior: historical execution on Node 22 and Python 3.12; current package declares Node `>=18`; renewed target matrix remains required
- performance and allocation: one Promise/Task/Future per run object plus one weak controller entry while live
- cancellation, retry, and recovery: automatic replay absent; failed receipt cached; explicit retry policy deferred
- generated output: Python sync remains generated and deterministic
- migration or rollback: delete additive types/coordinator and abort-owner helper; no data migration

## Adversarial and edge controls

- concurrent callers on one object share one request and object-identical receipt
- one async Python waiter cancellation leaves the shared request alive
- later caller receives settled receipt without replay
- request failure exposes fixed prose and no provider body
- later authoritative completion/cancellation wins
- request cancellation during a pending real agent-stream body read
- request cancellation after receipt settlement with a newly attached controller
- timeout abort remains separately classified
- cancel-first/timeout-second and timeout-first/cancel-second retain the first owner
- two wrappers with one box/run ID issue two requests, documenting per-object scope
- command/code stream tests document the current absence of local controller shutdown
- distinct run objects remain isolated

## Consequence and claim boundary

### Established

- Baseline false-terminal and duplicate-request behavior exists in local mocked target execution.
- The additive receipt API, immutable values, fixed diagnostics, legacy return compatibility, Python waiter isolation, deterministic generation, and per-object no-replay behavior passed the executed matrix.
- Current relevant source paths are unchanged from the executed base through `9f7533c...`.
- The candidate stores coordination on a `Run` object, so two wrappers with one remote ID coordinate independently.
- Box's agent stream already uses `detached` for local reader termination while remote work may continue.
- Current Box CLI cancellation work expects iterator rejection and tracks caller intent separately.

### Inferred

- A first-owner map is the smallest repair that handles timeout/cancel races without public API or runtime abort-reason dependence.
- A cancellation-specific `BoxError` plus `detached` status preserves the open CLI control flow more accurately than silent iterator completion.

### Unknown or unmeasured

- Hosted endpoint acceptance, acknowledgement wording, and idempotency
- Actual remote termination or natural completion after local abort
- Billing and production interruption behavior
- Whether command/code stream local abort should join this contribution
- Cross-process or multi-wrapper coordination requirements
- Maintainer naming and receipt-lifetime preference

## Review risks

- Some callers may currently catch the false `Stream timed out` text after calling `cancel()`; the message correction is observable.
- `detached` may surprise callers who previously read local `cancelled`; that is the intended truthfulness correction and needs clear release wording.
- Caching failed receipts removes implicit retry; document that policy and defer explicit retry.
- Open PR #82 is compatibility evidence but remains unmerged and may change.
- Completed timeout callbacks appear not to be cleared in the inspected source. This is retained as an adjacent source finding, not included without execution.

## Reversing evidence

Reopen the selected direction if:

- target maintainers define local `cancelled` as intentional client state independent of remote outcome;
- the cancellation endpoint supplies a durable request ID or confirmed terminal response that supports a richer receipt;
- a real stream-path test shows rejection plus `detached` breaks accepted target behavior;
- current main gains equivalent receipt or abort-ownership work;
- target runtime support makes the weak-map helper unsuitable.

## Adjacent work excluded

- provider-side idempotency keys
- cross-process or account-wide cancellation coordination
- automatic polling/reconciliation to terminal state
- explicit retry APIs after failed/unknown request delivery
- command/code stream controller introduction unless required for consistency
- timeout-timer cleanup as a separate lifecycle claim
- CLI Ctrl+C implementation beyond compatibility analysis
- hosted billing or cost measurements
