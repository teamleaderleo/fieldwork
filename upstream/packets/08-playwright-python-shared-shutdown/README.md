# Unit 08 — fix(async): shield shared shutdown from caller cancellation

## In simple words

Playwright Python exposes one async context manager behind both `async with async_playwright()` and `playwright.stop()`. The old manager sets a one-way exit flag before awaiting cleanup. Cancellation of that caller can leave transport shutdown in progress while every later caller returns through the flag, so connection cleanup stays incomplete.

The retained candidate gives shutdown one shared task. Caller cancellation still reaches that caller, while the cleanup task continues and remains joinable by concurrent and later callers. A failed cleanup remains the same failure for every joiner. When every current waiter has left before that task fails, the manager reports the unobserved failure once through the event loop and still preserves it for a later caller.

A clean three-file candidate exists against current public upstream. The selected historical head passed the focused lifecycle comparison. The repaired clean head is now under the repository's native full CI through an exact-base `release-*` execution carrier.

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
- Canonical source head: [`1ac8797ab4dc85fd91a38d526c3912a72a8fba23`](https://github.com/teamleaderleo/playwright-python/commit/1ac8797ab4dc85fd91a38d526c3912a72a8fba23)
- Exact-base internal source PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Exact comparison base branch: `upstream/base-3b7c24c`
- Native-CI exact-base carrier: [`teamleaderleo/playwright-python#11`](https://github.com/teamleaderleo/playwright-python/pull/11), base branch `release-unit08-exact-base`, base SHA `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- Active valid run: [`CI 30690680740`](https://github.com/teamleaderleo/playwright-python/actions/runs/30690680740)
- Fieldwork packet branch: `p0/435-unit-08-playwright-python-shared-shutdown`
- Fieldwork packet head: see latest handoff and branch head
- Retired base-drift PR: [`teamleaderleo/playwright-python#7`](https://github.com/teamleaderleo/playwright-python/pull/7)
- Retired non-enqueuing carriers: [`#9`](https://github.com/teamleaderleo/playwright-python/pull/9) and [`#10`](https://github.com/teamleaderleo/playwright-python/pull/10)
- Historical execution/source records: PRs [`#1`](https://github.com/teamleaderleo/playwright-python/pull/1), [`#2`](https://github.com/teamleaderleo/playwright-python/pull/2), [`#3`](https://github.com/teamleaderleo/playwright-python/pull/3), [`#4`](https://github.com/teamleaderleo/playwright-python/pull/4), [`#5`](https://github.com/teamleaderleo/playwright-python/pull/5), and [`#6`](https://github.com/teamleaderleo/playwright-python/pull/6)

## Repairs after the first clean-source handoff

1. Prior head `54c17acaa1189bca3cf66da0bd9c22dae224b1ec` was associated with runs `30674333313` and `30674333365`, but their logs checked out the closed PR #7 merge rather than PR #8's exact-base merge. They are base-drift evidence only and are not clean-head receipts.
2. The stale merge lint job nevertheless exposed one real source defect: an unused `# type: ignore[method-assign]` in `test_async_stop_exit_contract.py`. Commit `33cbc587830d2083d43dcdf67339696634c24936` removes it.
3. Commit `1ac8797ab4dc85fd91a38d526c3912a72a8fba23` strengthens the abandoned-failure control by asserting that the loop exception context's `task` is the authoritative shared stop task.
4. Docker is not an ordinary gate for this change: the repository workflow is path-filtered to its workflow file, `setup.py`, and Dockerfiles. The three-file candidate does not match those paths.
5. PR #11 uses an exact-base branch whose name matches the native CI workflow's `release-*` filter, so the real repository CI runs without modifying the canonical source or widening the diff.

## Current code and tests

### Product code

- [`playwright/async_api/_context_manager.py`](https://github.com/teamleaderleo/playwright-python/blob/1ac8797ab4dc85fd91a38d526c3912a72a8fba23/playwright/async_api/_context_manager.py) — shared task ownership, waiter accounting, stable failure retention, and one deferred loop report.

### Target-native tests

- [`tests/async/test_async_stop_cancellation.py`](https://github.com/teamleaderleo/playwright-python/blob/1ac8797ab4dc85fd91a38d526c3912a72a8fba23/tests/async/test_async_stop_cancellation.py) — six direct stop cancellation, concurrency, idempotence, and failure controls.
- [`tests/async/test_async_stop_exit_contract.py`](https://github.com/teamleaderleo/playwright-python/blob/1ac8797ab4dc85fd91a38d526c3912a72a8fba23/tests/async/test_async_stop_exit_contract.py) — five context-manager, exception precedence, pre-timeslice cancellation, abandoned-failure, and loop-context identity controls.

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
| Clean candidate applies to current upstream with exactly three files | `source-read` | PR #8 head `1ac8797ab4dc85fd91a38d526c3912a72a8fba23` against base `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021` | native full CI run `30690680740` pending |
| Manual loop report carries failure, message, and authoritative task | `source-read` plus retained focused execution | exact assertions in `test_async_stop_exit_contract.py`; historical repair run `30595174700` covered message/exception and current head adds task identity | current-head cross-version confirmation pending in `30690680740` |

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

1. Let native exact-base CI run `30690680740` settle; classify every failure by whether candidate assertions were reached and whether the failure is product, setup, or unrelated suite behavior.
2. Confirm the run's `Lint` job completes the repository pre-commit gate, including `mypy playwright`.
3. Re-read the final three-file diff at exact source head and record the final source disposition.
4. Update `TESTS.md`, PR #8, PR #442, issue #149, and issue #435 with exact run/job receipts and the new packet head.
5. Close PR #11 after receipt transfer. Await explicit authority before any public upstream issue, pull request, comment, or review.

## Blockers and limits

- Native exact-base CI run `30690680740` is pending.
- Independent human review is not present; the current review is a complete worker re-read plus executed controls.
- Underlying cancellation of the authoritative stop task itself is outside the retained matrix; caller cancellation is covered.
- Frequency and downstream impact remain unmeasured. The supported consequence is incomplete connection cleanup and loss of joinable shutdown ownership.

## Latest handoff

State: `REPAIR`  
Exact source head: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`  
Exact packet head: update after final packet commit  
Tests: historical selected head passed 33 focused controls plus Black and diff hygiene; valid native exact-base CI run `30690680740` is queued  
Temporary machinery remaining: execution-only PR #11; none on canonical source  
Next worker action: classify run `30690680740`, update all records, then close PR #11  
Public upstream interaction: none
