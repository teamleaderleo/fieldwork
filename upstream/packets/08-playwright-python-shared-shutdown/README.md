# Unit 08 — fix(async): shield shared shutdown from caller cancellation

## In simple words

Playwright Python exposes one async context manager behind both `async with async_playwright()` and `playwright.stop()`. The old manager sets a one-way exit flag before awaiting cleanup. Cancellation of that caller can leave transport shutdown in progress while every later caller returns through the flag, so connection cleanup stays incomplete.

The retained candidate gives shutdown one shared task. Caller cancellation still reaches that caller, while the cleanup task continues and remains joinable by concurrent and later callers. A failed cleanup remains the same failure for every joiner. When every current waiter has left before that task fails, the manager reports the unobserved failure once through the event loop and still preserves it for a later caller.

A clean three-file candidate now exists against current public upstream. Focused lifecycle execution passed on the selected historical head. Ordinary repository CI for the clean head is queued.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `OpenAI`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Owning candidate: [`teamleaderleo/fieldwork#149`](https://github.com/teamleaderleo/fieldwork/issues/149)  
Upstream contact authorized: `no`

## Contribution

- Target project: `microsoft/playwright-python`
- Proposed upstream destination: `microsoft/playwright-python:main`
- Proposed title: `fix(async): shield shared shutdown from caller cancellation`
- Contribution synopsis: replace the pre-await exit flag with one shielded shared stop task, retain stable success or failure for all callers, and emit one loop-level report when a failed shared task has no remaining observer.
- Work class: `upstream-fork research`

## Exact identities

- Public upstream base inspected: [`3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`](https://github.com/microsoft/playwright-python/commit/3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021)
- Original candidate base: [`9a10128e0ffc7c7429da3779283a2400c2707575`](https://github.com/microsoft/playwright-python/commit/9a10128e0ffc7c7429da3779283a2400c2707575)
- Selected historical source: [`teamleaderleo/playwright-python#6`](https://github.com/teamleaderleo/playwright-python/pull/6) at [`beb025b6ee98e4b15b80335039f5d0afec5a7efd`](https://github.com/teamleaderleo/playwright-python/commit/beb025b6ee98e4b15b80335039f5d0afec5a7efd)
- Owned target fork: `teamleaderleo/playwright-python`
- Canonical source branch: `upstream/08-playwright-python-shared-shutdown`
- Canonical source head: [`54c17acaa1189bca3cf66da0bd9c22dae224b1ec`](https://github.com/teamleaderleo/playwright-python/commit/54c17acaa1189bca3cf66da0bd9c22dae224b1ec)
- Exact-base internal PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Exact comparison base branch: `upstream/base-3b7c24c`
- Fieldwork packet branch: `p0/435-unit-08-playwright-python-shared-shutdown`
- Fieldwork packet head: see latest handoff and branch head
- Active exact-head runs: [`CI 30674333313`](https://github.com/teamleaderleo/playwright-python/actions/runs/30674333313), [`Test Docker 30674333365`](https://github.com/teamleaderleo/playwright-python/actions/runs/30674333365)
- Retired base-drift PR: [`teamleaderleo/playwright-python#7`](https://github.com/teamleaderleo/playwright-python/pull/7)
- Historical execution/source records: PRs [`#1`](https://github.com/teamleaderleo/playwright-python/pull/1), [`#2`](https://github.com/teamleaderleo/playwright-python/pull/2), [`#3`](https://github.com/teamleaderleo/playwright-python/pull/3), [`#4`](https://github.com/teamleaderleo/playwright-python/pull/4), [`#5`](https://github.com/teamleaderleo/playwright-python/pull/5), and [`#6`](https://github.com/teamleaderleo/playwright-python/pull/6)

## Current code and tests

### Product code

- [`playwright/async_api/_context_manager.py`](https://github.com/teamleaderleo/playwright-python/blob/54c17acaa1189bca3cf66da0bd9c22dae224b1ec/playwright/async_api/_context_manager.py) — shared task ownership, waiter accounting, stable failure retention, and one deferred loop report.

### Target-native tests

- [`tests/async/test_async_stop_cancellation.py`](https://github.com/teamleaderleo/playwright-python/blob/54c17acaa1189bca3cf66da0bd9c22dae224b1ec/tests/async/test_async_stop_cancellation.py) — six direct stop cancellation, concurrency, idempotence, and failure controls.
- [`tests/async/test_async_stop_exit_contract.py`](https://github.com/teamleaderleo/playwright-python/blob/54c17acaa1189bca3cf66da0bd9c22dae224b1ec/tests/async/test_async_stop_exit_contract.py) — five context-manager, exception precedence, pre-timeslice cancellation, and abandoned-failure controls.

### Required generated or dependency files

- not applicable

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `playwright/async_api/_context_manager.py` | production | yes |
| `tests/async/test_async_stop_cancellation.py` | regression | yes |
| `tests/async/test_async_stop_exit_contract.py` | regression | yes |

No temporary workflow exists on the canonical source head.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Cancellation poisons retry through `_exit_was_called` | `target-executed` | run `30492906544`, jobs `90714870057` and `90714870025` | Ubuntu, Python 3.10 and 3.14, no browser launch |
| Shared-task baseline owns one completion and passes lifecycle controls except abandoned-failure reporting | `target-executed` | PR #5 head `13848d073c9d23629a9a8300c89262a4d8b42411`, run `30595155697`, job `91045840683`: 30 passed, 3 expected failures | focused Ubuntu run; browser parametrization supplied Chromium, Firefox, WebKit |
| Selected waiter-owned reporting policy passes all retained controls | `target-executed` | PR #6 head `beb025b6ee98e4b15b80335039f5d0afec5a7efd`, run `30595174700`, job `91045896030`: 33 passed, 2 warnings in 7.20s; Black and diff hygiene passed | focused lifecycle gate, Python 3.12 Ubuntu |
| Clean candidate applies to current upstream with exactly three files | `source-read` | PR #8 head `54c17acaa1189bca3cf66da0bd9c22dae224b1ec` against base `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021` | ordinary gates pending |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Public upstream open issues checked for async stop cancellation: no matching open issue found.
- Public upstream closed issue [`#2581`](https://github.com/microsoft/playwright-python/issues/2581) concerns cancellation during connection callback cleanup and `InvalidStateError`; it is adjacent lifecycle prior art with a different mechanism.
- Searches for `_exit_was_called` cancellation, `stop_async` context-manager cancellation, and an existing shared `_stop_task` implementation found no equivalent public patch.
- Equivalent implementation found: `no`
- Relationship to prior work: `independent repair of a distinct shutdown-owner defect`

## Remaining work

Complete in this order:

1. Let exact-head `CI` run `30674333313` and `Test Docker` run `30674333365` finish; classify each failure by assertion reachability.
2. Confirm the repository-declared `mypy playwright` and `pre-commit run --all-files` gates ran on `54c17ac...`, or execute and retain them separately.
3. Review the manual event-loop exception context keys/message against supported Python versions and record an exact-head independent disposition.
4. Update this README with the final packet head and close or mark superseded historical PRs after their receipts are fully linked.
5. Await explicit authority before any public upstream issue, pull request, comment, or review.

## Blockers and limits

- Exact-head ordinary repository gates are queued.
- The focused accepted receipt used Ubuntu and Python 3.12. Earlier negative reproduction covered Python 3.10 and 3.14; the selected repair lacks a retained clean-head two-version receipt.
- The loop exception context is intentional candidate behavior. Compatibility review remains for custom exception handlers and supported Python versions.
- Underlying cancellation of the authoritative stop task itself is outside the retained matrix; caller cancellation is covered.
- Frequency and downstream impact remain unmeasured. The supported consequence is incomplete connection cleanup and loss of joinable shutdown ownership.

## Latest handoff

State: `REPAIR`  
Exact source head: `54c17acaa1189bca3cf66da0bd9c22dae224b1ec`  
Exact packet head: update after final packet commit  
Tests: historical selected head passed 33 focused controls plus Black and diff hygiene; clean-head CI and Docker runs queued  
Temporary machinery remaining: none on canonical source; historical PR #5/#6 branches retain evidence workflows  
Next worker action: inspect runs `30674333313` and `30674333365`, then update `TESTS.md` and issue #435 with exact results  
Public upstream interaction: none
