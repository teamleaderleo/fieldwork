# Approaches — Unit 11: stabilize lifecycle fanout targets

## In simple words

The selected repair is deliberately narrow: snapshot supported mutable processor fanouts and convert direct synchronous throws without changing concurrency, ordering, or error contracts. Metrics is excluded because the earlier path depended on private state rather than a supported runtime mutation boundary.

## Selected boundary

Repair supported mutable processor fanouts only:

- `MultiSpanProcessor`: opening snapshot plus eager synchronous safe-call;
- public `TracerProvider.forceFlush()`: opening snapshot plus synchronous-error normalization through the existing timeout/error path;
- `MultiLogRecordProcessor`: opening snapshot plus eager synchronous safe-call.

Metrics is excluded. `MeterProvider` constructs its collector list internally and does not retain the caller’s reader array; the prior mutation tests reached private state only. `MetricCollector` lifecycle methods are already async.

## Why trace has two force-flush sites

`TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly maps the aggregate’s processor list. Repairing only the multi-processor leaves the public provider path exposed to live removal.

The provider also arms a timeout before processor invocation. A synchronous throw was converted by the Promise executor, but bypassed timeout cleanup. The selected helper converts it to a rejected promise so the existing `.catch()` clears the timer and records the error without changing the provider’s error-array contract.

## Package decisions

### Trace aggregate

- snapshot `_spanProcessors`;
- protect direct lifecycle calls with an eager local try/catch helper;
- preserve shutdown rejection and force-flush global-handler/resolve structure.

### Trace provider

- snapshot the processor list before mapping;
- call each processor through the same eager helper;
- retain per-processor timeout, result filtering, and outward rejection shape;
- retain a non-settling processor test to prove the real timeout path still works.

### Logs

- snapshot the public processor array;
- protect direct processor calls;
- retain timeout wrapping and rejection behavior.

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
- Treating queued CI or a named reviewer as a code-repair blocker: confuses evidence/authority with implementation work.

## Decision history

1. Safe-call-only head passed gates but failed review on live mutation.
2. First snapshot fixtures had test-only typing failures.
3. Earlier clean head passed all named workflows.
4. Review removed redundant metrics safe-call behavior.
5. Deeper review removed metrics entirely as private-state-only.
6. Deeper trace review added public provider force flush and timeout cleanup.
7. Follow-up added an explicit genuine-timeout compatibility control and formatting repair.
8. The exact reviewed six-file tree was collapsed from four commits to one commit on the pinned base.
9. Packet and source PR were synchronized to the new canonical identity and owner-decision handoff.

## Exact current state

- base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- clean source head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- reviewed pre-squash tree source: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- relation: ahead 1, behind 0;
- boundary: three production files and three tests;
- focused assertions: eleven;
- validation carrier: PR #19;
- public upstream contact: unauthorized and not performed.
