# Review — Unit 11: OpenTelemetry lifecycle fanout

## Final disposition

`SOURCE REVIEW ACCEPTED — SUBMITTED UPSTREAM`

The final patch is one signed commit over the submission base. It contains three production files, three regression-test files, and two changelog files. The complete diff remains limited to the reported lifecycle-fanout defect.

## Identity

- upstream issue: [#6977](https://redirect.github.com/open-telemetry/opentelemetry-js/issues/6977)
- upstream pull request: [#6980](https://redirect.github.com/open-telemetry/opentelemetry-js/pull/6980)
- submission base: `7f3e7eaa9f6bbc9622136479ed846f98c760a408`
- final head: `1e5bd20fb823a9c47a2b2ccc974e18d88b765f16`
- source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`
- commit count: one
- changed files: eight
- signature: verified locally
- sign-off: present
- AI assistance trailer: present
- EasyCLA: passing

## Technical review

### `MultiSpanProcessor`

- snapshots the opening processor set;
- invokes children eagerly;
- converts direct synchronous throws into rejected promises;
- preserves shutdown rejection;
- preserves force-flush global-error reporting and resolution;
- leaves normal span processing unchanged.

### `TracerProvider.forceFlush()`

- snapshots the direct fanout targets;
- keeps the per-call timeout option;
- routes direct throws through the existing catch path;
- clears the processor timer;
- preserves the existing error-array rejection;
- retains genuine timeout behavior.

### `MultiLogRecordProcessor`

- snapshots the retained processor list;
- protects direct lifecycle calls without microtask deferral;
- preserves timeout wrapping and rejection behavior.

### Test judgment

Eleven regression tests are appropriate for the three distinct implementations and their different outward policies. Trace and logs need separate coverage because they are maintained in separate packages. The provider tests cover the additional timer and error-array behavior.

## Validation judgment

Every workflow on the owned fork passed for the final signed head. The upstream runs are waiting for maintainer approval and have not produced failing jobs.

## Scope judgment

The patch includes:

- opening-set preservation;
- direct-throw normalization;
- provider timer cleanup;
- regression tests;
- required changelog entries.

The patch excludes metrics, retries, cancellation, settle-all aggregation, multi-error redesign, dependency changes, and public API changes.

## Recommendation

Leave the upstream pull request with reviewers. Make further changes only for a concrete review request, upstream movement that affects the patch, or an actual check failure.
