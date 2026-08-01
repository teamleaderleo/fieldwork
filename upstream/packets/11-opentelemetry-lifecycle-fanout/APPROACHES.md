# Approaches — Unit 11: snapshot lifecycle targets before concurrent fanout

## Decision

The repaired contribution uses the smallest mechanism required by each package:

- trace: opening snapshot plus synchronous safe-call;
- logs: opening snapshot plus synchronous safe-call;
- metrics: opening snapshot only.

All three retain eager `Promise.all` fanout, existing outward failure behavior, and mutation visibility for future operations.

## Why the packages differ

`SpanProcessor.shutdown()` / `forceFlush()` and `LogRecordProcessor.shutdown()` / `forceFlush()` are interface calls made directly by their aggregate. A conforming object can still throw before returning its declared promise. Without a local safe-call, that throw interrupts promise-list construction and later opening processors are never invoked.

`MeterProvider` calls `MetricCollector.shutdown()` and `MetricCollector.forceFlush()`, not readers directly. Both collector methods are `async`; they call and await the reader internally. A synchronous reader throw therefore becomes a rejected collector promise before control returns to `MeterProvider`, and array mapping continues. Metrics needs a stable opening list against mutation, but no additional safe-call wrapper.

## Selected implementation

### Trace

- copy `_spanProcessors` with `.slice()`;
- retain the existing promise array, outer `new Promise`, and `globalErrorHandler` structure;
- wrap each direct processor lifecycle invocation in `callLifecycle()`.

This avoids the earlier unnecessary refactor to `Promise.all(...).then(success, failure)` and removes a compatibility review question.

### Logs

- copy the public `processors` array with `.slice()`;
- invoke each direct processor through `callLifecycle()`;
- keep `callWithTimeout()` and the existing timeout/default behavior.

### Metrics

- copy `sharedState.metricCollectors` with `.slice()`;
- map directly to the existing async collector lifecycle methods;
- keep only mutation reversing tests.

## Evidence-changing repairs

1. Safe-call-only generation `80e3b74b...` passed gates but failed review because live-array removal could skip a later child.
2. Snapshot generation `e19247b...` had test-fixture TS2322 failures from callbacks inferred as `() => never`; explicit `() => void` typing repaired the fixture.
3. Clean generation `641528c...` passed all gates, but complete review found the metrics safe-call and its regression claim redundant.
4. Repaired source removed metrics helper churn and metrics throw regressions.
5. Deeper review found the trace test restored `loggingErrorHandler` rather than `loggingErrorHandler()`; repaired head restores the actual default handler.
6. Deeper baseline comparison restored the original trace outer promise/error-handler scaffolding.

## Rejected alternatives

### Safe-call over live arrays

It protects against direct throws but not removal of a later indexed child during iteration.

### Safe-call in metrics

It duplicates the async boundary already supplied by `MetricCollector` and falsely suggests a baseline defect.

### Promise microtask deferral

`Promise.resolve().then(callback)` would catch throws but defer child invocation, changing current eager synchronous start order. The local try/catch helper preserves eager invocation.

### Permanent copies or freezing

They would change future membership semantics, especially for the public logs processor array.

### Sequential awaiting

It would serialize lifecycle work and change latency and ordering.

### Settle-all aggregation

It would change caller-visible error timing/types and trace force-flush policy. This unit retains first-rejection `Promise.all` behavior.

### Shared cross-package helper

It would introduce package-boundary and ownership questions for only two direct-call sites. Local helpers keep the patch bounded.

## Current exact state

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- repaired source head: `1b7609141e87ad226e64bb0238ef602e76812896`;
- compare relation: ahead 10, behind 0, six changed files;
- exact repaired-head workflow set: queued under runs `30693695533` through `30693695562`;
- independent repaired-head acceptance: pending;
- public upstream contact: unauthorized and not performed.

## Reopening triggers

Reopen the design only if maintainers require live mutation to affect an operation already in progress, request settle-all semantics, identify an equivalent current fix, or request a shared helper after reviewing the narrow patch.
