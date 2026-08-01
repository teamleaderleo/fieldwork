# Deep dive — Unit 11: stabilize lifecycle fanout targets

## Governing invariant

Every supported lifecycle fanout attempts each processor present when the operation begins, preserves its outward failure contract, and releases operation-owned timers after synchronous failure.

## Exact subject

- base/current public main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact candidate: `f4910b355d12895edf25372444f76d4def08901c`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- validation carrier: owned draft PR #19;
- relation: one commit ahead, zero behind;
- boundary: three production files and three target-native tests.

## Call-chain analysis

### `MultiSpanProcessor`

It retains the constructor processor array and directly invokes lifecycle methods while constructing promise inputs. A synchronous throw can stop later calls; an earlier processor can also remove a later processor from the live array.

Repair: shallow-copy the opening array and use an eager try/catch helper. The existing shutdown rejection and force-flush global-error-handler/resolve structure remains.

### Public `TracerProvider.forceFlush()`

The provider bypasses `MultiSpanProcessor.forceFlush()`. It directly maps `_activeSpanProcessor['_spanProcessors']` and creates one timeout-controlled promise per processor.

Two baseline mechanisms matter:

1. live mapping permits removal of a later opening processor;
2. a timeout is armed before invocation. A synchronous throw rejects the Promise executor, bypasses the processor-result catch, and leaves the timeout active until expiry.

Repair: snapshot the opening list and normalize direct throws to rejected promises. The existing per-processor catch then clears the timeout and records the error, preserving the outer error-array rejection.

### `MultiLogRecordProcessor`

`LoggerProvider` delegates lifecycle work to this aggregate, which retains a publicly exposed processor array. Direct throws and live removal are reachable.

Repair: snapshot the array, use eager safe-call, and retain `callWithTimeout()` placement and options.

### Metrics exclusion

Metrics was removed because `MeterProvider` owns its collector list internally, no supported post-construction removal path was found, collector lifecycle methods are already async, and predecessor mutation tests reached private state through casts.

## Reversing controls

- aggregate trace shutdown/force flush: direct throw and live removal;
- provider force flush: direct throw, later invocation, one-error array shape, zero fake-clock timers, and live removal;
- logs shutdown/force flush: direct throw and live removal.

Mutation tests verify that the backing array remains changed, distinguishing stable current membership from permanent freezing.

## Compatibility

- API/types unchanged;
- eager concurrency retained;
- aggregate trace force flush still reports globally and resolves;
- provider force flush retains array-shaped rejection;
- logs retain timeout and rejection behavior;
- future mutation remains visible;
- the provider timeout change only clears work with no owner after synchronous failure.

## Changed files

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics or non-product residue remains. Public main and duplicate searches were refreshed during repair and must be repeated immediately before authorized filing.
