# F171: Make failed async response close terminal without sharing exception state

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#171`  
Canonical implementation: `teamleaderleo/httpx#4`  
Exact carrier head: `43047aaa1ae10d4fc4cf55b14230d53eca90c5cb`  
Exact base revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`  
Strongest evidence class: `target-executed` focused candidate and same-harness baseline/candidate discriminator  
Review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

An HTTP response can delegate closing to a user-provided async stream. That cleanup may commit work and then raise. Retrying can repeat an external side effect, while reporting success can hide an uncertain cleanup outcome.

The selected contract is terminal outcome-unknown after delegated close begins:

- the initiating caller receives the original failure or control-flow signal;
- the arbitrary stream is invoked once;
- body reads remain blocked after close admission;
- every concurrent or later observer receives a fresh neutral `CloseError` linked to the initiating failure;
- successful callers join one close attempt;
- elapsed time is published only after delegated close succeeds.

## Why this matters

Blind retry can commit cleanup twice. Reusing one exception object lets concurrent callers mutate shared traceback state. Publishing `is_closed` before cleanup finishes reports a false terminal result.

Leaving the current behavior unchanged preserves those bounded correctness and diagnostic failures whenever delegated close raises or is interrupted after work begins. Their frequency is unknown.

## Governing invariant

After arbitrary `AsyncByteStream.aclose()` begins, HTTPX must not claim a stronger result than it observed and must not repeat cleanup that has no public idempotency guarantee.

Required properties:

1. preserve the initiating exception identity;
2. isolate observer traceback state;
3. invoke arbitrary cleanup at most once;
4. block reads once terminalization begins;
5. retain successful concurrent joining;
6. keep request and error compatibility;
7. attach full-repository claims only to an exact source head containing the product change.

## Current finding

Once delegated async cleanup begins, an escaped failure is terminal outcome-unknown at the generic response layer. The response stores the initiating cause, not a reusable neutral exception. Each observer constructs a new `CloseError` with the same message, request, and cause.

A hidden clean-full-suite requirement is unsuitable as a pre-publication gate when the exact pinned base cannot pass it. Same-job run `30583588970`, job `91009597059`, produced the same `test_write_timeout[trio]` failure on the base in `3/3` attempts and on the materialized candidate in `3/3` attempts. The selected gate therefore publishes after focused and static candidate checks, then attaches the ordinary repository matrix to the exact source-only head.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Released closed state precedes delegated cleanup completion | `source-read`, `target-executed` | HTTPX pin `b5addb64...`; Fieldwork #171/#173 | Does not choose failure settlement |
| Retrying arbitrary close can commit cleanup twice | `target-executed` | `teamleaderleo/httpx#1`, commit-then-raise control | HTTPCore-owned recovery remains separate |
| Shared neutral exception identity is unsafe | `source-read`, focused `target-executed` | Python raise semantics and traceback-isolation controls | Does not define arbitrary-cause serialization |
| Fresh observer errors preserve diagnostic isolation | focused `target-executed` | PR #4 materialized native tests | Source-only publication remains pending |
| The recurring Trio failure exists on the pinned base | `target-executed` | run `30583588970`: base `3/3`, candidate `3/3` | Ordinary source-head CI remains required |

## Ownership map

- Public entrypoint: `httpx.Response.aclose()`.
- Response owner: close admission, in-flight event, initiating cause, observer settlement, read barrier.
- Delegated side effect: arbitrary `self.stream.aclose()` user code.
- Client wrapper: `BoundAsyncStream.aclose()` publishes elapsed only after success.
- Failure settlement: store cause, release waiters, keep later calls terminal, never invoke the stream again.
- Success settlement: set `is_closed`, release waiters, allow later close calls to return.

## Historical precedent

### Python exception traceback attachment

The Python raise statement attaches traceback state to the raised exception object. The language rule establishes why one shared exception is mutable; HTTPX still owns the API decision to isolate observer objects.

### HTTPX public async stream contract

`httpx/_types.py` at `b5addb64f0161ff6bfe94c124ef76f6a1fba5254` exposes async iteration and close without a generic idempotency promise. Built-in HTTPCore streams may support narrower retirement rules below this boundary.

## Decision criteria

1. no duplicate arbitrary cleanup;
2. truthful terminal state;
3. original initiating failure preserved;
4. observer traceback isolation;
5. no unbounded cancellation wait without policy;
6. compatible successful joining;
7. bounded generic-response implementation;
8. broad validation bound to exact product source.

## Alternatives and results

| Option | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- |
| Retry failed arbitrary close | commit-then-raise stream | cleanup committed twice | rejected |
| Terminal failure with one shared `CloseError` | concurrent and repeated raises | shared mutable identity and traceback | rejected |
| Unbounded shielding | stuck arbitrary close | no deadline or unfinished-cleanup policy | rejected |
| Terminal cause plus fresh observer errors | owner/waiter/later identity controls | preserves invariant and compatibility | selected |
| Require hidden clean full suite before publication | three base and three candidate attempts | both failed `3/3`; cannot distinguish candidate | rejected |
| Focused/static publication plus source-head CI | exact candidate checks followed by ordinary matrix | broad claims attach to product source | selected |

## Independent criticism

- Review found that the first terminal candidate reused one mutable neutral exception. The repair stores only the cause and constructs a fresh observer exception.
- Review rejected an early “unrelated flake” claim because the green carrier matrix lacked product source. The exact base/candidate discriminator resolved that criticism.
- A reversing result would show a candidate-related ordinary source-head failure while the exact supported base control passes.

## Covered edge cases

- ordinary delegated exception;
- custom control-flow `BaseException`;
- concurrent waiters and repeated later observers;
- traceback isolation;
- successful concurrent close;
- body read after close admission;
- pickle state;
- same-harness base/candidate full-suite comparison.

## Deferred boundaries

| Boundary | Owner or reopening path |
| --- | --- |
| Real asyncio and Trio cancellation identity | #171 after source publication |
| HTTPCore retry, retirement, and socket reuse | #227 |
| Sync response close | #185 |
| Client multi-transport shutdown | #177 |

## Exact receipts

| Head or carrier | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| materialized predecessor | publisher `30579958463`, Python 3.9 focused | passed | `target-executed` |
| materialized predecessor | same publisher, Python 3.13 full | `1 failed, 1424 passed, 1 skipped` | target failure |
| carrier `c1f510de...` | Test Suite `30583588861` | Python 3.9–3.13 passed; product source absent | carrier-only |
| carrier `c1f510de...` | publisher `30583588970` | base `3/3`, candidate `3/3` same failure | discriminator |
| carrier `43047aaa...` | publisher `30587691914` and Test Suite `30587691908` | queued at last refresh | `target-test-prepared` |

## Complete-diff boundary

Materialized product fence:

- `httpx/_models.py`;
- `httpx/_client.py`;
- `tests/models/test_async_response_close_terminal_unknown.py`;
- `.github/workflows/fieldwork-terminal-close-unknown.yml`.

Temporary publication workflows are excluded from the source-only review head.

## Selected direction and reopening trigger

Selected direction: terminal outcome-unknown with the original initiating failure and a fresh neutral error for every observer. Publish after focused/static validation; require ordinary full CI on the source-only exact head.

Reopen for a public arbitrary-close idempotency guarantee, a bounded generic cleanup policy, or exact source-head evidence showing the candidate changes unrelated cleanup behavior.

Non-delegable human decision: none.

## Exact transition

Execute carrier `43047aaa1ae10d4fc4cf55b14230d53eca90c5cb`, publish the source-only head, run ordinary exact-head CI, remove transient machinery, and obtain independent complete-diff review.
