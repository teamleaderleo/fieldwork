# Unit 11 — fix: snapshot lifecycle targets before concurrent fanout

## Current disposition

`HOLD — repair complete; exact-head validation and independent review pending`

Last refreshed: `2026-08-01`  
Priority-zero parent: `teamleaderleo/fieldwork#435`  
Public upstream contact authorized: `no`

## Contribution

OpenTelemetry JS lifecycle aggregates can skip a child that belonged to the operation's opening set when an earlier child removes it from a live array during shutdown or force flush.

Trace and logs have an additional direct-call failure: a processor can throw before returning its declared promise, interrupting later promise-input construction. Metrics already calls async `MetricCollector` methods, so it needs snapshotting but no extra safe-call wrapper.

## Exact identities

- target: `open-telemetry/opentelemetry-js`;
- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`;
- exact repaired source head: `1b7609141e87ad226e64bb0238ef602e76812896`;
- owned validation PR: `teamleaderleo/opentelemetry-js#18`;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout`;
- proposed title: `fix: snapshot lifecycle targets before concurrent fanout`.

The source is ahead 10, behind 0. The ten commits are contents-API file writes and should be squashed before authorized public submission.

## Final code boundary

| Area | Production change | Focused tests |
| --- | --- | --- |
| trace | snapshot opening processors; eager safe-call; retain original outer promise/error-handler structure | shutdown/force-flush direct throw and live removal; global handler restoration |
| logs | snapshot opening processors; eager safe-call; retain timeout wrapping | shutdown/force-flush direct throw and live removal |
| metrics | snapshot opening collectors only | shutdown/force-flush live removal |

Changed files:

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
3. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
4. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`
5. `packages/sdk-metrics/src/MeterProvider.ts`
6. `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`

No workflow, dependency, lock, generated, publisher, or research-only file is present.

## Repair history

- safe-call-only generation passed gates but review found live removal could still skip children;
- first snapshot tests had TS2322 fixture inference failures and were repaired;
- clean head `641528c...` passed all repository workflow groups;
- review `4834242586` found metrics safe-call scope redundant;
- repaired source removed the metrics helper and throw tests;
- deeper comparison restored the baseline trace outer promise/error structure;
- deeper test review corrected `loggingErrorHandler` to `loggingErrorHandler()` during cleanup.

## Current validation

Queued on exact repaired head `1b7609141e87ad226e64bb0238ef602e76812896`:

- Unit `30693695553`;
- E2E `30693695548`;
- Lint `30693695562`;
- Bundler `30693695536`;
- W3C `30693695557`;
- API peer dependency `30693695533`;
- CodeQL `30693695552`;
- Zizmor `30693695550`.

No repaired-head pass conclusion is claimed yet. The previous head's full pass is retained as historical evidence only.

## Current-main and duplicate result

Public `main` remained identical to the pinned base during the repair pass. Open issue/PR searches for the affected symbols, lifecycle fanout, snapshot wording, and skipped-later-child behavior found no replacement contribution. Repeat immediately before filing.

## Changelog boundary

Target guidance requires behavior changes to be listed in:

- root `CHANGELOG.md` for sdk-trace/sdk-metrics;
- `experimental/CHANGELOG.md` for sdk-logs.

Final entries need the real upstream PR number and current repository link format. Draft wording is preserved in `UPSTREAM_PR.md`.

## Remaining work

1. settle all repaired-head workflows;
2. obtain eligible independent complete-diff acceptance;
3. squash source history;
4. repeat current-main/duplicate/policy checks;
5. add both changelog entries using the real authorized PR number;
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
