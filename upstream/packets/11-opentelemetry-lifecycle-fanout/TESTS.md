# Tests and receipts — Unit 11: snapshot lifecycle targets before concurrent fanout

## Identity

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact clean candidate: `59f83f889bed06a951d458556b2e7e1695cbea10`;
- validation carrier: `teamleaderleo/opentelemetry-js#18`;
- source relation: ahead 1, behind 0;
- execution authority: repository GitHub Actions matrix.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown direct throw still attempts later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush direct throw still attempts later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

Cleanup restores `loggingErrorHandler()`.

### `TracerProvider.forceFlush` — two tests

- direct synchronous throw still attempts the second processor, preserves the existing one-element error-array rejection, and leaves zero fake timers armed;
- live removal does not shrink the provider force-flush opening set.

These tests cover the public provider path that bypasses `MultiSpanProcessor.forceFlush()`.

### Logs — four tests

Shutdown and force flush each cover direct throw and live removal. Rejections and timeout wrapping remain unchanged.

### Metrics — two tests

Shutdown and force flush cover live removal. Direct-throw controls were removed because async `MetricCollector` methods already make those cases pass on the baseline.

## Claim matrix

| Claim | Reversing evidence | Current state |
| --- | --- | --- |
| direct trace/log throw cannot stop later opening invocation | four aggregate direct-throw controls | final-head Unit queued |
| provider force flush uses stable opening membership | provider mutation control | final-head Unit queued |
| provider sync throw clears its timeout | fake-timer count assertion | final-head Unit queued |
| live removal cannot shrink current operation | eight mutation controls across aggregate/provider/logs/metrics | final-head Unit queued |
| future operations still observe mutation | backing-array postconditions | final-head Unit queued |
| metrics is snapshot-only | source chain plus metrics mutation tests | source-reviewed; Unit queued |
| trace global handler does not leak | cleanup invokes handler factory | Unit/Lint queued |

## Exact final-head workflows

| Workflow | Run | State |
| --- | ---: | --- |
| Unit Tests | `30694080939` | queued |
| E2E Tests | `30694080935` | queued |
| Lint | `30694080925` | queued |
| Bundler tests | `30694080933` | queued |
| W3C Trace Context Integration | `30694080910` | queued |
| Ensure API Peer Dependency | `30694080929` | queued |
| CodeQL Analysis | `30694080926` | queued |
| Zizmor GitHub Actions Security Analysis | `30694080955` | queued |

No final-head pass is claimed until these settle.

## Historical evidence

Head `641528c9786f7d027fef4f4a76ae685f7107d394` passed the complete named workflow set, including a 10-job Unit matrix and 7-job E2E matrix. Those receipts validate the earlier six-file generation but are superseded for promotion by the provider repair and clean-history rewrite.

## Failure/repair history

| Generation | Result | Classification | Repair |
| --- | --- | --- | --- |
| `80e3b74b...` | gates passed; review found removal skip | design insufficiency | opening snapshots |
| `e19247b...` | TS2322 in mutation fixture | test typing | explicit callback types |
| `641528c...` | all gates passed; metrics overclaim found | scope review | metrics snapshot-only |
| trace cleanup | factory installed as handler | test global-state leak | use `loggingErrorHandler()` |
| provider deep pass | live fanout plus uncleared sync-throw timer | missed public entrypoint | snapshot provider list and clear timer in catch |

## Changelog boundary

Target policy requires behavior entries in root `CHANGELOG.md` for sdk-trace/sdk-metrics and `experimental/CHANGELOG.md` for sdk-logs. Final entries require the real authorized upstream PR number.

## Current judgment

`HOLD`

Source repair and history cleanup are complete. Clearing conditions: successful final-head workflows, eligible independent complete-diff acceptance, changelog packaging, final staleness/duplicate refresh, and separate public-contact authorization.
