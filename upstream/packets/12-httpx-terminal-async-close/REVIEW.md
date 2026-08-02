# Review — Unit 12 terminal async-response close

## Current review disposition

`ACCEPT — published source matches the reviewed and executed repair`

Public upstream contact remains unauthorized.

## Exact review subject

- Target: `encode/httpx`
- Public base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Owned source PR: `teamleaderleo/httpx#6`
- Canonical branch: `fieldwork/171-terminal-close-source`
- Exact published head: `d5f9e3dffce3342d8c02ec2c1d3ed9588a83b803`
- Work class: upstream-fork research
- Changed-file fence: six files
- Exact full-gate run: `30752805069`

## Complete-diff judgment

The accepted implementation preserves the existing terminal outcome-unknown model and fixes two defects:

1. re-entry no longer waits on the event it prevents from settling;
2. successful elapsed retains the pre-cleanup measurement boundary while failed cleanup publishes no value.

An inherited `ContextVar` tuple stack is the correct demonstrated ownership boundary:

- direct re-entry finds the active state;
- descendant tasks inherit the state;
- nested outer -> inner -> outer cycles find the outer marker anywhere in the stack;
- unrelated callers created outside cleanup do not inherit the marker and remain ordinary waiters;
- the token resets in `finally` under success, failure, and cancellation.

The marker retains only the close event and failure bit. It stores no task, response, request, escaped exception, or traceback graph.

Settlement ordering remains sound: failure is recorded before wakeup; successful close is published before wakeup; observers receive new neutral errors; caught re-entry does not poison an external waiter; and arbitrary cleanup remains at most once.

## Exact published identity

The source PR shows exactly:

1. `httpx/_client.py`
2. `httpx/_models.py`
3. `tests/client/test_async_client_terminal_close_elapsed.py`
4. `tests/models/test_async_response_close_reentry.py`
5. `tests/models/test_async_response_close_terminal_cancellation.py`
6. `tests/models/test_async_response_close_terminal_unknown.py`

Published repaired blobs:

- `_models.py`: `0533a7324d0ed45ffb1087570551efcdaed02fa5`
- `_client.py`: `510b41959383dcf78bd311a236afc44dd92d010a`
- elapsed regression: `67545aede0ba92364f70dc9f37c5c2e0a010c836`
- re-entry regression: `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67`

These are the exact blobs inspected and executed in the retained packet patch. Head movement from the pre-publication source is semantically proven within the reviewed fence.

## Exact execution evidence

Run `30752805069` passed:

- Python 3.9 focused asyncio and Trio controls;
- Python 3.13 focused asyncio and Trio controls;
- exact six-file fence;
- Ruff format and lint;
- mypy across 64 source files;
- package and Twine checks;
- documentation build;
- complete suite: `1445 passed, 1 skipped`;
- coverage: `8210` statements, `0` missed, `100%`.

The automatic source-head workflow run `30755566581` concluded `action_required` before creating jobs. It is a workflow-admission result, not a product result, and does not invalidate the exact full-gate evidence.

## Hygiene and coordination

- execution PR #9 is closed without merge;
- the canonical source contains no workflow or Fieldwork-only file;
- source PR, issue #171, packet, and Human Review Desk name the published head;
- issue state and `state:ready` label agree;
- no public upstream contact occurred.

## Final conclusion

No blocking technical or packaging finding remains. The unit is ready for the user’s policy judgment and, only after separate explicit authorization, an HTTPX Potential Issue discussion.

Synchronous response close and HTTPCore convergence remain independent questions.
