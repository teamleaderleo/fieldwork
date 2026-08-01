# Deep dive — Unit 11: snapshot lifecycle targets before concurrent fanout

## Governing invariant

A lifecycle aggregate attempts every child present when the operation begins, while preserving the package's existing outward failure policy and allowing collection mutations to affect later operations.

## Exact subject

- upstream repository: `open-telemetry/opentelemetry-js`;
- current public main and reviewed base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- repaired owned source: `1b7609141e87ad226e64bb0238ef602e76812896`;
- source branch: `upstream/unit-11-lifecycle-fanout`;
- changed-file fence: three production files and three target-native test files.

## Call-chain analysis

### Trace

`MultiSpanProcessor` directly invokes `SpanProcessor.forceFlush()` and `SpanProcessor.shutdown()` while constructing its promise array. Type declarations promise `Promise<void>`, but arbitrary implementations can throw before returning. A direct throw exits the loop before later processors are invoked.

The processor array is retained from the constructor, so external mutation of the same array can also remove a later indexed processor during the current loop.

Repair:

1. shallow-copy `_spanProcessors` before the first child call;
2. invoke each direct child through a local eager try/catch helper;
3. retain the original outer promise and `globalErrorHandler` scaffolding.

### Logs

`MultiLogRecordProcessor` directly invokes `LogRecordProcessor.forceFlush()` and `shutdown()`. The same direct-throw mechanism applies. Its processor array is public, making live mutation an explicit runtime possibility.

Repair:

1. shallow-copy `processors`;
2. call each processor through the eager helper;
3. keep force-flush timeout wrapping unchanged.

### Metrics

`MeterProvider` invokes `MetricCollector.shutdown()` and `forceFlush()`. Those collector methods are already `async` and await the reader internally. A reader that throws synchronously causes the collector async function to return a rejected promise; it does not throw out of `MeterProvider`'s mapping callback. Later collectors are already attempted on the baseline.

The collector method does execute synchronously until its first await. A reader can mutate the live shared collector array during that prefix, causing a later collector to be skipped by live indexed mapping.

Repair:

1. shallow-copy `metricCollectors`;
2. map the snapshot directly to the existing async collector methods;
3. do not add another safe-call helper.

## Why the helper is eager

The retained helper is:

```ts
function callLifecycle(callback: () => Promise<void>): Promise<void> {
  try {
    return callback();
  } catch (error) {
    return Promise.reject(error);
  }
}
```

Using `Promise.resolve().then(callback)` would also convert throws, but would defer invocation to a microtask. The direct try/catch preserves the existing eager start order while allowing promise-list construction to continue.

## Trace compatibility refinement

The earlier clean generation rewrote trace force flush to `Promise.all(...).then(success, failure)`. Although focused tests showed equivalent behavior, the rewrite was unnecessary. The repaired head restores the baseline structure:

- the original `new Promise(resolve => ...)` remains;
- the original `globalErrorHandler` call remains;
- force flush still resolves after reporting failure;
- shutdown still rejects through the original outer promise.

Only snapshot selection and direct-call protection now differ from the baseline.

## Test-harness refinement

The added trace tests temporarily restored global error handling with `setGlobalErrorHandler(loggingErrorHandler)`. `loggingErrorHandler` is a factory; passing it without invocation installs the factory itself as the delegate. Because callback return values are assignable to `void`, TypeScript accepts the mistake, but later errors would not be logged by the intended handler.

The repaired test uses `setGlobalErrorHandler(loggingErrorHandler())`, matching existing repository convention and preventing cross-test global-state leakage.

## Reversing controls

- trace shutdown: first processor throws; second opening processor is still invoked; aggregate rejects;
- trace force flush: first processor throws; second is invoked; error is reported; aggregate resolves;
- trace shutdown/force flush: first removes second from backing array; second opening processor is still invoked;
- logs shutdown/force flush: equivalent direct-throw and removal controls; aggregate rejects on error;
- metrics shutdown/force flush: removal controls prove snapshot behavior; synchronous-throw controls were removed because they pass the baseline without source changes.

All mutation controls also assert that the original collection remains changed, distinguishing stable current membership from permanent freezing.

## Compatibility and limits

- public API and exported types: unchanged;
- concurrency: eager `Promise.all` retained;
- error policy: trace shutdown rejects; trace force flush reports and resolves; logs and metrics reject;
- allocation: one shallow child-list copy per affected lifecycle operation;
- future mutation: retained;
- settle-all completion/error aggregation: not provided;
- child idempotence, one-shot ownership, final metrics collection, delayed recursion, and post-shutdown telemetry admission: separate units.

## Current source cleanliness

The exact compare contains only:

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
3. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
4. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`
5. `packages/sdk-metrics/src/MeterProvider.ts`
6. `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`

No workflow, dependency, lock, generated, publisher, or research-only file is present.

## Staleness and overlap

During the repair pass, public `main` remained identical to the pinned base. Open pull-request and issue searches for the affected symbols, shutdown/force-flush fanout, snapshot wording, and skipped-later-child behavior found no replacement contribution. Repeat immediately before any authorized filing.
