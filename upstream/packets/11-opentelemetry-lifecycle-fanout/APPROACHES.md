# Approaches — Unit 11: snapshot lifecycle targets before concurrent fanout

## Selected boundary

Use the smallest mechanism required at each fanout site:

- `MultiSpanProcessor`: opening snapshot plus eager synchronous safe-call;
- `TracerProvider.forceFlush`: opening snapshot plus synchronous-throw normalization inside the existing per-processor timeout wrapper;
- `MultiLogRecordProcessor`: opening snapshot plus eager synchronous safe-call;
- `MeterProvider`: opening snapshot only, because `MetricCollector` lifecycle methods are already async.

All paths retain eager invocation, existing outward error behavior, first-rejection semantics, and collection mutation for future operations.

## Why trace has two force-flush sites

Public `TracerProvider.forceFlush()` does not delegate to `MultiSpanProcessor.forceFlush()`. It reaches into the aggregate's processor array and creates one timeout-controlled promise per processor. Therefore repairing only `MultiSpanProcessor` leaves the public provider path vulnerable to live-array removal.

Its `new Promise` executor already converts a direct processor throw into rejection, but the timeout is armed before invocation and was not cleared on that synchronous path. The repaired provider catches the throw explicitly, clears the timer, and resolves the per-processor result with the error so the existing outer rejection shape is preserved.

## Package-specific rationale

### Trace aggregate

- copy `_spanProcessors` before the first call;
- use local try/catch so later opening processors are invoked after a direct throw;
- preserve the original outer promise and global-error-handler scaffolding.

### Trace provider

- copy the same processor list before mapping;
- keep the existing timeout and aggregate result model;
- catch synchronous invocation/then attachment failures, clear the timeout, and return the error through the existing result list.

### Logs

- copy the public processor array;
- protect direct processor calls;
- retain `callWithTimeout()` placement and default timeout.

### Metrics

- copy `metricCollectors`;
- call async collector methods directly;
- retain only mutation reversing tests.

## Rejected alternatives

- Safe-call over live arrays: still permits removal-based skipping.
- Metrics safe-call: duplicates the collector async boundary and overstates the defect.
- Microtask deferral: changes eager start ordering.
- Permanent freezing/copying: changes future membership behavior.
- Sequential awaiting: changes concurrency and latency.
- Settle-all aggregation: changes error timing and types.
- Repairing only `MultiSpanProcessor`: misses public `TracerProvider.forceFlush()`.

## Decision history

1. Safe-call-only head `80e3b74b...` passed gates but failed review on live mutation.
2. Snapshot fixture `e19247b...` had test-only TS2322 inference failures.
3. Clean head `641528c...` passed all named workflows.
4. Review `4834242586` narrowed metrics to snapshot-only.
5. Deeper review restored trace aggregate scaffolding and fixed `loggingErrorHandler()` test cleanup.
6. End-to-end review found the separate provider force-flush fanout and timeout leak.
7. Final source was collapsed to one commit directly on current public main.

## Exact current state

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- clean source head: `59f83f889bed06a951d458556b2e7e1695cbea10`;
- relation: ahead 1, behind 0;
- boundary: four production files and four test files;
- exact-head workflow set: queued under runs `30694080910` through `30694080955`;
- public upstream contact: unauthorized and not performed.
