# Unit 11 — invoke all lifecycle processors

## Current disposition

`VALIDATING — relevant spec-compliance fix; repaired exact-head CI running`

Last refreshed: `2026-08-02`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## In simple words

OpenTelemetry JS lets applications install multiple trace and log processors. Shutdown and force flush are required to call every registered processor. Today, a custom processor that throws before returning its promise can stop the aggregate trace/log fanout before later processors are called. Synchronous mutation of the retained array can also skip an opening processor. The public trace provider has a related timer-cleanup defect.

The repair snapshots the processor set when each lifecycle operation starts and converts direct synchronous throws into ordinary promise rejections without delaying invocation. It preserves existing error behavior and real timeouts.

This is a legitimate upstream bugfix, but its trigger is uncommon. It should be described as bounded shutdown/specification correctness, not as widespread telemetry loss.

## Contribution

Retained paths:

- `MultiSpanProcessor.shutdown()` and `forceFlush()`;
- `TracerProvider.forceFlush()`;
- `MultiLogRecordProcessor.shutdown()` and `forceFlush()`.

Metrics was removed after deeper review. Its collector lifecycle methods are async, the provider owns the collector list internally, and the predecessor mutation tests relied on private-state casts.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- current source head: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- source relation: ahead 4, behind 0;
- validation PR: `teamleaderleo/opentelemetry-js#19`;
- superseded carrier: closed PR #18;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-v2`;
- proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`.

The source branch remains unsquashed during current validation and will be squashed before final exact-head review.

## Changed-file fence

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Behavior and impact

- aggregate trace/logs: every processor in the opening set is invoked after a direct synchronous throw or synchronous removal;
- public provider: opening membership is stable, synchronous failure clears its timeout, and the existing error-array rejection is retained;
- real pending provider work still times out;
- processor calls remain eager and ordered;
- future array mutations remain visible to future operations;
- one shallow array copy is added per repaired lifecycle call;
- normal telemetry delivery paths are untouched.

A dependency-free Node.js model confirmed that the stale provider timer can keep natural process termination alive until timeout. With a 200 ms timer, the model exited after approximately 0.22 seconds. This demonstrates the mechanism, not prevalence.

## Validation

Previous head `f4910b355d12895edf25372444f76d4def08901c` passed Unit, W3C, Bundler, API peer dependency, CodeQL, E2E, and Zizmor. Lint failed only on Prettier formatting in `TracerProvider.ts`.

Current exact-head runs on `987a2bde097fe2e44531830e38c7c15a59c35c23`:

- Unit `30755343888`;
- Lint `30755343692`;
- W3C `30755343695`;
- Bundler `30755343708`;
- API peer dependency `30755343685`;
- CodeQL `30755343693`;
- E2E `30755343697`;
- Zizmor `30755343702`.

No current-head pass is claimed until those runs settle.

## Remaining gates

- successful current-head workflow matrix;
- squash and complete-diff re-review;
- eligible independent acceptance;
- root sdk-trace and experimental sdk-logs changelog entries with a real upstream PR number;
- final current-main, duplicate, contribution-policy, and disclosure refresh;
- explicit authority for public upstream interaction.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests](./TESTS.md)
- [Issue draft](./UPSTREAM_ISSUE.md)
- [PR draft](./UPSTREAM_PR.md)
- [Review](./REVIEW.md)
- [Handoff](./HANDOFF.md)

Public upstream interaction authorized/performed: `false` / `false`.
