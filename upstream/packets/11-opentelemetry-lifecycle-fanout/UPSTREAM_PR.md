# Upstream pull-request draft

Proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`  
Draft status: `review-ready wording — exact-head validation pending`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Exact prepared head: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`  
Public interaction authorized: `no`  
Internal technical record: [`DEEP_DIVE.md`](./DEEP_DIVE.md)

The text between the dividers is the proposed public PR body. The issue should be filed and reviewed first; replace `#ISSUE` only after that issue exists. Internal workflow IDs, Fieldwork history, and superseded source generations do not belong in the public body.

---

## Which problem is this PR solving?

Trace and log lifecycle fanouts currently invoke processors while walking retained processor arrays.

A processor that throws synchronously before returning its declared promise can stop construction of the remaining promise inputs. A processor can also mutate the retained array during the call and cause another processor that was present when the operation began to be skipped.

`TracerProvider.forceFlush()` performs a separate timeout-wrapped fanout. A direct synchronous throw there is caught by the surrounding `Promise` constructor, so it does not stop later `.map()` callbacks, but it bypasses the returned-promise rejection handler that clears that processor's timeout.

The SDK lifecycle contract separates processor invocation from the operation result. Trace and logs require lifecycle calls to reach all registered processors, while the caller should still be told whether the operation succeeded, failed, or timed out. This change does not turn failure into success: a processor failure remains visible through each entrypoint's existing result policy, but it no longer suppresses unrelated processors' final export or cleanup opportunity.

If several operations are deliberately dependent, that dependency can be owned inside one composite processor rather than arising accidentally from a synchronous throw.

Fixes #ISSUE

## Short description of the changes

```text
lifecycle operation starts
    -> snapshot the current processor list
    -> invoke every processor in that snapshot, in order
    -> convert only direct synchronous throws into rejected promises
    -> preserve the entrypoint's existing error and timeout behavior
```

The implementation:

- snapshots trace and log processor lists before shutdown or force-flush fanout begins;
- invokes children eagerly through a small `try`/`catch` helper;
- snapshots the separate `TracerProvider.forceFlush()` target list;
- routes synchronous provider failures through the existing timeout-clearing and error-array path;
- preserves the current per-call trace timeout option and log timeout wrapping;
- adds regression coverage for direct throws, opening-set mutation, provider error shape, timeout cleanup, and genuine timeout behavior.

Metrics is intentionally out of scope. The comparable collector list is internally constructed, prior mutation controls required private-state access, and metric collector lifecycle methods are already `async`.

## Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How Has This Been Tested?

Eleven assertions cover:

- trace aggregate shutdown and force flush after a direct synchronous throw;
- log aggregate shutdown and force flush after a direct synchronous throw;
- opening-set mutation during each repaired aggregate operation;
- public trace-provider opening-set mutation;
- provider error-array preservation and timeout cleanup after synchronous failure;
- genuine provider timeout behavior for a processor that remains pending.

The exact candidate is being validated through the repository's Unit, Lint, W3C integration, Bundler, API peer-dependency, CodeQL, E2E, Zizmor, and old-Node-compatibility workflows.

## Compatibility and side effects

- No new public API, type, configuration, dependency, generated-output, or normal telemetry hot-path change.
- The current `forceFlush({ timeoutMillis })` API remains unchanged.
- One shallow array copy is added per affected lifecycle operation.
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
- [ ] Root and experimental changelog entries use this pull request's real number
- [ ] All commits are signed and CLA status is confirmed
- [ ] Exact-head workflows pass

## AI assistance disclosure

ChatGPT was used to assist with code exploration, implementation review, test preparation, and drafting. I reviewed the complete diff and validation results.

---

## Internal filing sequence

1. Finish and independently review the exact-head validation on the private source preview.
2. Reconfirm public `main`, package versions, contribution guidance, specification links, and overlap.
3. Obtain explicit authorization to file the reviewed issue draft.
4. Give maintainers an initial opportunity to confirm the combined trace/log scope and preferred test placement.
5. If maintainers respond, incorporate that direction. If there is no scope objection after a short review window, update this draft with the issue number and proceed to the PR decision.
6. Obtain separate explicit authorization to open the public PR.
7. Open the PR from the owned fork.
8. Add the two required changelog entries using the assigned PR number and rerun affected checks.

Required changelog lines:

```md
<!-- CHANGELOG.md -->
* fix(sdk-trace): invoke all lifecycle processors during flush and shutdown [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): invoke all lifecycle processors during flush and shutdown [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

Creating the issue, opening the PR, commenting, requesting reviewers, or otherwise contacting public upstream remains separately unauthorized.