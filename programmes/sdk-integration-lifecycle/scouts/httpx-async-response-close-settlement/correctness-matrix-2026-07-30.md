# HTTPX close and shutdown correctness matrix

Date: `2026-07-30`

Parent scout: #171  
Async response candidate: `teamleaderleo/httpx#1`  
Sync response characterization: #185 / `teamleaderleo/httpx#2`  
Client shutdown lane: #177  
Upstream contact authorized: `false`

## Why this matrix exists

HTTPX exposes a small set of public terminal-looking facts such as `response.is_closed` and client `CLOSED` state, but those facts sit above several different cleanup owners:

- one sync or async response stream;
- a bound transport stream that also publishes elapsed time;
- one HTTP/1.1 connection lease or one HTTP/2 stream slot;
- a client main transport;
- zero or more mounted proxy transports;
- context-manager callers and explicit close callers;
- transient concurrency state that must not survive serialization.

A single broad “close bug” label would hide important differences. Each row below has its own evidence floor and next gate.

## Evidence legend

- `source-read` — implementation and ownership path inspected;
- `target-executed` — repository or released public behavior executed;
- `integration-executed` — a real transport/pool boundary executed;
- `decision` — correctness contract still needs explicit selection;
- `absent` — no accepted implementation exists.

## Surface and ownership matrix

| Surface | Cleanup owners | Current released risk | Evidence | Current disposition | Canonical record | Next bounded gate |
|---|---:|---|---|---|---|---|
| Async `Response.aclose()` | 1 async stream attempt | Publishes `is_closed=True` before awaited cleanup; cancellation, failure, or a concurrent caller can leave public state ahead of settlement | released probe `target-executed`; candidate and adjacent controls `target-executed` | Accept exercised per-attempt AnyIO ownership model | #171 / HTTPX PR #1 @ `04e2da580eea759e712df1656323ae0dd7d26bff` | Apply directly to clean source/tests and review the source-only diff |
| Async close attempt join | 1 current owner plus waiters | A second released caller returns early rather than joining authoritative cleanup | candidate `target-executed` under asyncio and Trio | One owner; waiters join; cancelled waiter does not cancel owner | #171 / HTTPX PR #1 | Preserve behavior on direct source branch |
| Async interruption retry | 1 interrupted attempt, then later owner | Released cancellation or close failure makes later public retry a no-op | candidate `target-executed` | Interruption clears attempt ownership without reopening body reads | #171 / HTTPX PR #1 | Probe interruption after delegation inside HTTPCore, not only before delegation |
| Ordinary async close error | owner plus current waiters | Released state becomes terminal; no retry | candidate `target-executed` | Share ordinary `Exception` with current waiters; later explicit call may retry | #171 / HTTPX PR #1 | Review arbitrary custom transport retry safety |
| Async control-flow `BaseException` | interrupted owner plus unrelated waiters | A careless shared-error design can replay process/control-flow interruption into waiters | dedicated candidate regression `target-executed` | Keep control-flow signal owner-scoped; wake waiters to retry | #171 / HTTPX PR #1 | Preserve exact exception classification on direct source branch |
| Body-read admission after close begins | response content consumer | Moving `is_closed` after cleanup could accidentally reopen body reads after failure | candidate `target-executed` | Separate permanent close-started barrier from cleanup completion | #171 / HTTPX PR #1 | Review public/private state naming and invariants |
| `AsyncClient.stream()` context exit | response stream plus context-exit caller | Caller cancellation can interrupt implicit response cleanup | candidate `target-executed` | Cancelled exit leaves manual response close retryable | #171 / HTTPX PR #1 | Add real transport interruption after partial body consumption |
| `BoundAsyncStream` elapsed publication | bound stream plus response timing state | Released code publishes elapsed time before underlying close succeeds | candidate `target-executed` | Publish elapsed only after successful underlying close | #171 / HTTPX PR #1 | Confirm no compatibility expectation relies on elapsed after failed close |
| Response pickle during in-progress async close | live response attempt plus serialized copy | Transient AnyIO event/attempt state must not be serialized | candidate `target-executed` | Exclude transient state; restored response is closed and unattached | #171 / HTTPX PR #1 | Review older pickle compatibility and direct-source field defaults |
| Default transport pool-slot recovery | response wrapper, HTTPCore stream, one-slot pool | Interrupted cleanup may retain a scarce pool slot | one deterministic local-server path `integration-executed` with HTTPCore `1.0.9` | Retry releases the tested slot and a follow-up request succeeds | #171 / HTTPX PR #1 | Separate HTTP/1.1 connection reuse from HTTP/2 stream-capacity recovery |
| Same-socket reuse | connection pool and specific socket | Pool availability does not prove the identical socket was safely reusable | absent | No claim | #171 | Instrument connection identity and protocol before/after retry |
| Every HTTPCore close interruption point | HTTP/1.1 or HTTP/2 stream state machine | The executed blocker interrupts before delegation, not inside each transport state transition | absent | No claim | #171 | Map and test post-delegation interruption points in HTTPCore |
| Sync `Response.close()` | 1 sync stream | Publishes `is_closed=True` before cleanup; ordinary failure makes retry a no-op | released probe and target-native characterization `target-executed` | Defect characterized; production contract not yet selected | #185 / HTTPX PR #2 @ `544638159ebfca6137e2a15001c00e9250dfb385` | Decide retry safety, pickle state, and thread ownership before source code |
| Sync body-read admission | response content consumer | A retryable completion flag must not reopen content after close starts | target-native characterization `target-executed` | Preserve a separate close-started barrier | #185 / HTTPX PR #2 | Add candidate only after concurrency policy is selected |
| Two-thread sync response close | one stream, two OS-thread callers | HTTPX does not currently provide an explicit shared close operation | `decision` | Do not silently promise thread-safe joining | #185 | Decide serialize, reject, or preserve non-thread-safe boundary |
| Sync `Client.close()` | main transport plus mounted transports | Publishes client `CLOSED` before all owners settle; first failure can skip later owners and make retry a no-op | `source-read` | Separate multi-owner shutdown policy required | #177 | Execute main/middle/last-owner failures and partial retry model |
| Async `AsyncClient.aclose()` | main async transport plus mounted proxy transports | Same early terminal publication plus cancellation and concurrent callers | `source-read` | Separate multi-owner async settlement required | #177 | Select continuation, aggregation, retry, and waiter policy |
| Client context exits | client plus all transports | `__exit__` / `__aexit__` should not diverge from explicit close ownership | `source-read` | Explicit and context-manager close should share one contract | #177 | Add parity controls after policy selection |
| Arbitrary custom transport/stream retry | user-defined cleanup owner | Some custom cleanup operations may be destructive or intentionally one-shot | `decision` | Do not claim universal retry safety | #171 / #185 / #177 | Document minimum close contract or narrow retry guarantee |

## Failure-phase test matrix

| Phase | Async response | Sync response | Client shutdown | Current status |
|---|---|---|---|---|
| Before cleanup owner starts | pre-cancelled entry covered | ordinary call only | untested | Async executed |
| While underlying close is blocked | owner cancellation and joined waiter covered | not cancellable in same model | source-read only | Async executed |
| Underlying ordinary failure | owner and current waiter sharing covered | released failure characterized | owner fan-out untested | Async/sync executed at response layer |
| Control-flow interruption | owner-scoped, waiter retry covered | thread/process signals undecided | undecided | Async executed |
| Second concurrent caller | joins current attempt | thread policy undecided | task/thread policy undecided | Async executed only |
| Retry after interruption/failure | covered | desired contract is strict expected failure | partial-owner retry undecided | Async accepted; sync/client open |
| Body read after close starts | blocked | blocked in current behavior | not applicable | Response layers executed |
| Repeated close after success | idempotent | idempotent | multi-owner idempotence untested | Response layers executed |
| Context-manager exit | cancelled async exit covered | ordinary sync exit adjacent only | explicit/context parity untested | Partial |
| Serialization | in-progress async pickle covered | sync pickle decision open | client serialization not applicable | Async executed |
| Real pool/resource recovery | one deterministic default-pool slot covered | absent | absent | Narrow integration receipt |
| Full ordinary repository suite | passed on async exact head | passed on sync characterization head | absent | Response branches green |

## Accepted async invariant

For the exercised async response contract:

```text
body_read_closed = close has started
cleanup_complete = underlying stream close succeeded
current_attempt = one owner plus zero or more waiters
```

Rules:

1. `body_read_closed` never goes back to false.
2. `is_closed` represents `cleanup_complete`, not merely intent.
3. One current attempt owns one underlying close invocation.
4. Ordinary errors are visible to current participants.
5. Cancellation and other control-flow signals stay with the interrupted caller.
6. An interrupted or failed attempt clears current ownership so a later explicit close may retry.
7. Successful completion is idempotent.
8. Transient coordination state is not serialized.

## Important non-claims

The current evidence does **not** establish:

- that every interrupted response leaks a socket;
- that every custom stream can safely retry close;
- same-socket reuse;
- all HTTP/2 stream-reset and capacity-release paths;
- every interruption point inside HTTPCore;
- a selected synchronous production repair;
- a selected multi-transport client shutdown repair;
- upstream readiness or contact authority.

## Breadcrumbs for the next investigator

### Best next coding task

Create a clean direct async source/test branch from HTTPX PR #1's accepted state machine. Do not merge the exact-anchor transformer into production history. Preserve all focused tests and run the repository's ordinary gate on the direct diff.

### Best next research tasks

1. Instrument HTTP/1.1 connection identity to distinguish pool-slot recovery from same-socket reuse.
2. Map HTTP/2 response close into stream reset/removal and connection stream-capacity accounting.
3. Inject cancellation after HTTPCore has begun close, at each meaningful transition.
4. Decide the synchronous two-thread boundary before implementing #185.
5. Build a small multi-owner client shutdown model before touching #177 source.
6. Review whether request admission needs an internal `CLOSING` state while client teardown is incomplete.

### Review requirements

- Self-review does not satisfy independent acceptance.
- Exact-head receipts expire when source, tests, transformer, workflow, or runtime pins change.
- Harness/setup failures remain separate from product behavior.
- Keep response, sync response, and client shutdown as distinct review nodes.
- Public upstream remains read-only unless separate authority is granted.
