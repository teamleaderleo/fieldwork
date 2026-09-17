# Playwright Python async stop cancellation — executed reproduction

Date: 2026-07-30

Parent scout: #26

Central candidate: #149

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

Stopping Playwright is like locking a shop.

The first caller starts shutdown, gets cancelled, and leaves an “already started” sign on the door. A later caller sees that sign and returns even though connection cleanup did not finish.

## Owned fork records

| Field | Value |
| --- | --- |
| Repository | `teamleaderleo/playwright-python` |
| Test PR | `#1` |
| Execution PR | `#2` |
| Test head | `c81f671af0adac2b866d8255e2f802ae0aba9ece` |
| Execution head | `6d32ca74784c5083d31e2d736f7178818da64ed0` |
| Workflow run | `30492906544` |
| Python 3.10 job | `90714870057` |
| Python 3.14 job | `90714870025` |
| Runner | Ubuntu 24.04 |
| Browser launched | no |

## Scenario

The test:

1. starts `async_playwright()`;
2. replaces transport `wait_until_stopped()` with a bounded blocker;
3. starts `playwright.stop()`;
4. cancels the stop task after shutdown enters the blocked wait;
5. observes `CancelledError`;
6. releases the transport wait and awaits the original transport completion;
7. calls `playwright.stop()` again;
8. requires connection cleanup to have set `_closed_error`.

## Exact result

Repository dependencies installed and the standard driver assembly completed successfully in both jobs.

Both Python versions failed at the intended assertion:

```text
await playwright.stop()
assert manager._connection._closed_error is not None
E assert None is not None
```

The failure is not a browser, dependency-installation, or driver-build failure.

## Mechanism

`PlaywrightContextManager.__aexit__` sets `_exit_was_called` before awaiting `stop_async()`.

Cancellation escapes while the guard remains set. After transport shutdown later completes, the second `stop()` call returns through the guard instead of completing connection cleanup.

## Supported conclusion

Async shutdown is not retryable after caller cancellation in the tested path. A later stop caller can return while connection cleanup remains incomplete.

## Required design properties

A repair should:

- keep shutdown joinable after cancellation;
- ensure one authoritative shutdown operation owns transport and connection cleanup;
- avoid duplicate concurrent cleanup;
- preserve caller cancellation rather than swallowing it indefinitely;
- retain shutdown errors for later callers;
- keep repeated successful stop calls idempotent.

## Required regression matrix

- two concurrent stop callers;
- first caller cancelled before transport stop;
- first caller cancelled after transport stop but before cleanup completes;
- transport shutdown failure;
- connection cleanup failure;
- repeated stop after successful completion;
- async context-manager exit cancellation;
- Linux, macOS, and Windows boundaries;
- oldest and newest supported Python versions.

## Evidence classification

Executed target reproduction on Python 3.10 and 3.14 under Ubuntu 24.04.

No source repair has been implemented or selected.
