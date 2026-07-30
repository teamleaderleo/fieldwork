# F171: Make failed async response close terminal without sharing exception state

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#171`  
Canonical finding path: `findings/F171-httpx-async-close-terminal-settlement/finding.md`  
Canonical implementation: `teamleaderleo/httpx#4`  
Exact implementation carrier head: `43047aaa1ae10d4fc4cf55b14230d53eca90c5cb`  
Exact base revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`  
Strongest evidence class: `target-executed` focused candidate plus same-harness baseline/candidate discriminator  
Reviewed input generation: `teamleaderleo/httpx#4 at 43047aaa1ae10d4fc4cf55b14230d53eca90c5cb`  
Current review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

An HTTP response may close a network stream, file, or user-provided async stream. Cleanup can commit work and then raise. Retrying can repeat an external side effect, while reporting success can hide an uncertain cleanup outcome.

The selected contract is terminal outcome-unknown after delegated close begins:

- the initiating caller receives the original failure or control-flow signal;
- the arbitrary stream is invoked once;
- body reads remain blocked after close admission;
- every concurrent or later observer receives a fresh neutral `CloseError` linked to the initiating failure;
- successful callers join one close attempt;
- elapsed time is published only after delegated close succeeds.

The implementation is prepared by an owned publisher. The remaining gate is to publish the source-only head after focused and static validation, then run the repository's ordinary pull-request matrix on that exact product head.

## Why we care

Blind retry can commit cleanup twice. Reusing one exception object lets concurrent callers mutate shared traceback state. Publishing `is_closed` before cleanup finishes reports a false terminal state. These are correctness and diagnosability failures at a public stream boundary where HTTPX cannot assume user code is idempotent or bounded.

## What happens if we leave it alone

The released close path can publish closed state before delegated cleanup completes. A retry wrapper can invoke a commit-then-raise stream twice. A shared observer exception can accumulate traceback mutations across callers.

The exact frequency is unknown. The failure is bounded to close paths that raise or are interrupted after delegated cleanup begins.

## Governing project goals and invariant

Governing invariant: after an arbitrary `AsyncByteStream.aclose()` begins, HTTPX must never claim a stronger cleanup result than it observed and must never repeat an unproven-idempotent cleanup side effect.

Required properties:

1. preserve the initiating exception identity;
2. isolate each observer's mutable diagnostic state;
3. invoke arbitrary cleanup at most once;
4. block reads once terminalization begins;
5. retain successful concurrent joining;
6. preserve existing package error and request-context behavior;
7. attach full-repository claims only to an exact source head that contains the product change.

## Current finding

Once delegated async cleanup begins, an escaped failure is terminal outcome-unknown at the generic response layer. The response stores the initiating cause rather than a reusable neutral exception. Each observer constructs a new `CloseError` with the same message, request, and cause.

The publication gate must not require a hidden clean full suite that the pinned base cannot pass. Same-job execution proved the pinned base and candidate each failed `test_write_timeout[trio]` in all three attempts. Focused and static candidate gates may therefore publish the source-only head, while ordinary exact-head pull-request CI remains the authoritative full repository gate.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Released closed state precedes delegated cleanup completion | source-read and target-executed | HTTPX pin `b5addb64...`; Fieldwork #171/#173 | Does not choose the failure contract |
| Retrying an arbitrary custom stream can commit cleanup twice | target-executed | `teamleaderleo/httpx#1`; commit-then-raise control | Built-in HTTPCore recovery remains separate |
| Shared neutral exception identity is unsafe | source-read and focused target-executed | Python raise semantics; traceback-isolation tests | Does not define serialization policy for arbitrary causes |
| Fresh per-observer `CloseError` preserves diagnostic isolation | focused target-executed | materialized native tests from PR #4 | Source-only publication still pending |
| The recurring Trio full-suite failure is present on the pinned base | target-executed | publisher `30583588970`, job `91009597059`: base `3/3`, candidate `3/3` failures | Does not excuse unrelated failures in ordinary source-head CI |
| A carrier-only green matrix does not validate materialized product source | source/execution review | Test Suite `30583588861` and earlier carrier matrices | Ordinary CI must rerun after source publication |

## System and ownership map

- Public entrypoint: `httpx.Response.aclose()`.
- Response owner: close admission, in-flight event, initiating failure, later observation, read barrier.
- Delegated side effect: arbitrary `self.stream.aclose()` user code.
- Client wrapper owner: `BoundAsyncStream.aclose()` publishes elapsed only after success.
- Failure settlement: store initiating cause, release waiters, keep later calls terminal, never invoke the stream again.
- Success settlement: set `is_closed`, release waiters, and allow later close calls to return.
- Test boundary: AnyIO asyncio/Trio execution, ordinary exception, custom `BaseException`, concurrent and later observers, traceback isolation, successful joining, pickle state, and read barriers.

## Historical precedent

### Python raise statement and traceback attachment

- Source: Python language reference, raise statement.
- Principle supported: raising an exception attaches traceback state to the exception object.
- Important difference: HTTPX must decide whether separate API observers share that mutable object.

### HTTPX public async stream contract

- Source: `httpx/_types.py` at `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`.
- Principle supported: `AsyncByteStream` exposes async iteration and close without a generic idempotency promise.
- Important difference: built-in HTTPCore streams may support narrower retirement or retry behavior below this boundary.

## Decision criteria

1. no duplicate arbitrary cleanup;
2. truthful terminal state;
3. original initiating failure preserved;
4. observer traceback isolation;
5. cancellation cannot create unbounded waiting without a policy;
6. successful concurrent behavior remains compatible;
7. implementation and tests stay bounded to the generic response owner;
8. repository validation attaches to the exact source head.

## Alternatives and comparative results

| Option | Implementation or evidence | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- | --- |
| A — retry failed arbitrary close | predecessor wrapper | commit-then-raise stream | cleanup committed twice | rejected |
| B — terminal failure with one shared `CloseError` | first terminal candidate | concurrent and repeated raises | shared mutable traceback/identity | rejected |
| C — unbounded shield | paper design | stuck arbitrary close under cancellation | no deadline or unfinished-cleanup policy | rejected |
| D — terminal cause plus fresh observer errors | PR #4 materialized candidate | owner/waiter/later/error identity controls | preserves invariant and compatibility | selected |
| Gate 1 — require hidden clean full suite before publication | publisher `30583588970` | three base and three candidate attempts | base and candidate failed `3/3`; cannot distinguish candidate | rejected |
| Gate 2 — focused/static publication, ordinary source-head full CI | carrier `43047aaa...` | focused close tests, Ruff, Mypy, then PR matrix | attaches broad claims to actual source head | selected |

## Independent criticism

- Review found the first terminal candidate reused one mutable neutral exception. The repair stores only the cause and constructs a fresh observer exception.
- Review challenged the claim that the Trio warning was unrelated because the green matrix lacked product source. The same-job discriminator answered that criticism: the exact pinned base and candidate both failed all three attempts.
- A reversing test would show the materialized source failing ordinary exact-head CI in a candidate-related path while the pinned/base control passes under the same supported environment.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Ordinary delegated exception | native focused test | owner gets original; observers get fresh `CloseError` |
| Custom control-flow `BaseException` | native focused test | initiating signal remains unchanged |
| Concurrent waiters | native focused test | one stream call; distinct neutral errors |
| Repeated later observers | native focused test | fresh error each time; no retry |
| Traceback isolation | native focused test | later raises do not mutate earlier traceback depth |
| Successful concurrent close | native focused test | all callers complete from one close |
| Body read after close begins | adjacent response test | permanent `StreamClosed` barrier |
| Pickle state | adjacent response tests | transient event and cause excluded |
| Baseline/candidate full-suite discriminator | run `30583588970` | base `3/3` and candidate `3/3` same Trio failure |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning record or reopening trigger |
| --- | --- | --- |
| Real asyncio and Trio cancellation identity | custom signal is narrower | #171 after source publication |
| HTTPCore retry/retirement | different state and socket owner | #227 |
| Sync response close | different concurrency model | #185 |
| Client multi-transport shutdown | aggregate lifecycle contract | #177 |
| Same-socket reuse after close failure | transport integration proof | #227 or successor finding |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| materialized predecessor candidate | publisher `30579958463`, Python 3.9 focused | passed | target-executed |
| materialized predecessor candidate | publisher `30579958463`, Python 3.13 full | `1 failed, 1424 passed, 1 skipped` | target-executed failure |
| carrier `c1f510de...` | ordinary Test Suite `30583588861` | Python 3.9–3.13 passed; product source absent | carrier-only gate |
| carrier `c1f510de...` materialization | publisher `30583588970` | base failures `3/3`; candidate failures `3/3` | target-executed discriminator |
| carrier `43047aaa...` | focused/static source publisher | dispatch or execution pending | target-test-prepared |

## Complete-diff and compatibility review

Materialized product fence:

- `httpx/_models.py`;
- `httpx/_client.py`;
- `tests/models/test_async_response_close_terminal_unknown.py`;
- `.github/workflows/fieldwork-terminal-close-unknown.yml`.

Temporary publication workflows are excluded from the source-only review head. Compatibility review covers exception identity, traceback ownership, request context, close idempotency, read admission, elapsed publication, pickle behavior, and Python 3.9/3.13 support.

## Selected direction, losing reasons, and reopening trigger

Selected direction: terminal outcome-unknown with the original initiating exception and fresh neutral errors for every observer. Publish after focused/static validation; require ordinary full CI on the source-only exact head.

Losing reasons:

- retry duplicates unproven-idempotent cleanup;
- shared exception identity corrupts observer-local diagnostics;
- unbounded shielding lacks deadline and unfinished-cleanup policy;
- hidden pre-publication full-suite purity cannot distinguish a candidate when the pinned base fails identically.

Reopening trigger: a public idempotency guarantee for arbitrary stream close, a bounded generic cleanup policy, or exact source-head evidence showing the selected implementation changes unrelated timeout cleanup.

Non-delegable human decision: none.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `D2`
- Exact next transition: execute carrier `43047aaa...`, publish the source-only head, run ordinary exact-head CI, then perform independent complete-diff review.
- Clearing condition: focused and static publication gates pass, source-only ordinary matrix passes or any exact failure is classified and repaired, and transient workflows are absent.
- Required subgates: Python 3.9 focused, Python 3.13 Ruff/Mypy, ordinary Python 3.9–3.13 matrix, complete-diff review.
- Non-delegable decision: none.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | `teamleaderleo/httpx#1` | retry rejected after duplicate committed cleanup |
| 2026-07-30 | repair before `7784400878...` | shared neutral exception rejected; fresh observers selected |
| 2026-07-31 | publisher `30583588970` | candidate-regression hypothesis defeated by base and candidate `3/3` failures |
| 2026-07-31 | carrier `43047aaa...` | selected focused/static publication followed by ordinary exact-head full CI |

## References

- Fieldwork #171, #173, #177, #185, and #227
- `teamleaderleo/httpx#1` and `#4`
- HTTPX source `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- GitHub Actions runs `30579958463`, `30580580154`, `30580580180`, `30583588861`, and `30583588970`
