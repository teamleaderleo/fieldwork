# Deep dive — Unit 11: snapshot lifecycle targets before concurrent fanout

## Governing invariant

Every lifecycle fanout attempts each child present when the operation begins, while preserving package-specific failure behavior and allowing collection changes to affect later operations.

## Exact subject

- upstream base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- clean candidate: `59f83f889bed06a951d458556b2e7e1695cbea10`;
- source branch: `upstream/unit-11-lifecycle-fanout`;
- changed-file fence: four production files and four target-native test files.

## Call-chain analysis

### `MultiSpanProcessor`

It directly invokes processor shutdown/force-flush methods while constructing a promise array. An implementation can throw before returning its declared promise, exiting the loop before later processors run. The retained constructor array can also be mutated during iteration.

Repair: snapshot the array and use an eager local try/catch helper. The original shutdown rejection and force-flush global-error-handler/resolve structure remains.

### `TracerProvider.forceFlush`

The public provider does **not** call `MultiSpanProcessor.forceFlush()`. It directly reads `_activeSpanProcessor['_spanProcessors']` and creates one timeout-controlled promise per processor.

Two independent baseline mechanisms exist:

1. mapping the live array allows an earlier processor to remove a later opening processor before its index is visited;
2. the timeout is armed before `spanProcessor.forceFlush()` is called. A synchronous throw rejects the Promise executor automatically, but bypasses the code that clears the timer, leaving it armed until expiry.

Repair:

- snapshot the processor array before mapping;
- retain the existing timeout, result filtering, and outward rejection shape;
- wrap invocation and handler attachment in try/catch;
- clear the timeout and resolve the per-processor result with the caught error.

This keeps later opening processors eager, returns the existing error array from the provider, and leaves no timeout after synchronous failure.

### `MultiLogRecordProcessor`

It directly invokes processor lifecycle methods over a public mutable array. Snapshot plus eager safe-call is required. Force-flush timeout wrapping remains unchanged.

### `MeterProvider`

It calls async `MetricCollector.shutdown()` / `forceFlush()`. Reader throws are already converted to rejected collector promises, so mapping continues. Only live collector-array removal is defective. Metrics therefore uses snapshot-only.

## Eager helper rationale

A direct try/catch helper preserves synchronous start order. `Promise.resolve().then(callback)` would catch throws but defer invocation to a microtask.

## Test-harness finding

The added aggregate trace test initially restored the global handler with `loggingErrorHandler` rather than `loggingErrorHandler()`. The factory itself is assignable to a void-returning handler, so type checking did not catch the mistake. The repaired test installs the actual default handler and avoids cross-test global-state leakage.

## Reversing controls

- trace aggregate shutdown and force flush: direct throw and live removal;
- trace provider force flush: live removal, direct throw, later invocation, existing `[error]` rejection shape, and zero remaining fake timers;
- logs shutdown and force flush: direct throw and live removal;
- metrics shutdown and force flush: live removal only.

Mutation controls verify that the backing collection remains changed, distinguishing stable current membership from permanent freezing.

## Compatibility

- public API and exported types: unchanged;
- eager concurrency: retained;
- trace aggregate force flush: still reports globally and resolves;
- trace provider force flush: still rejects with collected non-resolved results;
- logs/metrics: still reject;
- timeout behavior: unchanged except synchronous failure no longer leaves a dead timer;
- future mutation: retained;
- allocation: one shallow array copy per affected lifecycle entrypoint.

## Limits

This unit does not add settle-all error aggregation, child cancellation, retries, idempotence, final metric collection, delayed recursion handling, or post-shutdown telemetry admission changes.

## Changed files

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`
7. `packages/sdk-metrics/src/MeterProvider.ts`
8. `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`

No workflow, dependency, lock, generated, publisher, or research-only file is present.

## Staleness and overlap

Public main remained identical to the base during the repair pass. Open issue/PR searches for the affected symbols and lifecycle wording found no replacement work. Repeat immediately before authorized filing.
