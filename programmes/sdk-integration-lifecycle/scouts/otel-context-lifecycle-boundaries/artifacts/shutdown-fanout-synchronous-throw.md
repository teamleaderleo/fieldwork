# Lifecycle fanout after a synchronous component exception

## In simple words

Shutdown and force-flush operations are supposed to fan out across owned processors, readers, collectors, and signal providers. Several JavaScript SDK aggregates eagerly call child methods while building arrays for `Promise.all`. If one child throws synchronously, array construction stops and later children are never called.

Tracing exposes the sharpest version: a custom trace processor can throw synchronously all the way out of `NodeSDK.shutdown()`, preventing logger- and meter-provider shutdown from even being requested. Logs and metrics use `async` wrappers, so the caller receives a rejected promise, but later processors or readers inside their `.map()` are still skipped. The prepared NodeSDK characterizations now cover both forms.

This is retained as a lower-level cross-signal lead. The characterization source has not been executed in the current environment, so it is not yet promoted to a separate upstream candidate.

## Pinned scope

- repository: `open-telemetry/opentelemetry-js`
- revision: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- packages: `@opentelemetry/sdk-trace`, `@opentelemetry/sdk-logs`, `@opentelemetry/sdk-metrics`, and `@opentelemetry/sdk-node`
- characterization branch: `fieldwork/nodesdk-shutdown-lifecycle-characterization`
- initial trace characterization commit: `c4b8b1ea44563c2ae826ea36f6906c84dfb67642`
- expanded cross-signal characterization commit: `548b8a4b801bbc0a9624323585179de44e44e174`

## Source comparison

### Traces

`MultiSpanProcessor.shutdown()` calls each processor's `shutdown()` while constructing a promise array:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/MultiSpanProcessor.ts#L64-L74

`forceFlush()` uses the same eager invocation pattern:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-trace/src/MultiSpanProcessor.ts#L24-L41

Because these methods are not declared `async`, a synchronous child exception escapes immediately before later processors are invoked and before a promise is returned.

### Logs

`MultiLogRecordProcessor.shutdown()` and `forceFlush()` call child methods inside `.map()` expressions passed to `Promise.all`:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts#L26-L43

These aggregate methods are `async`, so a synchronous child throw becomes a rejected returned promise. However, `.map()` still aborts before later processors are invoked.

The log force-flush path also calls `processor.forceFlush()` before passing the result into `callWithTimeout`, so the timeout wrapper cannot contain a synchronous exception thrown while obtaining the promise.

### Metrics

`MeterProvider.shutdown()` and `forceFlush()` call collectors inside `.map()` expressions passed to `Promise.all`:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/packages/sdk-metrics/src/MeterProvider.ts#L91-L123

The methods are `async`, so synchronous collector exceptions reject the returned promise, but later collectors are not invoked once `.map()` aborts.

The provider sets its own shutdown state before invoking collectors. A failed first collector can therefore leave a later collector uncalled while repeated provider shutdown no longer retries the fanout.

### NodeSDK

`NodeSDK.shutdown()` eagerly invokes providers in trace → logs → metrics order while constructing its own promise array:

https://redirect.github.com/open-telemetry/opentelemetry-js/blob/7b06368b7362a30ca69c178f43bd94dfbb36f85d/experimental/packages/opentelemetry-sdk-node/src/sdk.ts#L365-L381

A synchronous trace-provider exception therefore prevents logger- and meter-provider shutdown calls. Provider methods that return rejected promises do not stop NodeSDK from invoking later providers, but skipped children inside those providers remain skipped.

## Characterization

Test file:

`experimental/packages/opentelemetry-sdk-node/test/lifecycle-shutdown-fanout-characterization.test.ts`

### Case 1 — trace synchronous escape stops later signals

The test configures:

1. a first custom span processor whose first shutdown call throws synchronously;
2. a second span processor that records shutdown calls;
3. a log processor that records shutdown calls.

Source-predicted first-call result:

- the first processor is called once and throws;
- the second span processor is not called;
- the logger processor is not called;
- `NodeSDK.shutdown()` throws synchronously rather than returning a rejected promise.

The test makes the first processor succeed on a second call so remaining components can be cleaned up and the previously skipped calls can be observed.

### Case 2 — log and metric async wrappers still skip later children

The expanded test configures:

1. a first log processor whose `shutdown()` throws synchronously;
2. a second log processor that records shutdown calls;
3. a first metric reader whose `onShutdown()` throws synchronously;
4. a second metric reader that records shutdown calls.

Source-predicted result:

- `NodeSDK.shutdown()` returns a rejected promise rather than throwing before return;
- the first log processor is called once;
- the second log processor is never called;
- the first metric reader is called once;
- the second metric reader is never called;
- repeated SDK shutdown reuses the rejected or terminal provider state and does not reach the skipped children.

This moves the logs/metrics result beyond plain `.map()` inference: the prepared target-native NodeSDK test exercises the actual `LoggerProvider`, `MeterProvider`, and aggregate processor/reader paths.

Direct package-level tests for each aggregate and for force-flush remain to be added.

## Why this matters

A lifecycle fanout coordinator should normally attempt cleanup or flush for every owned component even when one component fails. Skipping later components can leave:

- exporter queues unflushed;
- worker threads or timers active;
- network resources open;
- later signals incompletely shut down;
- readers or processors permanently skipped after their provider becomes terminal;
- failure behavior dependent on whether a child throws before or after returning a promise.

The synchronous-versus-asynchronous distinction is externally visible and surprising:

- an asynchronous rejection generally occurs after all child calls were started;
- a synchronous throw can stop invocation itself;
- trace may throw before returning a promise;
- logs and metrics return rejected promises but still skip later children internally.

JavaScript's `Promise<void>` type does not prevent an implementation from throwing before returning its promise.

## Possible fixes

### Lazy promise wrapping

Wrap every child invocation so synchronous exceptions become rejections without aborting scheduling of later calls:

```ts
const promises = children.map(child =>
  Promise.resolve().then(() => child.shutdown())
);
return Promise.all(promises).then(() => {});
```

The same structure can wrap force-flush calls and timeout helpers.

### Error aggregation policy

`Promise.all` preserves fail-fast rejection after all callbacks have been scheduled. `Promise.allSettled` could retain every failure, but choosing which error or aggregate to expose is a separate API decision.

### Shared internal utility

Because trace, logs, metrics, and NodeSDK have related fanout surfaces, a shared core helper could normalize:

- synchronous throws;
- promise rejections;
- timeout wrapping;
- attempt-all semantics;
- aggregate error reporting.

A shared utility reduces repeated subtle differences, but it may create a broader review unit than small per-package patches.

## Relationship to existing candidates

This is adjacent to the promoted trace-provider shutdown-contract candidate, which currently focuses on one-shot shutdown and post-shutdown no-op behavior.

Do not automatically expand that issue draft. First decide whether the review unit should be:

- one broader trace shutdown-contract issue;
- a narrow `MultiSpanProcessor` fanout issue and PR;
- equivalent per-signal patches;
- a NodeSDK aggregate-shutdown robustness issue;
- or a shared cross-signal lifecycle fanout utility and contract.

The new logs/metrics characterization strengthens the cross-signal case, but the preferred error policy and package boundary still require a decision.

## Prior-art search

A targeted search of open and closed `opentelemetry-js` issues for synchronous shutdown exceptions and skipped later processors did not return a direct match at the recorded check.

This negative search result is not proof that no related issue exists.

## Validation boundary

The NodeSDK test source is present in the fork, but dependencies are unavailable in the current work environment and no passing CI run is claimed.

Local command:

```bash
npm ci
npm run compile
npm test --workspace=@opentelemetry/sdk-node -- --grep "NodeSDK shutdown fanout characterization"
```

Additional direct package tests should cover:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`;
- `MeterProvider.shutdown()` and `forceFlush()` with multiple collectors;
- error selection when several children fail;
- NodeSDK provider fanout after a synchronous trace failure.

## Evidence class

- source comparison: `source-read`;
- NodeSDK characterizations: `target-test-prepared`;
- target execution: not retained.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or direct backlink was created.
