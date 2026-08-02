# Upstream issue draft — processor lifecycle fanout can stop early

Draft status: `fallback only — a focused pull request is likely sufficient`  
Public interaction authorized: `no`

## What happened?

### Steps to reproduce

Configure two custom span or log processors. Make the first processor throw synchronously from `shutdown()` or `forceFlush()` before returning its declared promise. Then call the corresponding aggregate lifecycle method.

On the current implementation:

- `MultiSpanProcessor` and `MultiLogRecordProcessor` stop constructing their promise lists at the synchronous throw, so the later processor is not invoked;
- a processor that synchronously removes a later entry from the retained processor array can also make the live iteration skip that opening processor;
- public `TracerProvider.forceFlush()` does attempt later processors after a synchronous throw because the call happens inside a Promise constructor, but the throwing processor's timeout remains armed until it expires;
- public `TracerProvider.forceFlush()` can still skip a later opening processor when an earlier processor mutates the live array during invocation.

### Expected result

Every processor registered when `shutdown()` or `forceFlush()` begins is invoked once for that operation. Synchronous implementation errors are reported through the existing asynchronous failure path, and no obsolete timeout remains armed after a processor has already failed.

### Actual result

Depending on the entrypoint, a synchronous processor failure or mutation can skip a later processor from the operation's opening set. The public trace provider can also retain its per-processor timeout after it has already rejected for a synchronous failure.

## Why this matters

The trace and logs SDK specifications require provider shutdown and force flush to invoke the operation on all registered processors. A skipped processor may therefore miss its final export or cleanup opportunity.

The affected boundary is mainly custom or third-party processors and code that retains and mutates the configured processor array; ordinary built-in processors normally return promises as declared. This is a correctness and shutdown-reliability issue, not evidence of widespread telemetry loss.

In Node.js, the provider's default 30-second timeout is a referenced timer. If a custom processor throws synchronously and the application does not call `process.exit()`, the stale timer can delay natural process termination until it expires.

## OpenTelemetry setup code

```ts
const processors: SpanProcessor[] = [];

const first: SpanProcessor = {
  onStart() {},
  onEnd() {},
  shutdown: () => Promise.resolve(),
  forceFlush: () => {
    throw new Error('synchronous processor failure');
  },
};

const second: SpanProcessor = {
  onStart() {},
  onEnd() {},
  shutdown: () => Promise.resolve(),
  forceFlush: () => {
    console.log('second processor flushed');
    return Promise.resolve();
  },
};

processors.push(first, second);
await new TracerProvider({ spanProcessors: processors }).forceFlush();
```

Equivalent custom `LogRecordProcessor` implementations reproduce the aggregate logs behavior.

## Proposed direction

- take a shallow snapshot of the processor array at the beginning of each repaired lifecycle operation;
- invoke each processor eagerly, while converting a direct synchronous throw into a rejected promise;
- route public trace-provider synchronous failures through its existing timeout cleanup and error-array result handling;
- preserve all existing outward error policies and genuine timeout behavior.

Affected entrypoints:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`;
- `TracerProvider.forceFlush()`.

Metrics is intentionally excluded. Metric collector lifecycle methods are already `async`, the provider owns its collector list internally, and no supported post-construction mutation route was established.

## Compatibility and limits

- no public API, type, configuration, or telemetry hot-path change;
- one shallow array copy per repaired lifecycle call;
- processors are still invoked eagerly and in their existing order;
- mutations remain visible to later lifecycle calls, but not to the operation already in progress;
- aggregate trace shutdown still rejects;
- aggregate trace force flush still reports through the global error handler and resolves;
- logs still reject;
- public trace-provider force flush still rejects with an error array;
- genuine pending operations still time out;
- this does not add `Promise.allSettled`, retries, cancellation, idempotence, or multi-error aggregation.

## Environment and duplicate check

- reproduced against `open-telemetry/opentelemetry-js` revision `2c931bf4eec18a234a28706567c6977f08139abd`;
- Node.js model check: v22.16.0;
- issue, pull-request, and commit searches found no equivalent current repair at the time of drafting;
- older force-flush work changes propagation or provider structure but does not repair this opening-set and synchronous-failure behavior.

## Filing checklist

- [ ] repeat current-main and duplicate searches immediately before filing;
- [ ] confirm the reproduction against the then-current public revision;
- [x] match the repository bug-report structure;
- [x] distinguish aggregate skipping from the provider timer-cleanup defect;
- [x] exclude unsupported metrics-private-state claims;
- [x] avoid unsupported prevalence or severity claims;
- [ ] record explicit authority before public interaction.
