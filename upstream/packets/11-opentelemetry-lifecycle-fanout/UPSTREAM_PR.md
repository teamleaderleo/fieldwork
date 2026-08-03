# Upstream pull-request draft

Proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`  
Draft status: `review-ready — file only after issue review and explicit authorization`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Canonical owned head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`  
Public interaction authorized: `no`

The text below is the proposed public PR body. Internal workflow IDs, Fieldwork terminology, superseded branches, and validation-carrier history are intentionally omitted.

---

## Which problem is this PR solving?

The trace and logs SDK specifications require provider shutdown and force flush to invoke the operation on every registered processor.

`MultiSpanProcessor` and `MultiLogRecordProcessor` currently invoke lifecycle methods while constructing a promise collection from a retained processor array. A custom processor that throws before returning its declared promise stops that construction, so later processors are not invoked. Synchronous mutation of the retained array can likewise make live iteration skip a processor that was registered when the operation began.

`TracerProvider.forceFlush()` performs a separate public fanout. A direct synchronous throw is caught by its Promise constructor, so it does not stop later `.map()` callbacks, but it bypasses the existing rejection handler that clears the processor timeout. This path also maps the live processor array, so synchronous removal can skip a later opening processor.

The affected cases are unusual but meaningful at shutdown: a skipped processor can lose its final flush or cleanup opportunity, and the provider's referenced timeout can delay natural Node.js process termination after failure has already been reported.

Fixes #ISSUE

## Short description of the changes

- Snapshot the processor set when aggregate trace and logs lifecycle work begins.
- Invoke processors eagerly in the existing order while converting direct synchronous throws into rejected promises.
- Snapshot public `TracerProvider.forceFlush()` targets and route synchronous failures through its existing timeout cleanup and error-array handling.
- Preserve the existing settlement policy of each surface, including genuine timeout behavior.
- Add focused regression coverage for direct throws, opening-set mutation, provider error shape, timer cleanup, and genuine timeout behavior.

Metrics is intentionally not changed. Metric collector lifecycle methods are already `async`, the provider owns its collector list internally, and no supported post-construction mutation path was established.

## Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How Has This Been Tested?

Focused unit tests cover:

- aggregate trace shutdown and force flush after a direct synchronous throw;
- aggregate logs shutdown and force flush after a direct synchronous throw;
- opening-set mutation during each repaired aggregate operation;
- public trace-provider opening-set mutation;
- the provider's existing error-array shape and timeout cleanup after synchronous failure;
- genuine provider timeout behavior for a processor that remains pending.

The exact candidate passed the repository's:

- Unit Tests;
- Lint;
- W3C Trace Context Integration Test;
- Bundler tests;
- API peer-dependency check;
- CodeQL Analysis;
- E2E Tests;
- Zizmor GitHub Actions security analysis.

## Compatibility and side effects

- No public API, type, configuration, dependency, generated-output, or normal telemetry hot-path change.
- One shallow array copy per repaired lifecycle operation.
- Processor calls still begin eagerly and in the existing order.
- Mutations affect later operations, not the operation already in progress.
- Aggregate trace shutdown still rejects.
- Aggregate trace force flush still reports through the global error handler and resolves.
- Logs still reject.
- Public trace-provider force flush still rejects with an error array.
- Genuinely pending provider operations still time out.
- No `Promise.allSettled`, retries, cancellation, idempotence, malformed non-Promise return validation, or multi-error redesign.

## Checklist

- [x] Followed the style guidelines of this project
- [x] Unit tests have been added
- [x] Documentation is not required because no public API or configuration changes
- [ ] Root and experimental changelog entries use the real pull-request number
- [ ] Commits are signed and CLA status is confirmed

## AI assistance disclosure

ChatGPT was used to assist with code exploration, implementation review, test preparation, and drafting. I reviewed the complete diff and the validation results.

---

## Filing notes — not part of the public PR body

### Recommended sequence

1. File the reviewed bug issue first.
2. Let maintainers confirm that one cross-signal PR is an acceptable scope.
3. Refresh the source branch onto the then-current public `main` if it moved.
4. Open the PR from the fork and replace `#ISSUE` with the accepted issue number.
5. Once the real PR number exists, add both required changelog entries and rerun the affected checks.
6. Confirm commit signing and CLA status before requesting review.

### Required changelog entries

```md
<!-- CHANGELOG.md -->
* fix(sdk-trace): invoke all lifecycle processors [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): invoke all lifecycle processors [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

### Why issue first

A direct PR would be technically possible, but issue-first is recommended because the report spans stable trace, experimental logs, and two distinct JavaScript failure mechanisms. An issue lets maintainers confirm the combined scope, test placement, and wording before a public PR and before PR-number-dependent changelog commits are added.

### Remaining preflight

- [ ] user approves the issue wording;
- [ ] user approves the PR wording;
- [ ] explicit authority is granted for the exact public interaction;
- [ ] current-main and overlap searches are refreshed immediately before filing;
- [ ] contribution guide, CLA, commit-signing, and disclosure expectations are rechecked;
- [ ] issue and PR placeholders are replaced with real numbers.
