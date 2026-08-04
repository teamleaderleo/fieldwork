# Approaches — Unit 11: stabilize lifecycle fanout targets

## In simple words

The selected repair is deliberately narrow: snapshot supported mutable processor fanouts and convert direct synchronous throws without changing concurrency, ordering, or error contracts. Metrics is excluded because the earlier path depended on private state rather than a supported runtime mutation boundary.

## Selected boundary

Repair supported mutable processor fanouts only:

- `MultiSpanProcessor`: opening snapshot plus eager synchronous safe-call;
- public `TracerProvider.forceFlush()`: opening snapshot plus synchronous-error normalization through the existing timeout/error path;
- `MultiLogRecordProcessor`: opening snapshot plus eager synchronous safe-call.

Metrics is excluded. `MeterProvider` constructs its collector list internally and does not retain the caller's reader array; the prior mutation tests reached private state only. `MetricCollector` lifecycle methods are already async.

## Why trace has two force-flush sites

`TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly maps the aggregate's processor list. Repairing only the multi-processor leaves the public provider path exposed to live removal.

The provider also arms a timeout before processor invocation. A synchronous throw bypasses timeout cleanup. The selected helper converts it to a rejected promise so the existing `.catch()` clears the timer and records the error without changing the provider's error-array contract.

Upstream PR #6929 subsequently added a per-call timeout option to this same method. The current preparation keeps that API intact and resolves the timeout before snapshotting and invoking processors.

## Package decisions

### Trace aggregate

- snapshot `_spanProcessors`;
- protect direct lifecycle calls with an eager local `try`/`catch` helper;
- preserve shutdown rejection and force-flush global-handler/resolve structure;
- leave `onStart`, `onEnding`, and `onEnd` unchanged.

### Trace provider

- preserve `forceFlush(options?: ForceFlushOptions)` from current main;
- snapshot the processor list before mapping;
- call each processor through the same eager helper;
- retain per-processor timeout, result filtering, and outward rejection shape;
- use the per-call timeout option in the focused tests;
- retain a non-settling processor test to prove the real timeout path still works.

### Logs

- snapshot the public processor array;
- protect direct processor calls;
- retain the per-call timeout option, timeout wrapping, and rejection behavior.

### Metrics excluded

- reader array is transformed into an internal collector list during construction;
- no supported public mutation path was established;
- direct reader throws already cross an async collector boundary;
- private-state mutation is insufficient for an upstream defect claim.

## Rejected alternatives

- Safe-call over live arrays: removal can still skip children.
- Microtask deferral: changes eager start ordering.
- Permanent freezing or constructor copying: changes future membership behavior.
- Sequential awaiting: changes concurrency and latency.
- Settle-all aggregation: changes error timing and types.
- Repairing only `MultiSpanProcessor`: misses public provider force flush.
- Keeping metrics for symmetry: broadens the patch without a supported reversing path.
- Dropping or overriding #6929 during rebase: would regress a newly merged public API.
- Treating queued CI as a final disposition: confuses pending evidence with acceptance.

## Decision history

1. Safe-call-only head passed gates but failed review on live mutation.
2. First snapshot fixtures had test-only typing failures.
3. Earlier clean head passed all named workflows.
4. Review removed redundant metrics safe-call behavior.
5. Deeper review removed metrics entirely as private-state-only.
6. Deeper trace review added public provider force flush and timeout cleanup.
7. Follow-up added an explicit genuine-timeout compatibility control and formatting repair.
8. The reviewed six-file tree was collapsed to one commit on the earlier pinned base.
9. The owner approved advancement into upstream preparation.
10. Public `main` was refreshed to `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`.
11. The six-file patch was rebased while preserving #6929's per-call timeout API and current-main `onEnding()` behavior.
12. The rebased tree was squash-built to one commit and the source preview was returned to draft for fresh exact-head execution.
13. Current issue/PR overlap and current contribution/changelog/template requirements were refreshed.

## Exact current state

- refreshed base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact prepared head: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- relation: ahead 1, behind 0;
- boundary: three production files and three tests;
- focused assertions: eleven;
- validation carrier: PR #19;
- fresh source review: accepted, exact-head CI pending;
- public upstream contact: unauthorized and not performed.
