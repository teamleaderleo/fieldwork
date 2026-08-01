# Unit 11 — fix: stabilize lifecycle fanout targets

## Current disposition

`HOLD — successor exact-head validation pending`

Last refreshed: `2026-08-01`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

OpenTelemetry JS trace and logs lifecycle fanouts can skip processors that belonged to the operation's opening set. A processor can remove a later processor from a retained mutable array during shutdown or force flush. Trace and logs also call processor interfaces directly, so a synchronous throw can interrupt later invocation before the aggregate promise set is complete.

Deeper code-path review removed metrics from this unit. `MeterProvider` constructs and owns its collector list internally, and `MetricCollector.shutdown()` / `forceFlush()` are async. The previous metrics tests only mutated private state and did not establish a supported runtime defect.

The same deeper review found a missing public trace path: `TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and directly fans out over the processor list. A synchronous throw there also left the processor timeout armed until expiry.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact source head: `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`;
- owned validation PR: `teamleaderleo/opentelemetry-js#19`;
- superseded carrier: closed PR `teamleaderleo/opentelemetry-js#18`;
- canonical packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-v2`;
- proposed title: `fix: stabilize lifecycle fanout targets`.

The source is ahead 6, behind 0. Its six contents-API commits should be squashed before any authorized public submission.

## Final code boundary

| Area | Production change | Focused tests |
| --- | --- | --- |
| trace multi-processor | snapshot opening processors and eagerly convert direct synchronous throws to rejections | shutdown/force-flush throw and live-removal controls; global-handler compatibility |
| public trace provider | snapshot force-flush targets; route sync throws through the existing cleanup path | later processor attempted, rejection shape retained, timeout cleared, live-removal control |
| logs | snapshot opening processors and eagerly convert direct synchronous throws while retaining timeout wrapping | shutdown/force-flush throw and live-removal controls |

Changed files:

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/src/TracerProvider.ts`
3. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
4. `packages/sdk-trace/test/common/TracerProvider.attempt-all.test.ts`
5. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
6. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`

No metrics, workflow, dependency, lock, generated, publisher, or research-only file is present.

## Repair history

- safe-call-only generation passed gates but review found live removal could still skip later children;
- first snapshot fixtures had TS2322 inference failures and were repaired;
- clean predecessor head `641528c...` passed all named repository workflow groups;
- review `4834242586` found the metrics safe-call claim redundant;
- deeper review then found metrics mutation was private-state-only and removed metrics entirely;
- deeper trace review found public `TracerProvider.forceFlush()` bypassed the repaired multi-processor method;
- the successor adds that public path and clears its timeout after synchronous failure;
- concurrent rewrites made PR #18 non-authoritative, so clean successor PR #19 and a successor packet branch were created from stable bases.

## Current validation

Triggered on exact successor head `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`:

- Unit Tests `30694086716`;
- CodeQL Analysis `30694086713`;
- W3C Trace Context Integration Test `30694086725`;
- Zizmor GitHub Actions Security Analysis `30694086726`;
- Ensure API Peer Dependency `30694086723`;
- Bundler tests `30694086727`;
- E2E Tests `30694086733`;
- Lint `30694086746`.

No successor-head pass conclusion is claimed until these runs settle.

## Current-main, duplicate, and packaging boundary

Public `main` remained identical to the pinned base during this repair pass. Open issue/PR searches for the affected symbols, provider force-flush fanout, snapshot wording, and skipped-later-processor behavior found no replacement contribution. Repeat immediately before filing.

Target guidance requires a root changelog entry for sdk-trace and an `experimental/CHANGELOG.md` entry for sdk-logs. Final entries need a real authorized upstream PR number.

## Remaining work

1. settle all successor-head workflows;
2. obtain eligible independent complete-diff acceptance;
3. squash source history;
4. repeat current-main, duplicate, contribution-policy, and AI-disclosure checks;
5. add root and experimental changelog entries using the real upstream PR number;
6. obtain explicit authority before any public upstream action.

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
