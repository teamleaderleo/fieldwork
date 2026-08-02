# Descendant and nested async-close re-entry probe — 2026-08-02

## Scope

This receipt extends upstream unit 12 only. It tests whether the task-ID repair retained in the first packet revision closes every re-entry cycle reachable from delegated `AsyncByteStream.aclose()`.

Pinned clean source:

- repository: `teamleaderleo/httpx`
- branch: `fieldwork/171-terminal-close-source`
- head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`

## New counterexample

A delegated stream close can create a child task, ask that child to call the same response's `aclose()`, and await the child through an AnyIO task group.

The first repair stored `anyio.get_current_task().id` in the active close state. The child has a different task ID, so it follows the external-waiter path and waits for the owner's event. The owner is waiting for the child task group to exit. Neither side can progress.

Exact local control against the task-ID repair:

```text
PYTHONPATH=/tmp/httpx-unit12-pkg python -m pytest -q \
  /tmp/httpx-unit12-tests/test_descendant_reentry.py -x

1 failed in 0.43s
TimeoutError
```

The timeout interrupted the owner while its task group waited for the descendant; the descendant was waiting on the owner's close event.

## Selected stronger repair

Use an inherited `contextvars.ContextVar` stack of active `_AsyncCloseState` markers.

- An owner pushes its state immediately before invoking arbitrary stream cleanup.
- Context variables propagate into child tasks created by the stream cleanup.
- A close caller rejects waiting when its target state is anywhere in the inherited active stack.
- A tuple, rather than a single current marker, preserves nested response-close ancestry: outer close -> inner close -> outer close is detected.
- Unrelated external waiters are created outside the owner's modified context and continue to wait for normal settlement.
- The context token is reset in `finally`, including cancellation and failure paths.
- The marker state retains no response or owner exception, preserving the existing traceback-release goal.

## Exact repaired blobs

- `httpx/_models.py`: `0533a7324d0ed45ffb1087570551efcdaed02fa5`
- `httpx/_client.py`: `510b41959383dcf78bd311a236afc44dd92d010a`
- `tests/client/test_async_client_terminal_close_elapsed.py`: `c3a27b2f65f04c723a4fc330f25215dcc6565e1c`
- `tests/models/test_async_response_close_reentry.py`: `058459952675150661fbd53795ed8cb9d250ebe1`

## Local repaired controls

The focused local package now covers:

- requestless direct re-entry;
- request-bound direct re-entry;
- a caught direct re-entry with an unrelated external waiter;
- descendant-task re-entry;
- a nested outer/inner/outer response-close cycle;
- failed cleanup keeping elapsed unavailable;
- successful elapsed excluding cleanup latency.

Result:

```text
7 passed in 0.10s
```

Syntax compilation passed for both repaired production files.

Local environment limit: Python 3.13 with asyncio; Trio was not installed locally. The owned executor PR performs Python 3.9/3.13 focused tests with the repository requirements, which include Trio, plus the complete Python 3.13 target gates.

## Execution surface

- owned executor: `teamleaderleo/httpx#9`
- carrier branch: `fieldwork/171-terminal-close-repair-carrier`
- revised carrier head: `2fb199d3deca67535eff8202eb0243a2940365ef`

This carrier is execution-only and must close without merge after transferring exact receipts. No public upstream contact is authorized.
