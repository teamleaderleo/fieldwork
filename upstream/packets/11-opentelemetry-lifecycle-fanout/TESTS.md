# Tests and receipts — Unit 11: stabilize lifecycle fanout targets

## Identity

- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact clean candidate: `f4910b355d12895edf25372444f76d4def08901c`;
- validation carrier: `teamleaderleo/opentelemetry-js#19`;
- relation: ahead 1, behind 0;
- execution authority: repository GitHub Actions matrix.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown synchronous throw still attempts the later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush synchronous throw still attempts the later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

Cleanup restores `loggingErrorHandler()`.

### `TracerProvider.forceFlush()` — two tests

- synchronous throw still attempts the second processor, preserves the one-element error-array rejection, and leaves no fake timer armed;
- live removal does not shrink the provider force-flush opening set.

### Logs — four tests

Shutdown and force flush each cover synchronous throw and live removal. Rejection and timeout behavior remain unchanged.

### Metrics — intentionally absent

The earlier metrics mutation controls reached private provider state. No supported public collector-list mutation path was established, and async `MetricCollector` methods already normalize reader throws.

## Claim matrix

| Claim | Reversing evidence | Current state |
| --- | --- | --- |
| direct trace/log throw cannot stop later opening invocation | four direct-throw controls | successor Unit queued |
| aggregate live removal cannot shrink current operation | four aggregate mutation controls | successor Unit queued |
| provider force flush uses stable opening membership | provider mutation control | successor Unit queued |
| provider sync throw clears its timeout | fake-timer count assertion | successor Unit queued |
| provider error shape is retained | one-element error-array predicate | successor Unit queued |
| trace handler cleanup does not leak | default handler factory invoked | Unit/Lint queued |
| metrics is outside supported scope | source ownership review | no target change/test |

## Exact successor workflows

| Workflow | Run | State |
| --- | ---: | --- |
| Unit Tests | `30694264703` | queued |
| W3C Trace Context Integration | `30694264710` | queued |
| Bundler tests | `30694264711` | queued |
| Ensure API Peer Dependency | `30694264708` | queued |
| CodeQL Analysis | `30694264717` | queued |
| E2E Tests | `30694264735` | queued |
| Zizmor GitHub Actions Security Analysis | `30694264748` | queued |
| Lint | `30694264729` | queued |

No successor-head pass is claimed until these settle.

## Historical evidence

Earlier head `641528c9786f7d027fef4f4a76ae685f7107d394` passed every named workflow, including 10 Unit jobs and 7 E2E jobs. Those receipts validate the earlier broader generation but are superseded for promotion.

## Failure/repair history

| Generation | Result | Classification | Repair |
| --- | --- | --- | --- |
| safe-call-only | gates passed; removal still skipped child | design insufficiency | opening snapshots |
| first snapshot fixture | TS2322 callback inference | test typing | explicit callback types |
| six-file trace/logs/metrics | all gates passed; metrics claim unsupported | scope review | remove metrics |
| trace cleanup | handler factory installed as handler | test isolation | call `loggingErrorHandler()` |
| provider deep pass | missed live fanout and armed timer | incomplete public path | provider snapshot + safe-call |
| successor history | six file-level commits | packaging | collapsed to one commit |

## Changelog boundary

Target policy requires a root changelog entry for sdk-trace and an experimental changelog entry for sdk-logs. Final entries require the real authorized upstream PR number.

## Current judgment

`HOLD`

Source scope and history are clean. Clearing conditions: successful successor workflows, eligible independent exact-head acceptance, changelog packaging, final current-main/duplicate refresh, and public-contact authorization.
