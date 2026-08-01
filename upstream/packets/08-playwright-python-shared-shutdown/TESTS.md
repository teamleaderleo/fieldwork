# Unit 08 tests and receipts

## In simple words

The defect has an exact two-version negative reproduction. The selected repair has a paired focused comparison covering direct stop calls, context-manager exit, concurrency, cancellation timing, failure precedence, and abandoned-failure reporting. The repaired clean current-base head is now under the repository's native full CI through an exact-base `release-*` carrier.

## Evidence classes

- Source reading: current public context manager and connection shutdown ordering.
- Target-executed negative reproduction: Python 3.10 and 3.14.
- Target-executed focused comparison: Python 3.12, Ubuntu, Chromium/Firefox/WebKit parameters.
- Repaired clean-head ordinary gate: native CI run `30690680740`, pending.
- Invalid base-drift runs: `30674333313` and `30674333365`; both checked out PR #7's merge, not PR #8's exact-base merge.

## Negative reproduction

### Source

- PR: [`teamleaderleo/playwright-python#1`](https://github.com/teamleaderleo/playwright-python/pull/1)
- Head: `c81f671af0adac2b866d8255e2f802ae0aba9ece`
- Execution carrier: [`teamleaderleo/playwright-python#2`](https://github.com/teamleaderleo/playwright-python/pull/2)
- Carrier head: `6d32ca74784c5083d31e2d736f7178818da64ed0`

### Command

```text
pytest tests/async/test_async_stop_cancellation.py --timeout 90
```

### Environment and result

Workflow `30492906544`, Ubuntu 24.04:

| Python | Job | Result |
| --- | --- | --- |
| 3.10 | `90714870057` | failed at intended `_closed_error is not None` assertion |
| 3.14 | `90714870025` | failed at intended `_closed_error is not None` assertion |

Dependency installation and driver assembly succeeded. No browser launched.

### Supported claim

After the first `playwright.stop()` waiter is cancelled while transport shutdown is blocked, a later `stop()` returns through `_exit_was_called` while connection cleanup remains incomplete.

## Six-test shared-task matrix

Historical PR #3 head: `dbbc8834acd69dc1f7f122ba1d3f49360565e7ef`.

Cases:

1. cancelled stop can be retried;
2. concurrent callers share one operation;
3. cancelling one waiter leaves the shared stop and another waiter alive;
4. repeated successful stop reuses completion;
5. concurrent and later callers receive one stable shutdown failure;
6. failure after a cancelled waiter remains visible to a later caller.

Repository run `30497487411` ended cancelled. The six tests passed in inspected Windows async jobs before both jobs timed out later in the same existing page-evaluation test:

- Python 3.12 job `90729623317`;
- Python 3.14 job `90729623318`;
- later failure: `tests/async/test_page_evaluate.py::test_evaluate_throw_when_evaluation_triggers_reload[chromium]`.

Classification:

- candidate assertions in those jobs: passed;
- complete repository gate: absent;
- unrelated timeout classification: historical observation, never promoted to a green gate.

## Lifecycle and observability comparison

### Cases

The six shared-task cases plus five lifecycle controls, parametrized across Chromium, Firefox, and WebKit:

1. body error waits for successful context-manager cleanup;
2. body cancellation waits for cleanup and preserves cancellation;
3. cleanup failure takes precedence and chains the body error;
4. outer cancellation before the shared task's first timeslice preserves one cleanup owner;
5. an unjoined stop failure reaches the loop exception handler once and remains joinable afterward.

Total: 33 cases.

### Invalid first run

- workflow: `30590715257`;
- job: `91032218906`;
- formatting passed;
- driver assembly was omitted;
- existing tests failed during startup and reran automatically;
- first new context-manager control timed out waiting for entry;
- job cancelled.

Classification: setup/harness result only.

### Corrected baseline

- PR: [`teamleaderleo/playwright-python#5`](https://github.com/teamleaderleo/playwright-python/pull/5)
- exact head: `13848d073c9d23629a9a8300c89262a4d8b42411`
- workflow: `30595155697`
- job: `91045840683`
- environment: Ubuntu 24.04, Python 3.12
- setup: repository requirements, editable install, `python -m build --wheel`
- reruns: disabled
- result: 30 passed, 3 failed
- exact failures: abandoned stop failure did not reach loop exception handler, once per browser
- Black: passed
- tracked diff hygiene: passed

Supported conclusion: shared task, shielding, context-manager ordering, pre-timeslice cancellation, stable success, and stable failure all pass. Silent abandoned failure is the sole executed loss.

### Corrected selected repair

- PR: [`teamleaderleo/playwright-python#6`](https://github.com/teamleaderleo/playwright-python/pull/6)
- exact head: `beb025b6ee98e4b15b80335039f5d0afec5a7efd`
- workflow: `30595174700`
- job: `91045896030`
- environment: Ubuntu 24.04, Python 3.12
- setup: repository requirements, editable install, `python -m build --wheel`
- reruns: disabled
- command shape:

```text
pytest tests/async/test_async_stop_cancellation.py tests/async/test_async_stop_exit_contract.py --timeout 20 --reruns 0 -vv --tb=long
```

- result: `33 passed, 2 warnings in 7.20s`
- Black: passed
- tracked diff hygiene: passed
- exact-head review: `4827700772`, ACCEPT for focused mechanism

Supported conclusion: one deferred loop report closes the baseline's only failing control while preserving stable failure for later callers.

## Clean current-base source and repair commits

- canonical PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- exact base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- exact head: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- changed files: three
- temporary workflows on canonical source: zero

Follow-up repairs:

| Commit | Change | Reason |
| --- | --- | --- |
| `33cbc587830d2083d43dcdf67339696634c24936` | remove unused `# type: ignore[method-assign]` on restoration of `connection.stop_async` | repository mypy reported `unused-ignore` on the first clean head |
| `1ac8797ab4dc85fd91a38d526c3912a72a8fba23` | assert `contexts[0]["task"] is manager._stop_task` | make the manual loop exception context identify the authoritative task and force a fresh exact-head CI event |

The production state machine is unchanged by these two commits.

## Invalid first clean-head classification

Runs originally associated with head `54c17acaa1189bca3cf66da0bd9c22dae224b1ec`:

| Workflow | Run | Actual checkout | Classification |
| --- | --- | --- | --- |
| CI | `30674333313` | closed PR #7 merge `ef04e3d1...` | base-drift run, not exact PR #8 evidence |
| Test Docker | `30674333365` | closed PR #7 merge | base-drift run, not exact PR #8 evidence |

The CI lint job exposed the unused suppression above, so that diagnostic was repaired. Other failures from these runs are not attributed to the clean three-file candidate because the checkout included PR #7's widened comparison surface.

Test Docker is not expected for a clean upstream version of this candidate. Its workflow path filter includes only `.github/workflows/test_docker.yml`, `setup.py`, and Dockerfiles; none is changed by unit 08.

## Valid native exact-base ordinary CI

- execution PR: [`teamleaderleo/playwright-python#11`](https://github.com/teamleaderleo/playwright-python/pull/11)
- base branch: `release-unit08-exact-base`
- base SHA: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- head branch: `upstream/08-playwright-python-shared-shutdown`
- head SHA: `1ac8797ab4dc85fd91a38d526c3912a72a8fba23`
- diff: same three files as PR #8
- workflow: native repository `CI`
- run: [`30690680740`](https://github.com/teamleaderleo/playwright-python/actions/runs/30690680740)
- state at this packet commit: queued

The `release-*` base name activates the unchanged native workflow while preserving the exact public-base commit. The matrix contains:

- repository `Lint` / full pre-commit gate on Python 3.10;
- build, wheel, common, reference-count, installation, sync, and async suites on Linux, Windows, and macOS;
- Python 3.10 and 3.14 across Chromium, Firefox, and WebKit where supported;
- Chromium coverage on Python 3.11, 3.12, and 3.13;
- stable Chrome/Edge channels and examples.

## Repository-declared ordinary gates

From current `CONTRIBUTING.md`:

```text
pytest --browser chromium
mypy playwright
pre-commit run --all-files
```

Current state:

- `pytest --browser chromium`: included in native CI run `30690680740`; final jobs pending.
- `mypy playwright`: part of the repository pre-commit configuration; final `Lint` job `91344746279` pending.
- `pre-commit run --all-files`: native `Lint` job `91344746279` pending.
- Test Docker: not path-applicable to this three-file candidate.

## Assertions prepared and executed

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
| cleanup failure precedence and context | yes | `30595174700` |
| caller cancellation before stop task timeslice | yes | `30595174700` |
| abandoned failure reaches loop handler once | yes | baseline fail `30595155697`, repair pass `30595174700` |
| exception context identifies authoritative shared task | source assertion added | current-head run `30690680740` pending |
| same three-file candidate on current upstream | source applied | PR #8 / PR #11 exact head `1ac8797...`; ordinary execution pending |
| underlying authoritative task cancellation | no | outside current scope |

## Coverage limits

- Focused accepted repair execution: Ubuntu, Python 3.12.
- Browser parameters exercise fixture setup and package paths; this shutdown behavior concerns the Python connection and does not claim browser-engine-specific semantics.
- Negative reproduction: Ubuntu, Python 3.10 and 3.14.
- Inspected Windows PR #3 jobs passed candidate tests, while their broader jobs later timed out elsewhere.
- Current native exact-base CI supplies the missing cross-platform and supported-version coverage when complete.
- No production workload, process-leak measurement, benchmark, or ecosystem-frequency study exists.

## Next receipt update

After run `30690680740` settles, record:

- every failed or cancelled job name, platform, Python version, command, and exact assertion or setup failure;
- whether the 11 candidate tests executed in each relevant async suite;
- exact `Lint` status, including mypy and pre-commit;
- any unrelated existing-suite failure separately from product failure;
- final source disposition only after the exact-head run is classified and the three-file diff is re-read.
