# F171: Make failed async response close terminal without sharing exception state

Finding state: `research-active`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#171`  
Canonical finding path: `findings/F171-httpx-async-close-terminal-settlement/finding.md`  
Canonical implementation: `teamleaderleo/httpx#4`  
Exact implementation carrier head: `c1f510deaa72ce8161788ff43a6cb7bc9f1ccc3d`  
Exact base revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`  
Strongest evidence class: `target-executed` for the selected failure contract and focused materialized candidate; current full-suite discriminator pending  
Reviewed input generation: `teamleaderleo/httpx#4 body and workflow generation at c1f510deaa72ce8161788ff43a6cb7bc9f1ccc3d`  
Current review disposition: `EXECUTE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

An HTTP response may need to close a network stream, file, or user-provided async stream. Closing can partly succeed and then raise. Calling close again can repeat a non-idempotent cleanup action, while pretending the response closed successfully can hide unfinished work.

The selected rule is:

- the caller that starts cleanup receives the original failure;
- the stream is never closed a second time after that failure;
- every other observer receives a new neutral `CloseError` linked to the original failure;
- body reads stay blocked once closing begins;
- successful close callers still join one cleanup attempt.

A fresh neutral error per observer is important because Python mutates an exception's traceback when it is raised. Reusing one exception object across concurrent callers makes their diagnostic state interfere with each other.

The product source is still materialized by an owned one-time workflow. Publication remains blocked until a same-run baseline-versus-candidate full-suite discriminator settles a repeated Trio async-generator warning.

## Why we care

Blindly retrying cleanup can commit an external side effect twice. Reusing one exception instance can make one caller alter another caller's traceback. Publishing `is_closed` before delegated cleanup finishes can report a false terminal state.

These are correctness and diagnosability failures at a public stream boundary. The caller may provide an arbitrary `AsyncByteStream`, so HTTPX cannot assume close is idempotent or bounded.

## What happens if we leave it alone

The released implementation can publish the response as closed before delegated cleanup has completed. A retry-oriented wrapper can invoke an arbitrary custom stream twice after the first attempt has already committed cleanup and then raised. A shared neutral exception can accumulate or overwrite traceback state across observers.

The exact exposure frequency is unknown. The failure is bounded to close paths that raise or are interrupted after delegated cleanup begins.

## Current finding

Once `Response.aclose()` starts delegated cleanup on an arbitrary public `AsyncByteStream`, an escaped failure should become terminal outcome-unknown at the generic response layer.

The initiating caller keeps the original exception or control-flow signal. Concurrent waiters and later callers receive independently created `CloseError` objects with the same message, request, and initiating cause. No observer shares mutable exception identity or traceback state.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Released close state is published before delegated async cleanup completes | source-read and target-executed | HTTPX pin `b5addb64...`, `httpx/_models.py`; Fieldwork #171/#173 | Does not determine the preferred failure contract |
| Retrying an arbitrary custom stream can commit cleanup twice | target-executed | `teamleaderleo/httpx#1` and Fieldwork #171 retained receipt | Custom-stream control; does not classify HTTPCore-owned streams |
| The initiating failure must remain original while other observers receive neutral errors | model-executed and focused target-executed | materialized candidate tests in `tests/models/test_async_response_close_terminal_unknown.py`; publisher run `30579958463` Python 3.9 focused step | Current source-only head has not published |
| Neutral observer exceptions must be distinct objects | source-reviewed and focused target-executed | carrier materialization at `c1f510de...`; traceback-isolation assertions in the native test | Full repository result on the materialized source remains unsettled |
| The repeated Trio warning may be candidate-caused | observed, unresolved | publisher runs `30579958463` and `30580580154` failed `test_write_timeout[trio]` after `1424 passed, 1 skipped`; carrier-only matrix `30580580180` passed | The green matrix did not contain materialized product source |

## System and ownership map

- Public entrypoint: `httpx.Response.aclose()`.
- State owner: the response instance owns close admission, the in-flight close event, the initiating failure, and terminal observation behavior.
- Delegated side effect: `self.stream.aclose()` may be arbitrary user code.
- Client wrapper: `BoundAsyncStream.aclose()` owns elapsed-time publication and must publish elapsed only after delegated close succeeds.
- Read barrier: `aiter_raw()` must reject once close begins, even when close later fails.
- Cleanup result:
  - success sets `is_closed` and releases waiters;
  - failure stores the initiating cause, releases waiters, and keeps later close calls terminal without another stream call.
- Test boundary: native AnyIO tests cover asyncio and Trio through the repository plugin, ordinary exceptions, custom `BaseException`, concurrent observers, later observers, successful joining, traceback isolation, pickle state, and read barriers.

## Historical precedent

### Python raise statement and traceback attachment

- Source: https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement
- Principle supported: raising an exception attaches traceback state to that exception object.
- Important difference: Python describes language behavior; HTTPX must choose whether concurrent API observers share one mutable object.

### HTTPX public async stream contract

- Source: https://github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_types.py
- Revision: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Principle supported: `AsyncByteStream` exposes async iteration and close, without a generic idempotency promise.
- Important difference: built-in HTTPCore streams may support narrower retry or retirement behavior below this public boundary.

## Approaches considered

### Retained approach: terminal outcome-unknown with fresh observer errors

This prevents duplicate cleanup and preserves the initiating failure. It also keeps each observer's traceback independent. The response stores the initiating cause, not a reusable neutral exception instance.

### Declined: retry arbitrary stream close

The public stream contract does not promise idempotency. The executed commit-then-raise control observed duplicate cleanup commits.

### Declined: reuse one neutral `CloseError`

A single exception instance is mutable diagnostic state. Repeated raises can change traceback ownership and make concurrent callers interfere.

### Declined: unbounded shielding

`Response.aclose()` has no generic cleanup deadline or unfinished-cleanup policy. Shielding arbitrary user code can make cancellation wait indefinitely.

### Deferred: HTTPCore-specific recovery

Connection retirement, same-socket reuse, and retry before or after transport delegation require separate evidence at the HTTPCore layer.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Ordinary delegated exception | focused native test | owner receives original exception; observers receive fresh `CloseError` |
| Custom control-flow `BaseException` | focused native test | same terminal rule without converting the initiating signal |
| Two concurrent waiters | focused native test | one stream call; distinct observer errors with common cause |
| Repeated later observers | focused native test | fresh exception each time; no second stream call |
| Traceback isolation | focused native test | later raises do not mutate earlier observer traceback depth |
| Successful concurrent close | focused native test | all callers complete from one stream close |
| Body read after close begins | adjacent response control | `StreamClosed` barrier remains permanent |
| Pickle state | adjacent response controls | transient event and failure state excluded |
| Python 3.9 focused set | publisher run `30579958463` and later attempts | passed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Real asyncio cancellation identity | Current custom control-flow signal is narrower | #171 continuation after source publication |
| Real Trio cancellation identity | Requires target-native cancellation timing | #171 continuation after source publication |
| HTTPCore before/after-delegation recovery | Different state owner and connection consequences | #227 |
| Sync response close | Different implementation and concurrency model | #185 |
| Client multi-transport shutdown | Aggregate cleanup contract | #177 |
| Same-socket reuse after close failure | Transport-level retirement proof | #227 or a new integration finding |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| materialized candidate from predecessor carrier | publisher run `30579958463`, Python 3.9 focused | Ubuntu 24.04, Python 3.9 | focused close and adjacent response controls passed | target-executed |
| same materialized candidate | publisher run `30579958463`, Python 3.13 full suite | Ubuntu 24.04, Python 3.13 | `1 failed, 1424 passed, 1 skipped`; Trio `test_write_timeout` unraisable async-generator warning | target-executed failure |
| carrier `7784400878...` merge ref | Test Suite `30580580180` | Python 3.9–3.13 | all jobs passed | carrier-only full gate; product source absent |
| materialized candidate from `7784400878...` | publisher `30580580154` | Python 3.13 | same `test_write_timeout[trio]` failure after `1424 passed` | target-executed failure |
| carrier `c1f510de...` | baseline/candidate discriminator | Python 3.13 | queued or pending receipt | target-test-prepared |

The carrier matrix and materialized-source results are separate evidence classes. A green carrier merge-ref run does not validate source that only exists inside the publisher worktree.

## Complete-diff and compatibility review

- Carrier changed-file fence: transient workflow files only.
- Materialized product fence:
  - `httpx/_models.py`;
  - `httpx/_client.py`;
  - `tests/models/test_async_response_close_terminal_unknown.py`;
  - `.github/workflows/fieldwork-terminal-close-unknown.yml`.
- Base relationship: exact pinned HTTPX base `b5addb64...`.
- Temporary carrier: yes; do not merge the carrier head.
- Compatibility surfaces examined: close idempotency, concurrent observation, exception identity, traceback ownership, elapsed publication, pickle behavior, body-read barriers, Python 3.9/3.13.
- Known repair remaining: settle whether the Trio full-suite warning reproduces on the pinned base and candidate under the same worktree, dependencies, and test order.
- Reviewer eligibility: source-only head absent; implementation review cannot reach review-ready until publication and exact-head checks complete.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: execute the same-job three-run baseline/candidate full-suite discriminator at carrier `c1f510de...`.
- Clearing condition: pinned base passes all discriminator attempts and materialized candidate also passes, or a source repair makes the candidate pass after a candidate-only failure.
- Required subgates: source-only publication, focused Python 3.9/3.13 workflow, ordinary repository matrix, complete-diff review.
- User decision requested: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | `teamleaderleo/httpx#1` | Retry-oriented joining rejected after duplicate committed cleanup was executed |
| 2026-07-30 | repair review before `7784400878...` | Shared neutral exception rejected; fresh per-observer errors selected |
| 2026-07-30 | publisher `30580580154` review | Carrier matrix reclassified as carrier-only; repeated materialized-source warning retained as a possible product regression |
| 2026-07-31 | `c1f510de...` | Added same-job pinned-base versus materialized-candidate full-suite discriminator |

## References

- https://github.com/teamleaderleo/fieldwork/issues/171
- https://github.com/teamleaderleo/fieldwork/pull/173
- https://github.com/teamleaderleo/httpx/pull/1
- https://github.com/teamleaderleo/httpx/pull/4
- https://github.com/teamleaderleo/fieldwork/issues/185
- https://github.com/teamleaderleo/fieldwork/issues/227
- https://github.com/teamleaderleo/fieldwork/issues/177
- https://github.com/encode/httpx/tree/b5addb64f0161ff6bfe94c124ef76f6a1fba5254
- GitHub Actions runs `30579958463`, `30580580154`, and `30580580180`
