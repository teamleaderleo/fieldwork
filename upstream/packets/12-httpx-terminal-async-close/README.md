# Unit 12 — Preserve terminal async-response state after uncertain close

## Current disposition

`ACCEPT REPAIR — guarded source publication pending`

Last verified: `2026-08-02`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Public upstream contact authorized: `no`

## In simple words

HTTPX delegates asynchronous response cleanup to a public `AsyncByteStream`. Cleanup can commit an irreversible effect and then raise or receive cancellation. Blind retry can duplicate work, while claiming successful close can hide an uncertain outcome.

The selected contract makes an escaped delegated-close failure terminal:

- arbitrary cleanup is attempted once;
- the initiating caller receives the original exception or cancellation;
- observers receive fresh neutral `CloseError` objects;
- reads remain blocked after close begins;
- successful `is_closed` publication occurs only after cleanup succeeds;
- the response retains no arbitrary owner traceback graph.

The original source candidate had two defects: re-entry could wait on its own close event, and successful elapsed time included arbitrary cleanup latency. An initial task-ID repair fixed direct re-entry but failed when stream cleanup created and awaited a descendant task. The selected repair uses an inherited `ContextVar` stack of active close-state markers, covering direct, descendant, and nested response-close cycles while preserving ordinary external waiter settlement.

## Exact identities

- Public upstream: `encode/httpx`
- Current upstream/base SHA: [`b5addb64f0161ff6bfe94c124ef76f6a1fba5254`](https://github.com/encode/httpx/commit/b5addb64f0161ff6bfe94c124ef76f6a1fba5254)
- Owned fork: `teamleaderleo/httpx`
- Canonical source branch: `fieldwork/171-terminal-close-source`
- Pre-repair clean source head: [`18256f10d1b306bdf87a1bab24b214c15839147b`](https://github.com/teamleaderleo/httpx/commit/18256f10d1b306bdf87a1bab24b214c15839147b)
- Canonical source PR: [`teamleaderleo/httpx#6`](https://github.com/teamleaderleo/httpx/pull/6)
- Execution-only PR: [`teamleaderleo/httpx#9`](https://github.com/teamleaderleo/httpx/pull/9), closed without merge
- Execution carrier head: `5b3d8f1ee6b08435d45c6a37b1f6d1a06977cb2f`
- Final exact executor run: `30752805069`
- Packet branch: `upstream/12-httpx-terminal-async-close`
- Authoritative repair: [`patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)

## Selected repair

### Inherited close ownership

A module-level `contextvars.ContextVar` stores a tuple stack of active `_AsyncCloseState` markers.

- The owner pushes its state immediately before invoking arbitrary stream cleanup.
- Descendant tasks created by cleanup inherit that state.
- A caller rejects waiting when its target state appears anywhere in the inherited stack.
- A stack, rather than one marker, detects outer -> inner -> outer response-close cycles.
- Unrelated tasks created outside the owner context remain ordinary waiters.
- The context token resets in `finally` under success, failure, and cancellation.
- Markers retain no response or escaped exception.

### Elapsed compatibility

`BoundAsyncStream.aclose()` samples elapsed immediately before delegated cleanup, then publishes the sample only after cleanup succeeds. Failed cleanup leaves elapsed unavailable.

## Exact repaired blobs

| File | Blob |
| --- | --- |
| `httpx/_models.py` | `0533a7324d0ed45ffb1087570551efcdaed02fa5` |
| `httpx/_client.py` | `510b41959383dcf78bd311a236afc44dd92d010a` |
| `tests/client/test_async_client_terminal_close_elapsed.py` | `67545aede0ba92364f70dc9f37c5c2e0a010c836` |
| `tests/models/test_async_response_close_reentry.py` | `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67` |

The existing terminal-unknown and cancellation tests remain unchanged.

## Proposed clean source fence

1. `httpx/_client.py`
2. `httpx/_models.py`
3. `tests/client/test_async_client_terminal_close_elapsed.py`
4. `tests/models/test_async_response_close_reentry.py`
5. `tests/models/test_async_response_close_terminal_cancellation.py`
6. `tests/models/test_async_response_close_terminal_unknown.py`

No workflow, packet, generated, dependency, or adjacent-lane file belongs in the source commit.

## Exact evidence

### Baseline

Exact reconstructed clean-source production blobs:

```text
4 failed, 1 passed in 3.28s
```

The task-ID repair then failed the descendant-task control with a timeout.

### Local stronger repair

```text
7 passed
```

The revised re-entry test reports 100% local coverage.

### Final target run `30752805069`

Python 3.9 focused job `91509719800`: `success`

- exact source and repaired hashes;
- asyncio and Trio controls;
- diff hygiene.

Python 3.13 focused job `91509719821`: `success`

- same exact identity, backend, and hygiene controls.

Python 3.13 full job `91509719767`: `success`

```text
Ruff format: 64 files already formatted
Mypy: no issues in 64 source files
Ruff lint: all checks passed
Package and Twine checks: passed
Documentation build: passed
Complete suite: 1445 passed, 1 skipped in 16.86s
Coverage: 8210 statements, 0 missed, 100%
```

The executor verified the exact six-file fence before running these gates.

## Review

Independent complete-diff review: `ACCEPT REPAIR PATCH`.

The review found no blocking issue in context propagation, settlement ordering, cancellation cleanup, elapsed semantics, traceback retention, serialization, scope, or test design. See [`REVIEW.md`](./REVIEW.md).

## Publication state

The final executor job `91511644836`, `Commit clean repaired source`, is queued after all three required jobs succeeded. It is guarded to:

1. require canonical source head `18256f10...`;
2. apply the exact packet patch;
3. stage and verify the six-file fence;
4. commit `Fix inherited async-close reentry and elapsed sampling`;
5. push only to `fieldwork/171-terminal-close-source`.

Do not use or merge the execution carrier. Verify the canonical source PR after the guarded push.

## Duplicate and policy result

- Current `encode/httpx:master` remains `b5addb64...`.
- Current issue and PR searches found no equivalent terminal async-close re-entry implementation.
- HTTPX contribution guidance still prefers a Potential Issue discussion before a public behavioral change PR.
- No public upstream interaction occurred.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue/discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Independent review](./REVIEW.md)
- [Original reentrant-close probe](./receipts/reentrant-close-probe.md)
- [Initial repair execution](./receipts/repair-execution-2026-08-01.md)
- [Materialization attempt](./receipts/materialization-attempt-2026-08-01.md)
- [Descendant re-entry probe](./receipts/descendant-reentry-probe-2026-08-02.md)
- [Final exact executor receipt](./receipts/final-executor-run-30752805069.md)
- [Authoritative repair patch](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)

## Continuation-ready next actions

1. Confirm finalizer job `91511644836` succeeds.
2. Record the new canonical source head.
3. Verify PR #6 has exactly the six-file fence above.
4. Verify all four repaired blob hashes.
5. Record normal source-branch CI at the new head.
6. Keep PR #9 closed without merge.
7. Synchronize issue #171 and the final #435 handoff with immutable source and packet heads.
8. Seek separate explicit authority before any public HTTPX discussion.

Synchronous response close, HTTPCore retirement, same-socket/capacity behavior, and multi-transport shutdown remain separate lanes.
