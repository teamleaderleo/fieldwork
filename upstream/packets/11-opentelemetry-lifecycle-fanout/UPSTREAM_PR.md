# Upstream pull-request draft — fix: stabilize lifecycle fanout targets

Draft status: `not ready`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

---

## Summary

- Attempt every trace or log processor present when shutdown or force flush begins.
- Protect direct processor calls from synchronous throws.
- Clear `TracerProvider.forceFlush()` timeouts after synchronous processor failure.
- Preserve eager fanout, existing error behavior, and future processor-array mutation.

## Problem

Trace and logs aggregates retain mutable processor arrays and invoke processors while iterating them. An earlier processor can remove a later opening processor, or throw before returning its declared promise, preventing later invocation.

Public `TracerProvider.forceFlush()` performs a separate live-array fanout instead of delegating to `MultiSpanProcessor.forceFlush()`. Its synchronous-throw path also bypasses normal timeout cleanup.

Metrics is not included: its collector list is internally constructed and the previous mutation test depended on private-state access.

## Change

- snapshot `MultiSpanProcessor` shutdown/force-flush targets and protect direct calls;
- snapshot `TracerProvider.forceFlush()` targets and route synchronous throws through its existing rejected-promise `.catch()` cleanup path;
- snapshot log processor targets and protect direct calls without moving timeout wrapping;
- add focused trace aggregate, trace provider, and logs tests.

## Behavior retained

- trace aggregate shutdown rejects;
- trace aggregate force flush reports globally and resolves;
- trace provider force flush retains its collected-error-array rejection;
- logs reject;
- calls begin eagerly;
- future operations observe processor-array mutation;
- first-rejection/result semantics remain.

## Tests

Exact clean head: `f4910b355d12895edf25372444f76d4def08901c`.

Queued workflows:

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

## Compatibility

- API/types unchanged;
- one shallow processor-list copy per affected operation;
- provider cleanup changes only a timeout with no useful owner after synchronous failure;
- no metrics behavior change;
- no migration; revert the one-commit six-file patch to roll back.

## Changelog packaging

After an authorized public PR number exists, add Unreleased Bug Fix entries:

```md
<!-- root CHANGELOG.md -->
* fix(sdk-trace): stabilize lifecycle fanout targets [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): stabilize lifecycle fanout targets [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Final wording remains maintainer-reviewable; do not invent a PR number on the owned carrier.

## Limits

No settle-all aggregation, cancellation, retry, idempotence, delayed recursion, or post-shutdown admission changes.

---

## Submission checklist

- [x] one commit directly on current public main;
- [x] three production and three test files only;
- [x] public provider force-flush path included;
- [x] metrics private-state-only path removed;
- [x] global-handler test cleanup repaired;
- [ ] exact successor matrix passes;
- [ ] independent complete-diff review accepts exact head;
- [ ] root and experimental changelog entries added with real PR number;
- [ ] duplicate/current-main and policies refreshed at filing time;
- [ ] explicit public-contact authorization recorded.
