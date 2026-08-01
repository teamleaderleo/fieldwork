# Unit 11 — fix: snapshot lifecycle targets before concurrent fanout

## In simple words

OpenTelemetry JS trace, logs, and metrics fan lifecycle calls out to child processors or readers. All three areas can skip a later opening child when an earlier callback removes it from the live array. Trace and logs have an additional problem: a synchronous child throw can stop construction before later processors are invoked.

The current candidate correctly uses opening snapshots everywhere and synchronous safe-call protection for trace and logs. Complete-diff review found that metrics does not need the added safe-call helper because its `MetricCollector` lifecycle methods are already async and already convert reader throws into rejected promises.

All exact-head workflows passed. The unit is in `REPAIR` until metrics is narrowed to snapshot-only and the new exact head is rerun and independently reviewed.

## Current disposition

`REPAIR`

Last reviewed: `2026-08-01`  
Worker/reviewer: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Public upstream contact authorized: `no`

## Exact identities

- Reviewed public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Canonical source branch: [`upstream/unit-11-lifecycle-fanout`](https://github.com/teamleaderleo/opentelemetry-js/tree/upstream/unit-11-lifecycle-fanout);
- Reviewed source head: [`641528c9786f7d027fef4f4a76ae685f7107d394`](https://github.com/teamleaderleo/opentelemetry-js/commit/641528c9786f7d027fef4f4a76ae685f7107d394);
- Validation PR: [`teamleaderleo/opentelemetry-js#18`](https://github.com/teamleaderleo/opentelemetry-js/pull/18);
- Packet branch: [`p0/435-unit-11-opentelemetry-lifecycle-fanout`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-11-opentelemetry-lifecycle-fanout);
- Packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`;
- Changed-file fence: three production files and three target-native test files;
- Current-main relation: ahead 6, behind 0 at review time.

## Review result by package

| Package | Snapshot needed? | Safe-call needed? | Review judgment |
| --- | --- | --- | --- |
| trace | yes | yes | current direction accepted |
| logs | yes | yes | current direction accepted |
| metrics | yes | no | remove redundant safe-call helper; keep snapshot |

Metrics synchronous-throw tests may remain only as compatibility controls. They must not be described as regressions proving the metrics production change.

## Exact-head validation

All named workflows passed on source head `641528c9786f7d027fef4f4a76ae685f7107d394`:

- Unit Tests `30674494793` — success, 10 jobs;
- E2E Tests `30674494785` — success, 7 jobs;
- Lint `30674494830` — success;
- Bundler `30674494832` — success;
- W3C Trace Context Integration `30674494799` — success;
- Ensure API Peer Dependency `30674494801` — success;
- CodeQL `30674494779` — success;
- Zizmor `30674494823` — success.

These receipts are exact to the reviewed source head. Any repair invalidates them for promotion and requires a new complete run.

## Durable packet

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — mechanism and claim boundary;
- [`APPROACHES.md`](./APPROACHES.md) — selected and rejected approaches;
- [`TESTS.md`](./TESTS.md) — exact receipts and evidence classification;
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — fallback draft requiring metrics narrowing;
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — public draft requiring metrics narrowing;
- [`REVIEW.md`](./REVIEW.md) — complete-diff `REPAIR` review;
- [`HANDOFF.md`](./HANDOFF.md) — continuation steps.

## Required repair

1. In `packages/sdk-metrics/src/MeterProvider.ts`, retain opening `.slice()` snapshots but remove the metrics-local `callLifecycle()` helper and wrappers.
2. Map snapshots directly to `collector.forceFlush(options)` and `collector.shutdown(options)`.
3. Retain metrics mutation controls as reversing regressions; reclassify or remove metrics synchronous-throw controls.
4. Narrow every durable and public-facing claim to distinguish trace/logs safe-call behavior from metrics snapshot-only behavior.
5. Rerun the complete workflow set on the repaired exact head.
6. Obtain an eligible independent complete-diff review of that repaired head.
7. Before authorized filing, refresh current main and duplicate search, squash the file-level commits if appropriate, and add required changelog entries using the real PR number.

## Evidence and authority limits

- The current workflow matrix is green but the reviewed source still needs repair.
- This review was performed by the branch builder and is not independent final acceptance.
- Production frequency, ecosystem impact, and extreme child-count allocation costs remain unmeasured.
- Public upstream interaction remains unauthorized and none was performed.
