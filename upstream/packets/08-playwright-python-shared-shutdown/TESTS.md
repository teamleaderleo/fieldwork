# Unit 08 tests and receipts

## In simple words

The defect has an exact two-version negative reproduction. The selected repair has a paired focused comparison covering direct stop calls, context-manager exit, concurrency, cancellation timing, failure precedence, and abandoned-failure reporting. The clean current-base head has repository CI queued and therefore remains short of a full-gate receipt.

## Evidence classes

- Source reading: current public context manager and connection shutdown ordering.
- Target-executed negative reproduction: Python 3.10 and 3.14.
- Target-executed focused comparison: Python 3.12, Ubuntu, Chromium/Firefox/WebKit parameters.
- Clean-head ordinary gates: queued.

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

## Clean current-base source

- PR: [`teamleaderleo/playwright-python#8`](https://github.com/teamleaderleo/playwright-python/pull/8)
- exact base: `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`
- exact head: `54c17acaa1189bca3cf66da0bd9c22dae224b1ec`
- changed files: three
- temporary workflows: zero

Current runs:

| Workflow | Run | State at 2026-08-01 |
| --- | --- | --- |
| CI | `30674333313` | queued |
| Test Docker | `30674333365` | queued |

No combined status contexts were present at the first exact-head check.

## Repository-declared ordinary gates

From current `CONTRIBUTING.md`:

```text
pytest --browser chromium
mypy playwright
pre-commit run --all-files
```

Current state:

- `pytest --browser chromium`: expected within CI; exact job coverage must be confirmed after run completion.
- `mypy playwright`: exact clean-head receipt pending.
- `pre-commit run --all-files`: exact clean-head receipt pending.
- Test Docker: queued; relevance must be described by actual jobs after completion.

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
| same three-file candidate on current upstream | source applied | ordinary execution queued |
| underlying authoritative task cancellation | no | outside current scope |

## Coverage limits

- Focused accepted repair execution: Ubuntu, Python 3.12.
- Browser parameters exercise fixture setup and package paths; this shutdown behavior concerns the Python connection and does not claim browser-engine-specific semantics.
- Negative reproduction: Ubuntu, Python 3.10 and 3.14.
- Inspected Windows PR #3 jobs passed candidate tests, while their broader jobs later timed out elsewhere.
- macOS execution for the selected repair is absent.
- No production workload, process-leak measurement, benchmark, or ecosystem-frequency study exists.

## Next receipt update

After runs `30674333313` and `30674333365` settle, record:

- every job name, platform, Python version, command, and result that affects this candidate;
- whether the 11 candidate tests executed and how many parametrized cases ran;
- exact mypy and pre-commit status;
- any setup failure separately from product failure;
- final full-gate claim only when the named repository gate completed on `54c17ac...`.
