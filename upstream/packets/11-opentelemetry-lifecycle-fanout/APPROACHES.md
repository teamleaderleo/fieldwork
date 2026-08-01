# Approaches — Unit 11: stabilize lifecycle fanout targets

## Selected boundary

- `MultiSpanProcessor`: opening snapshot plus eager synchronous safe-call;
- `TracerProvider.forceFlush()`: opening snapshot plus safe-call inside the existing timeout wrapper;
- `MultiLogRecordProcessor`: opening snapshot plus eager synchronous safe-call;
- metrics: excluded after supported-reachability review.

All retained paths preserve eager invocation, outward error behavior, and future array mutation.

## Why trace has two force-flush sites

Public `TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly fans out over the processor list. Repairing only the aggregate misses live removal and synchronous-failure timer cleanup on the public provider path.

The provider's Promise executor already converts a direct throw into rejection, but that path bypasses its timer-clearing result catch. The selected helper routes the failure through that existing catch and preserves the current outer errors-array rejection.

## Rejected alternatives

- safe-call over live arrays: still permits removal-based skipping;
- microtask deferral: changes eager start ordering;
- permanent freezing: changes future membership behavior;
- sequential awaiting: changes concurrency and latency;
- settle-all aggregation: changes error timing and types;
- aggregate-only trace repair: misses the public provider path;
- metrics snapshot-only: hardens private state without supported reachability evidence.

## Decision history

1. Safe-call-only generation passed gates but failed review on live mutation.
2. Snapshot fixtures had test-only TS2322 inference failures and were repaired.
3. Predecessor `641528c...` passed all named workflows.
4. Review `4834242586` exposed the metrics overclaim.
5. Deeper review removed metrics and added public provider force flush plus timer cleanup.
6. Concurrent rewrites made the original source/packet carriers non-authoritative.
7. Isolated successors were created; source was then cleanly squashed.

## Exact current state

- base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source head: `f4910b355d12895edf25372444f76d4def08901c`;
- relation: ahead 1, behind 0;
- boundary: three production files and three tests;
- validation PR: #19;
- workflow runs: `30694264703`, `30694264708`, `30694264710`, `30694264711`, `30694264717`, `30694264729`, `30694264735`, `30694264748`;
- public upstream contact: unauthorized and not performed.
