# F171: Make failed async response close terminal without sharing exception state

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#171`  
Canonical implementation carrier: `teamleaderleo/httpx#4`  
Exact carrier head: `4f784ab6e2868b9002f2ed2398056f645934c4f8`  
Intended clean source branch: `fieldwork/171-terminal-close-source`  
Exact base revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`  
Strongest evidence class: `target-executed` focused/static materialized candidate plus baseline/candidate discriminator  
Review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

An HTTP response can delegate closing to a user-provided async stream. Cleanup may commit work and then raise. Retrying can repeat an external side effect, while reporting success can hide an uncertain outcome.

The selected contract is terminal outcome-unknown after delegated close begins:

- the initiating caller receives the original failure or control-flow signal;
- the arbitrary stream is invoked once;
- body reads remain blocked after close admission;
- every concurrent or later observer receives a fresh neutral `CloseError` linked to the initiating failure;
- successful callers join one close attempt;
- elapsed time is published only after delegated close succeeds.

## Why this matters

Blind retry can commit cleanup twice. Reusing one exception object lets callers mutate shared traceback state. Publishing `is_closed` before cleanup finishes reports a false terminal result.

The exact exposure frequency is unknown. The bounded failure requires delegated close to raise or be interrupted after work begins.

## Governing invariant

After arbitrary `AsyncByteStream.aclose()` begins, HTTPX must not claim a stronger result than it observed and must not repeat cleanup that has no public idempotency guarantee.

Required properties:

1. preserve the initiating exception identity;
2. isolate observer traceback state;
3. invoke arbitrary cleanup at most once;
4. block reads after terminalization begins;
5. retain successful concurrent joining;
6. preserve request/error compatibility;
7. attach broad repository claims only to an exact source head containing the product change.

## Current finding

Once delegated cleanup begins, an escaped failure is terminal outcome-unknown at the generic response layer. The response stores the initiating cause rather than a reusable neutral exception. Each observer constructs a new `CloseError` with the same message, request, and cause.

A hidden clean-full-suite requirement is unsuitable before publication when the pinned base cannot pass it. Run `30583588970`, job `91009597059`, produced the same `test_write_timeout[trio]` failure on the base in `3/3` attempts and on the materialized candidate in `3/3` attempts.

The source publisher then proved the candidate itself through:

- Python 3.9 focused controls: `12 passed, 102 deselected`;
- Python 3.13 Ruff: passed;
- Python 3.13 Mypy: no issues in 23 source files.

Publisher `30587691914`, job `91022827095`, failed only when pushing a commit that created `.github/workflows/fieldwork-terminal-close-unknown.yml`. GitHub rejected that write because the GitHub App lacks workflow permission. This is an authority/capability publication failure, not a product or test failure.

Carrier `4f784ab6e2868b9002f2ed2398056f645934c4f8` now validates the same materialized tree, creates a detached worktree at the pinned base, copies exactly two product files and one regression file, and pushes a new workflow-free source branch. No workflow mutation crosses the permission boundary.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Released closed state precedes delegated cleanup completion | `source-read`, `target-executed` | HTTPX pin `b5addb64...`; #171/#173 | Does not choose failure settlement |
| Retrying arbitrary close can commit cleanup twice | `target-executed` | `teamleaderleo/httpx#1` commit-then-raise control | HTTPCore recovery remains separate |
| Shared neutral exception identity is unsafe | `source-read`, focused `target-executed` | Python raise semantics and traceback controls | Does not define cause serialization |
| Fresh observer errors preserve diagnostic isolation | focused `target-executed` | publisher jobs through `91022827095` | Clean branch publication pending |
| Trio warning exists on pinned base | `target-executed` | run `30583588970`: base `3/3`, candidate `3/3` | Ordinary source-head CI remains required |
| First source push failed on workflow authority only | execution/authority receipt | run `30587691914`, push rejection | Product files were not published by that run |

## Ownership map

- Public entrypoint: `httpx.Response.aclose()`.
- Response owner: close admission, in-flight event, initiating cause, observer settlement, read barrier.
- Delegated side effect: arbitrary `self.stream.aclose()` user code.
- Client wrapper: publishes elapsed only after successful delegated close.
- Failure settlement: retain cause, release waiters, keep later calls terminal, never invoke stream again.
- Success settlement: set `is_closed`, release waiters, allow later close calls to return.

## Historical precedent

### Python exception traceback attachment

Raising an exception attaches traceback state to that object. HTTPX therefore must decide whether observers share mutable diagnostic identity; the selected answer is no.

### HTTPX public async stream contract

`httpx/_types.py` at `b5addb64f0161ff6bfe94c124ef76f6a1fba5254` exposes async close without a generic idempotency promise. HTTPCore-owned streams may support narrower retirement behavior below this boundary.

## Decision criteria

1. no duplicate arbitrary cleanup;
2. truthful terminal state;
3. original initiating failure preserved;
4. observer traceback isolation;
5. no unbounded cancellation wait without policy;
6. compatible successful joining;
7. bounded generic-response implementation;
8. validation attached to exact product source.

## Alternatives and results

| Option | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- |
| Retry failed arbitrary close | commit-then-raise stream | cleanup committed twice | rejected |
| One shared `CloseError` | concurrent/repeated raises | shared mutable identity and traceback | rejected |
| Unbounded shielding | stuck arbitrary close | no deadline or unfinished-cleanup policy | rejected |
| Terminal cause plus fresh observer errors | owner/waiter/later controls | preserves invariant and compatibility | selected |
| Require hidden clean full suite before publication | three base and candidate attempts | both failed `3/3`; cannot distinguish candidate | rejected |
| Push source plus new workflow in one commit | exact App push | rejected by workflow permission | rejected |
| Publish product/test-only branch from pinned base | exact three-file fence | avoids unrelated authority and carrier files | selected |

## Independent criticism

- Review found the first terminal candidate reused one mutable neutral exception. The repair stores only the cause.
- Review rejected an early “unrelated flake” claim because the green carrier matrix lacked product source. The exact discriminator resolved it.
- Publication review found a workflow-permission boundary after all candidate checks passed. The repair removes workflow files from the clean source commit rather than widening authority.
- A reversing result would show candidate-related ordinary source-head failure while the exact supported base control passes.

## Covered edge cases

- ordinary delegated exception;
- custom control-flow `BaseException`;
- concurrent and repeated later observers;
- traceback isolation;
- successful concurrent close;
- body read after close admission;
- pickle state;
- same-harness base/candidate comparison;
- clean three-file publication fence.

## Deferred boundaries

| Boundary | Owner or reopening path |
| --- | --- |
| Real asyncio and Trio cancellation identity | #171 after clean publication |
| HTTPCore retry, retirement, socket reuse | #227 |
| Sync response close | #185 |
| Client multi-transport shutdown | #177 |

## Exact receipts

| Head or carrier | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| materialized predecessor | publisher `30579958463`, Python 3.9 focused | passed | `target-executed` |
| materialized predecessor | Python 3.13 full suite | `1 failed, 1424 passed, 1 skipped` | target failure |
| carrier `c1f510de...` | publisher `30583588970` | base `3/3`, candidate `3/3` same failure | discriminator |
| carrier `43047aaa...` | Test Suite `30587691908` | passed | carrier-only full matrix |
| same carrier | publisher `30587691914`, job `91022827095` | focused/static passed; push rejected only for workflow permission | target plus authority evidence |
| carrier `4f784ab6...` | publisher `30593129384`; Test Suite `30593129351` | queued at latest refresh | `target-test-prepared` |

## Complete-diff boundary

The intended clean source branch differs from pinned base in exactly:

- `httpx/_models.py`;
- `httpx/_client.py`;
- `tests/models/test_async_response_close_terminal_unknown.py`.

Carrier and workflow files remain outside the clean source review surface.

## Selected direction and reopening trigger

Selected direction: terminal outcome-unknown with original initiating failure and fresh neutral observer errors. Publish a workflow-free three-file source branch after focused/static validation, then run ordinary full CI on that exact head.

Reopen for a public arbitrary-close idempotency guarantee, a bounded generic cleanup policy, or exact source-head evidence showing unrelated behavior changes.

Non-delegable human decision: none.

## Exact transition

Settle publisher `30593129384`; when it publishes `fieldwork/171-terminal-close-source`, open the clean source PR, run the ordinary Python 3.9–3.13 matrix on that exact head, retire the carrier from delivery consideration, and obtain independent complete-diff review.
