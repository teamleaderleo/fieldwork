# Approaches — Unit 27 cancellation-request receipt

## In simple words

The selected direction keeps remote run status authoritative and returns a separate immutable request receipt. The deeper review selects a small TypeScript repair: record which owner first aborts an agent-stream controller, keep cancellation rejection distinct from timeout, and let the existing iterator cleanup publish `detached`.

## Decision criteria

1. Local request state stays separate from remote terminal outcome.
2. Legacy TypeScript and Python `cancel()` returns remain compatible.
3. Concurrent callers within one run object share one operation and result.
4. One caller cancellation cannot cancel shared Python work.
5. TypeScript timeout and cancellation-request aborts remain distinguishable under either race order.
6. Existing catch-based CLI cancellation behavior remains viable.
7. Generated sync Python remains reproducible.
8. The change avoids a new polling lifecycle or cross-object registry.

## Selected approach

### Additive shared request receipt per run object

- Design: `requestCancel()` / `request_cancel()` returns an immutable request receipt with remote outcome `unknown`; existing `cancel()` delegates.
- Owning boundary: each in-memory `Run` object.
- Evidence: target execution `30642924979`; exact patch and receipt retained in this packet.
- Advantages:
  - preserves legacy returns;
  - prevents duplicate requests within one run object;
  - gives callers a bounded operation result;
  - keeps provider detail out of the public value;
  - works across TypeScript, async Python, and generated sync Python.
- Costs and risks:
  - failed receipts stay cached;
  - separate wrappers for one remote run do not coordinate;
  - `accepted` may be stronger wording than the endpoint contract supports;
  - TypeScript agent-stream abort composition needs repair.

### First-owner abort map for TypeScript agent streams

- Design: private module-local `WeakMap<AbortController, "cancel-request" | "timeout">`; one helper records the first owner and performs ordinary `abort()`.
- Cancellation-request branch: reject with cancellation-specific `BoxError`; leave status running until iterator `finally` stores partial output and marks `detached`.
- Timeout branch: preserve current behavior during this unit.
- Why selected:
  - first call wins without relabeling;
  - controller replacement starts cleanly;
  - no public API or persisted state;
  - no reliance on arbitrary abort-reason propagation through fetch/body streams;
  - existing open CLI work still receives iterator rejection.
- Required execution: pending-read cancellation, timeout control, both race orders, later controller, same-ID wrappers, full current gates.

## Viable alternatives

### Separate controllers plus a composed signal

- Design: one controller for timeout and one for caller-requested observer shutdown, combined with `AbortSignal.any()`.
- Improvement: ownership is visible in separate signal objects.
- Cost: wider runtime compatibility and signal-composition surface; still needs race precedence and cleanup policy.
- Reopening trigger: target prefers explicit signal families or adds external caller signals.

### Abort reason as the ownership carrier

- Design: call `AbortController.abort(reason)` and inspect `signal.reason`.
- Improvement: no side map.
- Cost: body-stream rejection behavior for arbitrary reasons needs cross-runtime proof; custom reasons can alter the caught error value.
- Reopening trigger: target runtime matrix proves one reason strategy consistently.

### Mutable abort-origin field on `Run`

- Design: store `cancel-request` or `timeout` beside `_abortController`.
- Improvement: easy direct access from cancellation methods.
- Cost: must reset correctly on controller replacement and cleanup; ownership belongs more naturally to the controller.
- Reopening trigger: target rejects module-level weak ownership.

### Nonterminal `cancelling` plus reconciliation

- Design: publish a new nonterminal status and poll or consume events until terminal state arrives.
- Why plausible: richer lifecycle visibility.
- What it improves: callers can distinguish request initiation from terminal reconciliation.
- What it widens: public state, network ownership, retries, backoff, stop conditions, event/poll ordering, compatibility.
- Reopening trigger: maintainers require built-in terminal reconciliation.

### Throw request failures from legacy `cancel()`

- Design: preserve status and reject `cancel()` on HTTP/transport failure.
- Why plausible: conventional error propagation and easy deliberate retry.
- Cost: breaks the existing non-throwing caller contract and open CLI cancellation work.
- Reopening trigger: project policy permits a breaking change.

### Box/run-ID keyed registry

- Design: store cancellation operations by box plus remote run ID.
- Improvement: coordination across wrapper objects.
- Cost: lifecycle, garbage collection, retries, stale IDs, cross-client semantics, and process boundaries.
- Reopening trigger: documented cross-wrapper coordination requirement.

## Executed losing approaches

### Directly change `cancel()` return type

- Record: model comparison PR #372 at `c178f689ab165d30c9ba863187b8424031a6c78f`.
- Result: runtime-compatible for ignored results, but static assignments and overrides can break.
- Why it lost: additive split preserves stronger source compatibility.

### `cancelling` plus mandatory reconciliation

- Record: PR #372.
- Result: coherent but wider than required to fix false terminal publication and duplicate requests.
- Why it lost: more network and lifecycle obligations.

### Initial patch artifact generation

- Record: PR #389 early heads and artifact `8797603134`.
- Result: retained patch omitted untracked new files.
- Why it lost: tested tree and durable patch differed.
- Retained lesson: exact path inventory and replayable artifact are required.

### Abort observer only when creating the shared request

- Record: pre-rerun PR #389 generation.
- Result: a later controller attached after receipt settlement stayed active.
- Why it lost: legacy `cancel()` behavior expected current observer shutdown.
- Retained lesson: every cancellation call may stop the current attached observer while the network request remains single-flight.

## Newly rejected easy answers

### Silently finish the iterator after cancellation request

This would allow the open CLI cancellation consumer to continue into its ordinary completion path. Keep rejection control flow and correct the error meaning instead.

### Treat every `AbortError` as timeout

Abort ownership is known before `abort()` and must be retained. Error name alone cannot publish timeout semantics.

### Overwrite the owner on repeated abort attempts

A timeout/cancel race must preserve the first effective abort. Once the controller is aborted, later calls cannot relabel the cause.

### Claim observer shutdown for every `StreamRun`

Current command and code streams do not attach the controller used by `Run.cancel()`. Keep the claim agent-stream-specific unless those paths are deliberately changed and tested.

### Keep assigning `status = "cancelled"`

Request completion or failure does not prove remote terminal outcome. Baseline request failure still assigns terminal `cancelled`.

### Swallow failure with no receipt

Callers still cannot distinguish request success/failure, and concurrent calls still duplicate the operation.

### Retry failed requests automatically

A request may have reached the provider despite local failure. Hidden replay can duplicate an operation.

### Claim at-most-once per remote run

Coordinator state lives on one object. Two wrappers with the same ID remain independent.

## Related context

See [`RELATED_CONTEXT.md`](./RELATED_CONTEXT.md) for exact revisions and evidence labels covering:

- current Box `detached` semantics and stream-type asymmetry;
- open Box CLI cancellation control flow;
- Upstash Redis expected local abort handling;
- Ky timeout ownership;
- Google long-running cancellation contracts;
- Temporal cancellation-stage vocabulary.

## Prior upstream approaches

| Link | Approach | Status | Relationship |
| --- | --- | --- | --- |
| [`upstash/box#68`](https://github.com/upstash/box/pull/68) | current `Run`/`StreamRun` model and cached status | merged | defines the ownership boundary |
| [`upstash/box#51`](https://github.com/upstash/box/pull/51) | integration cancellation coverage | merged | confirms cancellation is a supported path |
| [`upstash/box#82`](https://github.com/upstash/box/pull/82) | Ctrl+C calls `run.cancel()` and tracks caller intent separately | open | requires iterator rejection for its cancellation catch path |
| Fieldwork PR #332 | exact baseline characterization | closed historical | establishes current defect |
| Fieldwork PR #337 | bounded characterization claims | closed historical | separates observer control from full stream execution |
| Fieldwork PR #372 | repair-family comparison | closed historical | selects additive receipt |
| Fieldwork PR #389 | target materialization and execution | open research carrier | retained candidate and blocker |
| Fieldwork PR #391 | duplicate rerun carrier | closed superseded | no unique source |

## Deferred adjacent work

- terminal polling/reconciliation;
- explicit retry;
- cross-object registry;
- command/code stream controller introduction;
- timeout timer cleanup;
- hosted behavior and billing;
- CLI implementation beyond compatibility.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | #329 characterization | select truthful operation receipt | false terminal state and duplicate requests are separable from reconciliation | baseline disproved |
| 2026-07-31 | PR #372 `c178f689...` | select additive split API | strongest compatibility | target policy permits direct return-type change |
| 2026-07-31 | PR #389 `1e7909da...`, run `30642924979` | retain cross-SDK candidate | focused/full gates green and artifact complete | stronger complete-path review |
| 2026-07-31 | review `4830012327` at `ccaa28e...` | `REPAIR` | real stream iterator maps cancellation-request abort to terminal cancelled | stream-path repair and renewed execution |
| 2026-08-01 | upstream `9f7533c...` plus artifact verification | keep `REPAIR` | relevant source unchanged; blocker persists | repaired target-native stream control passes |
| 2026-08-01 | Box CLI PR #82 head `fce8c8c...`, Box stream paths, Upstash Redis, Ky, Google LRO, Temporal Go | select first-owner weak map plus rejection/`detached` | smallest repair that preserves target semantics and caller control flow | target execution or maintainer contract contradicts it |
