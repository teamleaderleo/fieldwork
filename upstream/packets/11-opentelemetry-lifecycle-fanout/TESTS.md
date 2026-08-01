# Tests and receipts — Unit 11: stabilize lifecycle fanout targets

## Identity

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact successor head: `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`;
- validation carrier: `teamleaderleo/opentelemetry-js#19`;
- source relation: ahead 6, behind 0;
- execution authority: repository GitHub Actions matrix.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown direct throw still attempts the later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush direct throw still attempts the later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

Cleanup restores `setGlobalErrorHandler(loggingErrorHandler())`.

### `TracerProvider.forceFlush()` — two tests

- synchronous throw attempts the later processor, preserves the existing one-error array rejection, and leaves zero fake-clock timers;
- live removal does not shrink the provider's opening processor set.

### Logs — four tests

Shutdown and force flush each cover direct throw and live removal. Rejections and timeout wrapping remain unchanged.

### Metrics

No metrics source or tests remain. The predecessor tests mutated private collector state and did not reverse a supported runtime path.

## Claim matrix

| Claim | Reversing evidence | Current state |
| --- | --- | --- |
| direct aggregate trace/log throw cannot stop later opening invocation | four direct-throw controls | successor Unit run queued at creation |
| provider force flush uses stable opening membership | provider mutation control | successor Unit run queued at creation |
| provider synchronous throw clears its timeout | fake-timer count assertion | successor Unit run queued at creation |
| live removal cannot shrink current supported operation | aggregate trace, provider trace, and logs mutation controls | successor Unit run queued at creation |
| future operations observe mutation | backing-array postconditions | successor Unit run queued at creation |
| trace global handler cleanup is valid | `loggingErrorHandler()` restoration | Unit/Lint queued at creation |

## Exact successor workflows

| Workflow | Run | State at packet repair |
| --- | ---: | --- |
| Unit Tests | `30694086716` | queued |
| CodeQL Analysis | `30694086713` | queued |
| W3C Trace Context Integration Test | `30694086725` | queued |
| Zizmor GitHub Actions Security Analysis | `30694086726` | queued |
| Ensure API Peer Dependency | `30694086723` | queued |
| Bundler tests | `30694086727` | queued |
| E2E Tests | `30694086733` | queued |
| Lint | `30694086746` | queued |

No successor-head pass is claimed until these settle.

## Historical evidence and repairs

| Generation | Result | Classification | Repair |
| --- | --- | --- | --- |
| safe-call-only | gates passed; review found removal skip | design insufficiency | opening snapshots |
| first snapshot fixture | TS2322 callback inference | test typing | explicit callback typing |
| `641528c...` | all named gates passed | valid predecessor execution | superseded by scope changes |
| metrics review | safe-call claim redundant | scope review | then deeper removal of metrics |
| trace cleanup | handler factory installed as handler | test isolation | invoke `loggingErrorHandler()` |
| provider deep pass | missed live fanout and uncleared sync-failure timer | missed public entrypoint | add provider source/test pair |
| shared carrier | concurrent force rewrites | carrier integrity | isolate branch v2 and PR #19 |

## Changelog boundary

Target policy requires a root `CHANGELOG.md` entry for sdk-trace and an `experimental/CHANGELOG.md` entry for sdk-logs. Final entries require the real authorized upstream PR number.

## Current judgment

`HOLD`

The source repair is complete. Clearing conditions are a successful exact successor matrix, eligible independent complete-diff acceptance, history cleanup, changelog packaging, final staleness/duplicate refresh, and separate public-contact authorization.
