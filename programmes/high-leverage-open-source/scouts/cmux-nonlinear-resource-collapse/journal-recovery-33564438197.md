# cmux journal backpressure — stall / stop / recover result

Date: 2026-09-01  
Pinned upstream revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Owned fork: `teamleaderleo/cmux`  
Experiment branch: `fieldwork/nonlinear-resource-collapse`  
Run: `33564438197`  
Job: `100044270329`  
Artifact: `9822660301` (`journal-source-results`)  
Run head: `bc71bd878c7ffb7152bdc2e994a4187a32f0875f`  
Production journal promotion commit: `3948c73c4cac4dd2fe10e5bc0275b8c56bdd9ed7`  
Upstream contact: none

## Sequence

This run measures convergence after load ceases without cancelling the journal forwarder.

1. Start 128 synthetic cmux-tui journal sessions.
2. Start the real `journal_forwarder::start` path from the landed fork source.
3. Let the managed-events endpoint accept the first POST and hold the response.
4. Produce 1 KiB records for 1,500 ms.
5. Stop the producers while keeping the forwarder and all session subscriptions alive.
6. Wait until all 128 producers acknowledge the stop.
7. Freeze the generated-record target and measure the stalled state.
8. Release the held HTTP response; subsequent POSTs ACK immediately.
9. Wait until the HTTP receiver has counted every generated record in POST bodies.
10. Measure recovery settle time, RSS, and FDs while the forwarder remains alive.
11. Cancel the forwarder and measure final cleanup.

The generated count is taken after producer stop. It includes records accepted by the Unix sockets, so recovery must drain both the relay's bounded batches and bounded upstream socket/server pressure before the experiment declares convergence.

## Measurements

- accepted sessions: 128
- generated records at producer stop: 12,018
- delivered records at stalled measurement: 0
- HTTP requests at stalled measurement: 1
- baseline RSS: 5,188 KiB
- stalled loaded RSS: 15,684 KiB
- baseline FDs: 141
- stalled loaded FDs: 399

After endpoint recovery:

- delivered records: 12,018 / 12,018
- settle time: **839 ms**
- total HTTP requests: 121
- recovered RSS: 18,200 KiB
- recovered FDs: 397

After final forwarder cancellation:

- cleanup RSS: 18,264 KiB
- cleanup FDs: **12**

## Interpretation

The bounded journal implementation recovers from the stalled single-consumer condition without cancelling or recreating the forwarder. All 12,018 records that had been accepted before producer stop were delivered in 839 ms after the endpoint resumed.

The 121 total HTTP requests are consistent with the first held batch plus roughly 120 subsequent ~100-record batches. This is the intended trade: more bounded requests in exchange for a strict retained-memory ceiling.

The FD count remains 397 immediately after delivery because the 128 journal session subscriptions are intentionally still connected. Delivery backlog has converged; session ownership remains live. Final cancellation closes those owned session resources and returns the process to 12 FDs.

RSS rises from 15,684 KiB under stall to 18,200 KiB after drain and remains 18,264 KiB after cleanup. This short-horizon RSS value reflects allocator page retention and request/serialization activity; it does not track live ownership cleanly after deallocation. FD convergence and the exact delivered-record count provide stronger teardown and settle evidence here.

## Result against the invariant

Under the repaired forwarder:

- load during a downstream outage stays within a small bounded working set;
- producer pressure is propagated backward instead of accumulating in one uncapped relay pool;
- after producer stop and endpoint recovery, delivery converges in under one second in this 128-session run;
- live session subscriptions remain until explicit teardown, as intended;
- teardown returns owned FDs to the same 12-FD floor seen in the stalled and healthy controls.

The original collapse consequence was resource exhaustion / outage risk. The repaired consequence under the same downstream failure is a bounded delivery stall with backpressure and prompt recovery.

## Evidence limits

- This is a synthetic high-rate workload designed to expose the owner and convergence behavior; it does not estimate ordinary interactive event rates.
- The forwarder and Unix socket path are real; the journal producers and HTTP endpoint are local synthetic peers.
- The recovery harness is measurement-only and is applied in CI to the example harness. Production code under test is the landed `journal_forwarder.rs` source.
- Server-side queue bounds are source-confirmed separately; this run does not sample RSS from a separate full cmux-tui server process.
