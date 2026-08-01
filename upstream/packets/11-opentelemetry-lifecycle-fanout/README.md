# Unit 11 — fix: stabilize lifecycle fanout targets

## Current disposition

`HOLD — clean successor exact-head validation pending`

Last refreshed: `2026-08-01`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

OpenTelemetry JS trace and logs lifecycle fanouts can skip processors that belonged to the operation's opening set. A processor can remove a later processor from a retained mutable array during shutdown or force flush. Direct processor calls can also throw before later promise inputs are built.

Public `TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly fans out over the processor list. A synchronous throw there also left the processor timeout armed until expiry.

Metrics is excluded. `MeterProvider` constructs and owns its collector list internally, and the prior mutation tests only reached it through private state. `MetricCollector` lifecycle methods are already async.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact clean source head: `f4910b355d12895edf25372444f76d4def08901c`;
- owned validation PR: `teamleaderleo/opentelemetry-js#19`;
- superseded carrier: closed PR #18;
- source relation: ahead 1, behind 0;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- proposed title: `fix: stabilize lifecycle fanout targets`.

## Final code boundary

| Area | Production change | Focused tests |
| --- | --- | --- |
| trace multi-processor | snapshot opening processors and eagerly convert direct synchronous throws to rejections | shutdown/force-flush throw and live-removal controls; global-handler cleanup |
| public trace provider | snapshot force-flush targets; route sync throws through existing timeout/error cleanup | later processor attempted, rejection shape retained, timeout cleared, live-removal control |
| logs | snapshot opening processors and eagerly convert direct synchronous throws while retaining timeout wrapping | shutdown/force-flush throw and live-removal controls |

Changed files:

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

The source is one clean commit. No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Repair history

- safe-call-only generation passed gates but live removal still skipped later children;
- first snapshot fixtures required typing repair;
- clean predecessor head passed all named repository workflows;
- review found metrics safe-call redundant;
- deeper review removed metrics entirely as private-state-only;
- deeper trace review found public `TracerProvider.forceFlush()` bypassed the repaired aggregate;
- successor added that public path and cleared its timeout after synchronous failure;
- successor history was collapsed to one commit on the pinned public base.

## Current validation

Queued on exact successor head `f4910b355d12895edf25372444f76d4def08901c`:

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

No successor-head pass conclusion is claimed until these settle.

## Current-main, duplicate, and packaging boundary

Public main remained identical to the pinned base during repair. Open issue/PR searches found no replacement contribution. Repeat immediately before filing.

Target guidance requires a root changelog entry for sdk-trace and an experimental changelog entry for sdk-logs. Final entries need a real authorized upstream PR number.

## Remaining work

1. settle all successor-head workflows;
2. obtain eligible independent exact-head acceptance;
3. repeat current-main, duplicate, contribution-policy, and AI-disclosure checks;
4. add root and experimental changelog entries using the real upstream PR number;
5. obtain explicit authority before any public upstream action.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue fallback](./UPSTREAM_ISSUE.md)
- [Upstream PR draft](./UPSTREAM_PR.md)
- [Review](./REVIEW.md)
- [Handoff](./HANDOFF.md)

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
