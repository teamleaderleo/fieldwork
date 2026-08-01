# Unit 08 tests and receipts

## Evidence classes

- Source reading: current public context manager, connection shutdown ordering, and exact clean compare.
- Target-executed negative reproduction: Ubuntu, Python 3.10 and 3.14.
- Target-executed focused comparison: Ubuntu, Python 3.12, Chromium/Firefox/WebKit parameters.
- Target-executed partial Windows candidate coverage: Python 3.12 and 3.14.
- Target-executed clean-source partial gate: Examples job only.
- Current-head sequential gate: prepared exactly, but hosted jobs never received runners.

## Negative reproduction

- source PR: [`teamleaderleo/playwright-python#1`](https://github.com/teamleaderleo/playwright-python/pull/1)
- source head: `c81f671af0adac2b866d8255e2f802ae0aba9ece`
- execution carrier: PR #2, head `6d32ca74784c5083d31e2d736f7178818da64ed0`
- workflow: `30492906544`
- command: `pytest tests/async/test_async_stop_cancellation.py --timeout 90`

| Python | Job | Result |
| --- | --- | --- |
| 3.10 | `90714870057` | failed at intended `manager._connection._closed_error is not None` assertion |
| 3.14 | `90714870025` | failed at the same intended assertion |

Dependency installation and driver assembly succeeded. No browser launched.

Supported claim: cancelling the first `playwright.stop()` waiter while transport shutdown is blocked lets a later stop return through `_exit_was_called` before connection cleanup completes.

## Six direct shared-task controls

Historical PR #3 final head: `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef`.

Controls:

1. cancelled stop can be retried;
2. concurrent callers share one operation;
3. cancelling one waiter leaves the shared stop and another waiter alive;
4. repeated successful stop reuses completion;
5. concurrent and later callers receive one stable shutdown failure;
6. failure after a cancelled waiter remains visible to a later caller.

Run `30497487411` ended cancelled. The six candidate tests passed in inspected Windows async jobs before both jobs later timed out in unrelated existing page-evaluation coverage:

- Python 3.12 job `90729623317`;
- Python 3.14 job `90729623318`;
- unrelated later test: `tests/async/test_page_evaluate.py::test_evaluate_throw_when_evaluation_triggers_reload[chromium]`.

Classification: candidate assertions passed; complete repository gate absent.

## Lifecycle and observability comparison

The six controls above plus five lifecycle controls were parametrized across Chromium, Firefox, and WebKit, for 33 cases:

1. body error waits for successful context-manager cleanup;
2. body cancellation waits for cleanup and preserves cancellation;
3. cleanup failure takes precedence and chains body error;
4. outer cancellation before the shared task's first timeslice preserves one cleanup owner;
5. unjoined stop failure reaches the loop exception handler once and remains joinable afterward.

### Invalid first run

- workflow `30590715257`, job `91032218906`
- formatting passed
- driver assembly omitted
- existing tests failed during startup/reran
- first context-manager control timed out waiting for entry
- classification: setup/harness only

### Corrected baseline

- PR #5 head: `13848d073c9d23629a9a8300c89262a4d8b42411`
- workflow: `30595155697`
- job: `91045840683`
- Ubuntu 24.04, Python 3.12
- repository requirements, editable install, `python -m build --wheel`
- reruns disabled
- result: 30 passed, 3 failed
- exact failures: abandoned stop failure did not reach the loop exception handler, once per browser
- Black: passed
- tracked diff hygiene: passed

Supported conclusion: shared ownership, shielding, context-manager ordering, pre-timeslice cancellation, stable success, and stable failure pass. Silent abandoned failure is the sole executed loss.

### Selected repair

- PR #6 head: `beb025b6ee98e4b15b80335039f5d0afec5a7efd`
- workflow: `30595174700`
- job: `91045896030`
- Ubuntu 24.04, Python 3.12
- reruns disabled
- command:

```text
pytest tests/async/test_async_stop_cancellation.py tests/async/test_async_stop_exit_contract.py --timeout 20 --reruns 0 -vv --tb=long
```

- result: `33 passed, 2 warnings in 7.20s`
- Black: passed
- tracked diff hygiene: passed
- review `4827700772`: ACCEPT for the bounded mechanism

Supported conclusion: one deferred loop report closes the baseline's only failing control while retaining the same failure for later callers.

## Repaired clean current-base source

- canonical PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- exact base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- exact clean head: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- compare: 5 commits, exactly 3 files, 467 additions, 6 deletions
- temporary workflows on canonical source: zero

Follow-up repairs:

| Commit | Change | Reason |
| --- | --- | --- |
| `33cbc587830d2083d43dcdf67339696634c24936` | remove unused `method-assign` suppression | stale lint run reported `unused-ignore` |
| `1ac8797ab4dc85fd91a38d526c3912a72a8fba23` | assert loop context `task` is `manager._stop_task` | verify the report identifies the authoritative task |

The production mechanism is unchanged by these two commits.

## Invalid first clean-head classification

| Workflow | Run | Actual checkout | Classification |
| --- | --- | --- | --- |
| CI | `30674333313` | closed PR #7 merge | base-drift, not PR #8 evidence |
| Test Docker | `30674333365` | closed PR #7 merge | base-drift, not PR #8 evidence |

Only the unused suppression diagnostic was carried forward and repaired. Other failures are not attributed to the clean candidate.

Test Docker is not path-applicable. Its workflow paths cover its workflow file, `setup.py`, and Dockerfiles; unit 08 changes none of them.

## Clean-source native partial gate

Exact-base PR #11 activated the unchanged native CI workflow against the clean source.

- run: `30690680740`
- exact clean source: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- Examples job: `91344746297`, passed
- remaining 29 jobs: intentionally cancelled to release the repository's effectively serial runner from unrelated broad coverage

Supported conclusion: the exact clean source checked out and passed the repository Examples job. No broader full-matrix claim is made.

## Preserved exact-head sequential gate

The final carrier is preserved at:

- branch: `upstream/08-playwright-python-exact-gate-0b34782a`
- carrier commit: `0b34782a2c2dd4f708ef542e2eb80e71a1d249b3`
- clean source ancestor: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- carrier-only path: `.github/workflows/ci.yml`
- execution PR #13: closed after runner allocation failed

The gate performs sequentially:

1. Python 3.10: dependencies, editable install, wheel build, full repository pre-commit, all 11 lifecycle tests;
2. Python 3.12: dependencies, editable install, wheel build, all 11 tests;
3. Python 3.14: dependencies, editable install, wheel build, all 11 tests;
4. reruns disabled;
5. `git diff --check` and tracked-worktree hygiene.

Hosted runners did not start the jobs:

| Run | Job | Pool/iteration | Result |
| --- | --- | --- | --- |
| `30691032136` | `91345676497` | Ubuntu 24.04 | cancelled before setup by superseding run |
| `30691125773` | `91345932225` | Ubuntu 22.04 | cancelled before setup by superseding run |
| `30691290371` | `91346367232` | `ubuntu-latest` | cancelled before setup by superseding run |
| `30691401327` | `91346660311` | Ubuntu 24.04 ARM | remained queued; no setup/test execution |
| `30691438464` | `91346756903` | preserved PR #13 event | remained queued; no setup/test execution |

No queued/cancelled job is counted as a pass or failure. The blocker is hosted runner allocation, not an observed product assertion.

## Repository-declared gates

Current target guidance names:

```text
pytest --browser chromium
mypy playwright
pre-commit run --all-files
```

Status:

- historical selected repair: focused pytest, Black, and diff hygiene passed;
- current clean head: the unused mypy suppression is repaired by source inspection;
- current clean head full pre-commit/mypy: prepared but unexecuted because no hosted runner started;
- current clean head broad Chromium suite: not claimed;
- Docker: not applicable by path filter.

## Assertion ledger

| Assertion | Executed? | Receipt |
| --- | --- | --- |
| original cancelled retry defect | yes | `30492906544` |
| concurrent stop owns one operation | yes | `30595174700` |
| cancelling one waiter preserves another | yes | `30595174700` |
| repeated success reuses task | yes | `30595174700` |
| shared failure reaches all callers | yes | `30595174700` |
| failure after cancelled waiter remains joinable | yes | `30595174700` |
| async-with body error waits for cleanup | yes | `30595174700` |
| async-with body cancellation waits for cleanup | yes | `30595174700` |
| cleanup failure precedence/context | yes | `30595174700` |
| cancellation before stop task first timeslice | yes | `30595174700` |
| abandoned failure reaches loop handler once | yes | baseline fail `30595155697`, repair pass `30595174700` |
| context identifies authoritative shared task | source assertion added | current-head execution unavailable due runner allocation |
| exact current-base candidate is only three files | yes, source compare | `3b7c24c...1ac8797` |
| authoritative task cancellation itself | no | outside this caller-cancellation unit |

## Coverage limits and next execution

- Accepted focused repair execution is Ubuntu/Python 3.12.
- Negative reproduction covers Ubuntu/Python 3.10 and 3.14.
- Partial Windows evidence covers Python 3.12 and 3.14 candidate tests.
- Current-head Python 3.10/3.12/3.14 sequential execution is still required.
- Independent human review is still required.
- No production workload, leak measurement, benchmark, or frequency study exists.

Next executor should open the preserved carrier branch, run the exact sequential gate on an available authorized runner, record every step/result, then update README, REVIEW, PR #8, PR #442, issue #149, and parent #435 together.
