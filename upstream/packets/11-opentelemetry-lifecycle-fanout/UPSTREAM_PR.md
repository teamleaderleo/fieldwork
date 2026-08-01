# Upstream pull-request draft — fix: stabilize lifecycle fanout targets

Draft status: `not ready`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

## Summary

- Attempt every trace or logs processor present when lifecycle fanout begins.
- Preserve eager invocation and existing outward error behavior.
- Clear the public trace provider's timeout after synchronous processor failure.

## Problem

`MultiSpanProcessor` and `MultiLogRecordProcessor` invoke lifecycle methods while iterating retained mutable arrays. A processor can remove a later processor before iteration reaches it. A direct synchronous throw can also stop construction of later promise inputs.

`TracerProvider.forceFlush()` is a separate public fanout that bypasses aggregate force flush. It maps the same live processor array and arms a timeout before invoking each processor. A synchronous throw bypasses the existing result catch and leaves the timeout armed.

## Change

- snapshot and eager-safe-call aggregate trace shutdown/force flush;
- snapshot and eager-safe-call logs shutdown/force flush while retaining timeout wrapping;
- snapshot public provider force-flush targets and route synchronous failure through existing timeout cleanup/result handling;
- add focused throw, mutation, error-shape, later-invocation, and timer-cleanup tests.

Metrics is intentionally absent because its collector list is internally owned, the predecessor mutation tests used private-state casts, and collector lifecycle methods are already async.

## Behavior retained

- aggregate trace shutdown rejects;
- aggregate trace force flush reports globally and resolves;
- provider force flush retains its error-array rejection;
- logs reject;
- calls begin eagerly;
- future array mutation remains visible.

## Tests

Exact source: `f4910b355d12895edf25372444f76d4def08901c`.

Runs on owned PR #19:

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

## Compatibility

- public API/types unchanged;
- one shallow copy per repaired lifecycle operation;
- eager start and error policies retained;
- provider timeout behavior changes only by clearing a timer after synchronous failure;
- no migration.

## Changelog packaging

After an authorized public PR number exists:

```md
<!-- root CHANGELOG.md -->
* fix(sdk-trace): stabilize lifecycle processor fanout [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): stabilize lifecycle processor fanout [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

## Submission checklist

- [x] one commit directly on public main `2c931bf4...`;
- [x] six target source/test files only;
- [x] metrics excluded;
- [x] public provider path and timer cleanup included;
- [ ] exact workflow matrix passes;
- [ ] eligible independent review accepts the exact head;
- [ ] changelog entries use the real PR number;
- [ ] current-main, duplicate, contribution, and AI-disclosure checks are repeated;
- [ ] explicit public-contact authority is recorded.
