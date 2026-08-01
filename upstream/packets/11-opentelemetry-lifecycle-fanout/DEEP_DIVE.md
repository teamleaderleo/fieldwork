# Deep dive — Unit 11: snapshot lifecycle targets before concurrent fanout

## In simple words

Trace, logs, and metrics all build lifecycle fanout from mutable child arrays. If an earlier child removes a later array entry, live indexed iteration can skip a child that belonged to the operation when it began.

Trace and logs also invoke user-controlled lifecycle methods directly while constructing the promise list. A synchronous throw there can stop construction before later processors are invoked. Metrics is different: `MetricCollector` lifecycle methods are already async wrappers, so synchronous reader throws already become rejected promises before control returns to `MeterProvider`.

The correct bounded direction is therefore:

- trace and logs: opening snapshot plus synchronous safe-call;
- metrics: opening snapshot only.

## Governing invariant

> A lifecycle aggregate attempts every child in its opening membership set while preserving package-specific outward failure behavior and future membership mutation.

## Reviewed source boundary

- Public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Candidate head: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Trace entrypoints: `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- Logs entrypoints: `MultiLogRecordProcessor.shutdown()` and `forceFlush()`;
- Metrics entrypoints: `MeterProvider.shutdown()` and `forceFlush()`;
- Metrics async boundary: `MetricCollector.shutdown()` and `forceFlush()`.

## Failure models

### Live-array mutation — all three packages

1. The aggregate begins mapping the mutable child array.
2. The first child removes a later indexed child from that same backing array.
3. Array iteration reaches the shortened array and skips the removed opening child.
4. That child receives no lifecycle call for the current operation.

A shallow copy before the first invocation fixes this while leaving the original collection mutable for future operations.

### Synchronous throw — trace and logs

1. The aggregate directly invokes a child while constructing `Promise.all` inputs.
2. The child throws before returning a promise.
3. Mapping aborts immediately.
4. Later opening processors are never invoked.

A small safe-call helper converts the throw into a rejected promise, allowing mapping to finish before `Promise.all` applies the existing package-specific error policy.

### Synchronous throw — metrics baseline already safe

`MeterProvider` calls `MetricCollector.shutdown()` or `forceFlush()`. Those methods are async and await the underlying reader. If the reader throws synchronously, the async method returns a rejected promise rather than throwing through the `MeterProvider` map. Later collectors are therefore already invoked on the baseline.

This means the metrics-local `callLifecycle()` helper in the reviewed candidate is redundant. The metrics production repair should retain only the snapshot.

## Package-specific result model

| Package | Current outward policy | Required implementation |
| --- | --- | --- |
| trace shutdown | reject | snapshot + safe-call + `Promise.all` |
| trace force flush | report one failure through `globalErrorHandler`, then resolve | snapshot + safe-call + existing handler path |
| logs shutdown/force flush | reject | snapshot + safe-call + existing timeout behavior |
| metrics shutdown/force flush | reject | snapshot; existing async collector boundary already normalizes reader throws |

## Exact-head execution

All current repository workflow groups passed at candidate head `641528c9786f7d027fef4f4a76ae685f7107d394`:

- Unit `30674494793`;
- E2E `30674494785`;
- Lint `30674494830`;
- Bundler `30674494832`;
- W3C `30674494799`;
- API peer dependency `30674494801`;
- CodeQL `30674494779`;
- Zizmor `30674494823`.

The pass proves the current candidate executes successfully, not that every line is necessary. Complete-diff review is what exposed the redundant metrics helper.

## Tests and evidence classification

- Trace/logs synchronous-throw controls: reversing regressions.
- Trace/logs/metrics live-removal controls: reversing regressions.
- Metrics synchronous-throw controls: baseline compatibility controls; they should not be used to claim a metrics source defect.
- Trace force-flush global-handler control: compatibility control.

## Selected repair

1. Keep the trace and logs source and focused tests as currently designed.
2. In `MeterProvider.ts`, keep `.slice()` for shutdown and force flush.
3. Remove the metrics-local safe-call helper and map directly to the async collector lifecycle methods.
4. Keep the metrics mutation tests.
5. Reclassify or remove metrics throw tests.
6. Rerun the complete exact-head workflow set and obtain independent review.

## Compatibility analysis

- Public API: unchanged.
- Future membership mutation: preserved because only the current opening array is copied.
- Concurrency: eager `Promise.all` fanout remains.
- Error model: unchanged per package.
- Allocation: one shallow array allocation per affected lifecycle operation.
- Generated output and dependencies: none.
- Changelog: required packaging remains pending a real authorized PR number.

## Claim boundary

Established:

- live removal can skip a later opening child in all three packages;
- synchronous direct invocation can stop later opening processors in trace and logs;
- metrics already normalizes reader synchronous throws through its async collector boundary;
- the candidate exact head passes all named repository workflow groups.

Not established:

- production frequency or ecosystem impact;
- settle-all completion or aggregate diagnostics;
- idempotent or retry-safe child shutdown;
- delayed lifecycle recursion, final metrics collection, or provider one-shot state;
- extreme child-count allocation cost.

## Adjacent work excluded

Provider/reader one-shot shutdown state, final metrics collection, delayed same-owner recursion, spans ending after shutdown begins, process-global disposal, and aggregation of every asynchronous child failure remain separate units.
