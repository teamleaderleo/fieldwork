# Unit 08 review and human inspection guide

## Review target

- Work class: upstream-fork research
- Clean source PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- Head: `54c17acaa1189bca3cf66da0bd9c22dae224b1ec`
- Complete diff: three files
- Current disposition: `REPAIR` pending clean-head ordinary gates and exact-head review
- Upstream contact authorized: `no`

## Complete-diff fence

Review only:

1. `playwright/async_api/_context_manager.py`;
2. `tests/async/test_async_stop_cancellation.py`;
3. `tests/async/test_async_stop_exit_contract.py`.

PR #7 is a retired base-drift comparison and must never be used for source review. PRs #3, #5, and #6 are historical evidence surfaces with stacked commits and temporary workflows.

## Self-review result

### Production ownership

- `_stop_task` is assigned before the first suspension.
- one event loop therefore installs one authoritative stop task without a lock.
- `asyncio.shield()` separates waiter cancellation from task cancellation.
- all later callers await the same completed or failed task.
- success and failure remain stable across repeated calls.

### Failure observation

- the done callback retrieves and stores a task failure;
- active waiters are counted;
- a waiter receiving failure marks it observed;
- zero waiters plus unobserved failure schedules one callback;
- a late waiter cancels that callback before joining;
- a post-report waiter still receives the task failure;
- reported and pending-handle flags prevent duplicate reports.

### Context-manager behavior

- body error waits for successful cleanup and then propagates;
- body cancellation enters `__aexit__`, waits for shielded cleanup, and then propagates;
- cleanup failure replaces the body error while preserving body error as exception context;
- direct `playwright.stop()` and `async with` use the same method.

### Current-base relation

Public upstream moved eight commits beyond the original base. The current upstream context-manager file remained unchanged. The candidate applies as a three-file diff against `3b7c24c...`.

## Claim-scoped evidence review

| Claim | Evidence | Review result |
| --- | --- | --- |
| old boolean loses joinable completion after cancellation | negative reproduction on Python 3.10/3.14 | supported |
| one shielded task fixes direct caller ownership | six focused controls | supported |
| context-manager cleanup and exception precedence remain coherent | four focused controls | supported |
| abandoned failure receives one fallback report and remains joinable | paired baseline fail and selected repair pass | supported |
| clean current-base branch passes ordinary gates | runs queued | pending |
| custom loop exception handler compatibility across supported versions | source/read plus Python 3.12 execution | review pending |

## Exact focused acceptance already retained

Historical selected head `beb025b6ee98e4b15b80335039f5d0afec5a7efd`:

- workflow `30595174700`;
- job `91045896030`;
- 33 passed, 2 warnings in 7.20s;
- Black passed;
- diff hygiene passed;
- independent review `4827700772`: ACCEPT for bounded mechanism.

That receipt does not automatically accept clean head `54c17ac...`; source equivalence and current-base execution still need exact-head judgment.

## Required clean-head review sequence

1. Inspect the complete PR #8 diff and confirm three-file scope.
2. Compare production and test blobs with selected PR #6, excluding the workflow.
3. Read every job in CI run `30674333313` and Docker run `30674333365`.
4. Confirm candidate assertions ran before interpreting a job result.
5. Record exact pytest, mypy, and pre-commit results.
6. Inspect custom event-loop exception context behavior under the project's supported Python range.
7. Confirm public upstream `main` has not moved or rebase and expire this review input.
8. Search current public issues and pull requests again.
9. Produce one exact-head disposition: ACCEPT, REPAIR, HOLD, or EXECUTE.
10. Update packet README, issue #149, PR #8, and #435 together.

## Failure classification guide

### Product failure

Examples:

- duplicate `Connection.stop_async()` calls;
- shared task cancelled by one waiter;
- late caller receives a different failure or success;
- loop handler receives zero or multiple abandoned-failure reports;
- body cancellation or body error returns before cleanup;
- typing or formatting error caused by the three changed files.

### Harness or repository failure

Examples:

- driver assembly or browser download failure before tests;
- unrelated existing test timeout after candidate controls passed;
- action permission or runner provisioning failure;
- stale base comparison that introduces unrelated files.

Record harness failures without upgrading or rejecting product claims.

## Compatibility questions for final reviewer

- Does `loop.call_exception_handler()` with `message`, `exception`, and `task` match project expectations and Python 3.10+ behavior?
- Should the message name Playwright, the context manager, or shutdown more narrowly?
- Should a late joiner after loop reporting still receive the same exception? Current policy says yes and tests it.
- Is one `call_soon` turn enough opportunity for a new waiter to suppress fallback reporting? Current policy says yes.
- Does the project prefer this manual report over retaining default never-retrieved behavior? The retained task requires an explicit route because the done callback retrieves the exception.

## Human deep-dive guide

Focus inspection on three questions:

1. **Ownership:** Can any timing create two stop tasks or let one caller cancel the shared task?
2. **Observation:** Can any failure path become silent, report twice, or disappear for a later caller?
3. **Precedence:** During `async with`, does cleanup completion or failure interact correctly with body cancellation/error?

Then review the narrower policy choice: one deferred loop report for a failed task with no current waiter.

## Current self-review disposition

`EXECUTE` the exact clean-head ordinary gates, then request independent review.

No source correction is requested from the current source read. Promotion remains blocked by pending execution and exact-head acceptance. No merge or public upstream interaction is authorized.
