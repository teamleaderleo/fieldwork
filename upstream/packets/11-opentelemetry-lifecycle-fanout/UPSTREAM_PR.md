# Upstream pull-request draft — fix: snapshot lifecycle targets before concurrent fanout

Draft status: `not ready`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

---

## Summary

- Snapshot the processors or collectors present when shutdown or force flush begins.
- Prevent direct synchronous trace/log processor throws from stopping later opening invocations.
- Preserve eager fanout, existing package-specific error behavior, and mutation for future operations.

## Problem

The trace, logs, and metrics lifecycle aggregates iterate mutable child arrays while starting lifecycle calls. A first child can remove a later indexed child before iteration reaches it, causing an opening child to be skipped.

Trace and logs invoke processors directly. A processor that throws before returning its declared promise also interrupts construction of later promise inputs.

Metrics differs: `MeterProvider` invokes async `MetricCollector` methods, so reader throws are already converted into rejected promises. Metrics only needs the opening snapshot.

## Change

- `MultiSpanProcessor`: copy the opening processor array and protect direct lifecycle calls with an eager try/catch helper. Keep the original outer promise and global-error-handler structure.
- `MultiLogRecordProcessor`: copy the opening processor array and protect direct calls while keeping timeout wrapping unchanged.
- `MeterProvider`: copy the opening collector array and call the existing async collector methods directly.
- Add focused shutdown and force-flush tests for direct throws where applicable and live removal in all three packages.

## Behavior retained

- trace shutdown rejects;
- trace force flush reports through `globalErrorHandler` and resolves;
- logs and metrics reject;
- child calls start eagerly before awaiting aggregate completion;
- original collections remain mutable for future operations;
- `Promise.all` retains first-rejection behavior.

## Tests

Exact repaired head: `1b7609141e87ad226e64bb0238ef602e76812896`.

Queued repository workflows:

- Unit Tests `30693695553`;
- E2E Tests `30693695548`;
- Lint `30693695562`;
- Bundler tests `30693695536`;
- W3C Trace Context Integration `30693695557`;
- Ensure API Peer Dependency `30693695533`;
- CodeQL Analysis `30693695552`;
- Zizmor GitHub Actions Security Analysis `30693695550`.

The previous clean head passed the complete named set. The repaired head must pass independently before this draft is ready.

## Compatibility

- public API/types: unchanged;
- allocation: one shallow list copy per lifecycle call;
- timing: existing eager start and package error policies retained;
- migration: none;
- rollback: revert the six-file patch.

## Changelog packaging

Target guidance requires behavior changes in both changelogs. After an authorized public PR number exists, add entries under Unreleased Bug Fixes using the repository's current link format, for example:

```md
<!-- root CHANGELOG.md -->
* fix(sdk-trace, sdk-metrics): attempt every opening lifecycle target [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): attempt every opening lifecycle processor [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Final wording should be checked against maintainer preference; do not invent a number on the owned validation carrier.

## Alternatives

- Safe-call over live arrays still permits removal-based skipping.
- A metrics safe-call duplicates the existing async collector boundary.
- Microtask deferral changes eager start ordering.
- Permanent freezing changes future membership.
- Sequential awaiting changes concurrency/latency.
- Settle-all aggregation changes outward error semantics.

## Limits

This patch does not provide settle-all error aggregation, child idempotence, retry, cancellation, final metrics collection, delayed recursion handling, or post-shutdown telemetry admission changes.

---

## Submission checklist

- [x] exact source is based directly on current public main `2c931bf4...`;
- [x] six target source/test files only;
- [x] metrics narrowed to snapshot-only;
- [x] trace outer promise/error-handler structure retained;
- [x] trace test global handler cleanup repaired;
- [ ] exact repaired-head matrix passes;
- [ ] eligible independent complete-diff review accepts the repaired head;
- [ ] ten contents-API commits are squashed;
- [ ] root and experimental changelog entries are added with the real PR number;
- [ ] duplicate/current-main and policy checks are repeated at filing time;
- [ ] explicit public-contact authorization is recorded.
