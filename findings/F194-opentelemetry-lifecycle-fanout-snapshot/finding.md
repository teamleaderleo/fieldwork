# F194: Attempt every lifecycle child from a stable opening snapshot

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#194`  
Canonical finding path: `findings/F194-opentelemetry-lifecycle-fanout-snapshot/finding.md`  
Canonical implementation: `teamleaderleo/opentelemetry-js#6`  
Exact implementation head: `e19247b801817abaf8c9fff5a39d00783d8c38e6`  
Exact base revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`  
Strongest evidence class: `target-executed` for synchronous-throw fanout; snapshot mutation controls are exact-head queued  
Reviewed input generation: `teamleaderleo/opentelemetry-js#6 at e19247b801817abaf8c9fff5a39d00783d8c38e6`  
Current review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

Trace, log, and metric providers each own a list of child processors or readers. When shutdown or force flush begins, every child that belonged to the list at that moment should receive the call.

Catching a synchronous exception is necessary but insufficient. JavaScript array iteration observes the live array. A first child can remove a later child before the iterator reaches it, silently shrinking the current lifecycle operation.

The selected repair copies the child list before invoking any child. The current operation uses that opening snapshot. Mutations remain visible to future operations.

## Why we care

A skipped processor or reader can leave telemetry buffered or resources open. The caller requested lifecycle work for the opening set. Child-controlled mutation should not silently erase that obligation.

## What happens if we leave it alone

A first child can synchronously mutate the shared array. `Array.map()` checks each index while iterating and skips a deleted property. A later child can therefore receive no shutdown or force-flush call even though it was registered when the operation began.

The exact frequency is unknown. The mechanism is available through retained constructor arrays, the public logs processor array, and internal metric collector storage.

## Governing project goals and invariant

Governing invariant: a lifecycle aggregate must attempt every child that belonged to its opening membership set, while preserving each package's existing outward error policy and future membership semantics.

Required properties:

1. one synchronous child throw cannot stop later child invocation;
2. one synchronous child mutation cannot remove a later opening child from the current operation;
3. additions after operation start do not join the current operation;
4. mutation remains effective for future operations;
5. trace, logs, and metrics keep their existing rejection/reporting policy;
6. child calls remain eagerly concurrent rather than becoming sequential;
7. the repair does not freeze public arrays or widen membership authority.

## Current finding

“Attempt every child” requires two independent mechanisms:

1. `callLifecycle()` converts synchronous throws into rejected promises so eager invocation continues;
2. each lifecycle entrypoint snapshots its child array before the first child call.

The selected implementation applies `.slice()` to trace processors, log processors, and metric collectors. Trace shutdown still rejects; trace force flush still reports through the global error handler and resolves; logs and metrics still reject.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Synchronous throws can stop eager promise-list construction | target-executed | predecessor head `80e3b74b...` and exact matrix | Does not cover mutation |
| Live `map()` can skip a removed later child | source-read and model-executed | source review plus mutation controls at `e19247b...` | Current exact-head workflow execution is queued |
| Opening snapshots preserve current-operation membership | source-reviewed | trace/logs/metrics source at `e19247b...` | Does not impose membership on future operations |
| Existing outward error policy can remain unchanged | target-executed predecessor plus source-reviewed repair | PR #6 complete diff | Does not aggregate every async failure |
| Mutation remains visible after the operation | source-reviewed and target-test-prepared | six mutation controls at `e19247b...` | Exact workflow receipts pending |

## System and ownership map

- Trace owner: `MultiSpanProcessor` and its `SpanProcessor[]`.
- Logs owner: `MultiLogRecordProcessor.processors`, a public mutable array.
- Metrics owner: `MeterProviderSharedState.metricCollectors`.
- Lifecycle entrypoints: `shutdown()` and `forceFlush()`.
- Invocation timing: child methods are invoked synchronously while promise inputs are built.
- Error conversion: `callLifecycle()` converts a synchronous throw into `Promise.reject(error)`.
- Membership rule: capture `.slice()` before any child invocation.
- Future membership rule: mutations affect later operations and remain observable after the current operation.

## Historical precedent

### ECMAScript array iterative-method semantics

- Source: ECMAScript `Array.prototype.map` algorithm.
- Principle supported: each indexed property is checked as iteration proceeds; deleted entries may be skipped.
- Important difference: OpenTelemetry must define lifecycle membership rather than merely inherit generic array behavior.

### Existing Promise.all fanout architecture

- Source: trace, logs, and metrics lifecycle implementations at `7b06368b...`.
- Principle supported: child calls are eagerly constructed and asynchronous completion is concurrent.
- Important difference: preserving concurrency does not require preserving live membership mutation during construction.

## Decision criteria

1. every opening child is invoked once;
2. synchronous errors do not stop later invocation;
3. current-operation membership is deterministic;
4. future membership changes remain possible;
5. outward failure behavior stays package-compatible;
6. concurrent fanout and latency shape remain unchanged;
7. implementation is local, readable, and easy to test;
8. no freeze, deduplication, or new mutation authority is introduced.

## Alternatives and comparative results

| Option | Implementation or analysis | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- | --- |
| A — live array plus direct calls | baseline | first child throws | later children skipped | rejected |
| B — live array plus `callLifecycle()` | predecessor `80e3b74b...` | first child removes second | deleted index skipped | rejected |
| C — opening snapshot plus `callLifecycle()` | head `e19247b...` | remove-second controls for shutdown/forceFlush in three packages | opening child still called; mutation persists afterward | selected |
| D — freeze arrays or copy permanently | paper design | future membership compatibility | changes observable mutation and ownership | rejected |
| E — sequentially await each child | paper design | concurrency and latency comparison | changes established eager fanout | rejected |
| F — settle-all or aggregate every async failure | paper design | outward error contract comparison | materially different error policy | deferred to separate finding |

## Independent criticism

- Cross-review found that the predecessor's “attempt all” claim was too broad because it used live arrays. Six mutation controls were added before promotion.
- The repair was challenged for potentially suppressing legitimate mutation. Tests assert that the original array remains changed after the operation, proving current-operation snapshotting rather than permanent freezing.
- A reversing test would show an opening child skipped, a later-added child incorrectly joining, mutation being suppressed for future operations, or package outward error behavior changing.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| First trace processor throws during shutdown | predecessor test | later processor called; shutdown rejects |
| First trace processor throws during force flush | predecessor test | later processor called; error reported globally |
| Logs synchronous throw | predecessor tests | later processor called; promise rejects |
| Metrics synchronous throw | predecessor tests | later reader called; promise rejects |
| First trace child removes second | new shutdown/forceFlush tests | second called from opening snapshot |
| First logs child removes second | new shutdown/forceFlush tests | second called from opening snapshot |
| First metric reader removes second collector | new shutdown/forceFlush tests | second called from opening snapshot |
| Mutation persists after operation | all mutation tests | original collection remains changed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning record or reopening trigger |
| --- | --- | --- |
| Child addition during operation | opening snapshot intentionally excludes it | reopen if live-add semantics are required |
| Duplicate child entries | existing list semantics call each entry | separate deduplication policy |
| All-error aggregation | changes outward failure contract | separate #194 comparison |
| Delayed lifecycle recursion | different promise/provenance problem | #216 |
| Provider one-shot state | different admission owner | provider-state finding |
| Spans ending after shutdown begins | different delivery boundary | pre-existing-span finding |

## Exact execution and receipts

| Repository/head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/opentelemetry-js@80e3b74b...` | Unit, Lint, E2E, CodeQL, Bundler, W3C, peer, security | product matrix passed; changelog policy separate | target-executed |
| `teamleaderleo/opentelemetry-js@e19247b...` | Unit `30584057854` | queued | target-test-prepared |
| same head | Lint `30584057575` | queued | target-test-prepared |
| same head | E2E, CodeQL, Bundler, W3C, peer, security | queued | target-test-prepared |
| same head | changelog `30584057544` | skipped by owned-fork policy | policy result |

## Complete-diff and compatibility review

Changed-file fence:

- `packages/sdk-trace/src/MultiSpanProcessor.ts`;
- `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`;
- `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`;
- `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`;
- `packages/sdk-metrics/src/MeterProvider.ts`;
- `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`.

Compatibility review covers synchronous invocation timing, `Promise.all` concurrency, trace/logs/metrics outward error policy, mutation visibility, future membership, and package boundaries. The branch remains pinned and requires a current-base relationship review before land-ready status.

## Selected direction, losing reasons, and reopening trigger

Selected direction: snapshot the opening child set and invoke every opening child through the synchronous safe-call wrapper.

Losing reasons:

- direct live iteration stops after synchronous throw;
- safe-call with live iteration still skips deleted entries;
- freezing changes public and future mutation semantics;
- sequential waiting changes concurrency and latency;
- settle-all aggregation changes outward error policy and belongs separately.

Reopening trigger: project evidence requiring live mutation to alter an already-started lifecycle operation, a performance regression from shallow copies at representative processor counts, or exact-head tests showing changed outward failure behavior.

Non-delegable human decision: none.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `D2`
- Exact next transition: settle the exact-head matrix at `e19247b...`, repair any concrete failure, and obtain independent complete-diff review.
- Clearing condition: six mutation controls and the named Unit, Lint, E2E, CodeQL, Bundler, W3C, peer-dependency, and workflow-security gates pass on one exact head.
- Required subgates: current exact-head matrix, current-base review, independent complete-diff review.
- Non-delegable decision: none.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | `80e3b74b...` | safe-call wrapper established synchronous-throw attempt-all behavior |
| 2026-07-30 | Fieldwork #225 audit | live-array mutation defeated the broad attempt-all claim |
| 2026-07-31 | `e19247b...` | opening snapshots and six mutation controls selected across all three signals |
| 2026-07-31 | decision-protocol review | reclassified from research-active to delivery-gate-ready; no human design choice remains |

## References

- Fieldwork #194, #216, and #225
- `teamleaderleo/opentelemetry-js#6`
- ECMAScript Array.prototype.map algorithm
- GitHub Actions runs `30584057854`, `30584057575`, `30584057970`, `30584057732`, `30584058528`, `30584057454`, `30584057580`, and `30584057991`
