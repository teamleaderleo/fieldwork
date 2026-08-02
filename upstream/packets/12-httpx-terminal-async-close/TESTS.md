# Tests and receipts — Unit 12 terminal async-response close

## Current judgment

`ACCEPT REPAIR EXECUTION — guarded source publication pending`

The inherited-context repair has passed the exact focused matrix, all ordinary HTTPX gates, the complete suite, and 100% coverage. The execution-only workflow is waiting to publish the verified patch as one clean child commit of the canonical source head.

## Exact identities

- HTTPX base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Clean source input: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Source branch: `fieldwork/171-terminal-close-source`
- Source PR: `teamleaderleo/httpx#6`
- Execution branch: `fieldwork/171-terminal-close-repair-carrier`
- Execution head: `5b3d8f1ee6b08435d45c6a37b1f6d1a06977cb2f`
- Execution PR: `teamleaderleo/httpx#9`
- Final exact run: `30752805069`
- Packet patch commit used by the run: `e59fb13a0a281be5ed2c94446430f5cb4b97424f`

## Exact repaired blobs

| File | Blob |
| --- | --- |
| `httpx/_models.py` | `0533a7324d0ed45ffb1087570551efcdaed02fa5` |
| `httpx/_client.py` | `510b41959383dcf78bd311a236afc44dd92d010a` |
| `tests/client/test_async_client_terminal_close_elapsed.py` | `67545aede0ba92364f70dc9f37c5c2e0a010c836` |
| `tests/models/test_async_response_close_reentry.py` | `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67` |

## Baseline failures

Exact reconstructed clean-source production blobs failed the first five new controls:

```text
4 failed, 1 passed in 3.28s
```

Failures:

1. requestless direct re-entry timed out;
2. request-bound direct re-entry timed out;
3. caught direct re-entry with an unrelated waiter timed out;
4. elapsed included cleanup latency: `10.0` seconds instead of `2.0`.

The first task-ID repair passed these five controls but failed a stronger descendant-task reproduction:

```text
1 failed in 0.43s
TimeoutError
```

The child task inherited no task identity, waited on the owner's event, and deadlocked with the owner waiting for the child task group.

## Stronger local controls

The selected `ContextVar` stack repair covers:

- requestless direct re-entry;
- request-bound direct re-entry;
- caught re-entry with an unrelated external waiter;
- descendant-task re-entry;
- nested outer -> inner -> outer response-close cycles;
- failed cleanup leaving elapsed unavailable;
- successful elapsed excluding delegated cleanup latency.

Local Python 3.13 result:

```text
7 passed
```

`python -m py_compile` passed for both repaired production files. The revised re-entry test reports 100% local coverage.

## Final exact hosted run

Run: `30752805069`

### Focused repair tests — Python 3.9

Status: `success`

Passed:

- exact clean source identity;
- exact repaired blob identities;
- repository dependency installation;
- direct, descendant, nested, waiter, cancellation, terminal-unknown, and elapsed controls;
- asyncio backend;
- Trio backend;
- diff hygiene.

### Focused repair tests — Python 3.13

Status: `success`

Passed the same exact source, repaired blob, asyncio, Trio, and hygiene controls as Python 3.9.

### Full repository gates — Python 3.13

Status: `success`

Exact execution sequence:

1. checked out canonical clean source `18256f10...`;
2. checked out packet patch commit `e59fb13a...`;
3. applied the patch with `git apply --check` and `git apply`;
4. verified the exact six-file fence;
5. installed `requirements.txt`;
6. ran `scripts/check`;
7. ran `scripts/build`;
8. ran `scripts/test`;
9. ran `scripts/coverage`.

Results:

```text
Ruff format: 64 files already formatted
Mypy: Success: no issues found in 64 source files
Ruff lint: All checks passed
Package build: passed
Twine wheel/sdist checks: passed
Documentation build: passed
Complete suite: 1445 passed, 1 skipped in 16.86s
Coverage: 8210 statements, 0 missed, 100%
```

The one skipped test is the existing Python-version-dependent netrc case in `tests/client/test_auth.py`.

## Exact six-file fence

1. `httpx/_client.py`
2. `httpx/_models.py`
3. `tests/client/test_async_client_terminal_close_elapsed.py`
4. `tests/models/test_async_response_close_reentry.py`
5. `tests/models/test_async_response_close_terminal_cancellation.py`
6. `tests/models/test_async_response_close_terminal_unknown.py`

The executor's fence check passed before all target gates.

## Claim-to-evidence matrix

| Claim | Evidence | Result |
| --- | --- | --- |
| arbitrary escaped cleanup is attempted once | terminal-unknown tests and full suite | passed |
| initiating caller receives original failure/cancellation | failure and backend-native cancellation controls | passed |
| observers receive fresh neutral errors | terminal-unknown observer controls | passed |
| no arbitrary owner traceback graph is retained | existing GC control | passed |
| direct re-entry does not wait on itself | requestless/request-bound controls | passed on Python 3.9/3.13, asyncio/Trio |
| inherited descendant re-entry does not deadlock | descendant task-group control | passed on Python 3.9/3.13, asyncio/Trio |
| nested response-close cycles do not deadlock | outer/inner/outer control | passed on Python 3.9/3.13, asyncio/Trio |
| unrelated waiter retains normal settlement | caught-re-entry waiter control | passed on Python 3.9/3.13, asyncio/Trio |
| successful elapsed excludes cleanup latency | deterministic clock control | passed |
| failed cleanup leaves elapsed unavailable | existing elapsed-failure control | passed |
| static compatibility is preserved | Ruff and mypy | passed |
| repository behavior remains intact | 1,445-test complete suite | passed |
| coverage remains complete | `scripts/coverage` | 100% |

## Historical harness corrections

The executor exposed and corrected four non-product issues before the final run:

1. a fence check initially omitted the new untracked file; it was corrected with `git add -N`;
2. Ruff required formatting the long re-entry message constant;
3. mypy rejected importing the internal `time` module as an exported HTTPX attribute; the test now monkeypatches the dotted target string;
4. coverage identified unreachable defensive exception-recording paths in the new test; those paths were removed so unexpected errors naturally fail the task group.

Each correction was rerun through the target gates. No product assertion was weakened.

## Publication state

The run's final job, `Commit clean repaired source`, is queued. It is guarded by the three successful jobs above and will:

- re-check clean source head `18256f10...`;
- apply the exact packet patch;
- stage and verify the six-file fence;
- commit `Fix inherited async-close reentry and elapsed sampling`;
- push only to `fieldwork/171-terminal-close-source`.

The execution carrier must be closed without merge after the source head and hashes are verified.
