# Approaches — Unit 11: invoke all lifecycle processors

## Selected boundary

- `MultiSpanProcessor`: opening snapshot plus eager synchronous-throw normalization;
- `TracerProvider.forceFlush()`: opening snapshot plus synchronous-throw normalization inside the existing timeout/result structure;
- `MultiLogRecordProcessor`: opening snapshot plus eager synchronous-throw normalization while preserving `callWithTimeout`;
- metrics: excluded after supported-reachability review.

All retained paths preserve eager invocation, existing outward error behavior, and visibility of membership changes to future operations.

## Why trace has two force-flush sites

Public `TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly fans out over the processor list.

The two sites have related but not identical defects:

- aggregate `MultiSpanProcessor.forceFlush()` can stop before invoking later processors when a processor throws directly;
- public provider force flush invokes inside a Promise executor, so that throw becomes a rejection and later `.map()` callbacks already run;
- the provider rejection bypasses its existing `.catch()` and therefore leaves the per-processor timeout armed;
- both sites can skip a later opening processor when an earlier processor synchronously removes it from the live array.

Repairing only the aggregate would therefore leave the public timer-cleanup and mutation defects.

## Why the call helper is eager

A tempting normalization is:

```ts
Promise.resolve().then(() => processor.forceFlush())
```

That defers invocation to a microtask. Existing package tests assert that processors are invoked before the aggregate lifecycle method returns, and changing that ordering could affect shutdown coordination.

The selected helper calls immediately inside `try/catch` and returns `Promise.reject(error)` only for a direct synchronous throw. Normal promise resolution/rejection behavior is unchanged.

## Why snapshot the operation instead of the constructor

Copying the configured array permanently in the constructor would prevent later caller mutation from ever reaching the provider. That is a larger and less clearly compatible change.

Taking a shallow copy at lifecycle-operation start gives the current operation a stable registered set while allowing later operations to observe subsequent changes. It also avoids freezing processor objects or changing their identity.

## One PR or two

Selected draft: one pull request covering sdk-trace and sdk-logs.

Reasons:

- the specification invariant is the same: invoke every registered lifecycle processor;
- the failure mechanism and repair pattern are the same in the aggregate implementations;
- the complete source boundary is three small production files;
- tests and compatibility claims can be reviewed as one coherent lifecycle behavior change.

Reasons maintainers might prefer a split:

- sdk-trace is stable while sdk-logs is released through the experimental changelog;
- different package owners may review the two areas;
- public `TracerProvider.forceFlush()` has provider-specific timeout behavior beyond the shared aggregate mechanism.

The draft should accept a maintainer request to split without creating a second independent finding. If split, the trace PR would include `MultiSpanProcessor` plus `TracerProvider`, and the logs PR would include `MultiLogRecordProcessor`.

## Rejected alternatives

- **Safe-call over live arrays:** still permits removal-based skipping.
- **Microtask deferral:** changes eager start ordering.
- **Constructor-only copying or freezing:** changes future membership behavior.
- **Sequential awaiting:** changes concurrency and latency.
- **`Promise.allSettled`:** changes completion timing, rejection behavior, and potentially error types.
- **Aggregate-only trace repair:** misses the public provider path.
- **Provider-only trace repair:** leaves aggregate shutdown and internal force-flush behavior inconsistent with the specification.
- **Metrics snapshot hardening:** changes private state without a supported reachable defect.
- **Runtime validation of non-Promise returns:** broadens the patch from type-valid synchronous throws to malformed JavaScript implementations.
- **Shared cross-package utility:** adds an abstraction and dependency surface for three small local call sites.

## Edge-case decisions

- Processors added after an operation starts do not join that operation.
- Processors removed after an operation starts still receive that operation's lifecycle call.
- Processor object mutation is not isolated; only list membership is snapshotted.
- Asynchronous failures retain existing fail-fast `Promise.all` behavior.
- A pending provider processor still times out.
- A synchronous provider failure clears only the timer created for that processor.
- Synchronous telemetry hooks (`onStart`, `onEnd`, `onEmit`) are outside scope because this contribution concerns asynchronous lifecycle contracts.

## Decision history

1. Safe-call-only generation passed gates but review found removal-based skipping.
2. Snapshot fixtures initially had test-only type inference failures and were repaired.
3. A predecessor candidate passed the ordinary workflow groups.
4. Review exposed that metrics tests relied on private collector-state mutation.
5. Deeper source review removed metrics and found the separate public provider fanout.
6. Provider coverage was added for opening membership, error-array compatibility, timer cleanup, and genuine timeout preservation.
7. The first revised head passed all workflows except Prettier lint; formatting was repaired on the current head.

## Current state

- public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source head: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- relation: ahead 4, behind 0;
- boundary: three production files and three tests;
- validation PR: #19;
- current workflows: `30755343685`, `30755343692`, `30755343693`, `30755343695`, `30755343697`, `30755343702`, `30755343708`, `30755343888`;
- public upstream contact: unauthorized and not performed.

The branch remains unsquashed until current-head validation and any final source repair are complete.
