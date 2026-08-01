# Tests and receipts — Unit 12 terminal async-response close

## In simple words

The current five-file source head passed its focused and ordinary HTTPX gates, but those tests omitted same-owner re-entry and successful elapsed sampling. Reconstructed exact source blobs fail four new discriminators: three re-entry cases time out and the successful elapsed value includes cleanup latency. The retained repair patch passes all five local package controls under Python 3.13 with AnyIO's asyncio backend.

The repaired patch still needs direct materialization and the target's complete asyncio/Trio and Python matrix. Existing green receipts remain valid only for source head `18256f10...`.

## Identity

- Exact upstream base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Exact current candidate head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Exact execution carrier head: `b0d72d521aa88c32f5ae48d5ce8943c1eb8ba8f5`
- Retained repair patch: [`patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
- Test date: `2026-08-01`
- Local environment: Linux, Python `3.13.5`, AnyIO `4.13.0`, asyncio backend, installed HTTPX dependencies from the container
- Network: unavailable in the container

## Exact reconstruction fence

The local current-candidate reconstruction started from installed `httpx==0.28.1`, applied the four known upstream grammatical changes between tag `0.28.1` and base `b5addb64...`, then applied PR #6's source diff.

The resulting source blobs matched GitHub exactly before repair:

| File | Reconstructed blob | GitHub blob at `18256f10...` | Result |
| --- | --- | --- | --- |
| `httpx/_models.py` | `3ccb5290ceb95d96e24047bcec2897c52de16176` | `3ccb5290ceb95d96e24047bcec2897c52de16176` | exact |
| `httpx/_client.py` | `79934d050cd77414fb6f9c1024f42f6029c924e0` | `79934d050cd77414fb6f9c1024f42f6029c924e0` | exact |

The reconstruction did not claim an exact full repository checkout; it established exactness for the two production files under the new discriminators.

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Retry after ambiguous close can duplicate committed cleanup | `target-executed` | PR #1 runs `30550892544` and `30550886069` | pass: duplicate effect characterized | synthetic public stream; lower layers separate |
| Current source invokes arbitrary cleanup once and isolates observer exceptions | `target-executed` | executor run `30631155839` | pass | exact old head; re-entry absent |
| Current source passes HTTPX's direct Test Suite | `full-gate` | run `30631127167` | success | old head; missing new discriminators |
| Current source deadlocks on requestless and request-bound same-task re-entry | `target-executed` on exact reconstructed production blobs | local pytest command below | fail by timeout in both cases | asyncio/Python 3.13 local |
| Current source deadlocks when the stream intends to catch re-entry while an external waiter joins | `target-executed` on exact reconstructed production blobs | local pytest command below | fail by timeout | asyncio/Python 3.13 local |
| Current source includes stream cleanup latency in successful `elapsed` | `target-executed` on exact reconstructed production blobs | local deterministic clock control | fail: `10.0`, expected `2.0` | client wrapper path, synthetic transport |
| Retained repair makes re-entry prompt and preserves the external waiter | `target-executed` on repaired local package | local pytest command below | pass | patch not on GitHub source branch |
| Retained repair samples elapsed before cleanup and publishes after success | `target-executed` on repaired local package | local deterministic clock control | pass | patch not on GitHub source branch |

## Current-head ordinary and focused execution

### Exact executor run `30631155839`

Canonical source: `18256f10d1b306bdf87a1bab24b214c15839147b`.

Python 3.13 job `91157545025` passed:

- exact source and five-file fence;
- repository dependency installation;
- `scripts/check`;
- package and documentation build;
- complete repository suite;
- `scripts/coverage` at 100%;
- 16 focused terminal-close controls;
- diff and clean-tree hygiene.

Python 3.9 job `91157545125` passed:

- exact source and five-file fence;
- dependency installation;
- the same 16 focused controls;
- diff and clean-tree hygiene.

### Direct source Test Suite `30631127167`

Status: success at `18256f10...`.

Limit: the direct suite did not contain the same-owner re-entry or successful pre-cleanup elapsed-sample assertions.

### Historical Python 3.9 full-suite red

A predecessor run reproduced the existing Trio async-generator `ResourceWarning` in unrelated `test_write_timeout`. The exact focused Python 3.9 controls passed. This remains a repository/harness compatibility note, not evidence for the new repair.

## New baseline discriminators

### Command

```text
PYTHONPATH=/tmp/httpx-current pytest -q \
  tests/models/test_async_response_close_reentry.py \
  tests/client/test_async_client_terminal_close_elapsed.py
```

### Assertions

- requestless same-task re-entry returns a prompt `CloseError`;
- request-bound same-task re-entry returns a prompt request-associated `CloseError`;
- a stream may catch the re-entry error and complete while an unrelated waiter joins normally;
- failed cleanup still leaves elapsed unavailable;
- successful elapsed excludes delegated cleanup latency.

### Result on exact current production blobs

```text
4 failed, 1 passed in 3.28s
```

Failures:

1. requestless re-entry timed out;
2. request-bound re-entry timed out;
3. caught re-entry/external waiter case timed out;
4. elapsed was `10.0` seconds instead of the pre-cleanup `2.0` seconds.

The separate direct probe printed:

```text
REENTRY_TIMEOUT 1 False True
ELAPSED_SECONDS 10.0
```

## Repaired patch execution

### Command

```text
PYTHONPATH=/tmp/httpx-repaired pytest -q \
  tests/models/test_async_response_close_reentry.py \
  tests/client/test_async_client_terminal_close_elapsed.py
```

### Result

```text
5 passed in 0.12s
```

The five cases are:

- requestless escaping re-entry;
- request-bound escaping re-entry;
- caught re-entry with an external waiter;
- failed cleanup elapsed remains unavailable;
- successful elapsed preserves the pre-cleanup sample.

### Syntax check

```text
python -m py_compile \
  /tmp/httpx-repaired/httpx/_models.py \
  /tmp/httpx-repaired/httpx/_client.py
```

Result: passed.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | old head executor `30631155839` | passed | repair patch has no target formatter receipt |
| lint | old head `scripts/check` | passed | rerun after materialization required |
| typecheck | old head `scripts/check` / Mypy | passed | `anyio.get_current_task().id` needs target Mypy confirmation |
| focused package tests | local repaired pytest, 5 cases | passed | asyncio only |
| complete target-declared suite | old head `30631127167` / executor | passed | expired for repaired source |
| build/docs | old head executor | passed | expired for repaired source |
| coverage | old head executor, 100% | passed | new test/source lines require rerun |
| Python 3.9 | old head focused executor | passed | repair patch needs Python 3.9 execution |
| Trio | old head cancellation/focused controls | passed | repair re-entry tests have not run under Trio |

## Reversing controls

- Current source fails request-bound and requestless re-entry; repaired patch passes.
- Current source reports `10.0` elapsed seconds; repaired patch reports `2.0` with the same deterministic clock.
- Existing failed-close elapsed test passes on both generations.
- Existing at-most-once/fresh-observer/GC/cancellation controls remain required after materialization.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| `git clone https://github.com/teamleaderleo/httpx.git` | container DNS/network unavailable | setup | no | reconstructed exact changed-source blobs through installed tag plus GitHub diff |
| local Trio execution | Trio absent | dependency | repair's Trio claim remains open | run target CI after materialization |
| direct source write | connected GitHub write surface offers full-file replacement but no patch application | tooling/safety | source branch remains unchanged | retained exact patch for safe application in a checkout or patch-capable worker |

## Checks prepared but not executed

- `tests/models/test_async_response_close_reentry.py` in the retained patch — target-native asyncio and Trio execution after patch application.
- successful elapsed sampling control — target-native Python matrix after patch application.
- existing 16 focused controls — rerun against repaired head.
- `scripts/check`, `scripts/test`, `scripts/coverage`, package build, and docs build — rerun against repaired head.

## Platform and integration gaps

- Python 3.9 repaired source.
- Trio repaired source.
- direct child-task re-entry provenance; the retained patch detects the exact same-task cycle only.
- real custom transports that re-enter close.
- HTTPCore trace and protocol retirement, intentionally separate.

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes` on old exact-head executor
- Immediate rerun performed: local repaired focused controls only
- Remaining temporary branches or PRs: source PR #6 remains open; retired executor PR #4 remains closed

## Current test judgment

`REPAIR`

Reason: two source-visible defects remain on the canonical branch. The retained patch makes the new discriminators pass locally, but no exact repaired GitHub source head or target CI receipt exists.

Clearing condition: apply the retained patch to `fieldwork/171-terminal-close-source`, then run the complete focused and ordinary HTTPX gates under Python 3.9 and 3.13 with asyncio and Trio on the resulting exact head.
