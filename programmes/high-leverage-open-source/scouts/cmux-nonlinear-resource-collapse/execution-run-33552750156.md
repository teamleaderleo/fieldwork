# cmux nonlinear resource-collapse execution receipt

Date: 2026-09-01
Worker: ChatGPT
Target upstream revision: `manaflow-ai/cmux` `8ef183f1e5de765b183aec9d1799f17a0848ae84`
Owned fork: `teamleaderleo/cmux`
Experiment branch at measured run: `fieldwork/nonlinear-resource-collapse` `7757893fabe2a592b590443b78e8ef4a0e5d5da4`
GitHub Actions run: `33552750156`
Upstream contact authorized: `false`

## In simple words

The live journal probe reproduced the source-predicted amplification in the actual `journal_forwarder`: one stalled HTTP POST left every discovered session feeding the same retained pending pool. RSS rose sharply with session count until the source's 128-session discovery cap, while one HTTP request remained in flight throughout each stalled case. Cancellation closed the session/socket resources, but process RSS remained at the high-water allocation on this allocator/runtime, so RSS alone is not a proof of live-object leakage after teardown.

The macOS RPC probe also established the original write-admission defect. Before the candidate fix, one physical stdio writer was enough to keep a caller past a 50 ms RPC deadline. The 200-caller responsive control completed successfully. After adding a write-admission deadline, the dedicated 1/10/50/200 scaling probe passed, but an all-tests-at-once package run produced two failures in the pre-existing PTY timeout-isolation suite. Those failures happened while the 200-caller scaling test was executing concurrently, so a follow-up run isolates the heavy scaling suite from ordinary package tests before changing production semantics again.

## Journal runtime measurements

Harness: real `chatmux_relay::journal_forwarder::start`, synthetic cmux-tui Unix journal sockets, local HTTP endpoint. Each stalled session generated 300 records with a 1024-byte payload. The endpoint accepted the first POST and withheld its response.

| requested sessions | accepted sessions | generated records | HTTP requests | baseline RSS KiB | loaded RSS KiB | cleanup RSS KiB | loaded FDs | cleanup FDs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 300 | 1 | 4,920 | 8,572 | 8,640 | 18 | 12 |
| 10 | 10 | 3,000 | 1 | 4,756 | 18,332 | 18,400 | 45 | 12 |
| 50 | 50 | 15,000 | 1 | 4,900 | 62,072 | 62,152 | 165 | 12 |
| 128 | 128 | 38,400 | 1 | 5,080 | 148,568 | 148,648 | 399 | 12 |
| 200 | 128 | 38,400 | 1 | 5,220 | 146,456 | 146,544 | 471 | 12 |

Source limits reported by the same harness: `MAX_BATCH_RECORDS=100`, `MAX_BATCH_BODY_BYTES=4194304`, `MAX_DISCOVERED_SESSIONS=128`.

Interpretation:

- The scaling variable is the number of concurrently subscribed producing sessions.
- The first saturating resource is retained journal record state / resident memory behind one in-flight POST.
- The curve rises through 128 active producers and then stops adding producers at the discovery cap.
- Exactly one HTTP request was observed in every stalled case, confirming that producers multiply behind one blocked consumer rather than creating multiple POST workers.
- FD cleanup converged to 12 in every stalled case.
- Cleanup RSS remained near the high-water RSS. This is consistent with allocator retention and cannot by itself distinguish retained live records from freed heap pages; internal pool counters or heap profiling are required for a live-object post-cleanup claim.

### Healthy control

50 sessions x 300 records, 1024-byte payload, immediate local ACK:

- accepted sessions: 50
- generated records: 15,000
- HTTP requests: 9
- baseline RSS: 4,988 KiB
- loaded RSS: 103,016 KiB
- cleanup RSS: 103,080 KiB
- loaded FDs: 163
- cleanup FDs: 12

This control is important because it shows a second effect: even a healthy endpoint can observe large temporary aggregation when producers outrun the single flusher. The stalled endpoint makes the retention persistent for the outage duration; healthy ACK makes it transient. The 100-record scheduling threshold is therefore neither an aggregate pending-record cap nor a strict POST batch-count cap once a flush is already active.

## RPC red / candidate-green evidence

Original red run: `33551061330` at fork head `ea0338c56b9bab22b8a37e794ed34ecbca907deb`.

- responsive stdio control: 200 concurrent `hello` RPC callers completed successfully in 0.727 s in the focused run;
- stalled case: failure already at N=1; one caller with a 50 ms response timeout remained behind the physical writer after the 750 ms test bound;
- direct stop was retained as the cleanup breaker.

Candidate implementation commit: `843accd73070a441ae4d24aa88e1a21bbbe02bc7` (`fix(remote): bound daemon RPC write admission by call deadline`). It moves request writes onto the serial write queue asynchronously, waits on a caller-owned absolute deadline, and stops the transport when write admission/physical write cannot finish by that deadline. The response wait receives only the remaining portion of the original timeout budget.

Run `33552750156` results:

- `RemoteDaemonRPCClient write admission scaling` passed, including the physical-stall 1/10/50/200 sequence;
- ordinary package run failed two pre-existing `RemoteDaemonRPCClient timeout isolation` expectations;
- the failures ran concurrently with the 200-caller scaling suite, so they are not yet classified as a production semantic regression.

## Current discriminator

Fork commits after run `33552750156` gate the heavy scaling suite behind `CMUX_FIELDWORK_SCALING=1` and run ordinary package tests separately from the focused scaling probe. The next execution asks one clean question:

> Do the existing PTY timeout-isolation tests pass when the 200-caller stress test is absent, while the candidate write-admission probe still passes in its own process?

If yes, the run-9 failures were test interference and the request/response candidate remains viable. If no, the candidate changes the established PTY timeout-isolation contract and needs to be narrowed before promotion.

## Evidence limits

- Journal RSS was measured on GitHub-hosted Ubuntu, not a production relay host.
- The harness drives real forwarder code but synthetic journal producers and a local HTTP endpoint.
- RSS after cancellation is allocator-sensitive; FD convergence is stronger teardown evidence in this run.
- The journal production path has not been patched in this receipt.
- The RPC candidate currently covers request/response calls. Fire-and-forget notifications such as `pty.write` and `pty.resize` still use synchronous `writeQueue` writes and remain a separate write-lane owner to probe.
- No upstream mutation or maintainer contact occurred.
