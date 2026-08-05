# Deep dive — Unit 11: stabilize lifecycle fanout targets

## In simple words

The bug is a lifecycle fanout membership problem, not a general promise-concurrency problem. The repair snapshots the processors present when shutdown or force flush begins, preserves eager invocation and existing error contracts, and limits the patch to trace and logs paths that have supported mutable processor membership.

## Governing invariant

A supported lifecycle fanout attempts every processor present when the operation begins, while preserving its existing failure policy and allowing processor-array mutations to affect later operations.

## Exact subject

- refreshed public-main base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact prepared candidate: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- changed-file fence: three production files and three tests;
- relation: one commit ahead, zero behind;
- current source preview: `teamleaderleo/opentelemetry-js#19`.

The earlier accepted head `db3d9e5e43d5abc6622784acf0ef87f3b038ac91` demonstrated the mechanism on the previous base. The current prepared head is a fresh squash-built commit that retains current-main changes and requires its own exact-head execution receipts.

## Current-main delta

Public `main` advanced by three commits after the earlier base was pinned. Most changes were dependency/workflow maintenance. The material source overlap was merged PR #6929:

- `TracerProvider.forceFlush()` now accepts `ForceFlushOptions`;
- a per-call `timeoutMillis` overrides the deprecated constructor timeout;
- new upstream tests cover the per-call and fallback timeout behavior.

The rebase preserves that public signature and timeout selection. The provider tests now use `forceFlush({ timeoutMillis: 1000 })` instead of adding new use of the deprecated constructor setting.

Current main also contains an unrelated `MultiSpanProcessor.onEnding()` forwarder. The candidate leaves that hot-path behavior unchanged.

## Call-chain analysis

### `MultiSpanProcessor`

The constructor retains the caller-supplied processor array. Shutdown and force flush directly invoked processor methods while building promise inputs. A processor could synchronously throw before returning its declared promise, stopping later invocation. A processor could also mutate the retained array and remove a later opening processor.

Repair: snapshot the array and invoke each processor through an eager `try`/`catch` helper. Existing shutdown rejection and force-flush global-error-handler/resolve behavior remain.

Normal span processing is untouched: `onStart`, `onEnding`, and `onEnd` continue to use the retained live list exactly as current main does.

### Public `TracerProvider.forceFlush()`

This method does not delegate to `MultiSpanProcessor.forceFlush()`. It directly reads the aggregate's processor list and builds timeout-controlled per-processor promises.

Baseline issues:

1. mapping the live array let an earlier processor remove a later opening processor;
2. the timeout was armed before invocation; a synchronous throw bypassed normal promise cleanup and left the timer pending.

Repair:

- resolve the current timeout from the per-call option or constructor fallback;
- snapshot the processor list before mapping;
- use the eager helper so synchronous throws become rejected promises;
- retain the existing `.catch()` path, which clears the timeout and resolves the per-processor result with the error;
- retain the provider's outer error-array rejection contract.

The negative control verifies that a genuinely pending processor still reaches the timeout path under the new per-call API.

### `MultiLogRecordProcessor`

`LoggerProvider` delegates lifecycle work to this aggregate, which retains the configured processor array as a public member. Direct processor calls could throw synchronously or mutate the live array. Snapshot plus eager safe-call is required; the existing per-call force-flush timeout option and timeout wrapping remain unchanged.

### Why metrics is excluded

`MeterProvider` creates a new internal `MetricCollector` for each supplied reader and owns the collector list. It does not retain the caller's readers array. The prior mutation tests accessed private provider state to splice that list, so they did not establish a supported public runtime path.

Additionally, `MetricCollector.shutdown()` and `forceFlush()` are async, so reader synchronous throws already become rejected promises. Symmetry with trace and logs is not enough to justify production changes.

## Eager helper rationale

A local `try`/`catch` preserves synchronous start order. `Promise.resolve().then(callback)` would catch throws but defer invocation to a microtask.

The helper does not suppress failures. It only converts a direct throw into the rejected-promise representation expected by the existing promise-based lifecycle aggregation.

## Test-harness controls

- aggregate trace tests restore `loggingErrorHandler()` after each test to avoid global-state leakage;
- provider tests restore Sinon state after each test;
- timer tests verify zero armed timers after synchronous failure and after genuine timeout;
- mutation tests verify the backing processor array really changed while the opening snapshot still completed.

## Reversing controls

- trace aggregate shutdown/force flush: synchronous throw and live removal;
- trace provider force flush: live removal, later invocation after synchronous throw, existing one-error-array rejection, zero remaining fake timers, and retained genuine-timeout behavior;
- logs shutdown/force flush: synchronous throw and live removal.

Mutation controls also verify the backing processor array remains mutated, distinguishing stable current membership from permanent freezing.

## Compatibility

- no new public API or type change;
- current-main `ForceFlushOptions` is retained;
- eager fanout retained;
- aggregate trace shutdown rejects;
- aggregate trace force flush reports globally and resolves;
- provider trace force flush retains collected-error rejection;
- logs retain rejection and timeout behavior;
- future mutation remains visible;
- one shallow copy per affected lifecycle entrypoint;
- no normal telemetry hot-path change.

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

Current main, issue/PR overlap, contribution guidance, changelog format, and pull-request template were refreshed on `2026-08-05`. No equivalent current repair was found. Reconfirm these immediately before any authorized public filing because the repository may move again.
