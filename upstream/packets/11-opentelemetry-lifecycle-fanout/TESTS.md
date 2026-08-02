# Tests and receipts — Unit 11: stabilize lifecycle fanout targets

## In simple words

The candidate contains eleven focused assertions across trace aggregate, public trace provider, and logs. The source is repaired and squashed. Exact-head GitHub Actions runs were triggered for the clean commit and are queued; older runs remain historical evidence only.

## Identity

- public base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- source branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact clean candidate: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- reviewed pre-squash tree source: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- validation carrier: `teamleaderleo/opentelemetry-js#19`;
- relation: ahead 1, behind 0;
- execution authority: repository GitHub Actions matrix.

The clean candidate uses the exact six file blobs reviewed at `987a2bde...`.

## Focused assertion set

### `MultiSpanProcessor` — four tests

- shutdown synchronous throw still attempts the later opening processor and rejects;
- shutdown removal still invokes the removed opening processor;
- force-flush synchronous throw still attempts the later processor, reports globally, and resolves;
- force-flush removal still invokes the removed opening processor.

Cleanup restores `loggingErrorHandler()`.

### `TracerProvider.forceFlush()` — three tests

- synchronous throw still attempts the second processor, preserves the one-element error-array rejection, and leaves no fake timer armed;
- live removal does not shrink the provider force-flush opening set;
- a genuinely non-settling processor still times out and rejects, with no timer left afterward.

### Logs — four tests

Shutdown and force flush each cover synchronous throw and live removal. Rejection and timeout behavior remain unchanged.

### Metrics — intentionally absent

The earlier metrics mutation controls reached private provider state. No supported public collector-list mutation path was established, and async `MetricCollector` methods already normalize reader throws.

## Claim matrix

| Claim | Reversing evidence | Exact-head state |
| --- | --- | --- |
| direct trace/log throw cannot stop later opening invocation | four direct-throw controls | Unit queued |
| aggregate live removal cannot shrink current operation | four aggregate mutation controls | Unit queued |
| provider force flush uses stable opening membership | provider mutation control | Unit queued |
| provider sync throw clears its timeout | fake-timer count assertion | Unit queued |
| provider error shape is retained | one-element error-array predicate | Unit queued |
| genuine provider timeout behavior is retained | non-settling processor control | Unit queued |
| trace handler cleanup does not leak | default handler factory invoked | Unit/Lint queued |
| metrics is outside supported scope | source ownership review | no target change/test |

## Exact-head workflows

| Workflow | Run | State |
| --- | ---: | --- |
| Unit Tests | `30756036668` | queued |
| Lint | `30756036660` | queued |
| W3C Trace Context Integration | `30756036656` | queued |
| Bundler tests | `30756036678` | queued |
| Ensure API Peer Dependency | `30756036662` | queued |
| CodeQL Analysis | `30756036671` | queued |
| E2E Tests | `30756036639` | queued |
| Zizmor GitHub Actions Security Analysis | `30756036691` | queued |

No exact-head pass is claimed before execution.

## Historical evidence

- earlier broader head `641528c9786f7d027fef4f4a76ae685f7107d394` passed every named workflow but included superseded scope;
- predecessor `f4910b355d12895edf25372444f76d4def08901c` passed Unit, W3C, Bundler, API peer dependency, CodeQL, E2E, and Zizmor; Lint found only Prettier formatting in `TracerProvider.ts`;
- reviewed pre-squash head `987a2bde097fe2e44531830e38c7c15a59c35c23` added the genuine-timeout control and formatting repair, but its workflows remained queued.

These receipts support the mechanism and repair history. They do not replace exact-head execution for `db3d9e5e...`.

## Failure and repair history

| Generation | Result | Classification | Repair |
| --- | --- | --- | --- |
| safe-call-only | gates passed; removal still skipped child | design insufficiency | opening snapshots |
| first snapshot fixture | TS2322 callback inference | test typing | explicit callback types |
| broader trace/logs/metrics | all gates passed; metrics claim unsupported | scope review | remove metrics |
| trace cleanup | handler factory installed as handler | test isolation | call `loggingErrorHandler()` |
| provider deep pass | missed live fanout and armed timer | incomplete public path | provider snapshot + safe-call |
| first provider successor | lint formatting and missing explicit real-timeout control | packaging/test completeness | formatting + timeout control |
| successor history | four commits | packaging | exact-blob one-commit squash |

## Changelog boundary

Target guidance calls for a root changelog entry for sdk-trace and an experimental changelog entry for sdk-logs. Final entries require the real authorized upstream PR number.

## Current judgment

`SOURCE REPAIRED — exact-head execution queued; owner decision prepared`
