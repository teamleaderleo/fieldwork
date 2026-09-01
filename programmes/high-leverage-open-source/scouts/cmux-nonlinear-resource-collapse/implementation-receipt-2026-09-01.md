# cmux nonlinear resource-collapse — implementation receipt

Date: 2026-09-01  
Pinned upstream revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Upstream contact: none

## Landed journal fix

Promotion commit: `3948c73c4cac4dd2fe10e5bc0275b8c56bdd9ed7`  
Commit message: `fix(relay): bound journal backlog during stalled delivery`

The guarded promotion required the production source to still have pinned upstream blob `9b4551770e807084c48c2cdbe94f15f2cf2358e0`. The promotion commit changed only:

`cmux-tui/crates/chatmux-relay/src/journal_forwarder.rs`

Diff size: +256 / -12.

The source now owns one bounded pending batch behind the retrying/in-flight batch. Bounds are both `MAX_BATCH_RECORDS` and `MAX_BATCH_BODY_BYTES`; session workers wait when that next batch is full. Capacity wake-up occurs when pending records are rotated into a ready/in-flight batch and when a POST completes. The post-completion producer handoff preserves the exact 100-record ready boundary.

The one-shot write-capable promotion workflow was removed immediately after the guarded commit.

## Landed-source verification

Run `33564015233` verifies the actual committed journal source without applying the candidate patches in CI.

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

## RPC write-lane fix

Production source changed at:

`Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+RPC.swift`

The current implementation gives non-WebSocket physical writes a separate one-second liveness budget. This is distinct from RPC response deadlines. A stalled write retires the shared transport, which releases queued request/response callers. The same liveness guard covers fire-and-forget notifications such as PTY write/resize, closing the residual path where terminal input could wedge the global writer.

Run `33564015233`:

- pinned-upstream RPC baseline: success
- candidate package outside timeout-isolation suite: success
- candidate timeout-isolation suite: success
- preserve-after-PTY-timeout discriminator: success
- blocked-cancellation discriminator: success
- request + notification write scaling probes: success

Earlier intermediate versions that reused the RPC response deadline for physical write admission were discarded after reproducing timing regressions. The final source uses a separate write-liveness budget.

## Matched journal collapse result

The decisive matched comparison is recorded separately in `journal-matched-control-33563251152.md`.

At 128 accepted sessions under the same 1.5-second stalled-endpoint workload:

- pinned upstream: 1,126,824 KiB loaded RSS
- bounded candidate: 15,136 KiB loaded RSS

This is about a 74× reduction. More importantly, the owner changes from an unbounded relay-side retained pool to bounded producer backpressure.

## Remaining verification

A measurement-only recovery harness is being exercised after source promotion. It stops producers while keeping the forwarder alive, releases the stalled HTTP request, and waits for every generated record accepted by the Unix sockets to be delivered. It will record settle time and RSS/FDs before recovery, after drain, and after final cancellation.

A small byte-threshold scheduling edge also remains to pin: a pending batch that reaches the 4 MiB threshold with fewer than 100 records is bounded correctly but can currently fall through to the debounce after the in-flight POST completes. This affects latency rather than the memory ceiling.

Remote proxy output to a slow local consumer remains a source-only candidate. `RemoteDaemonProxySession` submits `NWConnection.send` operations without an application-level pending-send byte/count budget; Network.framework behavior needs an executable slow-reader test before classifying it as resource amplification.
