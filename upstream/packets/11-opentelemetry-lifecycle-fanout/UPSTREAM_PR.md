# Upstream pull-request draft — fix: snapshot lifecycle targets before concurrent fanout

Draft status: `repair required`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

The owned candidate passed all named repository workflows, but complete-diff review found that metrics should be snapshot-only. This draft describes the intended repaired contribution rather than the over-broad current source head.

---

## Summary

- Snapshot trace processors, log processors, and metric collectors before lifecycle fanout so mutation cannot skip a child that belonged to the opening set.
- For trace and logs, convert direct synchronous processor throws into rejected promises so later opening processors are still invoked.
- Preserve eager concurrent fanout and existing package-specific outward error behavior.

## Problem

The trace, logs, and metrics lifecycle aggregators iterate mutable child arrays. A child can remove a later indexed child during shutdown or force flush, causing the current operation to skip an opening child.

Trace and logs also invoke child lifecycle methods directly while constructing promise inputs. A synchronous throw can stop construction before later processors are invoked.

Metrics differs: `MetricCollector.shutdown()` and `forceFlush()` are already async, so synchronous reader throws already become rejected promises. Metrics only needs the stable opening snapshot.

## Change

- `MultiSpanProcessor`: snapshot processors and invoke each through a local synchronous safe-call helper before `Promise.all`.
- `MultiLogRecordProcessor`: snapshot processors and invoke each through a local synchronous safe-call helper while retaining timeout behavior.
- `MeterProvider`: snapshot metric collectors and call the existing async collector lifecycle methods directly.

The original collections remain mutable for future operations.

## Behavior retained

- trace shutdown rejects;
- trace force flush reports through `globalErrorHandler` and resolves;
- logs and metrics reject;
- child calls remain eager and concurrent;
- `Promise.all` retains first-rejection behavior rather than aggregating every asynchronous error.

## Tests

Focused tests cover:

- synchronous throw and opening-set mutation for trace shutdown and force flush;
- synchronous throw and opening-set mutation for logs shutdown and force flush;
- opening-set mutation for metrics shutdown and force flush;
- metrics synchronous-throw behavior only as a baseline compatibility control if retained;
- trace global error-handler compatibility.

The reviewed owned head `641528c9786f7d027fef4f4a76ae685f7107d394` passed Unit, E2E, Lint, Bundler, W3C Trace Context Integration, API peer-dependency, CodeQL, and Zizmor workflows. Because the metrics source must change, all gates must run again on the repaired exact head.

## Compatibility

- Public API: unchanged.
- Allocation: one shallow child-array copy per affected lifecycle operation.
- Concurrency and failure timing: existing eager `Promise.all` model retained.
- Migration: none.
- Rollback: revert the bounded source/test patch.

## Alternatives considered

- Safe-call over live arrays does not prevent an earlier child from removing a later opening child.
- Permanent freezing or copying changes future membership behavior.
- Sequential awaiting changes concurrency and latency.
- Settle-all aggregation changes outward failure timing and error semantics.
- A metrics safe-call wrapper is unnecessary because the collector boundary is already async.

## Limits

- Production prevalence is unmeasured.
- The change does not aggregate all asynchronous failures.
- Delayed recursion, one-shot provider/reader state, final metrics collection, pre-existing span delivery, and global disposal remain separate.

---

## Submission checklist

- [ ] Repair metrics source to snapshot-only.
- [ ] Reclassify or remove metrics synchronous-throw controls.
- [ ] Rerun focused tests and all project-declared gates on the repaired exact head.
- [ ] Obtain eligible independent complete-diff review.
- [ ] Refresh current main and duplicate/overlap search immediately before filing.
- [ ] Squash the file-level commits if appropriate.
- [ ] Add required changelog entries using the real PR number.
- [ ] Recheck contribution and AI-disclosure policy.
- [ ] Record exact user authorization before any public upstream interaction.
