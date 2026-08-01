# Unit 08 review and human inspection guide

## Review target

- Work class: upstream-fork research
- Canonical source PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Public base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- Clean source head: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- Clean compare: 5 commits, exactly 3 files, 467 additions, 6 deletions
- Current disposition: `REPAIR`
- Upstream contact authorized: `no`

The canonical source branch is restored to the clean head. No workflow, generated file, or dependency change remains on it.

## Complete-diff fence

Review only:

1. `playwright/async_api/_context_manager.py`;
2. `tests/async/test_async_stop_cancellation.py`;
3. `tests/async/test_async_stop_exit_contract.py`.

PR #7 is a retired base-drift comparison and must not be used for clean-source review. PRs #3, #5, and #6 are historical evidence surfaces. PRs #9 through #13 are closed execution-only carrier attempts.

## Worker complete-diff review

### Production ownership

- `_stop_task` is assigned before the first suspension.
- one event loop installs one authoritative stop task without a lock.
- `asyncio.shield()` separates caller cancellation from task cancellation.
- concurrent and later callers await the same task.
- repeated callers receive one stable terminal result.

### Failure observation

- the done callback retrieves and stores task failure;
- active waiters are counted;
- a waiter receiving failure marks it observed;
- zero waiters plus unobserved failure schedules one deferred callback;
- a late waiter cancels a pending callback before joining;
- a post-report waiter still receives the original task failure;
- report and pending-handle flags prevent duplicate reports.

### Loop exception context

The fallback report supplies:

```python
{
    "message": "Playwright stop task failed",
    "exception": self._stop_failure,
    "task": self._stop_task,
}
```

The clean test asserts message, exact exception identity, and authoritative task identity. The shape follows the event-loop exception-handler context convention. Current-head execution of the new task-identity assertion remains unavailable because hosted jobs never started.

### Context-manager behavior

- body error waits for successful cleanup and then propagates;
- body cancellation waits for shielded cleanup and then propagates;
- cleanup failure takes precedence while preserving body error as context;
- direct `playwright.stop()` and `async with` share the same stop path.

### Current-base relation

The public context-manager file remained unchanged across the eight upstream commits after the original base. Exact compare `3b7c24c...1ac8797` confirms only the fenced three files.

## Repairs completed during continuation

1. Reclassified runs `30674333313` and `30674333365` as base-drift evidence because they checked out closed PR #7.
2. Removed an unused mypy suppression at `33cbc587830d2083d43dcdf67339696634c24936`.
3. Added authoritative task identity coverage at `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`.
4. Removed Test Docker as a false blocker because its path filters do not match unit 08.
5. Re-read the exact final diff; no additional production correction was found.
6. Removed all temporary workflows from the canonical source branch and closed every carrier PR.

## Claim-scoped review

| Claim | Evidence | Review result |
| --- | --- | --- |
| old boolean loses joinable completion after cancellation | negative reproduction on Python 3.10/3.14 | supported |
| one shielded task fixes direct ownership | six focused controls | supported |
| context-manager cleanup and precedence remain coherent | four focused controls | supported |
| abandoned failure receives one report and remains joinable | paired baseline fail and selected repair pass | supported |
| report context identifies the authoritative task | exact clean-source assertion | source-supported; current-head execution blocked |
| clean source is limited to intended scope | exact compare and PR #8 metadata | supported |
| current-head full pre-commit and 3-version focused gate | preserved carrier, no runner allocated | unexecuted |
| independent clean-head review | none | blocked |

## Executed receipts retained

### Negative reproduction

- run `30492906544`
- Python 3.10 job `90714870057`
- Python 3.14 job `90714870025`
- both fail the intended incomplete-cleanup assertion

### Paired focused comparison

Baseline:

- run `30595155697`, job `91045840683`
- 30 passed, 3 intended abandoned-failure failures
- Black and diff hygiene passed

Selected repair:

- run `30595174700`, job `91045896030`
- 33 passed, 2 warnings in 7.20s
- Black and diff hygiene passed
- review `4827700772`: ACCEPT for bounded mechanism

### Clean-source partial gate

- run `30690680740`
- exact source `1ac8797...`
- Examples job `91344746297`: passed
- remaining broad matrix cancelled to release the serial runner; no broad claim

## Preserved current-head gate

- branch: `upstream/08-playwright-python-exact-gate-0b34782a`
- carrier commit: `0b34782a2c2dd4f708ef542e2eb80e71a1d249b3`
- clean source ancestor: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- carrier-only path: `.github/workflows/ci.yml`
- execution PR #13: closed

Planned sequential gate:

1. Python 3.10 wheel build, full repository pre-commit, all 11 tests;
2. Python 3.12 wheel build and all 11 tests;
3. Python 3.14 wheel build and all 11 tests;
4. reruns disabled and tracked diff hygiene.

Jobs remained queued and never entered setup across Ubuntu 24.04, Ubuntu 22.04, `ubuntu-latest`, and Ubuntu 24.04 ARM. Final identities are recorded in `TESTS.md`. This is an infrastructure/runner blocker, not an observed product failure.

## Failure classification guide

### Product failure

- duplicate `Connection.stop_async()` calls;
- shared task cancelled by one waiter;
- later caller receives a different outcome;
- abandoned failure is silent or reported more than once;
- body cancellation/error returns before cleanup;
- typing or formatting error in the three changed files.

### Harness or repository failure

- runner never allocated;
- setup or driver assembly fails before candidate tests;
- unrelated existing suite timeout after candidate controls pass;
- stale comparison introduces unrelated files;
- execution-only workflow defect.

Harness failures do not upgrade or reject product claims.

## Independent reviewer questions

1. Is the loop message `Playwright stop task failed` appropriately scoped?
2. Should a late joiner after reporting still receive the same exception? Current policy says yes.
3. Is one `call_soon` turn an appropriate observation window? Current policy says yes.
4. Does the project prefer explicit loop reporting over default never-retrieved behavior for a retained task?
5. Should authoritative task cancellation itself be addressed in a separate unit?

## Final worker disposition

`REPAIR`

The source and regression-test corrections identified by this continuation are complete. No further production-code change is requested by the worker review. Promotion is blocked by:

1. current-head execution of the preserved pre-commit/Python 3.10/3.12/3.14 gate;
2. independent human complete-diff review;
3. explicit authority before any public upstream interaction.

No merge or public upstream action is authorized.
