# Approaches — Unit 11: stabilize lifecycle fanout targets

## Selected boundary

Use the smallest mechanism at each supported fanout site:

- `MultiSpanProcessor`: opening snapshot plus eager synchronous safe-call;
- `TracerProvider.forceFlush()`: opening snapshot plus safe-call inside the existing timeout wrapper;
- `MultiLogRecordProcessor`: opening snapshot plus eager synchronous safe-call;
- metrics: excluded after deeper reachability review.

All retained paths preserve eager invocation, existing outward error behavior, and future array mutation.

## Why trace has two force-flush sites

Public `TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly fans out over the processor list. Repairing only the aggregate leaves the public provider path exposed to live removal.

The provider's Promise executor already turns a synchronous throw into rejection, but that path bypasses timer cleanup. The selected safe-call sends the failure through the existing per-processor catch, which clears the timer and preserves the current outer errors-array rejection.

## Package-specific rationale

### Trace aggregate

- copy `_spanProcessors` before the first child call;
- use local eager try/catch so later opening processors are invoked;
- preserve the original outer promise and global-error-handler structure.

### Trace provider

- copy the processor list before mapping;
- retain the timeout and result filtering model;
- normalize synchronous invocation failure so the existing catch clears the timeout.

### Logs

- copy the public processor array;
- protect direct lifecycle calls;
- retain `callWithTimeout()` placement and default timeout.

### Metrics exclusion

The predecessor metrics proposal relied on mutation of private collector state. `MeterProvider` owns its collector list and exposes no supported mutation route; collector lifecycle methods are already async. Keeping metrics would broaden the patch without a demonstrated supported defect.

## Rejected alternatives

- Safe-call over live arrays: still permits removal-based skipping.
- Microtask deferral: changes eager start ordering.
- Permanent freezing/copying: changes future membership behavior.
- Sequential awaiting: changes concurrency and latency.
- Settle-all aggregation: changes outward error timing and types.
- Repairing only `MultiSpanProcessor`: misses public provider force flush.
- Metrics snapshot-only: private-state hardening without supported reachability.

## Decision history

1. Safe-call-only head passed gates but failed review on live mutation.
2. First snapshot fixture had test-only TS2322 inference failures.
3. Clean predecessor `641528c...` passed all named workflows.
4. Review `4834242586` removed the metrics safe-call claim.
5. Deeper review removed metrics entirely and found public provider force flush.
6. Concurrent branch rewrites made PR #18 non-authoritative.
7. Successor branch `upstream/unit-11-lifecycle-fanout-v2` and PR #19 were created directly from current public main.

## Exact current state

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- successor source head: `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`;
- relation: ahead 6, behind 0;
- boundary: three production files and three tests;
- exact-head workflows: runs `30694086713` through `30694086746`, initially queued;
- public upstream contact: unauthorized and not performed.
