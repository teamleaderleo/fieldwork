# Playwright expected-failure cleanup result model — self-review

Date: 2026-07-30

Parent scout: #26

Central candidate: #142

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

A test can be expected to fail and still suffer a second, unrelated cleanup failure.

Today Playwright sees only one public result label: `failed`. Because that label matches the test's expected label, the dispatcher treats the whole attempt as expected. It does not retry the test, does not count the cleanup error as an unexpected final outcome, and may keep later accounting from seeing the independent failure.

The smallest credible answer is an internal per-result marker that says an unexpected runner, hook, fixture, or cleanup error occurred even though the public status string matches `expectedStatus`.

## Executed starting point

Owned probe PR `teamleaderleo/playwright#28` and execution PR `#29`, workflow run `30487755057`, configured:

- `test.fail()`;
- an expected body failure;
- a fixture cleanup exception;
- one retry.

The nested run printed:

```text
cleanup-0-worker-0
1 passed
```

Only attempt zero ran. No fresh worker appeared. The nested exit code was zero.

## Source trace

### Worker result

`WorkerMain` records body, hook, fixture, and cleanup errors in `TestInfo.errors`, then builds `TestEndPayload` from:

- public `status`;
- `errors`;
- `expectedStatus`;
- non-retriable-error state;
- annotations and timeout.

There is no field that says one error is independent of the expected body failure.

### Retry selection

`JobDispatcher._onTestEnd()` currently computes failure as:

```ts
result.status !== 'skipped' && result.status !== test.expectedStatus
```

Only those tests enter `_failedTests`. Retry candidates are later built from `_failedTests`.

A worker-stop flag can replace the process, but it cannot place a matching-status test into the retry set.

### Serial suites

Serial-suite retry and future-test skipping are derived from `_failedTests` and its serial parents. An unexpected cleanup error must participate in that path or a serial group can be treated as healthy after an independent fixture failure.

### Max failures

`_reportTestEnd()` increments the failed-test count only when `test.outcome()` is `unexpected` after the last retry.

### Final outcome and merged reports

`computeTestCaseOutcome()` classifies each result using the same equality:

```ts
result.status === test.expectedStatus
```

This function is used by live test cases and tele-received or merged report test cases. A marker that exists only in worker memory or live IPC would disappear when blob reports are merged or replayed.

## Selected design boundary

Add one internal per-result boolean, provisionally named `_hasUnexpectedError` in live objects and `hasUnexpectedError` in internal payloads.

The marker means:

> At least one error in this attempt is unexpected independently of the test's declared expected status.

It does not replace `status`, `expectedStatus`, or the error list.

## Required propagation

The marker must travel through:

1. `TestInfoImpl`, where independent hook, fixture, cleanup, and runner errors are classified;
2. worker `TestEndPayload`;
3. dispatcher `TestResult` internal state;
4. retry candidate selection;
5. serial-suite failure propagation;
6. final `computeTestCaseOutcome()` classification;
7. max-failure counting;
8. blob and telemetry result-end serialization;
9. tele-received and merged report result objects.

Reporters may continue receiving the same public status and complete error list. No public reporter field is required for the first implementation slice.

## Classification rule

The difficult part is not transporting the boolean. It is deciding when to set it.

A minimal first slice should distinguish phases:

- an expected body assertion or exception remains covered by `test.fail()`;
- an error beginning in `afterEach`, test-fixture teardown, deferred cleanup recovery, `afterAll`, worker-fixture teardown, tracing finalization, or runner-owned cleanup sets the marker;
- setup and body errors retain current expected-status semantics unless another independent error occurs;
- timeout status remains public when the attempt actually timed out;
- one cleanup error does not erase or replace the original body error.

The implementation should use explicit error origin or phase at the point errors are recorded. Inferring origin later from message text, stack frames, or error order is unsafe.

## Outcome rule

For one result:

```text
unexpected = hasUnexpectedError
  OR (status is not skipped AND status differs from expectedStatus)
```

`computeTestCaseOutcome()` then uses this result-level unexpected classification instead of status equality alone.

This preserves:

- expected failure when only the expected body failure occurred;
- unexpected outcome when cleanup independently failed;
- flaky outcome when a retry later resolves both the body expectation and cleanup;
- existing public status strings.

## Why other options were rejected

### Force `timedOut`

This triggers retries but misstates failures that threw immediately and couples lifecycle accounting to a public label.

### Force `failed`

The public status is already `failed`, so this does not distinguish the independent error.

### Stop the worker only

This protects later tests but does not create a retry candidate or unexpected final outcome.

### Global worker error

This loses test attribution, reporter context, retry ownership, and serial-suite semantics.

### Inspect the second error

Error order is not a stable contract. Multiple body assertions, hook errors, tracing errors, and cleanup errors can coexist.

### Add a public status value

A new public status would affect reporters, APIs, compatibility, and user expectations. The confirmed need is internal accounting, not a new user-facing lifecycle vocabulary.

## Regression matrix

### Expected body behavior

- expected body failure only: no retry, expected outcome;
- expected body failure plus cleanup failure: retry and fresh worker;
- retry with expected body failure and successful cleanup: flaky or expected according to retained attempt semantics;
- unexpected body pass under `test.fail()`: remains unexpected.

### Cleanup origins

- `afterEach` failure;
- test-fixture teardown failure;
- deferred cleanup timeout or failure;
- `afterAll` failure attributable to the current attempt;
- tracing or artifact finalization failure;
- worker-fixture teardown, with explicit decision about test attribution versus worker-level error.

### Runner behavior

- immediate and isolated retry strategies;
- serial-suite retry and future-test skipping;
- `maxFailures: 1`;
- `failOnFlakyTests`;
- output preservation;
- worker replacement;
- reporter event order and complete errors.

### Durable reporting

- blob report creation and merge;
- JSON and HTML outcome consistency;
- tele-received report outcome;
- backward compatibility when older reports omit the marker.

Older report data should default `hasUnexpectedError` to `false`.

## Self-review disposition

Disposition: **accept invariant; revise implementation boundary**

Evidence checked:

- exact expected-body-plus-cleanup negative reproduction;
- worker test-end construction;
- dispatcher failure and retry selection;
- serial-suite handling;
- max-failure counting;
- final outcome computation;
- tele-received report path.

Strongest supported conclusion:

An independent cleanup error must be represented as internal per-result unexpectedness and serialized through live and durable result paths. A worker-only signal or public status mutation cannot satisfy the confirmed behavior.

Missing proof:

- phase-aware classification is not implemented;
- blob compatibility is not executed;
- reporter, serial-suite, and max-failure regressions are not yet retained;
- `afterAll` and worker-fixture attribution need explicit ownership decisions.

Required next action:

Implement a test-only payload and outcome prototype with phase-origin controls before changing fixture recovery production code.

Next owner: independent Playwright result-model reviewer or a bounded implementation lane.

Upstream contact authorized: no.
