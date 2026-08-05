# Unit 08 tests and receipts

## Final evidence classification

- Target-executed negative reproduction: Python 3.10 and 3.14.
- Target-executed paired baseline and first repair: Python 3.12, Chromium/Firefox/WebKit parameters.
- Target-executed partial Windows candidate evidence: Python 3.12 and 3.14.
- Target-executed final clean-source gate: Python 3.10, 3.12, and 3.14; full repository pre-commit; wheel build on every version; 99 focused cases total.
- Exact clean compare: current public base to `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`, exactly three files.

## Original negative reproduction

- source PR: [`teamleaderleo/playwright-python#1`](https://github.com/teamleaderleo/playwright-python/pull/1)
- source head: `c81f671af0adac2b866d8255e2f802ae0aba9ece`
- execution carrier: PR #2, head `6d32ca74784c5083d31e2d736f7178818da64ed0`
- workflow: `30492906544`
- command: `pytest tests/async/test_async_stop_cancellation.py --timeout 90`

| Python | Job | Result |
| --- | --- | --- |
| 3.10 | `90714870057` | failed at intended `manager._connection._closed_error is not None` assertion |
| 3.14 | `90714870025` | failed at the same intended assertion |

Dependencies and driver assembly succeeded; no browser launched. Supported claim: cancelling the first `stop()` waiter while transport shutdown is blocked lets a later call return through `_exit_was_called` before connection cleanup completes.

## Six direct ownership controls

Historical PR #3 final head: `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef`.

1. cancelled stop can be retried;
2. concurrent callers share one operation;
3. cancelling one waiter leaves the shared task and another waiter alive;
4. repeated successful stop reuses completion;
5. concurrent and later callers receive one stable failure;
6. failure after a cancelled waiter remains visible to a later caller.

Run `30497487411` ended cancelled. The six candidate tests passed in inspected Windows jobs before unrelated existing page-evaluation timeouts:

- Python 3.12 job `90729623317`;
- Python 3.14 job `90729623318`.

Classification: candidate assertions passed; no complete repository-gate claim.

## Eleven tests / 33-case lifecycle matrix

The six direct controls plus five lifecycle controls are parametrized across Chromium, Firefox, and WebKit:

1. body error waits for successful context-manager cleanup;
2. body cancellation waits for cleanup and preserves cancellation;
3. cleanup failure takes precedence and chains body error;
4. cancellation before the shared task's first timeslice preserves one cleanup owner;
5. an abandoned failure reaches the loop exception handler exactly once and remains joinable afterward.

### Invalid first lifecycle run

- workflow `30590715257`, job `91032218906`
- formatting passed
- driver assembly omitted
- existing tests failed at startup and reran
- classification: setup/harness only

### Silent shared-task baseline

- PR #5 head `13848d073c9d23629a9a8300c89262a4d8b42411`
- workflow `30595155697`, job `91045840683`
- Ubuntu 24.04, Python 3.12
- wheel build passed; reruns disabled
- result: 30 passed, 3 failed
- exact failures: the abandoned failure did not reach the loop handler, once per browser
- Black and tracked diff hygiene passed

Supported conclusion: shared ownership and cancellation behavior pass; silent exception retention is the only executed loss.

### First explicit reporting repair

- PR #6 head `beb025b6ee98e4b15b80335039f5d0afec5a7efd`
- workflow `30595174700`, job `91045896030`
- Ubuntu 24.04, Python 3.12
- command:

```text
pytest tests/async/test_async_stop_cancellation.py tests/async/test_async_stop_exit_contract.py --timeout 20 --reruns 0 -vv --tb=long
```

- result: `33 passed, 2 warnings in 7.20s`
- Black and tracked diff hygiene passed
- review `4827700772`: ACCEPT for the bounded mechanism

## Clean-source evidence corrections

### Base-drift runs

Runs `30674333313` and `30674333365` checked out closed PR #7, not canonical PR #8. They are not current-source evidence. Docker is not path-applicable because unit 08 changes no Docker workflow, `setup.py`, or Dockerfile path.

### Exact method-typing failure

- source at the start of this check: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- carrier run `30691401327`, job `91346660311`
- setup, editable install, and wheel build passed
- repository pre-commit reached mypy and failed at the final restoration of `connection.stop_async`
- diagnostics: assignment to method plus incompatibility between a broad `Callable[[], Awaitable[None]]` annotation and the bound coroutine method type

Repair `b0509982c7cb7ef9cfeaa6a65225ec6e64a28b92`:

- allow the bound method's exact type to be inferred;
- restore the narrow `# type: ignore[method-assign]` on monkeypatch restoration.

### Python 3.14 shield compatibility failure

- source: `b0509982c7cb7ef9cfeaa6a65225ec6e64a28b92`
- carrier PR #14, head `762e424a9fed259c13181f7643036a65f6bfdf1f`
- workflow `30692014938`, job `91348287797`

Results:

| Gate | Result |
| --- | --- |
| full repository pre-commit | passed |
| Python 3.10 wheel + focused matrix | `33 passed, 2 warnings in 10.10s` |
| Python 3.12 wheel + focused matrix | `33 passed, 2 warnings in 10.09s` |
| Python 3.14 wheel + focused matrix | `30 passed, 3 failed, 9 rerun` |
| tracked diff hygiene | passed |

The three Python 3.14 failures were the same observability case, once per browser. The custom handler received two contexts:

1. Python 3.14's automatic `RuntimeError exception in shielded future` context;
2. Playwright's intentional `Playwright stop task failed` context.

CPython source review confirmed that Python 3.14's `asyncio.shield` installs `_log_on_exception` when the outer waiter is cancelled, while earlier supported versions retrieve the inner exception without producing that second report.

## Final clean source

- canonical PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- exact base / current public `main`: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- exact head: `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`
- compare: 7 commits, exactly 3 files, 469 additions, 6 deletions
- temporary workflows: none

Final production repair:

```python
await asyncio.wait({stop_task})
await stop_task
```

`asyncio.wait` does not cancel the supplied task when its own waiter is cancelled. The second await receives the task's exact terminal result after the wait completes. This leaves the candidate's explicit observation policy in sole control and avoids Python 3.14 shield logging.

## Final exact-head gate

- execution carrier: closed PR #15
- carrier head: `79d799ab4cd1948c56144322080898da17ec1e33`
- workflow: `30692313951`
- job: `91349092242`
- runner: Ubuntu 24.04 ARM
- clean source ancestor: `4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`
- exact public base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`

| Python | Build | Focused result |
| --- | --- | --- |
| 3.10.20 | wheel passed | `33 passed, 2 warnings in 10.10s` |
| 3.12.13 | wheel passed | `33 passed, 2 warnings in 10.09s` |
| 3.14.6 | wheel passed | `33 passed, 2 warnings in 10.08s` |

Additional gates:

- full repository pre-commit: passed;
- Black: passed;
- mypy: passed;
- flake8: passed;
- isort: passed;
- pyright: passed;
- YAML/TOML/requirements/configuration checks: passed;
- AST, merge-conflict, executable/shebang, license checks: passed;
- reruns: disabled;
- tracked diff hygiene: passed.

The two warnings per version are unrelated pyOpenSSL deprecations. Total focused current-head evidence: 99 passed cases.

## Assertion ledger

| Assertion | Final evidence |
| --- | --- |
| original cancelled retry defect | negative run `30492906544` |
| one authoritative stop operation | final run `30692313951` on all three versions |
| cancelling one waiter preserves cleanup and other waiters | final run `30692313951` |
| repeated success reuses completion | final run `30692313951` |
| stable failure reaches concurrent and later callers | final run `30692313951` |
| failure after cancelled waiter remains joinable | final run `30692313951` |
| body error waits for cleanup | final run `30692313951` |
| body cancellation waits for cleanup | final run `30692313951` |
| cleanup failure precedence and context | final run `30692313951` |
| cancellation before first stop-task timeslice | final run `30692313951` |
| abandoned failure reports exactly once | negative baseline `30595155697`; shield compatibility failure `30692014938`; final pass `30692313951` |
| report context identifies authoritative task | final run `30692313951` |
| exact source passes typing and formatting | final full pre-commit in `30692313951` |
| authoritative task itself being cancelled externally | outside this unit |

## Coverage limits

- Final current-head gate is Ubuntu 24.04 ARM, not the entire repository OS/browser matrix.
- Browser parameters exercise the target-native fixture paths; the behavior under test is Python-side connection shutdown ownership.
- Historical partial Windows evidence covers the direct controls on Python 3.12 and 3.14.
- No production workload frequency study, benchmark, or process-leak measurement exists.
- Public upstream authorization remains absent.

Pre-review execution disposition: `ACCEPT`.
