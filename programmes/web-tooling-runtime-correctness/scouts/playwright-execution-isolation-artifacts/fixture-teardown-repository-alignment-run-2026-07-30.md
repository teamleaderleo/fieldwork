# Playwright fixture teardown — repository alignment runs

Date: 2026-07-30

No upstream contact occurred.

## Summary

Repository-history review changed one important part of the lead intervention.

The dependency-group scheduler remained valid, but retrying retained test fixtures only during later Worker Cleanup violated Playwright's existing `afterAll` fixture-isolation contract.

The corrected design performs bounded deferred test-fixture recovery before `afterAll` and reuses the same cleanup slot afterward.

## Negative ordering control

| Field | Value |
|---|---|
| Probe PR | `teamleaderleo/playwright#22` |
| Execution PR | `#23` |
| Workflow run | `30485904509` |
| Job | `90691366536` |
| Result | expected failure |

Observed order:

```text
resource-setup-1
test-resource-1
afterAll-resource-1
afterAll-saw-test-resource-closed-false
resource-teardown-1
```

The retained fixture from the failed test was reused by `afterAll` before teardown. A fresh second fixture was never created.

Decision: reject retry placement solely in later Worker Cleanup.

## Corrected ordering intervention

| Field | Value |
|---|---|
| Source PR | `teamleaderleo/playwright#24` |
| Execution PR | `#25` |
| Workflow run | `30486881047` |
| Job | `90694673635` |
| Runner | Ubuntu 24.04, Node 22, one worker |

The source change:

1. creates one full-cleanup slot using the existing project timeout;
2. spends the test-fixture portion before `afterAll` when After Hooks leave cleanup debt;
3. reuses the same slot during later Worker Cleanup;
4. leaves dependency-group scheduling unchanged;
5. does not extend the total cleanup deadline.

Results:

```text
11 passed (22.9s)
```

The campaign suite covered retention, retry worker replacement, independent fairness, dependency safety, recovery diagnostics, four receipt states, and fresh `afterAll` fixture isolation.

The repository's existing regression also passed:

```text
should run fixture teardown with custom timeout after afterEach timeout
1 passed (4.5s)
```

Confidence: high for the tested Ubuntu/Node 22 ordering intervention.

## Internal receipt alignment

| Field | Value |
|---|---|
| Source PR | `teamleaderleo/playwright#26` |
| Execution PR | `#27` |
| Workflow run | `30487474207` |
| Job | `90696663923` |
| Runner | Ubuntu 24.04, Node 22, one worker |
| Result | 11 passed in 22.8s |

Changes:

- attachment renamed from `fixture-cleanup` to `_fixture-cleanup`;
- phase renamed from `worker-cleanup` to `deferred-test-fixture-recovery`;
- each entry now includes opaque registration id, fixture name, and source location;
- budget and four-state vocabulary remain unchanged.

The underscore name follows existing built-in reporter behavior: terminal and HTML reporters hide internal underscore-prefixed attachments while custom reporters can consume them.

## Current lead wording

### Problem

> When the shared After Hooks timeout is already exhausted, Playwright can skip a test fixture finalizer and remove the fixture from the registry, preventing bounded recovery and suppressing artifacts or resource cleanup.

### Intervention

> Retain only never-started finalizers, recover them by dependency group within one existing cleanup budget before `afterAll`, reuse the remaining budget for worker cleanup, and emit an internal receipt before `testEnd`.

### Promise level

The intervention provides bounded recovery opportunities and explicit incomplete-cleanup reporting. It does not guarantee that stalled user callbacks complete.

## Remaining outcome-accounting question

A test marked with `test.fail()` may still absorb a separate fixture cleanup exception because public outcome calculation compares `status` with `expectedStatus`.

Retained probe:

- `teamleaderleo/playwright#28`
- execution PR `#29`

The required invariant is that cleanup failure remains unexpected, triggers retry in a fresh worker, and causes the final run to fail even when the body failure was expected.
