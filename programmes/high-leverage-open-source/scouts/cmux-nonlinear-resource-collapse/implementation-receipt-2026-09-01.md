# cmux nonlinear resource-collapse — implementation receipt

Date: 2026-09-01  
Pinned upstream revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Upstream contact: none

## Landed journal fix

Primary promotion commit: `3948c73c4cac4dd2fe10e5bc0275b8c56bdd9ed7`  
Commit message: `fix(relay): bound journal backlog during stalled delivery`

The guarded promotion required the production source to still have pinned upstream blob `9b4551770e807084c48c2cdbe94f15f2cf2358e0`. The promotion commit changed only:

`cmux-tui/crates/chatmux-relay/src/journal_forwarder.rs`

Diff size: +256 / -12.

The source now owns one bounded pending batch behind the retrying/in-flight batch. Bounds are both `MAX_BATCH_RECORDS` and `MAX_BATCH_BODY_BYTES`; session workers wait when that next batch is full. Capacity wake-up occurs when pending records are rotated into a ready/in-flight batch and when a POST completes. The post-completion producer handoff preserves the exact 100-record ready boundary.

### Byte-threshold continuation follow-up

Follow-up production commit: `e6f7f36fce1d27538acc2c3b05d1763044b397f8`  
Commit message: `fix(relay): flush byte-full journal backlog immediately`

This changed only `journal_forwarder.rs`, +19 / -5. The source now uses one `pending_threshold_reached(records, bytes)` predicate for both ingress and post-completion continuation. A next batch that reaches the 4 MiB byte ceiling with fewer than 100 records continues immediately after the current POST rather than waiting for the debounce.

The regression test `pending_threshold_considers_record_and_byte_limits` covers below-threshold, record-threshold, byte-threshold, and combined cases.

All temporary write-capable promotion workflows used for the guarded source commits were removed after promotion.

## Landed-source verification

Run `33564015233` verified the committed main journal backpressure source without applying the backpressure candidate patches in CI.

`journal-backpressure-source`: success.

- source guard: success
- journal-forwarder test suite: 28 passed
- healthy 50-session control: success
- stalled 1/10/50/128/200 fixed-duration sequence: success
- result artifact: `9822493269`

Healthy 50-session control (15,000 records, 1 KiB payloads):

- baseline RSS 4,928 KiB
- loaded RSS 14,472 KiB
- cleanup RSS 14,536 KiB
- FDs 63 → 163 → 12
- HTTP requests 150

Stalled 1.5-second landed-source points:

- N=1: 295 generated, 8,516 KiB RSS
- N=10: 1,111 generated, 8,840 KiB RSS
- N=50: 4,832 generated, 11,704 KiB RSS
- N=128: 12,116 generated, 16,368 KiB RSS
- N=200 requested / 128 accepted: 12,129 generated, 15,636 KiB RSS

All stalled cases issued one HTTP request and returned to 12 FDs after cancellation.

Run `33565064189` verified the byte-threshold follow-up as an applied candidate together with the full journal controls and recovery harness. Every job passed, including the journal tests, healthy control, stalled scaling, recovery probe, pinned-upstream RPC controls, and current RPC candidate checks. The subsequent guarded promotion produced exact production commit `e6f7f36fce1d27538acc2c3b05d1763044b397f8`.

## Journal recovery

Run `33564438197`, job `100044270329`, artifact `9822660301` measured stall → producer stop → endpoint recovery while the forwarder stayed alive.

At 128 accepted sessions:

- generated before stop: 12,018 records
- delivered before recovery: 0
- stalled RSS: 15,684 KiB
- stalled FDs: 399
- delivered after recovery: 12,018 / 12,018
- recovery settle time: **839 ms**
- total HTTP requests after drain: 121
- recovered RSS: 18,200 KiB
- recovered FDs: 397 while the 128 subscriptions intentionally remained live
- final cleanup FDs after forwarder cancellation: **12**

The repaired forwarder therefore keeps the outage working set bounded, drains accepted records promptly when the endpoint resumes, and returns owned session descriptors on teardown.

## RPC write-lane fix

Production source changed at:

`Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+RPC.swift`

The current implementation gives non-WebSocket physical writes a separate one-second liveness budget. This is distinct from RPC response deadlines. A stalled write retires the shared transport, which releases queued request/response callers. The same liveness guard covers fire-and-forget notifications such as PTY write/resize, closing the residual path where terminal input could wedge the global writer.

Run `33564015233` and later run `33565064189` both kept the relevant macOS checks green:

- pinned-upstream RPC package and timeout-isolation controls
- candidate package outside timeout isolation
- candidate timeout-isolation suite
- preserve-after-PTY-timeout discriminator
- blocked-cancellation discriminator
- request + notification write scaling probes

Earlier intermediate versions that reused the RPC response deadline for physical write admission were discarded after reproducing timing regressions. The final source uses a separate write-liveness budget.

## Matched journal collapse result

The decisive matched comparison is recorded separately in `journal-matched-control-33563251152.md`.

At 128 accepted sessions under the same 1.5-second stalled-endpoint workload:

- pinned upstream: 1,126,824 KiB loaded RSS
- bounded candidate: 15,136 KiB loaded RSS

This is about a 74× reduction. More importantly, the owner changes from an unbounded relay-side retained pool to bounded producer backpressure.

## Remaining measurement

Remote proxy output to a slow local consumer remains the active open lead. `RemoteDaemonProxySession` submits `NWConnection.send` operations without an application-level pending-send byte/count budget. A measurement-only macOS probe now instruments pending send count/bytes and compares active readers with clients that stop reading across 1 / 10 / 50 / 200 sessions. Network.framework behavior will determine whether this becomes a confirmed retention finding or a bounded transport behavior.
