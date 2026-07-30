# HTTPX close and shutdown correctness matrix

Date: `2026-07-30`

Parent scout: #171  
Async response candidate: `teamleaderleo/httpx#1`  
Sync response characterization: #185 / `teamleaderleo/httpx#2`  
Delegated HTTPCore close characterization: #227 / `teamleaderleo/httpx#3`  
Client shutdown lane: #177  
Upstream contact authorized: `false`

## Why this matrix exists

HTTPX exposes terminal-looking facts above several distinct cleanup owners:

- an HTTPX sync or async response wrapper;
- a bound stream that publishes elapsed time;
- an HTTPCore HTTP/1.1 or HTTP/2 response byte stream;
- an HTTP/1.1 connection lease or HTTP/2 stream-capacity slot;
- a client main transport and mounted proxy transports;
- explicit callers, context exits, concurrent callers, and user trace callbacks;
- transient operation state that must not survive serialization.

A single “close bug” label would hide different retry, cancellation, concurrency, and compatibility decisions.

## Evidence legend

- `source-read` — ownership and ordering inspected;
- `target-test-prepared` — target test exists without an accepted exact run;
- `target-executed` — released or repository behavior executed;
- `integration-executed` — a real transport/pool boundary executed;
- `decision` — contract selection remains open;
- `absent` — no accepted implementation exists.

## Surface and ownership matrix

| Surface | Owners | Current risk | Evidence | Disposition | Canonical record | Next bounded gate |
|---|---:|---|---|---|---|---|
| Async HTTPX `Response.aclose()` | one wrapper attempt | `is_closed` published before wrapped cleanup; interruption/failure/concurrency become terminal | released probe plus candidate `target-executed` | Accept exercised AnyIO owner/join state machine | #171 / PR #1 @ `04e2da580eea759e712df1656323ae0dd7d26bff` | Apply directly to clean source/tests |
| Wrapper concurrent callers | owner plus waiters | second released caller returns before cleanup | candidate executed under asyncio and Trio | one owner; waiters join; waiter cancellation stays local | #171 / PR #1 | Preserve on direct branch |
| Wrapper interruption retry | interrupted attempt then later owner | released retry is a no-op | candidate executed | clear wrapper ownership without reopening body reads | #171 / PR #1 | Keep claim pre-delegation scoped |
| Ordinary wrapper failure | owner plus current waiters | released response becomes terminal | candidate executed | share ordinary `Exception`; later explicit retry allowed | #171 / PR #1 | Review arbitrary custom-stream retry safety |
| Control-flow `BaseException` | interrupted owner plus waiters | careless sharing can replay process/control-flow signals | dedicated candidate executed | keep signal owner-scoped; wake waiters | #171 / PR #1 | Preserve exact classification |
| Body-read closure | content consumer | truthful cleanup state could accidentally reopen body access | candidate executed | permanent close-started barrier separate from completion | #171 / PR #1 | Review private-state naming |
| `AsyncClient.stream()` exit | context caller plus response | cancellation can interrupt implicit close | candidate executed | wrapper remains manually retryable | #171 / PR #1 | Test real partial-body transport path |
| Elapsed publication | bound stream plus timing state | elapsed available before cleanup succeeds | candidate executed | publish after successful close | #171 / PR #1 | Review failed-close compatibility |
| Pickle during close | live operation plus serialized copy | transient AnyIO state could be serialized | candidate executed | exclude attempt state; restored response closed/unattached | #171 / PR #1 | Review old pickle defaults |
| Default pool recovery before HTTPCore delegation | wrapper, bound stream, one-slot pool | interruption may retain pool slot | one deterministic `integration-executed` path | retry releases tested slot | #171 / PR #1 | Do not generalize post-delegation |
| HTTPCore HTTP/1.1 byte-stream close | byte stream plus connection release | `_closed=True` before lock/reuse/network close settles | `source-read`; tests prepared | no repair selected | #227 / PR #3 @ `0d9bbf8c8137102931d75fdf041980c67d22ab46` | Execute exact matrix, then instrument real connection state |
| HTTPCore HTTP/2 byte-stream close | byte stream, semaphore, event map, connection | `_closed=True` before capacity/event cleanup settles | `source-read`; tests prepared | no repair selected | #227 / PR #3 @ `0d9bbf8c8137102931d75fdf041980c67d22ab46` | Execute exact matrix, then instrument real capacity |
| HTTPCore trace callback reentry | close owner plus awaited user callback | shared-operation repair can create owner-waits-callback-waits-owner cycle | source-read; passing control prepared | preserve same-stream callback completion while external callers remain joinable | #227 / PR #3 | Execute control; require provenance/reentry review for shared operation |
| Same-socket reuse | pool plus socket identity | free pool slot does not prove identical socket safe | absent | no claim | #171 / #227 | instrument identity and protocol |
| Sync HTTPX `Response.close()` | one sync stream | close failure publishes terminal state and retry no-ops | released and target characterization executed | defect characterized; repair undecided | #185 / PR #2 @ `544638159ebfca6137e2a15001c00e9250dfb385` | decide retry, pickle, and thread policy |
| Two-thread sync close | stream plus OS-thread callers | no explicit shared ownership contract | decision | do not silently promise thread-safe joining | #185 | serialize, reject, or preserve boundary |
| Sync/async client close | main transport plus mounts | client `CLOSED` before every owner settles | source-read | multi-owner contract required | #177 | execute partial failure and retry model |
| Arbitrary custom close retry | user-defined owner | cleanup may be destructive or one-shot | decision | no universal retry claim | #171 / #185 / #227 / #177 | document minimum close contract |

## Failure-phase matrix

| Phase | HTTPX async wrapper | HTTPCore delegated close | Sync response | Client shutdown |
|---|---|---|---|---|
| Before owner starts | pre-cancelled entry executed | not applicable | ordinary call only | untested |
| Wrapper blocked before delegation | cancellation/join executed | not entered | not applicable | untested |
| Inner byte stream already marked closed | outer retry cannot force reentry | HTTP/1.1 and HTTP/2 controls prepared | not applicable | untested |
| Ordinary failure | sharing/retry executed | failure/retry no-op prepared | released failure executed | owner fan-out untested |
| Control-flow interruption | owner-scoped executed | cancellation prepared | thread/process signals open | open |
| Second concurrent caller | joins wrapper attempt | early return prepared | thread policy open | task/thread policy open |
| Same-owner callback reentry | no public callback at wrapper owner | trace-started close control prepared | sync trace callback is synchronous | multi-owner callback paths open |
| Retry after failure/interruption | wrapper-level executed | strict desired xfail prepared | strict desired xfail executed | partial-owner retry open |
| Serialization | in-progress pickle executed | inner stream not public serialized state | sync pickle open | not applicable |
| Real resource recovery | one pre-delegation pool path executed | post-delegation HTTP/1.1/HTTP/2 absent | absent | absent |
| Ordinary repository suite | async candidate passed | current PR #3 runs queued | sync characterization passed | absent |

## Accepted async wrapper invariant

```text
body_read_closed = close has started
cleanup_complete = wrapped stream close succeeded
current_attempt = one owner plus zero or more waiters
```

1. Body-read closure never reverses.
2. `is_closed` represents wrapped-stream completion, not intent.
3. One wrapper attempt owns one wrapped close call.
4. Ordinary failures are visible to current participants.
5. Cancellation and other control-flow signals stay with the interrupted caller.
6. Failed/interrupted wrapper ownership clears so a later explicit call may retry.
7. Successful completion is idempotent.
8. Transient coordination state is not serialized.
9. These rules do not prove an inner stream has not made its own release non-retryable.

## Competing HTTPCore contracts

| Direction | Benefit | Main risk |
|---|---|---|
| Shield delegated release | authoritative one-attempt completion | unbounded cancellation latency and late failure ownership |
| Retryable lower-layer state | completion truth and explicit retry | duplicate or partial HTTP/2 cleanup |
| Shared lower-layer operation | truthful joinable settlement | backend-neutral ownership and trace-callback reentry cycles |
| Explicit connection retirement | avoids retrying damaged protocol state | needs a durable retirement owner and truthful public state |

## Important non-claims

Current evidence does not establish:

- that every interrupted response leaks a socket;
- safe retry for every custom stream;
- same-socket reuse;
- post-delegation HTTP/2 capacity recovery;
- every HTTPCore interruption point;
- a selected shielding/retry/shared-operation/retirement contract;
- a sync production repair;
- a client multi-owner repair;
- upstream readiness or contact authority.

## Breadcrumbs

### Best next coding task

Create a clean direct async HTTPX source/test branch from PR #1's accepted state machine. Do not merge the exact-anchor transformer as production history.

### Best next research tasks

1. Process PR #3 exact head `0d9bbf8c8137102931d75fdf041980c67d22ab46` and confirm all current and strict-expected assertions.
2. Preserve the trace callback reentry control in every shared-operation design.
3. Instrument real HTTP/1.1 connection identity, reuse, and retirement.
4. Instrument real HTTP/2 semaphore capacity and event-map cleanup.
5. Inject interruption at named trace, lock, release, and network-close transitions.
6. Compare explicit close with HTTPCore's shielded error-cleanup paths.
7. Decide sync two-thread ownership before implementing #185.
8. Build a small multi-owner client shutdown model before touching #177 source.

### Review requirements

- Self-review is not independent acceptance.
- Exact-head receipts expire when source, tests, workflow, runtime pins, or reviewed invariants change.
- Harness/setup failures remain separate from product evidence.
- Keep HTTPX wrapper, HTTPCore delegated close, sync response, and client shutdown as distinct nodes.
- Public upstream remains read-only unless separately authorized.
