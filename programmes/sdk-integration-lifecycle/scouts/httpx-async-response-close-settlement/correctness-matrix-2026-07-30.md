# HTTPX close and shutdown correctness matrix

Date: `2026-07-30`

Parent scout: #171  
Async response candidate: `teamleaderleo/httpx#1`  
Sync response characterization: #185 / `teamleaderleo/httpx#2`  
Delegated HTTPCore close characterization: #227 / `teamleaderleo/httpx#3`  
Client shutdown lane: #177  
Upstream contact authorized: `false`

## Why this matrix exists

HTTPX exposes a small set of public terminal-looking facts such as `response.is_closed` and client `CLOSED` state, but those facts sit above several different cleanup owners:

- one sync or async response stream;
- a bound transport stream that also publishes elapsed time;
- an HTTPCore HTTP/1.1 or HTTP/2 response byte stream;
- one HTTP/1.1 connection lease or one HTTP/2 stream-capacity slot;
- a client main transport;
- zero or more mounted proxy transports;
- context-manager callers and explicit close callers;
- transient concurrency state that must not survive serialization.

A single broad “close bug” label would hide important differences. Each row below has its own evidence floor and next gate.

## Evidence legend

- `source-read` — implementation and ownership path inspected;
- `target-test-prepared` — target-native test exists but has no accepted execution receipt;
- `target-executed` — repository or released public behavior executed;
- `integration-executed` — a real transport/pool boundary executed;
- `decision` — correctness contract still needs explicit selection;
- `absent` — no accepted implementation exists.

## Surface and ownership matrix

| Surface | Cleanup owners | Current released risk | Evidence | Current disposition | Canonical record | Next bounded gate |
|---|---:|---|---|---|---|---|
| Async `Response.aclose()` | 1 async wrapper attempt | Publishes `is_closed=True` before awaited cleanup; cancellation, failure, or a concurrent caller can leave public state ahead of settlement | released probe `target-executed`; candidate and adjacent controls `target-executed` | Accept exercised per-attempt AnyIO ownership model | #171 / HTTPX PR #1 @ `04e2da580eea759e712df1656323ae0dd7d26bff` | Apply directly to clean source/tests and review the source-only diff |
| Async close attempt join | 1 current owner plus waiters | A second released caller returns early rather than joining authoritative cleanup | candidate `target-executed` under asyncio and Trio | One owner; waiters join; cancelled waiter does not cancel owner | #171 / HTTPX PR #1 | Preserve behavior on direct source branch |
| Async interruption retry before lower-layer ownership | 1 interrupted wrapper attempt, then later owner | Released cancellation or close failure makes later public retry a no-op | candidate `target-executed` | Interruption clears wrapper ownership without reopening body reads | #171 / HTTPX PR #1 | Keep claim scoped to wrapper/pre-delegation behavior |
| Ordinary async close error | owner plus current waiters | Released state becomes terminal; no retry | candidate `target-executed` | Share ordinary `Exception` with current waiters; later explicit call may retry | #171 / HTTPX PR #1 | Review arbitrary custom transport retry safety |
| Async control-flow `BaseException` | interrupted owner plus unrelated waiters | A careless shared-error design can replay process/control-flow interruption into waiters | dedicated candidate regression `target-executed` | Keep control-flow signal owner-scoped; wake waiters to retry | #171 / HTTPX PR #1 | Preserve exact exception classification on direct source branch |
| Body-read admission after close begins | response content consumer | Moving `is_closed` after cleanup could accidentally reopen body reads after failure | candidate `target-executed` | Separate permanent close-started barrier from cleanup completion | #171 / HTTPX PR #1 | Review public/private state naming and invariants |
| `AsyncClient.stream()` context exit | response stream plus context-exit caller | Caller cancellation can interrupt implicit response cleanup | candidate `target-executed` | Cancelled exit leaves manual response close retryable at wrapper level | #171 / HTTPX PR #1 | Add real transport interruption after partial body consumption |
| `BoundAsyncStream` elapsed publication | bound stream plus response timing state | Released code publishes elapsed time before underlying close succeeds | candidate `target-executed` | Publish elapsed only after successful cleanup | #171 / HTTPX PR #1 | Confirm no compatibility expectation relies on elapsed after failed close |
| Response pickle during in-progress async close | live response attempt plus serialized copy | Transient AnyIO event/attempt state must not be serialized | candidate `target-executed` | Exclude transient state; restored response is closed and unattached | #171 / HTTPX PR #1 | Review older pickle compatibility and direct-source field defaults |
| Default transport pool-slot recovery before HTTPCore delegation | response wrapper, bound stream, one-slot pool | Interrupted cleanup may retain a scarce pool slot | one deterministic local-server path `integration-executed` with HTTPCore `1.0.9` | Retry releases the tested slot and a follow-up request succeeds | #171 / HTTPX PR #1 | Do not generalize to post-delegation interruption |
| HTTPCore HTTP/1.1 byte-stream close | inner byte stream plus connection release | Sets private `_closed=True` before awaited connection-state or network close | `source-read`; target characterization prepared | No repair selected | #227 / HTTPX PR #3 @ `d75f374d4c6833602ffd3865f27afb45263efb84` | Execute cancellation, failure, concurrent caller, and strict retry controls |
| HTTPCore HTTP/2 byte-stream close | inner byte stream, semaphore slot, event map, connection state | Sets private `_closed=True` before stream-capacity/event cleanup settles | `source-read`; target characterization prepared | No repair selected | #227 / HTTPX PR #3 @ `d75f374d4c6833602ffd3865f27afb45263efb84` | Execute synthetic controls, then instrument real stream capacity |
| Same-socket reuse | connection pool and specific socket | Pool availability does not prove the identical socket was safely reusable | absent | No claim | #171 / #227 | Instrument connection identity and protocol before/after retry |
| Every HTTPCore close interruption point | HTTP/1.1 or HTTP/2 state machine | Existing integration interrupts before delegation; PR #3 begins lower-layer characterization but not real transition coverage | `target-test-prepared` | Research split selected; behavior pending | #227 / HTTPX PR #3 | Process exact runs, then inject real interruption at named transitions |
| Sync `Response.close()` | 1 sync stream | Publishes `is_closed=True` before cleanup; ordinary failure makes retry a no-op | released probe and target-native characterization `target-executed` | Defect characterized; production contract not yet selected | #185 / HTTPX PR #2 @ `544638159ebfca6137e2a15001c00e9250dfb385` | Decide retry safety, pickle state, and thread ownership before source code |
| Sync body-read admission | response content consumer | A retryable completion flag must not reopen content after close starts | target-native characterization `target-executed` | Preserve a separate close-started barrier | #185 / HTTPX PR #2 | Add candidate only after concurrency policy is selected |
| Two-thread sync response close | one stream, two OS-thread callers | HTTPX does not currently provide an explicit shared close operation | `decision` | Do not silently promise thread-safe joining | #185 | Decide serialize, reject, or preserve non-thread-safe boundary |
| Sync `Client.close()` | main transport plus mounted transports | Publishes client `CLOSED` before all owners settle; first failure can skip later owners and make retry a no-op | `source-read` | Separate multi-owner shutdown policy required | #177 | Execute main/middle/last-owner failures and partial retry model |
| Async `AsyncClient.aclose()` | main async transport plus mounted proxy transports | Same early terminal publication plus cancellation and concurrent callers | `source-read` | Separate multi-owner async settlement required | #177 | Select continuation, aggregation, retry, and waiter policy |
| Client context exits | client plus all transports | `__exit__` / `__aexit__` should not diverge from explicit close ownership | `source-read` | Explicit and context-manager close should share one contract | #177 | Add parity controls after policy selection |
| Arbitrary custom transport/stream retry | user-defined cleanup owner | Some custom cleanup operations may be destructive or intentionally one-shot | `decision` | Do not claim universal retry safety | #171 / #185 / #227 / #177 | Document minimum close contract or narrow retry guarantee |

## Failure-phase test matrix

| Phase | HTTPX async wrapper | HTTPCore delegated close | Sync response | Client shutdown | Current status |
|---|---|---|---|---|---|
| Before cleanup owner starts | pre-cancelled entry covered | not applicable | ordinary call only | untested | Wrapper executed |
| While wrapper close is blocked before delegation | owner cancellation and joined waiter covered | not entered | not cancellable in same model | source-read only | Wrapper executed |
| After HTTPCore byte stream marks closed | outer retry cannot force inner re-entry | HTTP/1.1 and HTTP/2 controls prepared | not applicable | untested | #227 prepared |
| Underlying ordinary failure | owner and current waiter sharing covered | failure/retry no-op controls prepared | released failure characterized | owner fan-out untested | Wrapper/sync executed; HTTPCore pending |
| Control-flow interruption | owner-scoped, waiter retry covered | cancellation control prepared | thread/process signals undecided | undecided | Wrapper executed; lower layer pending |
| Second concurrent caller | joins current wrapper attempt | early-return control prepared | thread policy undecided | task/thread policy undecided | Wrapper executed; lower layer pending |
| Retry after interruption/failure | covered at wrapper level | desired contract strict expected failure prepared | desired contract strict expected failure | partial-owner retry undecided | Async wrapper accepted; lower layers open |
| Body read after close starts | blocked | byte-stream content already owned by upper response | blocked in current behavior | not applicable | Response layers executed |
| Repeated close after success | idempotent | existing private guard | idempotent | multi-owner idempotence untested | Response layers executed |
| Context-manager exit | cancelled async exit covered | delegated behavior unresolved | ordinary sync exit adjacent only | explicit/context parity untested | Partial |
| Serialization | in-progress async pickle covered | lower stream is not public serialized state | sync pickle decision open | client serialization not applicable | Async wrapper executed |
| Real pool/resource recovery | one deterministic pre-delegation pool slot covered | real HTTP/1.1/HTTP/2 post-delegation gate absent | absent | absent | Narrow integration receipt only |
| Full ordinary repository suite | passed on async exact head | queued on PR #3 current head | passed on sync characterization head | absent | Wrapper/sync green; delegated pending |

## Accepted async wrapper invariant

For the exercised HTTPX async response contract:

```text
body_read_closed = close has started
cleanup_complete = wrapped stream close succeeded
current_attempt = one owner plus zero or more waiters
```

Rules:

1. `body_read_closed` never goes back to false.
2. `is_closed` represents wrapped-stream completion, not merely intent.
3. One current wrapper attempt owns one wrapped close invocation.
4. Ordinary errors are visible to current participants.
5. Cancellation and other control-flow signals stay with the interrupted caller.
6. An interrupted or failed wrapper attempt clears current ownership so a later explicit close may retry.
7. Successful completion is idempotent.
8. Transient coordination state is not serialized.
9. These rules do not prove that an inner stream has not separately made its own cleanup non-retryable.

## Important non-claims

The current evidence does **not** establish:

- that every interrupted response leaks a socket;
- that every custom stream can safely retry close;
- same-socket reuse;
- HTTP/2 stream-capacity recovery after post-delegation interruption;
- every interruption point inside HTTPCore;
- a selected shielding, lower-layer retry, shared operation, or connection-retirement contract;
- a selected synchronous production repair;
- a selected multi-transport client shutdown repair;
- upstream readiness or contact authority.

## Breadcrumbs for the next investigator

### Best next coding task

Create a clean direct async HTTPX source/test branch from PR #1's accepted state machine. Do not merge the exact-anchor transformer into production history. Preserve all focused tests and run the repository's ordinary gate on the direct diff.

### Best next research tasks

1. Process HTTPX PR #3 and confirm its HTTP/1.1/HTTP/2 assertions under asyncio and Trio.
2. Instrument real HTTP/1.1 connection identity to distinguish pool-slot recovery, socket reuse, and retirement.
3. Instrument real HTTP/2 semaphore capacity and event-map cleanup after delegated interruption.
4. Inject interruption after HTTPCore has begun close at named lock, release, and network-close transitions.
5. Compare explicit byte-stream close with HTTPCore's shielded exception-cleanup paths.
6. Decide the synchronous two-thread boundary before implementing #185.
7. Build a small multi-owner client shutdown model before touching #177 source.
8. Review whether request admission needs an internal `CLOSING` state while client teardown is incomplete.

### Review requirements

- Self-review does not satisfy independent acceptance.
- Exact-head receipts expire when source, tests, transformer, workflow, or runtime pins change.
- Harness/setup failures remain separate from product behavior.
- Keep HTTPX wrapper, HTTPCore delegated close, sync response, and client shutdown as distinct review nodes.
- Public upstream remains read-only unless separate authority is granted.
