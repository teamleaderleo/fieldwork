# Review — Unit 11: invoke all lifecycle processors

## Subject

- target: `open-telemetry/opentelemetry-js`;
- current public base: `2c931bf4eec18a234a28706567c6977f08139abd`;
- current source head: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- validation pull request: owned draft PR #19;
- relation: four commits ahead, zero behind;
- boundary: three production files and three target-native test files;
- public upstream authority: none.

The branch is intentionally unsquashed during the current repair/validation cycle. Final exact-head review must be repeated after squash.

## Disposition

`VALIDATING — technical direction retained; exact-head workflows running`

The finding is relevant and not already repaired on current public main. It is a bounded trace/logs specification-compliance and shutdown-reliability fix. The trigger is uncommon and mainly concerns custom processors or retained-array mutation, so it should not be presented as a high-severity or widespread telemetry-loss incident.

This is a technical self-review, not independent final acceptance.

## Change thesis

Current behavior:

- aggregate trace/log lifecycle fanout invokes children while building a promise collection from a retained mutable array;
- a direct synchronous throw can stop construction before later processors are invoked;
- synchronous removal can make live iteration skip an opening processor;
- public `TracerProvider.forceFlush()` uses a separate live-array fanout and leaves its timeout armed after a synchronous processor failure.

Consequence:

- a later processor can lose a required final flush or cleanup call;
- a stale provider timer can delay natural Node.js process termination until the configured timeout expires.

Proposed improvement:

- snapshot the opening processor set;
- preserve eager invocation while normalizing direct synchronous throws to rejections;
- preserve existing error and timeout contracts;
- clear provider timeouts after synchronous failure.

Boundary:

- trace and logs only;
- lifecycle methods only;
- no public API or normal telemetry delivery changes;
- no settle-all, retry, cancellation, or idempotence redesign.

## Findings by path

### Aggregate trace — accepted direction

- `MultiSpanProcessor.shutdown()` and `forceFlush()` take a shallow opening snapshot.
- The local helper invokes the callback immediately and converts only a direct throw into `Promise.reject(error)`.
- Eager call order is preserved; `Promise.resolve().then(callback)` was deliberately rejected because existing tests and behavior expect processors to be called before the aggregate method returns.
- Shutdown still rejects.
- Force flush still reports through `globalErrorHandler` and resolves.

### Public provider trace — accepted direction with precise mechanism

- `TracerProvider.forceFlush()` bypasses `MultiSpanProcessor.forceFlush()` and therefore needs its own repair.
- A direct processor throw occurs inside a Promise executor. The constructor catches it, so later `.map()` callbacks already run; the provider throw case must not be described as a later-invocation defect.
- The throw does bypass the existing `.catch()` that clears `timeoutInterval`. Routing it through the promise rejection path clears the timer and preserves the current error-array rejection.
- Mapping a shallow snapshot independently repairs synchronous live-array removal.
- A new control verifies that a genuinely pending processor still reaches the configured timeout.

### Logs — accepted direction

- `MultiLogRecordProcessor` exposes and retains a mutable processor array, so an operation-opening snapshot is appropriate.
- The safe call wraps both the processor invocation and existing `callWithTimeout` setup.
- Direct throws become rejections without delaying invocation.
- Returned promises retain their existing timeout behavior.
- Shutdown and force flush retain rejection semantics.

### Metrics — accepted exclusion

- `MetricCollector.shutdown()` and `forceFlush()` are async and already convert reader throws into rejected promises.
- `MeterProvider` constructs and owns its internal collector list.
- No supported post-construction collector removal route was found.
- The predecessor mutation tests required private-state casts and did not establish a supported runtime defect.

## Edge cases and side effects

### Covered

- first processor throws synchronously;
- first processor removes a later processor synchronously;
- later opening processors are still invoked where the baseline skipped them;
- package-specific outward failure behavior is preserved;
- provider error-array shape is preserved;
- provider synchronous failure clears its timer;
- provider pending work still times out;
- mutations remain visible to future lifecycle operations.

### Deliberately not changed

- a processor returning `undefined` or another type-invalid value;
- asynchronous array mutation after all eager calls have already begun;
- multiple asynchronous failures and first-error selection;
- waiting for every child after fail-fast `Promise.all` rejection;
- processor reentrancy, lifecycle idempotence, retry, or cancellation;
- synchronous telemetry delivery hooks such as `onStart`, `onEnd`, or `onEmit`.

### Cost/risk

- one O(n) shallow copy per repaired lifecycle call;
- lifecycle calls are infrequent relative to telemetry hot paths;
- no additional package dependency or exported helper;
- small risk that code relied on same-operation array removal to suppress a later lifecycle call; that behavior conflicts with the specification's all-registered-processor requirement and is not documented as a supported control mechanism.

## Codebase convention check

- conventional title remains under the repository's 72-character limit;
- production changes are local and avoid a speculative shared abstraction;
- tests use Mocha, `assert`, and Sinon patterns already present in the package suites;
- existing eager-call tests justify the local eager try/catch rather than microtask deferral;
- behavior changes require entries in both root `CHANGELOG.md` and `experimental/CHANGELOG.md` once a real upstream PR number exists;
- upstream issue and PR drafts follow the repository templates.

## Duplicate and relevance check

Current source still contains the vulnerable direct fanouts. Searches over upstream issues, pull requests, and commits found older force-flush propagation and provider-structure work, but no equivalent opening-snapshot plus synchronous-failure/timer-cleanup repair.

Custom processor interfaces are public extension points. OpenTelemetry-owned examples and packages contain custom span/log processors, supporting ecosystem relevance, but no claim is made that those specific implementations trigger this defect.

## Workflow status

Previous head `f4910b355d12895edf25372444f76d4def08901c` passed Unit, W3C, Bundler, API peer dependency, CodeQL, E2E, and Zizmor. Lint failed only on Prettier formatting in `TracerProvider.ts`.

Current head runs:

- Unit Tests `30755343888`;
- Lint `30755343692`;
- W3C Trace Context Integration `30755343695`;
- Bundler tests `30755343708`;
- Ensure API Peer Dependency `30755343685`;
- CodeQL Analysis `30755343693`;
- E2E Tests `30755343697`;
- Zizmor `30755343702`.

No current-head pass is claimed while those runs remain unsettled.

## Final-review checklist

- [x] current public source still contains the mechanism;
- [x] trace/log specification requirement identified;
- [x] metrics overclaim removed;
- [x] provider throw and mutation mechanisms distinguished;
- [x] genuine timeout compatibility control added;
- [x] public API and hot-path boundaries reviewed;
- [x] upstream issue and PR drafts rewritten to codebase conventions;
- [ ] exact-head workflow matrix passes;
- [ ] branch is squashed and complete diff is re-reviewed;
- [ ] independent reviewer accepts the squashed exact head;
- [ ] changelog entries contain a real upstream PR number;
- [ ] current-main and duplicate searches are repeated immediately before filing;
- [ ] explicit public-contact authority is recorded.

## Reviewer guide

1. Confirm the safe-call helper remains eager and does not broaden runtime validation beyond synchronous throws.
2. Confirm aggregate and provider snapshots repair distinct live-array iteration sites.
3. Confirm the provider throw test proves timer cleanup rather than falsely claiming baseline later-child skipping.
4. Confirm logs still apply `callWithTimeout` to returned lifecycle promises.
5. Confirm timeout, rejection, global-error, and opening-set controls match existing contracts.
6. Inspect the complete squashed diff rather than relying on this self-review.
