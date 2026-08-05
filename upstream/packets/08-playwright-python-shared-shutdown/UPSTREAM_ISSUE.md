# Upstream issue draft

## Current route

`not applicable — direct pull request preferred`

## Rationale

The defect has a deterministic target-native reproduction, a bounded three-file repair, a paired negative control, and focused execution covering the lifecycle and failure-observation contract. The proposed change does not introduce a public API or require a maintainer design choice before code review.

A direct pull request gives maintainers the smallest useful review surface: one internal context-manager implementation and two async regression files.

## Fallback issue draft

Use this only when a maintainer requests issue-first discussion after public contact is separately authorized.

### Title

Async `playwright.stop()` can return before cleanup after a cancelled first caller

### Body

`PlaywrightContextManager.__aexit__()` marks exit as called before awaiting `Connection.stop_async()`.

When the first `playwright.stop()` task is cancelled while transport shutdown is still in progress, the exit flag remains set. A later `stop()` call returns through that flag without joining shutdown, even when connection cleanup has not completed.

A deterministic reproduction:

1. start async Playwright;
2. block transport `wait_until_stopped()`;
3. start and cancel `playwright.stop()`;
4. release transport shutdown;
5. call `playwright.stop()` again;
6. observe that connection cleanup can remain incomplete.

Expected behavior:

- caller cancellation reaches the cancelled caller;
- the underlying shutdown operation continues;
- concurrent and later callers join the same completion;
- repeated successful stop remains idempotent;
- cleanup failure remains visible to every caller.

A candidate repair stores one shared shutdown task and awaits it through `asyncio.shield()`. It also preserves visibility of a shutdown failure when every active waiter has cancelled before the task fails.

The focused regression matrix covers direct stop cancellation, concurrent callers, context-manager exit, exception precedence, cancellation before the shutdown task's first timeslice, shared failures, and abandoned-failure reporting.

## Claim limits for any public issue

- describe incomplete connection cleanup and non-joinable shutdown ownership;
- omit claims about browser-process leaks or frequency;
- state exact tested Python/platform boundaries;
- avoid linking Fieldwork records or owned execution carriers unless explicitly approved for public use.
