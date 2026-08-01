# Upstream pull-request draft — fix: stabilize lifecycle fanout targets

Draft status: `not ready`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

---

## Summary

- Attempt every trace or logs processor present when lifecycle fanout begins.
- Preserve eager invocation and existing outward error behavior.
- Clear the public trace provider's timeout after synchronous processor failure.

## Problem

`MultiSpanProcessor` and `MultiLogRecordProcessor` invoke processor lifecycle methods while iterating retained mutable arrays. A processor can remove a later processor before iteration reaches it. A direct synchronous throw can also stop construction of later promise inputs.

`TracerProvider.forceFlush()` is a separate public fanout that bypasses `MultiSpanProcessor.forceFlush()`. It maps the same live processor array and arms a timeout before invoking each processor. A synchronous throw bypasses the existing result catch and leaves that timeout armed.

## Change

- `MultiSpanProcessor`: snapshot the opening processor array and protect direct lifecycle calls with an eager try/catch helper while retaining its original outer promise and global-error-handler structure.
- `MultiLogRecordProcessor`: snapshot the opening processor array and protect direct calls while keeping timeout wrapping unchanged.
- `TracerProvider.forceFlush()`: snapshot the opening processor list and route synchronous invocation failure through the existing per-processor cleanup/result path.
- Add focused tests for direct throws, live removal, provider rejection shape, later invocation, and timer cleanup.

Metrics is intentionally absent. Its collector list is internally owned, the prior mutation tests used private-state casts, and collector lifecycle methods are already async.

## Behavior retained

- trace aggregate shutdown rejects;
- trace aggregate force flush reports through `globalErrorHandler` and resolves;
- public provider force flush rejects with its existing error-result array;
- logs reject;
- child calls start eagerly;
- original arrays remain mutable for future operations;
- `Promise.all` behavior remains.

## Tests

Exact successor head: `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`.

Repository workflows triggered on owned PR #19:

- Unit Tests `30694086716`;
- CodeQL Analysis `30694086713`;
- W3C Trace Context Integration Test `30694086725`;
- Zizmor GitHub Actions Security Analysis `30694086726`;
- Ensure API Peer Dependency `30694086723`;
- Bundler tests `30694086727`;
- E2E Tests `30694086733`;
- Lint `30694086746`.

## Compatibility

- public API/types unchanged;
- one shallow list copy per repaired lifecycle operation;
- eager start and package error policies retained;
- provider timeout behavior changes only by clearing a timer after synchronous failure;
- migration: none;
- rollback: revert the six-file patch.

## Changelog packaging

After an authorized public PR number exists, add:

```md
<!-- root CHANGELOG.md -->
* fix(sdk-trace): stabilize lifecycle processor fanout [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): stabilize lifecycle processor fanout [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Final wording and link format must be checked at submission time.

## Alternatives

- safe-call over live arrays still permits removal-based skipping;
- microtask deferral changes eager start ordering;
- permanent freezing changes future membership;
- sequential awaiting changes concurrency and latency;
- settle-all aggregation changes outward error semantics;
- repairing only the aggregate misses public provider force flush;
- retaining metrics would harden private state without supported reachability evidence.

## Limits

No settle-all error aggregation, child cancellation, retry, idempotence, delayed recursion handling, or post-shutdown telemetry admission changes are included.

---

## Submission checklist

- [x] source is based directly on public main `2c931bf4...`;
- [x] six target source/test files only;
- [x] metrics removed;
- [x] public provider force-flush path included;
- [x] timer cleanup regression included;
- [ ] exact successor matrix passes;
- [ ] eligible independent complete-diff review accepts the head;
- [ ] six contents-API commits are squashed;
- [ ] root and experimental changelog entries use the real PR number;
- [ ] duplicate/current-main and policy checks are repeated at filing time;
- [ ] explicit public-contact authorization is recorded.
