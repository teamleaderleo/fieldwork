# Unit 08 — fix(async): shield shared shutdown from caller cancellation

## In simple words

Playwright Python uses one async context manager behind both `async with async_playwright()` and `playwright.stop()`. The old manager sets a one-way exit flag before awaiting cleanup. If that caller is cancelled, cleanup can continue without a joinable owner while later callers return through the flag and observe incomplete connection shutdown.

The repaired candidate gives shutdown one shared task. Caller cancellation still reaches that caller, but the cleanup task remains alive and joinable. Concurrent and later callers receive the same terminal success or failure. If every current waiter leaves before the task fails, the manager reports that unobserved failure once through the event loop and still preserves it for a later caller.

## Current disposition

`REPAIR`

The source defect and test defect found during this continuation are repaired. The canonical branch is clean. Promotion remains blocked by the absence of a current-head hosted execution receipt and independent human review.

Last verified: `2026-08-01`  
Worker: `OpenAI`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Owning candidate: [`teamleaderleo/fieldwork#149`](https://github.com/teamleaderleo/fieldwork/issues/149)  
Upstream contact authorized: `no`

## Exact identities

- Target project: `microsoft/playwright-python`
- Public upstream base: [`3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`](https://github.com/microsoft/playwright-python/commit/3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021)
- Original candidate base: [`9a10128e0ffc7c7429da3779283a2400c2707575`](https://github.com/microsoft/playwright-python/commit/9a10128e0ffc7c7429da3779283a2400c2707575)
- Selected historical repair: [`teamleaderleo/playwright-python#6`](https://github.com/teamleaderleo/playwright-python/pull/6), head `beb025b6ee98e4b15b80335039f5d0afec5a7efd`
- Canonical source PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Canonical source branch: `upstream/08-playwright-python-shared-shutdown`
- Canonical clean source head: [`1ac8797ab4dc85fd91a38d526c3912a72a8fba23`](https://github.com/teamleaderleo/playwright-python/commit/1ac8797ab4dc85fd91a38d526c3912a72a8fba23)
- Exact comparison base branch: `upstream/base-3b7c24c`
- Clean compare: 5 commits, exactly 3 files, 467 additions, 6 deletions
- Fieldwork packet branch: `p0/435-unit-08-playwright-python-shared-shutdown`
- Fieldwork packet head: see latest handoff and PR #442
- Preserved exact-gate branch: `upstream/08-playwright-python-exact-gate-0b34782a`
- Preserved exact-gate commit: `0b34782a2c2dd4f708ef542e2eb80e71a1d249b3`
- Execution-only carrier PRs #9, #10, #11, #12, and #13: closed
- Public upstream interaction: none

## Repairs completed after the first handoff

1. Runs `30674333313` and `30674333365` were re-read. Their logs checked out closed base-drift PR #7, not canonical PR #8, so they are not clean-head evidence.
2. Their lint output exposed one real candidate issue: an unused `# type: ignore[method-assign]` in `test_async_stop_exit_contract.py`. Commit `33cbc587830d2083d43dcdf67339696634c24936` removes it.
3. Commit `1ac8797ab4dc85fd91a38d526c3912a72a8fba23` strengthens the loop-report control by asserting that context key `task` identifies the authoritative shared stop task.
4. Docker was removed as a false blocker. The target workflow is path-filtered to its workflow file, `setup.py`, and Dockerfiles; none is changed by unit 08.
5. The complete state machine and exact compare were re-read. No additional production correction was found.
6. Temporary workflow commits were removed from the canonical branch. PR #8 is restored to the clean three-file head.

## Current code and tests

### Product code

- [`playwright/async_api/_context_manager.py`](https://github.com/teamleaderleo/playwright-python/blob/1ac8797ab4dc85fd91a38d526c3912a72a8fba23/playwright/async_api/_context_manager.py) — one shielded shared task, waiter accounting, stable failure retention, and one deferred loop report.

### Target-native tests

- [`tests/async/test_async_stop_cancellation.py`](https://github.com/teamleaderleo/playwright-python/blob/1ac8797ab4dc85fd91a38d526c3912a72a8fba23/tests/async/test_async_stop_cancellation.py) — six direct stop cancellation, concurrency, idempotence, and failure controls.
- [`tests/async/test_async_stop_exit_contract.py`](https://github.com/teamleaderleo/playwright-python/blob/1ac8797ab4dc85fd91a38d526c3912a72a8fba23/tests/async/test_async_stop_exit_contract.py) — five context-manager, precedence, pre-timeslice cancellation, abandoned-failure, and loop-context identity controls.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `playwright/async_api/_context_manager.py` | production | yes |
| `tests/async/test_async_stop_cancellation.py` | regression | yes |
| `tests/async/test_async_stop_exit_contract.py` | regression | yes |

No generated file, dependency file, or workflow exists on the canonical source head.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Cancellation poisons retry through `_exit_was_called` | target-executed | run `30492906544`, jobs `90714870057` and `90714870025` | Ubuntu, Python 3.10/3.14, no browser launch |
| Shared-task baseline loses only abandoned-failure reporting | target-executed | run `30595155697`, job `91045840683`: 30 passed, 3 intended failures | focused Python 3.12 Ubuntu |
| Selected reporting policy passes all retained controls | target-executed | run `30595174700`, job `91045896030`: 33 passed, 2 warnings; Black and diff hygiene passed | historical selected head, Python 3.12 Ubuntu |
| Six direct candidate tests also passed on Windows 3.12/3.14 | target-executed partial suite | jobs `90729623317`, `90729623318` | broader jobs later timed out in unrelated existing test |
| Clean candidate applies to current upstream with only three files | source-read | compare `3b7c24c...1ac8797`, PR #8 | exact current-head hosted gate did not receive a runner |
| Clean source can build/run repository examples | target-executed partial gate | run `30690680740`, Examples job `91344746297` passed | remaining unrelated full matrix intentionally cancelled |
| Manual loop context carries message, exception, and authoritative task | source-read plus historical execution | current exact assertions; historical run covered message/exception | new task-identity assertion lacks a current-head runner receipt |

## Hosted-runner attempts

A sequential exact-head gate was prepared to run:

1. Python 3.10 wheel build, full repository pre-commit, and all 11 lifecycle tests;
2. Python 3.12 wheel build and all 11 tests;
3. Python 3.14 wheel build and all 11 tests;
4. reruns disabled and tracked diff hygiene.

GitHub never allocated a runner to the sequential jobs across Ubuntu 24.04, Ubuntu 22.04, `ubuntu-latest`, or Ubuntu 24.04 ARM. The relevant runs/jobs remained queued and never entered setup:

- `30691032136` / `91345676497` — cancelled by a superseding carrier;
- `30691125773` / `91345932225` — cancelled by a superseding carrier;
- `30691290371` / `91346367232` — cancelled by a superseding carrier;
- `30691401327` / `91346660311` — never executed;
- `30691438464` / `91346756903` — never executed.

No queued or cancelled job is represented as a test pass or product failure. The exact gate remains preserved on branch `upstream/08-playwright-python-exact-gate-0b34782a`.

## Review result

Complete worker review found the following invariants coherent:

- the authoritative task is assigned before suspension;
- `asyncio.shield()` prevents one waiter from cancelling cleanup;
- waiter accounting preserves observation and late joining;
- one deferred report prevents silent abandoned failure;
- pending/report flags prevent duplicate reports;
- every later caller receives the same original terminal result;
- context-manager body error/cancellation waits for cleanup and preserves intended precedence.

No further production correction is requested by this review. Independent human review is still required.

## Duplicate and prior-art result

- Search date: `2026-08-01`
- No matching public upstream open issue, pull request, or equivalent shared `_stop_task` patch was found.
- Public issue [`microsoft/playwright-python#2581`](https://github.com/microsoft/playwright-python/issues/2581) is adjacent cancellation/cleanup prior art involving `InvalidStateError`, but uses a different mechanism.
- Relationship: independent repair of a distinct shutdown-owner defect.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Remaining blockers

1. Execute the preserved exact-head gate on an available hosted or explicitly authorized runner.
2. Obtain independent human complete-diff review.
3. Re-check current public upstream before any authorized filing.
4. Obtain explicit authority before any public upstream issue, pull request, comment, or review.

## Latest handoff

State: `REPAIR`  
Exact source head: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`  
Exact packet head: see PR #442 and latest #435 handoff  
Tests: historical selected repair passed 33 focused controls, Black, and diff hygiene; clean source Examples passed; exact current-head sequential jobs never received runners  
Temporary machinery remaining: preserved carrier branch only; all carrier PRs closed; none on canonical source  
Next action: run preserved gate, classify exact output, then obtain independent review  
Public upstream interaction: none
