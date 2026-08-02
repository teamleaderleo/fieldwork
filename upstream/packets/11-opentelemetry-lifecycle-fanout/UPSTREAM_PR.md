# Upstream pull-request draft

Proposed title: `fix(sdk-trace, sdk-logs): invoke all lifecycle processors`  
Draft status: `validating in owned fork`  
Proposed head: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`  
Proposed base: `open-telemetry/opentelemetry-js:main`  
Public interaction authorized: `no`

## Which problem is this PR solving?

The trace and logs specifications require provider shutdown and force flush to invoke the operation on every registered processor.

`MultiSpanProcessor` and `MultiLogRecordProcessor` currently invoke lifecycle methods while constructing a promise collection from the retained processor array. A custom processor that throws before returning its declared promise stops that construction, so later processors are not invoked. Synchronous mutation of the retained array can likewise make live iteration skip a processor that was registered when the operation began.

`TracerProvider.forceFlush()` has a separate public fanout. Its Promise executor prevents a synchronous processor throw from stopping later `.map()` callbacks, but that throw bypasses the existing rejection handler that clears the processor timeout. The stale timer remains armed until expiry. This provider path also maps the live array, so synchronous removal can still skip a later opening processor.

The affected cases are unusual but consequential at shutdown: a skipped processor loses its final flush or cleanup opportunity, and the provider's referenced timeout can delay natural Node.js process termination. The change is limited to custom/third-party processor failure and mutation behavior; it does not imply ordinary built-in processors commonly fail this way.

Fixes #ISSUE

## Short description of the changes

- snapshot the opening processor set in aggregate trace and logs lifecycle fanout;
- invoke processors eagerly while converting direct synchronous throws into rejected promises;
- snapshot public `TracerProvider.forceFlush()` targets;
- route synchronous provider failure through the existing timeout cleanup and error-array result path;
- add focused regression tests for synchronous throws, opening-set mutation, error behavior, timer cleanup, and genuine timeout preservation.

Metrics is intentionally not changed. Metric collector lifecycle methods are already `async`, the provider owns its collector list internally, and no supported post-construction mutation route was established.

## Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How Has This Been Tested?

Focused unit coverage verifies:

- aggregate trace shutdown and force flush invoke later opening processors after a direct synchronous throw;
- aggregate logs shutdown and force flush do the same;
- synchronous removal does not shrink the current operation's opening set;
- aggregate trace shutdown still rejects;
- aggregate trace force flush still reports through the global error handler and resolves;
- logs still reject;
- public trace-provider force flush retains its one-error-array rejection;
- a synchronous provider failure leaves no timer armed;
- a genuinely pending provider processor still times out and rejects.

Owned-fork exact-head workflows are running on `987a2bde097fe2e44531830e38c7c15a59c35c23`:

- Unit Tests `30755343888`;
- Lint `30755343692`;
- W3C Trace Context Integration `30755343695`;
- Bundler tests `30755343708`;
- Ensure API Peer Dependency `30755343685`;
- CodeQL Analysis `30755343693`;
- E2E Tests `30755343697`;
- Zizmor GitHub Actions Security Analysis `30755343702`.

The preceding candidate passed every listed workflow except Lint. That failure was limited to Prettier formatting in `TracerProvider.ts`; the current head contains the formatting repair and an added timeout-preservation control.

## Compatibility and side effects

- no public API, type, configuration, or generated-output changes;
- no change to normal span or log delivery paths;
- one shallow `slice()` allocation per repaired lifecycle call;
- processor calls still begin eagerly and in existing order;
- additions/removals affect later operations, not an operation already in progress;
- existing fail-fast `Promise.all` behavior is retained;
- no retries, cancellation, `Promise.allSettled`, idempotence, or multi-error aggregation are added.

## Changelog entries

After a real upstream pull-request number exists:

```md
<!-- CHANGELOG.md -->
* fix(sdk-trace): invoke every processor during lifecycle fanout [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo

<!-- experimental/CHANGELOG.md -->
* fix(sdk-logs): invoke every processor during lifecycle fanout [#PR](https://github.com/open-telemetry/opentelemetry-js/pull/PR) @teamleaderleo
```

## Checklist

- [x] Followed the style and pull-request structure of this project
- [x] Unit tests have been added
- [x] Public API and compatibility impact have been reviewed
- [x] Unsupported metrics scope has been removed
- [x] Aggregate skip and provider timer defects are described separately
- [ ] Exact-head ordinary workflows pass
- [ ] Changelog entries contain the real pull-request number
- [ ] Current-main and duplicate searches are repeated immediately before filing
- [ ] Signed commit and CLA state are confirmed before filing
- [ ] Public interaction is explicitly authorized
