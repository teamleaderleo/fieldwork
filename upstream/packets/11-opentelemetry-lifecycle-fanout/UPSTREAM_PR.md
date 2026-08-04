# Upstream pull-request draft — fix(sdk-trace, sdk-logs): invoke all lifecycle processors

## In simple words

This draft is technically prepared around one clean six-file source commit. It remains private because public upstream interaction has not been authorized. Exact-head CI is queued, and the repository owner decides whether the candidate advances.

Draft status: `ready for owner decision; public filing unauthorized`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Exact head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Pinned base snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`  
Public interaction authorized: `no`

---

## Summary

- Attempt every trace or log processor present when shutdown or force flush begins.
- Protect direct processor calls from synchronous throws.
- Clear `TracerProvider.forceFlush()` timeouts after synchronous processor failure.
- Preserve eager fanout, existing error behavior, genuine timeout behavior, and future processor-array mutation.

## Problem

Trace and logs aggregates retain mutable processor arrays and invoke processors while iterating them. An earlier processor can remove a later opening processor, or throw before returning its declared promise, preventing later invocation.

Public `TracerProvider.forceFlush()` performs a separate live-array fanout instead of delegating to `MultiSpanProcessor.forceFlush()`. Its synchronous-throw path also bypasses normal timeout cleanup.

Metrics is not included: its collector list is internally constructed and the previous mutation test depended on private-state access.

## Change

- snapshot `MultiSpanProcessor` shutdown and force-flush targets and protect direct calls;
- snapshot `TracerProvider.forceFlush()` targets and route synchronous throws through its existing rejected-promise cleanup path;
- snapshot log processor targets and protect direct calls without moving timeout wrapping;
- add focused trace aggregate, trace provider, and logs tests, including a real-timeout negative control.

## Behavior retained

- trace aggregate shutdown rejects;
- trace aggregate force flush reports globally and resolves;
- trace provider force flush retains its collected-error-array rejection;
- logs reject;
- calls begin eagerly;
- future operations observe processor-array mutation;
- genuine pending operations still time out;
- first-rejection and result semantics remain.

## Tests

Exact clean head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`.

Queued workflows:

- Unit Tests `30756036668`;
- Lint `30756036660`;
- W3C Trace Context Integration `30756036656`;
- Bundler tests `30756036678`;
- Ensure API Peer Dependency `30756036662`;
- CodeQL Analysis `30756036671`;
- E2E Tests `30756036639`;
- Zizmor GitHub Actions Security Analysis `30756036691`.

The clean commit reuses the exact six file blobs reviewed at pre-squash head `987a2bde097fe2e44531830e38c7c15a59c35c23`.

## Compatibility

- API and types unchanged;
- one shallow processor-list copy per affected operation;
- provider cleanup changes only a timeout with no useful owner after synchronous failure;
- no metrics behavior change;
- no migration;
- revert the one-commit six-file patch to roll back.

## Changelog packaging

After an authorized public PR number exists, add Unreleased Bug Fix entries:

```md
<!-- root CHANGELOG.md -->
* fix(sdk-trace): invoke all lifecycle processors [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): invoke all lifecycle processors [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Final wording remains maintainer-reviewable; do not invent a PR number on the owned carrier.

## Limits

No settle-all aggregation, cancellation, retry, idempotence, delayed recursion, or post-shutdown admission changes.

---

## Submission checklist

- [x] one commit directly on the pinned public-main snapshot;
- [x] three production and three test files only;
- [x] public provider force-flush path included;
- [x] metrics private-state-only path removed;
- [x] global-handler test cleanup repaired;
- [x] genuine-timeout negative control retained;
- [x] complete six-file diff technically reviewed;
- [ ] exact-head workflow matrix executes;
- [ ] root and experimental changelog entries added with real PR number;
- [ ] current main, duplicate/overlap, and policies refreshed at filing time;
- [ ] repository owner approves advancement;
- [ ] explicit public-contact authorization recorded.
