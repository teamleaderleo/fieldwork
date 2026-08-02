# Deep dive — Unit 11: stabilize lifecycle fanout targets

## In simple words

The bug is a lifecycle fanout membership problem, not a general promise-concurrency problem. The repair snapshots the processors present when shutdown or force flush begins, preserves eager invocation and existing error contracts, and limits the patch to trace and logs paths that have supported mutable processor membership.

## Governing invariant

A supported lifecycle fanout attempts every processor present when the operation begins, while preserving its existing failure policy and allowing processor-array mutations to affect later operations.

## Exact subject

- public base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- clean candidate: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- reviewed pre-squash tree source: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- changed-file fence: three production files and three tests;
- relation: one commit ahead, zero behind.

The clean candidate reuses the exact six file blobs from the reviewed pre-squash head.

## Call-chain analysis

### `MultiSpanProcessor`

The constructor retains the caller-supplied processor array. Shutdown and force flush directly invoked processor methods while building promise inputs. A processor could synchronously throw before returning its declared promise, stopping later invocation. A processor could also mutate the retained array and remove a later opening processor.

Repair: snapshot the array and invoke each processor through an eager try/catch helper. Existing shutdown rejection and force-flush global-error-handler/resolve behavior remain.

### Public `TracerProvider.forceFlush()`

This method does not delegate to `MultiSpanProcessor.forceFlush()`. It directly reads the aggregate’s processor list and builds timeout-controlled per-processor promises.

Baseline issues:

1. mapping the live array let an earlier processor remove a later opening processor;
2. the timeout was armed before invocation; a synchronous throw bypassed normal promise cleanup and left the timer pending.

Repair:

- snapshot the processor list before mapping;
- use the eager helper so synchronous throws become rejected promises;
- retain the existing `.catch()` path, which clears the timeout and resolves the per-processor result with the error;
- retain the provider’s outer error-array rejection contract.

The negative control verifies that a genuinely pending processor still reaches the timeout path.

### `MultiLogRecordProcessor`

`LoggerProvider` delegates lifecycle work to this aggregate, which retains the configured processor array as a public member. Direct processor calls could throw synchronously or mutate the live array. Snapshot plus eager safe-call is required; force-flush timeout wrapping remains unchanged.

### Why metrics is excluded

`MeterProvider` creates a new internal `MetricCollector` for each supplied reader and owns the collector list. It does not retain the caller’s readers array. The prior mutation tests accessed private provider state to splice that list, so they did not establish a supported public runtime path.

Additionally, `MetricCollector.shutdown()` and `forceFlush()` are async, so reader synchronous throws already become rejected promises. Symmetry with trace and logs is not enough to justify production changes.

## Eager helper rationale

A local try/catch preserves synchronous start order. `Promise.resolve().then(callback)` would catch throws but defer invocation to a microtask.

## Test-harness finding

The aggregate trace test originally restored `loggingErrorHandler` instead of `loggingErrorHandler()`. The repaired test installs the actual default handler and prevents global-state leakage.

## Reversing controls

- trace aggregate shutdown/force flush: synchronous throw and live removal;
- trace provider force flush: live removal, later invocation after synchronous throw, existing one-error-array rejection, zero remaining fake timers, and retained genuine-timeout behavior;
- logs shutdown/force flush: synchronous throw and live removal.

Mutation controls also verify the backing processor array remains mutated, distinguishing stable current membership from permanent freezing.

## Compatibility

- public API and types unchanged;
- eager fanout retained;
- aggregate trace shutdown rejects;
- aggregate trace force flush reports globally and resolves;
- provider trace force flush retains collected-error rejection;
- logs retain rejection and timeout behavior;
- future mutation remains visible;
- one shallow copy per affected entrypoint.

## Changed files

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Limits

No settle-all aggregation, cancellation, retry, idempotence, delayed recursion, or post-shutdown admission changes.

## Staleness and overlap

The pinned public-main snapshot matched the source base during repair. Refresh public main, duplicates, contribution policy, and disclosure requirements immediately before any authorized filing.
