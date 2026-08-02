# Deep dive — Unit 11: invoke all lifecycle processors

## Governing invariant

Every lifecycle fanout invokes each processor registered when the operation begins, preserves the package's outward failure contract, and releases operation-owned timers after a processor has already failed.

This follows the OpenTelemetry trace and logs provider requirements for shutdown and force flush to invoke all registered processors.

## Exact subject

- current public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- current candidate: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- validation carrier: owned draft PR #19;
- relation: four commits ahead, zero behind;
- boundary: three production files and three target-native tests.

Final packaging will squash the branch after current validation.

## Importance and relevance

### Why it is real

The public processor interfaces allow custom implementations. A method declared to return `Promise<void>` may still throw before it returns that promise; TypeScript accepts a throwing path because it never returns. The aggregate implementations currently assume invocation itself cannot throw.

The retained array behavior is also observable. `TracerProvider` passes the caller's configured array into `MultiSpanProcessor`, and `MultiLogRecordProcessor.processors` is publicly exposed as a readonly reference to a mutable array. Synchronous processor code can therefore change list membership while fanout is still walking it.

### Why it is not a crisis

Built-in processors normally return promises as declared and do not mutate their owning aggregate. No evidence establishes widespread production impact or common data loss.

The strongest supported consequence is bounded lifecycle correctness:

- a later custom processor may miss final export or cleanup;
- a public trace-provider timer may remain referenced after outward failure;
- natural Node.js termination may be delayed until that timeout expires.

This supports a normal bugfix priority, not a security advisory or emergency release.

## Call-chain analysis

### `MultiSpanProcessor`

The constructor retains its processor array. `shutdown()` and `forceFlush()` directly invoke lifecycle methods while building `Promise.all` inputs.

Baseline behavior:

- a direct throw exits the method before a promise is returned and before later processors are invoked;
- synchronous removal shortens live iteration and can skip a later opening processor.

Repair:

- shallow-copy the opening array;
- invoke each processor immediately inside a local try/catch helper;
- turn only the direct throw into `Promise.reject(error)`;
- retain the existing shutdown rejection and force-flush global-error-handler/resolve structures.

### Public `TracerProvider.forceFlush()`

The provider bypasses `MultiSpanProcessor.forceFlush()`. It maps `_activeSpanProcessor['_spanProcessors']` and creates one timeout-controlled promise per processor.

Baseline behavior has two distinct mechanisms:

1. live `.map()` can skip a later index removed synchronously by an earlier callback;
2. the processor call occurs inside a Promise executor, so a direct throw rejects that per-processor promise and later `.map()` callbacks still execute. However, the throw bypasses the explicit `.catch()` that clears `timeoutInterval`, leaving the timeout active until expiry.

Repair:

- map an opening snapshot;
- normalize the direct throw to a rejected promise before chaining the existing `.catch()`;
- allow that existing catch to clear the timer and resolve the per-processor result with the error;
- preserve the outer array-shaped rejection.

A compatibility control proves that a processor that genuinely never settles still reaches the configured timeout.

### `MultiLogRecordProcessor`

`LoggerProvider` delegates shutdown and force flush to this aggregate. It retains a publicly visible processor array.

Baseline behavior:

- direct throw during `.map()` stops later callback construction;
- synchronous removal can make `.map()` skip a later opening index.

Repair:

- snapshot the opening array;
- preserve immediate invocation;
- wrap invocation and existing `callWithTimeout()` setup in the direct-throw helper;
- retain rejection and timeout behavior for returned promises.

### Metrics exclusion

Metrics was removed because:

- `MetricCollector.shutdown()` and `forceFlush()` are async and already normalize reader throws into rejections;
- `MeterProvider` constructs and owns the collector list internally;
- no supported post-construction collector mutation route was found;
- predecessor tests reached private state through casts.

Hardening unreachable private state would weaken the upstream case and blur the supported contract.

## JavaScript control-flow model

A dependency-free Node.js v22.16.0 model reproduced the key language behavior:

- a direct loop stopped at the first synchronous throw and left the later child uncalled;
- the same throw inside a Promise executor became a rejection and did not stop later `.map()` callbacks;
- without explicit cleanup, the provider-style timer still fired;
- with a handled outward failure and a 200 ms referenced timer, process lifetime was approximately 0.22 seconds.

The model validates mechanism and consequence. It does not establish how often applications supply such processors.

## Reversing and compatibility controls

### Aggregate trace

- shutdown direct throw;
- shutdown live removal;
- force-flush direct throw with global reporting;
- force-flush live removal.

### Public provider

- synchronous failure retains one-error-array rejection and clears all timers;
- live removal does not shrink the opening set;
- genuinely pending work still times out.

### Logs

- shutdown direct throw and live removal;
- force-flush direct throw and live removal;
- existing timeout test suite remains applicable.

Mutation tests also verify that the backing array remains changed, distinguishing stable current-operation membership from permanent freezing.

## Compatibility and ramifications

- no API, type, configuration, or generated-output change;
- no change to normal span/log creation or delivery;
- one O(n) shallow copy per lifecycle call;
- eager invocation order retained;
- fail-fast `Promise.all` timing retained;
- later operations observe later membership changes;
- code that intentionally removed a processor during the same operation to suppress its lifecycle call will behave differently, but that behavior is undocumented and conflicts with the all-registered-processor requirement;
- pending promises, rejection shapes, global reporting, and real timeouts retain existing behavior.

## Explicit non-goals

- type-invalid non-Promise return values;
- `Promise.allSettled` or multi-error aggregation;
- waiting for every asynchronous child after fail-fast rejection;
- retries, cancellation, reentrancy, or idempotence;
- synchronous hooks such as `onStart`, `onEnd`, and `onEmit`;
- broader lifecycle refactoring or a shared cross-package utility.

## Changed files

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics or non-product residue remains. Current-main and duplicate searches were refreshed during this pass and must be repeated immediately before authorized filing.
