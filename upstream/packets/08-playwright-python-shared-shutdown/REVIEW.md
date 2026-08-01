# Unit 08 review and human inspection guide

## Review target

- Work class: upstream-fork research
- Clean source PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- Clean product/test head: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- Complete clean diff: three files, five commits, 467 additions, 6 deletions
- Current disposition: `REPAIR` pending the active exact-head execution receipt and independent human review
- Upstream contact authorized: `no`

The canonical branch is temporarily carrying an execution-only workflow commit while run `30691125773` is active. The clean source commit above is preserved and must be restored to the canonical branch after the run is classified.

## Complete-diff fence

Review only:

1. `playwright/async_api/_context_manager.py`;
2. `tests/async/test_async_stop_cancellation.py`;
3. `tests/async/test_async_stop_exit_contract.py`.

Exact compare `3b7c24c...1ac8797` confirms only those three files. PR #7 is a retired base-drift comparison and must never be used for clean-source review. PRs #3, #5, and #6 are historical evidence surfaces with stacked commits and temporary workflows. PRs #9, #10, #11, and #12 are execution-only carriers or failed carrier designs.

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

### Loop exception context

The manual report passes:

```python
{
    "message": "Playwright stop task failed",
    "exception": self._stop_failure,
    "task": self._stop_task,
}
```

This is compatible with the event-loop exception-handler context contract: handlers accept a dictionary whose recognized keys include `message`, `exception`, and `task`, and may ignore or inspect additional context. The current regression test asserts all three values, including identity of the authoritative shared task. Current-head execution across Python 3.10, 3.12, and 3.14 remains the active confirmation step.

### Context-manager behavior

- body error waits for successful cleanup and then propagates;
- body cancellation enters `__aexit__`, waits for shielded cleanup, and then propagates;
- cleanup failure replaces the body error while preserving body error as exception context;
- direct `playwright.stop()` and `async with` use the same method.

### Current-base relation

Public upstream moved eight commits beyond the original base. The current upstream context-manager file remained unchanged. The candidate applies as a three-file diff against `3b7c24c...`.

## Repair work after the first clean-source review

1. Runs `30674333313` and `30674333365` were demoted because their logs checked out closed base-drift PR #7 rather than canonical PR #8.
2. The stale lint job exposed one actionable issue: an unused `method-assign` suppression. Commit `33cbc587830d2083d43dcdf67339696634c24936` removes it.
3. Commit `1ac8797ab4dc85fd91a38d526c3912a72a8fba23` adds exact loop-context task-identity coverage.
4. Docker was removed from the blocker list because its workflow path filters do not match any unit 08 file.
5. The final clean compare was re-read at `3b7c24c...1ac8797` and remains exactly three files.

## Claim-scoped evidence review

| Claim | Evidence | Review result |
| --- | --- | --- |
| old boolean loses joinable completion after cancellation | negative reproduction on Python 3.10/3.14 | supported |
| one shielded task fixes direct caller ownership | six focused controls | supported |
| context-manager cleanup and exception precedence remain coherent | four focused controls | supported |
| abandoned failure receives one fallback report and remains joinable | paired baseline fail and selected repair pass | supported |
| loop report identifies the authoritative shared task | exact clean-head assertion | source-supported; current-head execution pending |
| clean current-base branch passes repository pre-commit and focused gates | active run `30691125773` | pending |
| full unrelated repository matrix | full run `30690680740` intentionally cancelled after Examples passed | not claimed |

## Exact focused acceptance already retained

Historical selected head `beb025b6ee98e4b15b80335039f5d0afec5a7efd`:

- workflow `30595174700`;
- job `91045896030`;
- 33 passed, 2 warnings in 7.20s;
- Black passed;
- diff hygiene passed;
- independent review `4827700772`: ACCEPT for bounded mechanism.

That receipt supports the mechanism but does not automatically accept clean head `1ac8797...`. The clean head has two test-only follow-ups and needs its own final execution classification.

## Active exact-head gate

Execution carrier commit `32f665a71ae56ea50ede79ffb28baa79c96a6c7c` has clean product/test head `1ac8797...` as its parent and changes only `.github/workflows/ci.yml`.

Run `30691125773`, job `91345932225`, executes sequentially on Ubuntu 22.04:

1. Python 3.10 dependency installation, wheel build, full repository pre-commit, and all 11 focused lifecycle tests;
2. Python 3.12 dependency installation, wheel build, and all 11 tests;
3. Python 3.14 dependency installation, wheel build, and all 11 tests;
4. tracked diff hygiene.

Reruns are disabled. The carrier revision is preserved on branch `upstream/08-playwright-python-exact-gate-32f665a7`.

## Required final review sequence

1. Classify run `30691125773` and retain exact step output.
2. Repair any product, test, typing, or formatting failure and repeat the gate.
3. Force-reset canonical branch `upstream/08-playwright-python-shared-shutdown` to clean head `1ac8797...`.
4. Confirm PR #8 again contains exactly the three fenced files and no workflow.
5. Update packet README/TESTS, PR #8, PR #442, issue #149, and issue #435 with exact receipts.
6. Close all execution-only carrier PRs after receipt transfer.
7. Request independent human review before promotion or public upstream interaction.

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

- driver assembly failure before tests;
- unrelated existing test timeout after candidate controls passed;
- action permission or runner provisioning failure;
- stale base comparison that introduces unrelated files;
- execution-only workflow defect.

Record harness failures without upgrading or rejecting product claims.

## Compatibility questions for independent reviewer

- Is the message `Playwright stop task failed` appropriately scoped?
- Should a late joiner after loop reporting still receive the same exception? Current policy says yes and tests it.
- Is one `call_soon` turn enough opportunity for a new waiter to suppress fallback reporting? Current policy says yes.
- Does the project prefer this explicit loop report over default never-retrieved behavior? The retained task requires an explicit route because the done callback retrieves the exception.
- Should authoritative task cancellation itself be addressed separately? It remains outside this caller-cancellation unit.

## Current self-review disposition

`EXECUTE` the active exact-head gate, restore the clean branch, and then request independent review.

No further production-code correction is requested by the complete worker re-read. No merge or public upstream interaction is authorized.
