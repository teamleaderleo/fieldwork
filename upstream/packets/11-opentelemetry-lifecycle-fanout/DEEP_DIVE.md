# Deep dive — Unit 11: stabilize lifecycle fanout targets

## Governing invariant

Every supported lifecycle fanout attempts each processor present when the operation begins, preserves its existing outward failure contract, and releases operation-owned timers after synchronous failure.

## Exact subject

- upstream base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical candidate: `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- validation carrier: owned draft PR #19;
- changed-file fence: three production files and three target-native tests.

## Call-chain analysis

### `MultiSpanProcessor`

It retains the constructor processor array and directly invokes processor lifecycle methods while constructing promise inputs. A processor can throw before returning its declared promise, stopping later calls. It can also remove a later processor from the retained live array.

Repair: snapshot the opening array and use an eager local try/catch helper. The original shutdown rejection and force-flush global-error-handler/resolve structure remains.

### Public `TracerProvider.forceFlush()`

The public provider does not delegate to `MultiSpanProcessor.forceFlush()`. It directly reads `_activeSpanProcessor['_spanProcessors']` and creates one timeout-controlled promise per processor.

Two baseline mechanisms matter:

1. live-array mapping permits an earlier processor to remove a later opening processor;
2. the timeout is armed before invocation. A synchronous throw rejects the Promise executor, bypasses the processor-result catch, and leaves that timeout armed until expiry.

Repair:

- snapshot the opening processor list;
- invoke through an eager safe-call;
- retain the existing timeout and aggregate error-array model;
- let the existing per-processor catch clear the timeout and record the error.

### `MultiLogRecordProcessor`

`LoggerProvider` delegates lifecycle operations to this aggregate. Its configured processor array is retained and publicly exposed. Direct throws and live removal are both reachable.

Repair: snapshot the array, use eager safe-call, and preserve `callWithTimeout()` placement and timeout options.

### Metrics exclusion

Metrics was removed after deeper source review:

- `MeterProvider` constructs an internal collector list and does not retain the caller's readers array;
- no supported post-construction collector-removal path was found;
- `MetricCollector.shutdown()` and `forceFlush()` are async, so reader synchronous throws already become rejections;
- predecessor mutation tests reached private provider state through casts.

That evidence supports excluding metrics rather than upstreaming speculative private-state hardening.

## Eager helper rationale

A direct try/catch preserves synchronous start order. Deferring through `Promise.resolve().then(...)` would alter invocation timing.

## Reversing controls

- aggregate trace shutdown and force flush: direct throw and live removal;
- public provider force flush: live removal, direct throw, later invocation, existing one-error array shape, and zero remaining fake timers;
- logs shutdown and force flush: direct throw and live removal.

Mutation tests assert that the backing array remains changed, distinguishing stable current membership from permanent freezing.

## Compatibility

- API and exported types unchanged;
- eager concurrency retained;
- aggregate trace force flush still reports globally and resolves;
- provider force flush retains its array-shaped rejection;
- logs retain timeout and rejection behavior;
- future mutation remains visible;
- the only timeout change is clearing work that has no owner after synchronous failure.

## Changed files

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Limits and staleness

This unit does not add settle-all diagnostics, cancellation, retry, child idempotence, delayed recursion, or post-shutdown admission changes. Public main remained at the pinned base and duplicate searches found no equivalent open work during the repair pass; repeat both checks immediately before authorized filing.
