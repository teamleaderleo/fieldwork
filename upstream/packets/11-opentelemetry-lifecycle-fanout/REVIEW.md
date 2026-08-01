# Review — Unit 11: snapshot lifecycle targets before concurrent fanout

## Review subject

- target: `open-telemetry/opentelemetry-js`;
- public base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- repaired source head: `1b7609141e87ad226e64bb0238ef602e76812896`;
- source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout`;
- changed-file fence: three production files and three test files;
- compare relation: ahead 10, behind 0;
- upstream-contact authority: none.

## Disposition

`HOLD — source repair complete, exact-head validation pending`

The prior `REPAIR` finding is addressed. This self-review finds no additional product defect in the repaired six-file diff. Promotion still requires successful exact-head workflows and an eligible independent complete-diff acceptance.

## Complete-diff findings

### Trace

Accepted direction:

- opening snapshot prevents current-operation membership loss;
- local eager try/catch converts direct synchronous processor throws into rejected promises;
- original promise array, outer `new Promise`, shutdown rejection, force-flush error reporting, and force-flush resolution structure are preserved;
- focused tests cover throw and removal paths.

The deeper pass intentionally removed the earlier outer-promise refactor, reducing semantic review surface.

### Logs

Accepted direction:

- opening snapshot protects the public processor array against removal during lifecycle invocation;
- direct processor calls need safe-call protection;
- `callWithTimeout` placement, default timeout, rejection behavior, and eager fanout remain unchanged;
- focused tests cover both mechanisms for shutdown and force flush.

### Metrics

Accepted repaired direction:

- `metricCollectors.slice()` is required for stable opening membership;
- direct calls to async `MetricCollector.shutdown()` / `forceFlush()` are sufficient;
- the redundant metrics `callLifecycle` helper is removed;
- metrics direct-throw tests are removed because they are baseline-compatible rather than reversing controls;
- mutation tests remain and use typed internal collector access.

### Test isolation

Accepted repair:

- the trace test now restores `loggingErrorHandler()` rather than installing the `loggingErrorHandler` factory;
- this matches the repository's existing `MultiSpanProcessor.test.ts` convention and avoids global handler leakage.

## Exact-head validation

Queued on `1b7609141e87ad226e64bb0238ef602e76812896`:

- Unit Tests `30693695553`;
- E2E Tests `30693695548`;
- Lint `30693695562`;
- Bundler tests `30693695536`;
- W3C Trace Context Integration `30693695557`;
- Ensure API Peer Dependency `30693695533`;
- CodeQL Analysis `30693695552`;
- Zizmor GitHub Actions Security Analysis `30693695550`.

The previous exact clean head passed all groups, but those receipts are superseded by the repair.

## Source cleanliness

- [x] only six target source/test files changed;
- [x] no workflows, publishers, dependency files, lockfiles, generated output, or research vocabulary;
- [x] public main still equals the pinned base;
- [x] open issue/PR searches found no replacement work during the repair pass;
- [x] product claims now distinguish trace/log direct-call behavior from the metrics async boundary;
- [ ] exact repaired-head matrix completed;
- [ ] contents-API commit series squashed;
- [ ] changelog entries added with a real upstream PR number;
- [ ] eligible independent reviewer accepted the exact repaired head.

## Compatibility review

- public API/types: unchanged;
- outward behavior: unchanged except later opening children are no longer skipped;
- concurrency: eager `Promise.all` retained;
- allocation: one shallow array copy per lifecycle call;
- future collection mutation: retained;
- first-rejection policy: retained;
- trace global error reporting/resolution: original code structure retained;
- logs timeout semantics: retained;
- metrics async throw conversion: baseline behavior retained without duplicate wrapping.

## Independent reviewer guide

Review these questions against the exact repaired compare:

1. Does the trace helper preserve eager invocation without altering outer promise/error behavior?
2. Is logs timeout wrapping still exactly where maintainers expect it?
3. Is metrics correctly limited to snapshot-only because the collector methods are async?
4. Do mutation tests prove both current-operation stability and future mutation visibility?
5. Are separate root and experimental changelog entries required, and is the proposed wording appropriate?

## Remaining blockers

1. repaired-head workflows are not yet complete;
2. independent exact-head review is pending;
3. ten contents-API commits should be squashed before public submission;
4. target changelog entries need the real upstream PR number;
5. current-main and duplicate search must be repeated at filing time;
6. public upstream interaction remains unauthorized.

## Reviewer eligibility

This is a technical self-review by the worker that repaired the branch. It can require changes and record evidence, but it is not independent final acceptance.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
