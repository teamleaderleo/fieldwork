# Tests and receipts — Unit 11: snapshot lifecycle targets before concurrent fanout

## Identity

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- repaired candidate head: `1b7609141e87ad226e64bb0238ef602e76812896`;
- execution carrier: `teamleaderleo/opentelemetry-js#18`;
- repaired-head workflow set: run number 63;
- direct local execution: unavailable in the original worker environment; repository GitHub Actions is the execution authority.

## Focused assertion set

### Trace — four tests

- shutdown direct throw: later opening processor is invoked and aggregate rejects;
- shutdown live removal: removed later opening processor is still invoked;
- force-flush direct throw: later opening processor is invoked, error reaches the global handler, and aggregate resolves;
- force-flush live removal: removed later opening processor is still invoked.

The test cleanup restores `setGlobalErrorHandler(loggingErrorHandler())`. The repaired form prevents leakage of the factory function into later tests.

### Logs — four tests

- shutdown direct throw and live-removal controls;
- force-flush direct throw and live-removal controls;
- error results remain rejections;
- timeout wrapping remains in the production path.

### Metrics — two tests

- shutdown live-removal control;
- force-flush live-removal control, with the removed collector restored before cleanup shutdown.

Metrics synchronous-throw cases were removed. `MetricCollector` is already async, so those cases pass the baseline and do not reverse the source change.

## Claim-to-evidence matrix

| Claim | Reversing evidence | Current status | Limit |
| --- | --- | --- | --- |
| direct trace/log throw cannot stop later opening invocation | four direct-throw tests | repaired-head Unit run queued | arbitrary thenable behavior not separately tested |
| live removal cannot shrink current opening set | six mutation tests | repaired-head Unit run queued | additions are guaranteed by snapshot semantics but not separately asserted |
| future operations observe mutation | backing-array postconditions | repaired-head Unit run queued | no duplicate-child policy |
| trace force flush still reports and resolves | global-handler assertion plus restored baseline structure | repaired-head Unit run queued | one observed `Promise.all` rejection |
| metrics needs snapshot but not safe-call | source chain `MeterProvider → MetricCollector → reader`, plus metrics mutation controls | source-reviewed; Unit queued | production prevalence unmeasured |
| no test global-handler leak | default handler factory invoked during cleanup | repaired-head Unit/Lint queued | repository has no public getter to restore an arbitrary prior handler |

## Exact repaired-head workflows

| Workflow | Run | Current state |
| --- | ---: | --- |
| Unit Tests | `30693695553` | queued |
| E2E Tests | `30693695548` | queued |
| Lint | `30693695562` | queued |
| Bundler tests | `30693695536` | queued |
| W3C Trace Context Integration Test | `30693695557` | queued |
| Ensure API Peer Dependency | `30693695533` | queued |
| CodeQL Analysis | `30693695552` | queued |
| Zizmor GitHub Actions Security Analysis | `30693695550` | queued |

No pass conclusion is claimed for the repaired head until these settle.

## Superseded exact-head receipts

Head `641528c9786f7d027fef4f4a76ae685f7107d394` passed:

- Unit Tests `30674494793` — 10 jobs;
- E2E Tests `30674494785` — 7 jobs;
- Lint `30674494830`;
- Bundler tests `30674494832`;
- W3C Trace Context Integration `30674494799`;
- Ensure API Peer Dependency `30674494801`;
- CodeQL Analysis `30674494779`;
- Zizmor GitHub Actions Security Analysis `30674494823`.

Those receipts validate the broader predecessor behavior but are expired for promotion because source and tests moved during repair.

## Historical setup failures

| Head/attempt | Failure | Classification | Resolution |
| --- | --- | --- | --- |
| `80e3b74b...` | product gates passed but review found live-array removal still skipped a child | design insufficiency | add opening snapshots |
| `e19247b...` | TS2322 from mutation callbacks inferred as `() => never` | test fixture typing | explicitly type callbacks `() => void` |
| `641528c...` review | metrics helper/regression overclaimed a baseline defect | scope/source review | metrics snapshot-only; remove throw tests |
| trace test cleanup | installed `loggingErrorHandler` factory rather than returned handler | test harness/global state | call `loggingErrorHandler()` |

## Ordinary gate and packaging boundary

The repository workflows cover compile-bearing checks, supported Node/browser/web-worker matrices, E2E, lint, bundler, API peer dependency, trace-context integration, and static/workflow security.

Changelog files are not yet changed. Target guidance requires behavior changes to be listed in both:

- root `CHANGELOG.md` under Unreleased Bug Fixes for sdk-trace/sdk-metrics;
- `experimental/CHANGELOG.md` under Unreleased Bug Fixes for sdk-logs.

Final entries must use the real authorized upstream PR number and current link format; they should not be fabricated on the owned validation carrier.

## Current judgment

`HOLD`

The source repair is complete. Clearing conditions are a successful exact repaired-head matrix, eligible independent complete-diff acceptance, history cleanup, changelog packaging, final current-main/duplicate refresh, and separate public-contact authorization.
