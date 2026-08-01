# Upstream pull-request draft — Preserve terminal async response state after uncertain close

Draft status: `issue first — repair patch prepared; direct source execution pending`  
Proposed head: `teamleaderleo/httpx:fieldwork/171-terminal-close-source` after applying the retained repair patch  
Proposed base: `encode/httpx:master` at or after `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`  
Public interaction authorized: `no`

---

## Summary

- Coordinate concurrent `Response.aclose()` callers around one delegated async stream-close attempt.
- Treat an escaped delegated failure or cancellation as terminal outcome-unknown, preserving the initiating exception while giving observers fresh neutral `CloseError` instances.
- Reject same-operation re-entry promptly and publish `elapsed` only after successful cleanup while preserving the pre-cleanup sample.

## Problem

`Response.aclose()` currently marks a response closed before awaiting its public `AsyncByteStream.aclose()` implementation. Cleanup can therefore fail or be cancelled after public state already reports completion. Concurrent callers can also return before delegated cleanup settles.

Retrying an arbitrary stream after an escaped failure is unsafe: a deterministic custom stream that commits an effect and then raises duplicates that effect when a waiter takes retry ownership.

A shared terminal exception is also unsafe because exception objects carry mutable traceback state. Retaining the original arbitrary exception on a long-lived response can retain the delegated frame and user objects.

## Change

The response now owns one private async-close attempt:

- close admission blocks future body reads;
- the first caller creates the in-flight event and invokes the stream once;
- unrelated concurrent callers wait for the same settlement;
- success sets `is_closed=True` and releases waiters;
- an escaped `BaseException`, including backend-native cancellation, is delivered unchanged to the initiating caller;
- only a terminal-failed bit remains on the response;
- concurrent and later observers receive fresh outer `CloseError` instances with fresh neutral causes;
- no arbitrary owner exception or traceback graph is retained;
- later calls never repeat uncertain arbitrary cleanup;
- same-task re-entry raises a prompt request-associated `CloseError` instead of waiting on the owner's event;
- pickling omits transient close state and restores an inert closed response.

The client response-stream wrapper samples elapsed time before delegated cleanup, awaits cleanup, and publishes the sample only after success. Failed cleanup therefore leaves elapsed unavailable, while successful cleanup keeps the previous measurement boundary and excludes arbitrary cleanup latency.

## Tests

Existing exact-head coverage before the final repair includes:

- ordinary and custom control-flow failures;
- AnyIO asyncio/Trio cancellation identity;
- concurrent owner/waiter success and failure;
- at-most-once delegated cleanup;
- distinct observer exceptions, causes, and tracebacks;
- request-bound and requestless responses;
- body-read barrier;
- frame-local garbage collection;
- pickling;
- failed client-bound elapsed publication;
- repository checks, full suite, build/docs, and 100% coverage.

The retained repair adds:

- requestless same-task re-entry;
- request-bound same-task re-entry;
- a stream that catches the re-entry error and completes while an unrelated waiter joins;
- deterministic successful elapsed sampling before a blocking stream close.

Local repaired-package result:

```text
5 passed in 0.12s
```

Required before submission:

```text
scripts/check
scripts/test
scripts/coverage
package and documentation build
focused repair controls on Python 3.9 and 3.13 under asyncio and Trio
```

## Compatibility

- public API: no new public method or attribute;
- existing successful repeated close remains idempotent;
- existing concurrent successful close callers join one attempt;
- initiating failure and cancellation identity is preserved;
- observers now receive neutral errors instead of a false success or shared mutable exception;
- failed terminal cleanup leaves `is_closed=False`, while reads and later close attempts remain blocked;
- same-task re-entry changes from an indefinite wait to `CloseError`;
- elapsed preserves its pre-cleanup sample and publishes only after cleanup succeeds;
- supported Python and AnyIO range must be confirmed by target CI;
- allocation cost: one AnyIO event and one task identifier for an active close attempt;
- migration: none;
- rollback: revert the private state and tests.

## Alternatives considered

- **Retry after failure:** rejected because a public custom stream can commit cleanup before raising, causing duplicate effects.
- **Set `is_closed=True` before delegation:** rejected because it reports successful cleanup before observing it.
- **Shield arbitrary cleanup indefinitely:** rejected because public user code may never finish and HTTPX has no generic deadline or retirement owner.
- **Share one exception object:** rejected because raises mutate shared traceback state.
- **Retain the original exception as observer cause:** rejected because it retains arbitrary traceback and user-object graphs.
- **Spawn an authoritative background task:** larger cancellation, lifetime, context, and leak surface than the current repair requires.
- **Document re-entry as unsupported:** leaves a silent owner/event cycle in public extension code.

## Limits

- The re-entry repair detects the exact owning task. Descendant-task provenance remains outside the current patch.
- HTTPCore HTTP/1.1 and HTTP/2 release interruption is separate.
- Synchronous response close is separate.
- Client-wide shutdown across main and mounted transports is separate.
- No production-frequency claim is made.

## Related work

A Potential Issue discussion should precede this pull request under the current HTTPX contribution guide. Add only public upstream links appropriate at submission time.

---

## Submission checklist

- [ ] Apply the retained repair patch to the clean source branch.
- [ ] Rebase onto a recent exact upstream `master` head.
- [ ] Confirm the diff contains only product source and target-native tests.
- [ ] Remove every temporary workflow, publisher, receipt, and internal term.
- [ ] Run the focused repair controls under asyncio and Trio on Python 3.9 and 3.13.
- [ ] Run `scripts/check`, full tests, coverage, package build, and docs build.
- [ ] Review the complete exact diff and renew independent acceptance.
- [ ] Repeat duplicate and overlap search.
- [ ] Confirm title and commit history follow target conventions.
- [ ] Check current contribution and AI-disclosure policy.
- [ ] Record exact user authority before opening any discussion or pull request.
