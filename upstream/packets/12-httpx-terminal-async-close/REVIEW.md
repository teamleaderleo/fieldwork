# Review — Unit 12 terminal async-response close

## Current review disposition

`ACCEPT REPAIR PATCH — source publication pending`

Independent complete-diff review found no blocking source, test, compatibility, or packaging defect in the inherited-context repair. The patch has passed the exact six-file fence, Python 3.9 focused asyncio/Trio controls, Python 3.13 full repository gates, and 100% coverage. The remaining operation is guarded publication to the canonical owned-fork source branch and immutable-head verification.

Public upstream contact remains unauthorized.

## Review subject

- Target repository: `encode/httpx`
- Public base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Owned fork: `teamleaderleo/httpx`
- Canonical source branch: `fieldwork/171-terminal-close-source`
- Pre-repair clean head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Source PR: `teamleaderleo/httpx#6`
- Execution-only PR: `teamleaderleo/httpx#9`
- Exact final run: `30752805069`
- Authoritative patch: [`patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
- Proposed repaired fence: six files

## Exact repaired blobs

- `httpx/_models.py`: `0533a7324d0ed45ffb1087570551efcdaed02fa5`
- `httpx/_client.py`: `510b41959383dcf78bd311a236afc44dd92d010a`
- `tests/client/test_async_client_terminal_close_elapsed.py`: `67545aede0ba92364f70dc9f37c5c2e0a010c836`
- `tests/models/test_async_response_close_reentry.py`: `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67`

The retained terminal-unknown and cancellation tests remain unchanged from the clean source candidate.

## Complete-diff findings

### Context ownership

The earlier task-ID proposal was rejected after a child-task reproduction deadlocked. The selected `ContextVar` stack correctly represents inherited close ownership:

- direct re-entry sees the active state;
- descendants created by delegated cleanup inherit the active state;
- nested outer -> inner -> outer cycles find the outer state anywhere in the stack;
- unrelated callers created outside the owner context do not inherit the marker and remain ordinary waiters;
- the context token is reset in `finally` on success, escaped failure, and cancellation.

No task object, response, or escaped exception is stored in the context. A descendant that outlives cleanup may retain only the lightweight close-state marker until that task exits. Calls after successful close return through `is_closed`; calls after failed cleanup return the terminal neutral error before context inspection.

### Settlement and races

The repair does not mutate the established settlement ordering:

- the initiating caller alone receives the delegated exception or cancellation;
- failure is recorded before the event is set;
- successful `is_closed` publication occurs before the event is set;
- observers receive fresh neutral `CloseError` instances;
- a caught re-entry does not poison an unrelated waiter;
- arbitrary stream cleanup remains at-most-once.

### Elapsed compatibility

`BoundAsyncStream.aclose()` now samples elapsed before delegated cleanup and assigns it only after cleanup succeeds. This restores the prior measurement boundary while retaining the newer rule that failed cleanup leaves elapsed unavailable.

### State retention and serialization

The context marker contains an event and failure bit only. Existing response state excludes the active state and terminal failure bit from pickling and restores an inert closed response. The repair introduces no new retained traceback path.

### Scope and hygiene

The repaired source fence is exactly:

1. `httpx/_client.py`
2. `httpx/_models.py`
3. `tests/client/test_async_client_terminal_close_elapsed.py`
4. `tests/models/test_async_response_close_reentry.py`
5. `tests/models/test_async_response_close_terminal_cancellation.py`
6. `tests/models/test_async_response_close_terminal_unknown.py`

No workflow, packet, generated, dependency, formatting-only, or adjacent-lane file belongs in the source commit.

## Exact execution evidence

Run `30752805069` used clean source head `18256f10...`, checked out packet head `e59fb13a...`, applied the exact patch, and verified the six-file fence.

### Python 3.9 focused job

Passed:

- exact clean source hashes;
- exact repaired blob hashes;
- asyncio and Trio controls;
- diff hygiene.

### Python 3.13 full job

Passed:

- exact source and six-file fence;
- `scripts/check`;
- Ruff format;
- mypy across 64 source files;
- Ruff lint;
- package build and Twine checks;
- documentation build;
- complete test suite: `1445 passed, 1 skipped`;
- complete coverage: `8210` statements, `0` missed, `100%`.

### Python 3.13 focused job

Still queued at the time of this review. Equivalent Python 3.13 asyncio/Trio focused coverage passed in earlier exact repair runs, and the current full Python 3.13 suite includes all ten re-entry parametrizations and the terminal-close controls. The guarded finalizer still requires the queued job before publication.

## Duplicate and policy refresh

- Public `encode/httpx:master` remains `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`.
- Current issue and PR searches found no equivalent async response-close re-entry or terminal-settlement implementation.
- HTTPX contribution guidance still routes feature/behavior proposals through a Potential Issue discussion before a public implementation PR.
- No public contact has occurred.

## Remaining operational checks

- [ ] Python 3.13 focused job in run `30752805069` completes.
- [ ] Guarded finalizer publishes one clean child commit.
- [ ] Source PR #6 shows exactly six files.
- [ ] Four repaired blob hashes match this review.
- [ ] Normal source-branch CI is recorded at the published head.
- [ ] Execution PR #9 is closed without merge.
- [ ] Packet, issue #171, and #435 handoff record immutable final heads.

## Reviewer conclusion

No blocking finding remains in the repair patch. The `ContextVar` stack is materially safer than task-ID comparison because it covers inherited and nested ownership cycles while preserving unrelated waiter behavior. The elapsed change restores compatibility without publishing a value on failed cleanup.

Clearing condition: verify the guarded source publication and its immutable hashes. Public upstream discussion remains a separately authorized action.
