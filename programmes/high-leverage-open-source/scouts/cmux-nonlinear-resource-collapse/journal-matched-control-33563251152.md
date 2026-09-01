# cmux journal forwarder — matched stalled-endpoint control

Date: 2026-09-01  
Target upstream: `manaflow-ai/cmux`  
Pinned upstream revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Pinned `journal_forwarder.rs` blob: `9b4551770e807084c48c2cdbe94f15f2cf2358e0`  
Owned fork: `teamleaderleo/cmux`  
Experiment branch: `fieldwork/nonlinear-resource-collapse`  
Unpatched matched run: `33563251152`, job `100040453057`, artifact `9822190187`  
Backpressure + handoff candidate run: `33563303120`, job `100040622915`, artifact `9822197573`  
Upstream contact: none

## Result

The managed session-journal forwarder has an executable resource-collapse failure behind one stalled POST. The scaling variable is aggregate records accepted into the forwarder's shared pending pool while its single HTTP consumer is blocked. Session count is one multiplier of that arrival rate; one sufficiently hot session is enough to trigger the failure.

The exact matched 1.5-second pressure run separates the mechanism sharply. The upstream-pinned forwarder consumed hundreds of thousands of 1 KiB synthetic journal records into retained state and reached roughly 0.56–1.13 GiB RSS. The candidate bounds the relay-side next batch and backpressures its session readers, accepting only roughly 300–12,000 records over the same 1.5 seconds and holding RSS around 9–16 MiB.

Both runs used the same harness, stall mode, record payload, duration, producer upper limit, session sequence, and HTTP endpoint behavior.

## Matched workload

For each requested session count `1, 10, 50, 128, 200`:

- HTTP endpoint accepts one POST and never responds during the measured load;
- per-record synthetic payload: 1,024 bytes;
- per-producer upper limit: 1,000,000 records;
- fixed load interval: 1,500 ms;
- post-load settle interval before cancellation: 100 ms;
- forwarder discovery cap remains 128 active sessions;
- resource samples are collected before forwarder cancellation;
- cleanup FD sample is collected after cancellation and worker joins.

## Unpatched upstream-pinned control

The workflow first verified that the branch copy of `cmux-tui/crates/chatmux-relay/src/journal_forwarder.rs` had blob `9b4551770e807084c48c2cdbe94f15f2cf2358e0`, the same blob as pinned upstream.

| Requested sessions | Accepted | Generated at measurement | Loaded RSS KiB | Loaded FDs | Cleanup FDs | HTTP requests |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 162,341 | 570,780 | 18 | 12 | 1 |
| 10 | 10 | 302,564 | 1,056,024 | 45 | 12 | 1 |
| 50 | 50 | 308,966 | 1,074,568 | 165 | 12 | 1 |
| 128 | 128 | 326,599 | 1,126,824 | 399 | 12 | 1 |
| 200 | 128 | 248,334 | 858,492 | 471 | 12 | 1 |

Baseline RSS was roughly 4.7–5.2 MiB. The 200-requested case again accepted 128 sessions because `MAX_DISCOVERED_SESSIONS = 128`.

The strongest threshold refinement is N=1. At a high enough event rate, one session reached 570,780 KiB RSS in 1.5 seconds behind one blocked HTTP request. This means session count itself is not the fundamental threshold. The first non-converging owner is the shared pending-record pool, and the controlling variable is the number/bytes of records admitted while the shared consumer has zero service rate.

## Candidate with bounded next-batch backpressure

Candidate semantics:

- retain at most one batch in the retrying POST owner;
- retain at most one bounded next batch in `PoolState.pending`;
- bound that pending batch by both `MAX_BATCH_RECORDS` and `MAX_BATCH_BODY_BYTES`;
- when the next batch reaches the limit, stop reading journal session sockets until capacity returns;
- when the in-flight POST completes and a producer wins the handoff race, rotate the already-full pending batch before admitting the producer's next record, preserving the exact 100-record ready boundary;
- wake blocked producers whenever pending records move into the in-flight/ready slot.

All 28 journal-forwarder tests passed, including:

- `busy_pool_backpressures_after_one_bounded_pending_batch`;
- `busy_pool_byte_budget_bounds_large_records`;
- `post_completion_handoff_keeps_the_next_ready_batch_exact`.

Matched stalled results after both candidate patches:

| Requested sessions | Accepted | Generated at measurement | Loaded RSS KiB | Loaded FDs | Cleanup FDs | HTTP requests |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 297 | 8,820 | 18 | 12 | 1 |
| 10 | 10 | 1,108 | 9,008 | 45 | 12 | 1 |
| 50 | 50 | 4,833 | 11,760 | 165 | 12 | 1 |
| 128 | 128 | 12,033 | 15,136 | 399 | 12 | 1 |
| 200 | 128 | 12,040 | 15,584 | 471 | 12 | 1 |

At 128 accepted sessions, the matched RSS reduction is approximately 1,126,824 KiB to 15,136 KiB, about 74x. The candidate turns retained-memory growth into producer backpressure.

## Healthy negative control

With 50 sessions × 300 records × 1 KiB and an immediate local ACK endpoint, the handoff candidate produced:

- baseline RSS: 5,200 KiB;
- loaded RSS: 14,524 KiB;
- cleanup RSS: 14,596 KiB;
- FDs: 63 → 163 → 12;
- generated records: 15,000;
- HTTP requests: 150.

The 150 requests correspond to exact 100-record batching for 15,000 records. Earlier upstream behavior coalesced the same burst into only nine POSTs and peaked around 103 MiB RSS, so the candidate deliberately exchanges more HTTP requests for a tight retained-memory bound.

## End-to-end pressure relocation check

Backpressure on the relay session reader does not create an unbounded second queue inside cmux-tui. The pinned server uses a backpressured resource-stream path with a two-message per-stream queue, regular outbound byte accounting, and an aggregate regular outbound byte budget. `REMOTE_SESSION_MESSAGE_MAX_BYTES` is 32 MiB and the process-wide regular outbound budget is four such units (128 MiB). Once those bounded budgets fill, the server-side sender waits.

The journal stream messages are themselves bounded well below the generic 32 MiB server-message ceiling by the journal line limit. Therefore the candidate changes the failure mode from unbounded relay heap growth into bounded socket/server backpressure.

## Teardown

Across every matched unpatched and candidate case, the forwarder process FD count returned to 12 after cancellation and worker joining. RSS remained elevated after large upstream runs because the allocator retained previously allocated pages; short-horizon RSS is therefore a weak teardown metric here. FD convergence and joined worker ownership are the stronger teardown evidence.

## Consequence classification

Upstream consequence: **resource exhaustion / outage risk**, preceded by severe degradation. One stalled managed-events POST can make a healthy session-journal producer population feed an uncapped retained pool. The mechanism does not require CPU saturation, retry overlap, or hundreds of sessions; it requires producer arrival to continue while the single HTTP consumer cannot make progress.

Candidate consequence under the same failure: **bounded delivery stall / producer backpressure**. Memory remains close to a small bounded working set while journal delivery waits for the endpoint to recover.

## Evidence limits

- The producer is synthetic and intentionally much hotter than ordinary interactive usage; the run proves mechanism and failure capability, not typical frequency in production.
- The relay harness is the actual Rust `journal_forwarder::start` path over Unix sockets and real reqwest POST handling, executed on Ubuntu GitHub Actions.
- The end-to-end server queue bound is source-confirmed; a full multi-process cmux-tui + relay RSS run under the same synthetic rate has not yet been executed.
- Cleanup-time `Broken pipe` lines from fake producers occur after the harness takes the loaded measurements and cancels the forwarder; they are harness shutdown noise.
- The candidate is validated as a patch applied to the pinned journal source. Promotion into the owned fork source should preserve the exact tested diff.
