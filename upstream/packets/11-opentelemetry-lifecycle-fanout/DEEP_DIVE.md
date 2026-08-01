# Deep dive — Unit 11: stabilize lifecycle fanout targets

## Governing invariant

A supported lifecycle fanout attempts every processor present when the operation begins, while preserving its existing failure policy and allowing processor-array mutations to affect later operations.

## Exact subject

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- clean candidate: `f4910b355d12895edf25372444f76d4def08901c`;
- changed-file fence: three production files and three tests.

## Call-chain analysis

### `MultiSpanProcessor`

The constructor retains the caller-supplied processor array. Shutdown and force flush directly invoke processor methods while building promise inputs. A processor may synchronously throw before returning its declared promise, stopping later invocation. A processor may also mutate the retained array and remove a later opening processor.

Repair: snapshot the array and invoke each processor through an eager try/catch helper. Existing shutdown rejection and force-flush global-error-handler/resolve behavior remain.

### Public `TracerProvider.forceFlush()`

This method does not delegate to `MultiSpanProcessor.forceFlush()`. It directly reads the aggregate's processor list and builds timeout-controlled per-processor promises.

Baseline issues:

1. mapping the live array lets an earlier processor remove a later opening processor;
2. the timeout is armed before invocation; a synchronous throw bypasses the normal promise `.catch()` cleanup and leaves the timer pending.

Repair:

- snapshot the processor list before mapping;
- use the eager helper so synchronous throws become rejected promises;
- retain the existing `.catch()` path, which clears the timeout and resolves the per-processor result with the error;
- retain the provider's outer error-array rejection contract.

### `MultiLogRecordProcessor`

`LoggerProvider` delegates lifecycle work to this aggregate, which retains the configured processor array as a public member. Direct processor calls can throw synchronously or mutate the live array. Snapshot plus eager safe-call is required; force-flush timeout wrapping remains unchanged.

### Why metrics is excluded

`MeterProvider` creates a new internal `MetricCollector` for each supplied reader and owns the collector list. It does not retain the caller's readers array. The prior mutation tests accessed private provider state to splice that list, so they did not establish a supported public runtime path.

Additionally, `MetricCollector.shutdown()` and `forceFlush()` are async, so reader synchronous throws already become rejected promises. Symmetry with trace/logs is not enough to justify production changes.

## Eager helper rationale

A local try/catch preserves synchronous start order. `Promise.resolve().then(callback)` would catch throws but defer invocation to a microtask.

## Test-harness finding

The aggregate trace test originally restored `loggingErrorHandler` instead of `loggingErrorHandler()`. The repaired test installs the actual default handler and prevents global-state leakage.

## Reversing controls

- trace aggregate shutdown/force flush: synchronous throw and live removal;
- trace provider force flush: live removal, later invocation after synchronous throw, existing one-error-array rejection, and zero remaining fake timers;
- logs shutdown/force flush: synchronous throw and live removal.

Mutation controls also verify the backing processor array remains mutated, distinguishing stable current membership from permanent freezing.

## Compatibility

- public API/types unchanged;
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

Public main remained identical to the base during repair. Refreshed open issue/PR searches found no equivalent current repair. Repeat immediately before authorized filing.
