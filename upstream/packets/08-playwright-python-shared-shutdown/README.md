# Unit 08 — fix(async): share shutdown completion across callers

## In simple words

Playwright Python uses the same async context manager for `async with async_playwright()` and `playwright.stop()`. The upstream implementation marks shutdown as started before awaiting cleanup. If that caller is cancelled, the marker remains set while cleanup is incomplete, so later callers return instead of joining shutdown.

The repaired source stores the shutdown operation itself. The first caller creates one authoritative task; concurrent and later callers join it. Cancelling a caller does not cancel cleanup. Success and failure remain stable for every caller. If all current waiters leave before cleanup fails, one deferred event-loop report preserves observability while the same failure remains available to a later caller.

## Current disposition

`ACCEPT` for human review.

The complete pre-review pass is finished. The exact clean source passed repository pre-commit, wheel builds, and all 33 focused cases on Python 3.10, 3.12, and 3.14. The remaining decisions belong to the human reviewer and to explicit authorization before any public upstream interaction.

Last verified: `2026-08-01`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Owning candidate: [`teamleaderleo/fieldwork#149`](https://github.com/teamleaderleo/fieldwork/issues/149)  
Public upstream contact authorized: `no`

## Exact identities

- Target: `microsoft/playwright-python`
- Current public upstream `main` / exact base: [`3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`](https://github.com/microsoft/playwright-python/commit/3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021)
- Original candidate base: `9a10128e0ffc7c7429da3779283a2400c2707575`
- Canonical source PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- Canonical source branch: `upstream/08-playwright-python-shared-shutdown`
- Clean source head: [`4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`](https://github.com/teamleaderleo/playwright-python/commit/4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27)
- Exact compare: 7 commits, exactly 3 files, 469 additions, 6 deletions
- Final execution carrier: closed PR [`#15`](https://github.com/teamleaderleo/playwright-python/pull/15), head `79d799ab4cd1948c56144322080898da17ec1e33`
- Final workflow/job: `30692313951` / `91349092242`
- Packet branch: `p0/435-unit-08-playwright-python-shared-shutdown`
- Packet PR: [`teamleaderleo/fieldwork#442`](https://github.com/teamleaderleo/fieldwork/pull/442)
- Public upstream interaction: none

## Clean changed-file fence

| Path | Role |
| --- | --- |
| `playwright/async_api/_context_manager.py` | production shutdown ownership and failure observation |
| `tests/async/test_async_stop_cancellation.py` | six direct cancellation, concurrency, idempotence, and shared-failure controls |
| `tests/async/test_async_stop_exit_contract.py` | five context-manager, precedence, timing, and observability controls |

No workflow, generated API, dependency, packaging, Docker, or configuration file exists on the canonical source branch.

## Final mechanism

- `_stop_task` is assigned synchronously before the first suspension.
- callers join the task through `asyncio.wait({stop_task})`, then await the completed task to receive its exact outcome;
- cancellation of the waiter removes only the wait callback and does not cancel `stop_task`;
- `_stop_waiters` tracks active observers;
- the task done callback stores a failure;
- zero waiters plus an unobserved failure schedules one `call_soon` report;
- a late waiter cancels a pending report and receives the same failure;
- a later caller after reporting still receives that same task failure;
- pending, observed, and reported flags prevent silence and duplicate reports.

## Repairs found during pre-review

1. **Base-drift evidence correction.** Runs `30674333313` and `30674333365` checked out closed PR #7, not canonical PR #8. They are not clean-head evidence. Docker is also not path-applicable to this three-file change.
2. **Exact method typing.** Run `30691401327`, job `91346660311`, reached pre-commit and exposed an incorrect restoration assignment in the observability test. Commit `b0509982c7cb7ef9cfeaa6a65225ec6e64a28b92` preserves the bound method's inferred coroutine type and restores the narrow `method-assign` suppression required by repository mypy.
3. **Python 3.14 duplicate reporting.** Run `30692014938`, job `91348287797`, passed pre-commit and all cases on Python 3.10/3.12, but Python 3.14 emitted its own `exception in shielded future` context in addition to Playwright's intentional report. Exactly three observability controls failed, one per browser parameter.
4. **Final runtime-compatible join.** Commit `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27` replaces `asyncio.shield` with `asyncio.wait` followed by an ordinary await of the completed task. This preserves cancellation-safe ownership without Python 3.14's automatic shield logger.
5. **Misleading title corrected.** The internal source PR and upstream draft now say “share shutdown completion” rather than “shield shared shutdown.”

## Exact final execution

Workflow `30692313951`, job `91349092242`, Ubuntu 24.04 ARM:

| Gate | Result |
| --- | --- |
| exact public-base checkout | passed |
| editable install | passed |
| wheel build, Python 3.10.20 | passed |
| full repository pre-commit | passed |
| focused controls, Python 3.10 | `33 passed, 2 warnings in 10.10s` |
| wheel build, Python 3.12.13 | passed |
| focused controls, Python 3.12 | `33 passed, 2 warnings in 10.09s` |
| wheel build, Python 3.14.6 | passed |
| focused controls, Python 3.14 | `33 passed, 2 warnings in 10.08s` |
| reruns | disabled |
| tracked diff hygiene | passed |

The pre-commit gate included Black, mypy, flake8, isort, pyright, YAML/TOML/requirements validation, AST and merge-conflict checks, and license checks. The warnings are unrelated pyOpenSSL deprecations.

## Evidence lineage

| Claim | Exact evidence |
| --- | --- |
| original boolean loses joinable cleanup after cancellation | run `30492906544`, jobs `90714870057` and `90714870025`, intended assertion fails on Python 3.10 and 3.14 |
| shared task fixes ownership but silent retention loses abandoned failure | run `30595155697`, job `91045840683`, 30 passed / 3 intended failures |
| first explicit reporting repair passes focused Python 3.12 controls | run `30595174700`, job `91045896030`, 33 passed / 2 warnings; Black and diff hygiene passed |
| first clean typing review finds exact test defect | run `30691401327`, job `91346660311` |
| `asyncio.shield` duplicates reporting on Python 3.14 | run `30692014938`, job `91348287797`; 3.10/3.12 green, exactly three 3.14 failures |
| final `asyncio.wait` design passes supported versions | run `30692313951`, job `91349092242`; 99 focused cases total, full pre-commit and wheel builds green |

## Broader review findings kept outside unit 08

These are follow-on leads, not extra changes in PR #8:

- [`microsoft/playwright-python#3132`](https://github.com/microsoft/playwright-python/issues/3132): failed async startup can leave the internal `Connection.init` task exception unretrieved. It has a real-driver reproduction and deserves a separate ownership-focused unit.
- Python `PipeTransport.run()` awaits process communication without an explicit shutdown bound. Java's `PlaywrightImpl.close()` waits at most 30 seconds for the driver process; public Python issue [`#2633`](https://github.com/microsoft/playwright-python/issues/2633) is adjacent historical process-termination evidence. A dedicated deterministic reproduction is required before proposing a Python timeout.
- Playwright Node's out-of-process wrapper keeps one shared close promise, and .NET funnels disposal through one connection object. Both support the single-terminal-completion model without requiring protocol changes.

No public issue, pull request, comment, or review was created for these leads.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches ledger](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Human inspection guide](./REVIEW.md)

## Human review boundary

The pre-review recommendation is `ACCEPT`. The human reviewer should decide:

1. whether one deferred event-loop report is the desired abandoned-failure policy;
2. whether the message `Playwright stop task failed` is appropriately scoped;
3. whether the clean seven-commit branch should be rebuilt or squashed before any authorized public submission;
4. whether to open separate work for startup-task ownership and bounded process shutdown.

Explicit authority is still required before any public upstream action.
