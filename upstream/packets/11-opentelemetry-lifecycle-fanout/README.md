# Unit 11 — fix: stabilize lifecycle fanout targets

## Current disposition

`HOLD — squashed successor validating`

Last refreshed: `2026-08-01`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

Trace and logs lifecycle fanouts can skip processors from the operation's opening set when a processor mutates a retained array during shutdown or force flush. Their aggregate interfaces can also throw synchronously before returning a promise, interrupting later invocation.

Deeper review removed metrics: `MeterProvider` owns its collector list internally, the predecessor mutation tests used private-state casts, and `MetricCollector` lifecycle methods are already async.

The same review found the separate public `TracerProvider.forceFlush()` fanout. It bypasses `MultiSpanProcessor.forceFlush()`, maps the live processor list, and leaves a per-processor timeout armed after synchronous failure unless the failure enters its existing cleanup path.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact squashed source head: `f4910b355d12895edf25372444f76d4def08901c`;
- source relation: ahead 1, behind 0;
- validation PR: `teamleaderleo/opentelemetry-js#19`;
- superseded carrier: closed PR #18;
- canonical packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-v2`;
- proposed title: `fix: stabilize lifecycle fanout targets`.

## Changed-file fence

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Final behavior

- aggregate trace: opening snapshot plus eager synchronous safe-call; original shutdown rejection and force-flush global-report/resolve behavior retained;
- public trace provider: opening snapshot plus synchronous-failure normalization through the existing timeout cleanup and error-array result path;
- logs: opening snapshot plus eager synchronous safe-call; timeout wrapping retained;
- future array mutations remain visible.

## Exact-head validation

Queued on `f4910b355d12895edf25372444f76d4def08901c`:

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

No squashed-head pass is claimed until these settle.

## Evidence and remaining gates

Predecessor head `641528c...` passed the complete named workflow set. Review `4834242586` exposed the metrics overclaim; deeper call-chain review removed metrics and added public provider coverage. The former carrier was concurrently rewritten, so source and packet successors were isolated before the final squash.

Remaining gates: successful exact-head workflows, eligible independent complete-diff acceptance, required sdk-trace and sdk-logs changelog entries using a real upstream PR number, final current-main/duplicate/policy refresh, and explicit public-contact authority.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests](./TESTS.md)
- [Issue fallback](./UPSTREAM_ISSUE.md)
- [PR draft](./UPSTREAM_PR.md)
- [Review](./REVIEW.md)
- [Handoff](./HANDOFF.md)

Public upstream interaction authorized/performed: `false` / `false`.
