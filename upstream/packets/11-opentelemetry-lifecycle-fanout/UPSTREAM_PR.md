# Upstream pull-request draft — fix: snapshot lifecycle targets before concurrent fanout

Draft status: `not ready`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

---

## Summary

- Attempt every processor or collector present when shutdown or force flush begins.
- Protect direct trace/log processor calls from synchronous throws.
- Clear `TracerProvider.forceFlush()` timeouts when a processor throws synchronously.
- Preserve eager fanout, existing error behavior, and future collection mutation.

## Problem

Several lifecycle entrypoints iterate live child arrays while starting work. An earlier child can remove a later opening child before its index is reached.

`MultiSpanProcessor` and `MultiLogRecordProcessor` directly call child methods, so a synchronous throw can stop later invocation. Public `TracerProvider.forceFlush()` performs a separate processor fanout instead of delegating to `MultiSpanProcessor.forceFlush()`; its synchronous-throw path also leaves the already-armed timeout pending.

Metrics calls async `MetricCollector` methods, so metrics needs only the opening snapshot.

## Change

- snapshot `MultiSpanProcessor` shutdown/force-flush targets and protect direct calls;
- snapshot `TracerProvider.forceFlush()` targets, catch synchronous call/then failures, clear the timeout, and retain the existing result-array rejection model;
- snapshot log processor targets and protect direct calls without moving timeout wrapping;
- snapshot metric collectors and call their async lifecycle methods directly;
- add focused aggregate/provider/logs/metrics tests.

## Behavior retained

- trace aggregate shutdown rejects;
- trace aggregate force flush reports globally and resolves;
- trace provider force flush rejects with its collected error/result array;
- logs and metrics reject;
- calls begin eagerly;
- future operations observe collection mutation;
- first-rejection/result semantics remain.

## Tests

Exact clean head: `59f83f889bed06a951d458556b2e7e1695cbea10`.

Queued workflows:

- Unit `30694080939`;
- E2E `30694080935`;
- Lint `30694080925`;
- Bundler `30694080933`;
- W3C `30694080910`;
- API peer dependency `30694080929`;
- CodeQL `30694080926`;
- Zizmor `30694080955`.

## Compatibility

- API/types unchanged;
- one shallow list copy per affected operation;
- provider timeout cleanup changes only the obsolete synchronous-failure timer;
- no migration;
- revert the one-commit eight-file patch to roll back.

## Changelog packaging

After an authorized public PR number exists, add Unreleased Bug Fix entries:

```md
<!-- root CHANGELOG.md -->
* fix(sdk-trace, sdk-metrics): attempt every opening lifecycle target [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): attempt every opening lifecycle processor [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Final wording and subject grouping remain maintainer-reviewable; do not invent a PR number on the owned carrier.

## Limits

No settle-all aggregation, cancellation, retry, idempotence, final metric collection, delayed recursion, or post-shutdown admission changes.

---

## Submission checklist

- [x] one commit directly on current public main;
- [x] four production and four test files only;
- [x] public trace provider force-flush path included;
- [x] metrics narrowed to snapshot-only;
- [x] global handler test cleanup repaired;
- [ ] exact final-head matrix passes;
- [ ] independent complete-diff review accepts the exact head;
- [ ] root and experimental changelog entries added with real PR number;
- [ ] duplicate/current-main and policies refreshed at filing time;
- [ ] explicit public-contact authorization recorded.
