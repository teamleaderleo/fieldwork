# cmux RPC write-liveness candidate receipt

Date: 2026-09-01
Worker: ChatGPT
Upstream contact authorized: `false`
Owned fork: `teamleaderleo/cmux`
Candidate branch: `fieldwork/nonlinear-resource-collapse`
Candidate gate run: `33560851123`
Gate head: `d059f9b98162d22b4a1f40f55a8fc3cbcb70f76c`
Production candidate commit: `ff826debbdcc0a392aefd7e01a77839a2a865cb7`
Original upstream audit revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`

## In simple words

The request/response RPC write-lane candidate now has a clean owned-fork gate. The repair gives non-WebSocket daemon writes a separate one-second liveness budget while leaving the established RPC response timeout intact after a healthy write completes. This prevents one physical stdio write from holding the global write lane forever before caller response deadlines can run.

The full upstream package has a separate parallel-test timing failure in `RemoteDaemonRPCClientTimeoutIsolationTests`. An untouched exact-upstream control reproduced the same three failures, so the candidate gate excludes that suite from the parallel package run and executes each of its two tests alone. Both isolated tests pass on the candidate.

## Original red

Run `33551061330`, pre-fix branch head `ea0338c56b9bab22b8a37e794ed34ecbca907deb`:

- responsive stdio control: 200 concurrent `hello` callers passed in 0.727 seconds;
- physical stdio write stall: failure already at N=1;
- one caller configured with a 50 ms response timeout remained parked behind the physical writer after the probe's 750 ms bound;
- direct transport stop released the blocked writer and queued work in the cleanup control.

This established the first non-converging owner: `RemoteDaemonRPCClient.writeQueue` plus a synchronous stdio `FileHandle.write` before `waitForCall` starts.

## Candidate implementation

`RemoteDaemonRPCClient+RPC.swift` now keeps two independent deadlines for non-WebSocket request/response calls:

1. a fixed one-second write-liveness budget covering serialized queue admission plus the physical stdio write;
2. the existing per-method response timeout, started after a healthy write completes.

If the write-liveness budget expires, the client retires the transport. Closing the transport breaks the physical writer and fails queued pending calls, converting an unbounded global-lane stall into bounded transport recovery.

WebSocket request handling retains its previous path.

## Green gate

Run `33560851123`, job `macos-rpc-candidate`, GitHub-hosted macOS 15 arm64.

- Package outside the known upstream-parallel-flaky timeout suite: **25 tests passed**, 2.060 s test runtime after build.
- `timedOutPTYAttachPreservesHealthyTransportState` alone: **passed**, 0.162 s.
- `timedOutPTYAttachBoundsCancellationWrite` alone: **passed**, 2.154 s.
- Responsive 200-caller scaling control: **passed**, 0.781 s.
- Physical stdio write-stall sequence **1 / 10 / 50 / 200 callers passed**, 4.961 s for the sequence.
- Complete focused scaling suite: **passed**, 5.743 s.

The stall test uses a helper that answers startup `hello`, then remains alive for ten seconds while refusing subsequent stdin. A 4 MiB physical write wedges the pipe. Each queued RPC uses a 50 ms response timeout. The candidate requires the entire caller population to settle within 1.75 seconds, giving scheduler margin over the one-second write-liveness budget and remaining far below the helper's ten-second safety exit.

## Upstream test control

Run `33560636263` checked out untouched `8ef183f1e5de765b183aec9d1799f17a0848ae84` and ran the ordinary `CmuxRemoteDaemon` package. It reproduced the same three timeout-isolation failures seen in candidate full-package parallel runs. Each timeout-isolation test passes alone on the candidate.

That control classifies the parallel package failure as pre-existing upstream test interference, not candidate evidence.

## Current upstream applicability

Public upstream `main` later advanced to `6044a8b3f43152d2e6fc17f771fd4b277b393118`. The audited RPC file remains blob-identical (`0eddc4847913125a2804e00487d43c47c9454b98`) to the original revision, so the source defect and red reproduction remain applicable to that current head.

## Remaining write-lane owner

The candidate covers request/response `call(...)` traffic. Fire-and-forget notifications still use synchronous `writeQueue.sync { writePayload(...) }` with no write-liveness deadline. This includes `pty.write` and `pty.resize`.

The bridge input owner has its own useful bounds — default 256 KiB maximum per write, 256 pending writes, and 4 MiB pending bytes — but one accepted 256 KiB notification can still block the bridge's RPC worker and the shared daemon write lane if the helper remains alive while ceasing to read. That notification-only path is the next red-first probe.

## Evidence limits

- This candidate has owned-fork macOS execution, not upstream review or deployment.
- The write-liveness value is currently one second and has been validated against the owned test scenarios, not production latency distributions.
- `callIfIdle` and notification writes remain separate write-lane owners requiring their own discrimination.
- Upstream remained read-only; no maintainer contact occurred.
