# F194: Attempt every lifecycle child from a stable opening snapshot

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#194`  
Canonical implementation: `teamleaderleo/opentelemetry-js#6`  
Exact implementation head: `db7a0b3a2179f43bf1e0145c8352ff0367bdce79`  
Exact base revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`  
Strongest evidence class: `target-executed` for synchronous-throw fanout; opening-snapshot source and controls are under repaired exact-head execution  
Review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

Trace, log, and metric providers own lists of child processors or readers. When shutdown or force flush begins, every child that belonged to the list at that moment should receive the call.

Catching a synchronous exception is necessary but insufficient. JavaScript array iteration observes the live array. A first child can remove a later child before the iterator reaches it, silently shrinking the current lifecycle operation.

The selected repair copies the child list before invoking any child. The current operation uses that opening snapshot. Mutations remain visible to future operations.

## Why this matters

A skipped processor or reader can leave telemetry buffered or resources open. Child-controlled mutation should not erase lifecycle work for the opening set.

Leaving live iteration unchanged preserves the bounded skip whenever a child synchronously throws or deletes a later entry. Frequency is unknown; the mechanism is available through retained constructor arrays, the public logs processor array, and metric collector storage.

## Governing invariant

A lifecycle aggregate must attempt every child in its opening membership set while preserving each package's outward error policy and future membership semantics.

Required properties:

1. synchronous throw cannot stop later child invocation;
2. synchronous mutation cannot remove a later opening child from the current operation;
3. additions after start do not join the current operation;
4. mutation remains effective for future operations;
5. trace, logs, and metrics keep established error behavior;
6. child calls remain eagerly concurrent;
7. the repair does not freeze public arrays or widen mutation authority.

## Current finding

Attempt-all requires two independent mechanisms:

1. `callLifecycle()` converts synchronous throws into rejected promises so eager invocation continues;
2. each lifecycle entrypoint snapshots its child array before the first child call.

The implementation uses `.slice()` for trace processors, log processors, and metric collectors. Trace shutdown still rejects; trace force flush still reports through the global error handler and resolves; logs and metrics still reject.

The first matrix on head `e19247b801817abaf8c9fff5a39d00783d8c38e6` exposed a test-only TypeScript inference defect. In the metrics mutation controls, a callback initialized solely by `throw` inferred as `() => never`, then rejected assignment of the real mutation callback `() => void`. Commit `db7a0b3a2179f43bf1e0145c8352ff0367bdce79` explicitly types both callbacks as `() => void`. Product lint had passed before compilation reached this test error.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Synchronous throws can stop eager promise-list construction | `target-executed` | predecessor `80e3b74b...` matrix | Does not cover mutation |
| Live `map()` can skip a removed later child | `source-read`, model control | source review and six mutation tests | Repaired exact-head execution pending |
| Opening snapshots preserve current membership | source-reviewed | trace/logs/metrics source at `db7a0b3...` | Future operations use mutated live arrays |
| Existing outward error policies remain represented | predecessor execution plus source review | PR #6 diff and tests | Does not aggregate every async failure |
| First red matrix was blocked by test typing | exact hosted compile | Lint run `30584057575`, job `91011127143`, TS2322 at metrics test lines 69 and 128 | New head must still execute behavior |

## Ownership map

- Trace: `MultiSpanProcessor` and its processor array.
- Logs: `MultiLogRecordProcessor.processors`, a public mutable array.
- Metrics: `MeterProviderSharedState.metricCollectors`.
- Entrypoints: `shutdown()` and `forceFlush()`.
- Invocation: child methods are called synchronously while promise inputs are built.
- Error conversion: synchronous throw becomes a rejected promise.
- Membership: `.slice()` before invocation.
- Future state: original-array mutation remains observable after the operation.

## Historical precedent

### ECMAScript array iteration

`Array.prototype.map` checks indexed properties as iteration proceeds; a deleted entry can be skipped. OpenTelemetry must define lifecycle membership rather than inherit that incidental behavior.

### Existing Promise.all fanout

The pinned implementations construct child promises eagerly and await them concurrently. Stable opening membership can preserve that latency shape without preserving live mutation during construction.

## Decision criteria

1. every opening child invoked once;
2. synchronous errors do not stop later invocation;
3. deterministic current membership;
4. future membership remains mutable;
5. package-compatible outward errors;
6. unchanged concurrent fanout;
7. local readable implementation;
8. no freeze, deduplication, or new authority.

## Alternatives and results

| Option | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- |
| Live array plus direct calls | first child throws | later children skipped | rejected |
| Live array plus safe-call | first child removes second | deleted index skipped | rejected |
| Opening snapshot plus safe-call | remove-second controls for six entrypoints | opening child retained; mutation persists | selected |
| Freeze or permanently copy arrays | future membership comparison | changes observable ownership | rejected |
| Sequentially await children | latency/concurrency comparison | changes eager fanout | rejected |
| Settle-all/error aggregation | outward error comparison | materially different contract | deferred |

## Independent criticism

- Cross-review found the predecessor's “attempt all” claim was too broad because it iterated live arrays.
- Tests assert that the original arrays remain mutated afterward, preventing the repair from silently freezing membership.
- The first exact-head matrix found a compile defect in test scaffolding rather than accepting a prepared test as executed evidence.
- A reversing result would show an opening child skipped, a later-added child joining, future mutation suppressed, or package error behavior changed.

## Covered edge cases

- first trace/log/metric child throws during shutdown and force flush;
- first child removes a later child during all six lifecycle entrypoints;
- later opening child still called;
- original collection remains mutated afterward;
- trace force-flush global error reporting retained;
- logs and metrics rejection retained by tests.

## Deferred boundaries

| Boundary | Owner or reopening path |
| --- | --- |
| Child addition during operation | reopen only if live-add semantics are required |
| Duplicate entries | separate deduplication policy |
| All-error aggregation | separate comparison/finding |
| Delayed lifecycle recursion | #216 |
| Provider one-shot state | provider-state finding |
| Spans ending after shutdown begins | pre-existing-span finding |

## Exact receipts

| Head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `80e3b74b...` | Unit, Lint, E2E, CodeQL, Bundler, W3C, peer, security | passed; live-array defect later found | `target-executed` predecessor |
| `e19247b...` | peer `30584057580`, CodeQL `30584057732`, Zizmor `30584057991` | passed | exact-head partial gates |
| `e19247b...` | Unit `30584057854`, Lint `30584057575`, E2E `30584057970`, Bundler `30584058528`, W3C `30584057454` | failed | hosted failure evidence |
| `e19247b...` | Lint job `91011127143` | product lint passed; compile failed on two `() => never` test inferences | classified test defect |
| `db7a0b3...` | replacement matrix including runs `30592187910` through `30592187954` | queued/in progress at last refresh | `target-test-prepared` |

## Complete-diff boundary

Current seven-file fence:

- `packages/sdk-trace/src/MultiSpanProcessor.ts`;
- `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`;
- `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`;
- `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`;
- `packages/sdk-metrics/src/MeterProvider.ts`;
- `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`;
- the last path only has the explicit callback type repair beyond the six-file candidate.

## Selected direction and reopening trigger

Selected direction: snapshot the opening child set and invoke every opening child through the synchronous safe-call wrapper.

Reopen for project evidence requiring live mutation to alter an already-started operation, representative performance regression from shallow copies, or exact-head behavior showing changed outward failure policy.

Non-delegable human decision: none.

## Exact transition

Settle the repaired matrix at `db7a0b3a2179f43bf1e0145c8352ff0367bdce79`, classify any remaining exact failures, repair concrete defects, review the current-base relationship, and obtain independent complete-diff disposition.
