# F194: Attempt every lifecycle child from a stable opening snapshot

Finding state: `research-active`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#194`  
Canonical finding path: `findings/F194-opentelemetry-lifecycle-fanout-snapshot/finding.md`  
Canonical implementation: `teamleaderleo/opentelemetry-js#6`  
Exact implementation head: `e19247b801817abaf8c9fff5a39d00783d8c38e6`  
Exact base revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`  
Strongest evidence class: `target-executed` for synchronous-throw fanout at predecessor head; mutation-safe repair is queued for target execution  
Reviewed input generation: `teamleaderleo/opentelemetry-js#6 at e19247b801817abaf8c9fff5a39d00783d8c38e6`  
Current review disposition: `EXECUTE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Trace, log, and metric providers each keep a list of child processors or readers. During shutdown or force flush, every child that existed when the operation began should receive the call.

The first candidate caught synchronous exceptions so one throwing child could not stop later calls. A deeper review found another trap: JavaScript `Array.map()` iterates the live array. A child can synchronously remove a later child while the map is running, causing the removed entry to be skipped.

The repair copies the child list at the start of each lifecycle operation. The current operation uses that stable snapshot. Mutations still affect future operations.

## Why we care

Skipping a later processor or reader can leave telemetry buffers unflushed or resources unclosed. The caller asked the provider to shut down or flush all children that were registered at operation start. Child-controlled mutation should not silently shrink that obligation.

## What happens if we leave it alone

A first child can mutate the shared array during its synchronous call. `Array.map()` records the original length but skips an index whose property disappears before that index is visited. A later child can therefore receive no shutdown or force-flush call even though it belonged to the opening set.

The exact frequency is unknown. The failure requires synchronous mutation during lifecycle invocation, including mutation through shared constructor arrays, public log processor arrays, or internal collector access.

## Current finding

“Attempt every child” requires two independent properties:

1. convert a synchronous child throw into a rejected promise so iteration continues;
2. iterate a stable snapshot captured before the first child call.

The exact outward error policy remains package-specific:

- trace shutdown rejects;
- trace force flush reports through the global error handler and resolves;
- logs shutdown and force flush reject;
- metrics shutdown and force flush reject.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Synchronous child throws can stop eager promise-list construction | target-executed | predecessor PR #6 head `80e3b74b...` tests and full product matrix | Does not cover mutation |
| A live-array map can skip a later child removed by an earlier callback | source-read and model-executed | source at `80e3b74b...`; mutation controls added at `e19247b...` | Target execution of the new controls is queued |
| Opening snapshots preserve current-operation membership | source-reviewed | `MultiSpanProcessor.ts`, `MultiLogRecordProcessor.ts`, `MeterProvider.ts` at `e19247b...` | Does not define membership for future operations |
| Trace, logs, and metrics can share the invariant while retaining different outward error policy | target-executed predecessor plus source-reviewed repair | PR #6 complete diff | Does not aggregate all asynchronous failures |

## System and ownership map

- Trace owner: `MultiSpanProcessor` stores an array of `SpanProcessor` children.
- Logs owner: `MultiLogRecordProcessor` stores a public `processors` array.
- Metrics owner: `MeterProviderSharedState.metricCollectors` stores one collector per reader.
- Lifecycle entrypoints:
  - `shutdown()`;
  - `forceFlush()`.
- Invocation timing: each child method is called synchronously while the promise list is constructed.
- Error conversion: `callLifecycle()` returns a rejected promise when a child throws synchronously.
- Membership rule: each operation now calls `.slice()` before invoking any child.
- Mutation rule: mutation of the original array is visible after the operation and affects later operations, while the current snapshot remains fixed.

## Historical precedent

### JavaScript array iterative method semantics

- Source: https://tc39.es/ecma262/multipage/indexed-collections.html#sec-array.prototype.map
- Principle supported: `map` checks whether each indexed property exists as iteration proceeds; deleted entries can be skipped.
- Important difference: the language behavior is generic. OpenTelemetry must choose whether lifecycle membership is live or fixed at operation start.

### OpenTelemetry SDK shutdown contract

- Source: https://github.com/open-telemetry/opentelemetry-specification/tree/main/specification
- Principle supported: SDK shutdown and flush operations own child processor or reader lifecycle work.
- Important difference: signal packages have distinct outward failure policies and internal ownership models.

## Approaches considered

### Retained approach: shallow opening snapshot

A shallow copy is sufficient because membership, not child identity, is the invariant. It preserves synchronous invocation timing and keeps each package's existing promise/error behavior.

### Declined: keep live `map()` and document mutation as unsupported

Logs expose the processor array publicly, and trace retains the constructor array by reference. The current implementation already permits mutation. Silent skipping is a poor failure mode even when mutation is unusual.

### Declined: freeze or clone children permanently

Permanent freezing changes public or observable mutability and would affect future operations. The requirement only concerns the opening set for one operation.

### Declined: sequentially await each child

Sequential waiting changes concurrency and latency. The existing contract builds all child promises eagerly and uses `Promise.all`.

### Deferred: all-error aggregation and settle-all async behavior

The repair attempts every synchronous child call, while `Promise.all` still rejects on the first observed asynchronous failure. Aggregation is a separate design decision.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| First trace processor throws during shutdown | predecessor native test | later processor still called; shutdown rejects |
| First trace processor throws during force flush | predecessor native test | later processor called; error reported globally |
| Logs synchronous throw | predecessor native tests | later processor called; public promise rejects |
| Metrics synchronous throw | predecessor native tests | later reader called; public promise rejects |
| First trace child removes second | new shutdown and force-flush tests at `e19247b...` | second remains in opening snapshot |
| First logs child removes second | new shutdown and force-flush tests | second remains in opening snapshot |
| First metrics reader removes second collector | new shutdown and force-flush tests | second collector remains in opening snapshot |
| Mutation persists after operation | new tests | original arrays show the removal, proving snapshot isolation rather than mutation suppression |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Child addition during operation | Opening snapshot intentionally excludes later additions | reopen only if live-add semantics are desired |
| Reordering during operation | Snapshot preserves opening order | covered by the same invariant; add exact control if implementation changes |
| Duplicate child entries | Existing array semantics call each opening entry | separate deduplication policy if requested |
| Async mutation after child promise returns | Promise list is already constructed | no current-operation membership effect |
| All-error aggregation | Separate outward error contract | #194 follow-up design finding |
| Provider one-shot state and delayed recursion | Different state owner | #216 and provider-specific findings |
| Span delivery after provider shutdown | Different admission/delivery boundary | trace pre-existing-span finding |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/opentelemetry-js@80e3b74b...` | Unit, Lint, E2E, CodeQL, Bundler, W3C, peer dependency, workflow security | hosted GitHub runners | passed; changelog-only policy failure recorded separately | target-executed |
| `teamleaderleo/opentelemetry-js@e19247b...` | Unit Tests `30584057854` | hosted runner | queued | target-test-prepared |
| same head | Lint `30584057575` | hosted runner | queued | target-test-prepared |
| same head | E2E, CodeQL, Bundler, W3C, peer dependency, workflow security | hosted runners | queued | target-test-prepared |
| same head | changelog `30584057544` | hosted runner | skipped by owned-fork policy | policy result |

## Complete-diff and compatibility review

- Changed-file fence: six files.
  - `packages/sdk-trace/src/MultiSpanProcessor.ts`;
  - `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`;
  - `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`;
  - `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`;
  - `packages/sdk-metrics/src/MeterProvider.ts`;
  - `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`.
- Base relationship: pinned base `7b06368b...`; current-base restack remains a later delivery gate.
- Temporary carrier: none; PR #6 is the canonical owned-fork implementation trial.
- Compatibility surfaces examined: synchronous invocation timing, outward error policy, mutation visibility, future-operation membership, trace/log/metric package boundaries.
- Known routine repair remaining: run formatter, TypeScript checks, native tests, and complete repository gates at `e19247b...`; repair any exact failure.
- Reviewer eligibility: the prior head is invalidated by the repair. Review begins from `e19247b...` after checks settle.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: settle all queued exact-head workflows and repair any test or lint failure.
- Clearing condition: mutation controls and all affected repository gates pass on one exact head with a complete-diff review.
- Required subgates: Unit, Lint, E2E, CodeQL, Bundler, W3C, peer dependency, workflow security.
- User decision requested: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | `80e3b74b...` | Safe-call wrapper established synchronous-throw attempt-all behavior |
| 2026-07-30 | Fieldwork #225 audit | Live-array mutation identified as a repair requirement |
| 2026-07-31 | `e19247b...` | Added opening snapshots and six mutation controls across trace, logs, and metrics |

## References

- https://github.com/teamleaderleo/fieldwork/issues/194
- https://github.com/teamleaderleo/fieldwork/issues/225
- https://github.com/teamleaderleo/opentelemetry-js/pull/6
- https://tc39.es/ecma262/multipage/indexed-collections.html#sec-array.prototype.map
- GitHub Actions runs `30584057854`, `30584057575`, `30584057970`, `30584057732`, `30584058528`, `30584057454`, `30584057580`, and `30584057991`
