# Fork trial: attempt every signal lifecycle child

## In simple words

Trace, logs, and metrics all call shutdown or force-flush children while constructing `Promise.all` input. A synchronous first-child exception stops iteration, so later processors or readers are never called.

The owned fork trial wraps each synchronous child invocation in a local `try`/`catch`, converts a throw into a rejected promise, and continues invoking every later child. It preserves each package's existing outward error policy and synchronous invocation timing.

## Status

- owned fork PR: https://redirect.github.com/teamleaderleo/opentelemetry-js/pull/6
- branch: `fieldwork/lifecycle-fanout-attempt-all`
- base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- exact head: `3f04b3de2e07e321d01abc86c38ca7ebe5966fc3`
- packages:
  - `@opentelemetry/sdk-trace`
  - `@opentelemetry/sdk-logs`
  - `@opentelemetry/sdk-metrics`
- work class: upstream-fork research
- evidence class: `target-test-prepared`
- upstream issue or PR opened: `false`

## Current failure mechanism

Affected code eagerly invokes a child inside a loop or `.map()` callback:

```ts
await Promise.all(children.map(child => child.shutdown()));
```

If `child.shutdown()` throws before returning a promise:

1. array construction stops;
2. later children are not invoked;
3. outward behavior depends on whether the aggregate method is itself `async`;
4. cleanup or flush coverage depends on whether a child failed synchronously or asynchronously.

The same public `Promise<void>` shape therefore produces different invocation behavior depending on implementation timing.

## Trial implementation

Each affected package uses a local synchronous safe-call wrapper:

```ts
function callLifecycle(callback: () => Promise<void>): Promise<void> {
  try {
    return callback();
  } catch (error) {
    return Promise.reject(error);
  }
}
```

Then every callback is invoked synchronously and independently:

```ts
await Promise.all(
  children.map(child => callLifecycle(() => child.shutdown()))
);
```

Properties:

- child invocation remains synchronous;
- every child is attempted;
- a synchronous throw becomes a rejected promise;
- `Promise.all` retains its existing fail-fast result policy;
- later asynchronous failures are observed by `Promise.all` rather than becoming unhandled;
- the patch does not require a new exported core utility.

## Why microtask deferral was rejected

The first trial used:

```ts
Promise.resolve().then(() => child.forceFlush())
```

That attempts every child, but moves child invocation into a later microtask. Existing trace tests expect `forceFlush()` to call processors synchronously before the aggregate method returns its promise.

The trial was repaired to preserve that timing contract. The safe-call wrapper catches each exception without delaying invocation.

## Package behavior retained

### Trace

`MultiSpanProcessor.shutdown()`:

- now always returns a promise;
- attempts every processor;
- rejects on failure.

`MultiSpanProcessor.forceFlush()`:

- attempts every processor;
- reports failure through the existing global error handler;
- resolves, preserving current outward behavior.

### Logs

`MultiLogRecordProcessor.shutdown()` and `forceFlush()`:

- attempt every processor;
- return rejected promises on failure, preserving existing outward behavior.

The force-flush timeout wrapper remains per processor.

### Metrics

`MeterProvider.shutdown()` and `forceFlush()`:

- attempt every registered collector/reader;
- return rejected promises on failure, preserving existing outward behavior.

Provider terminal-state and concurrency behavior are not changed by this trial.

## NodeSDK conclusion

No separate NodeSDK production change is included.

The NodeSDK skipped-signal case begins with trace provider shutdown throwing synchronously before NodeSDK can request logs or metrics shutdown. Once trace shutdown is normalized into a returned rejected promise, NodeSDK finishes constructing its provider promise list before rejection is observed.

Two separate trace directions can provide that normalization:

- this `MultiSpanProcessor` fanout repair;
- the trace provider one-shot trial, whose `BindOnceFuture` catches synchronous processor throws.

A NodeSDK wrapper would be defensive, but it is not required to repair the demonstrated path if the owning trace layer is corrected.

## Prepared tests

### Trace

`packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`

- synchronous first-processor shutdown failure still invokes the later processor and rejects;
- synchronous first-processor force-flush failure still invokes the later processor, reports through the global error handler, and resolves.

### Logs

`experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

- shutdown and force flush invoke the later processor and reject with the first failure.

### Metrics

`packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`

- shutdown and force flush invoke the later reader and reject with the first failure.

## Error policy not changed

The trial does not aggregate every failure.

`Promise.all` still exposes the first observed rejection. Every child is attempted, but callers may not receive a complete list of failures.

A future all-errors contract would require a separate decision around:

- `AggregateError` compatibility;
- stable failure ordering;
- timeout plus rejection combinations;
- diagnostic reporting for secondary errors;
- whether shutdown and force flush should share one policy.

## Review-unit choices

The common mechanism supports several upstream decompositions:

1. one cross-signal issue and three package PRs;
2. one trace/log processor PR plus one metrics provider PR;
3. one monorepo PR because the invariant and patch are identical;
4. a later shared core utility after the behavior lands locally.

The owned combined PR is a feasibility packet. It is not evidence that one broad upstream PR is the best review unit.

## Separate lifecycle work

This trial does not repair:

- trace provider one-shot state;
- metric provider and reader shutdown concurrency;
- reader constructor binding transactionality;
- NodeSDK shutdown/start interleaving;
- global registration ownership or disposal;
- asynchronous lifecycle recursion or promise cycles.

## Exact diff review

The initial microtask implementation was rejected during self-review because it changed synchronous force-flush timing.

The current production changes are limited to:

- local `callLifecycle()` wrappers;
- replacing eager unguarded child calls with guarded synchronous calls;
- simplifying trace promise plumbing without changing its outward result policy.

## Validation

```bash
npm ci --ignore-scripts
npm run compile
npm test --workspace=@opentelemetry/sdk-trace
npm test --workspace=@opentelemetry/sdk-logs
npm test --workspace=@opentelemetry/sdk-metrics
```

No target execution receipt or passing suite is claimed.

Current disposition: `EXECUTE`, then decide the upstream review split.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
