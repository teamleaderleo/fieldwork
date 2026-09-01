# cmux RPC upstream concurrency control

Date: 2026-09-01
Worker: ChatGPT
Upstream contact authorized: `false`
Owned execution repository: `teamleaderleo/cmux`
GitHub Actions run: `33560636263`
Control revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`

## In simple words

The ordinary `CmuxRemoteDaemon` package has a pre-existing parallel-test failure at the pinned untouched upstream revision. This control is important because the same timeout-isolation failures appeared while evaluating the resource-collapse RPC candidate. Running the untouched revision under the same GitHub-hosted macOS environment produced the same failure signature, so those full-package failures cannot be attributed to the candidate.

## Control setup

The experiment workflow itself lives only on the owned fork branch. The control job used `actions/checkout` with exact ref `8ef183f1e5de765b183aec9d1799f17a0848ae84`, verified `git rev-parse HEAD` against that value, and then ran:

`swift test --package-path Packages/macOS/CmuxRemoteDaemon`

The checked-out code contains none of the Fieldwork scaling test or candidate production changes.

## Result

The untouched package failed three expectations in `RemoteDaemonRPCClientTimeoutIsolationTests` while the Swift Testing suites ran in parallel:

1. `timedOutPTYAttachPreservesHealthyTransportState`: `existingPTYEvent` failed to arrive within 1 second.
2. `timedOutPTYAttachBoundsCancellationWrite`: `writeBlockEntered` failed to arrive within 2 seconds.
3. The same blocked-cancellation test then observed no unexpected-termination callback within its 2-second expectation window.

This is the same three-issue signature seen on the candidate full-package run.

The same two timeout-isolation tests have each passed when executed alone on the owned candidate branch. Therefore the current evidence classifies the full-package failures as an upstream parallel-test interaction / timing failure, not a regression discriminator for the RPC write-liveness candidate.

## Candidate consequence

The original resource-collapse red remains independent of this control:

- current upstream stdio RPC registers a call before `writeQueue.sync`;
- one physical write can hold the global write lane;
- the ordinary response deadline begins only after the physical write returns;
- the owned red probe reproduced the failure with one queued caller and a 50 ms response timeout still blocked after 750 ms;
- a responsive 200-caller control completed successfully.

The revised owned candidate uses a separate non-WebSocket write-liveness budget instead of consuming the established response timeout. Candidate-focused verification runs all package tests outside the upstream-parallel-flaky suite, executes each timeout-isolation test alone, and then executes the 1/10/50/200 physical-write scaling probe.

## Current-upstream applicability

During this follow-up, public upstream `main` advanced to `6044a8b3f43152d2e6fc17f771fd4b277b393118`. The two critical implementation blobs remain byte-identical to the original audit revision:

- `RemoteDaemonRPCClient+RPC.swift`: blob `0eddc4847913125a2804e00487d43c47c9454b98`
- `journal_forwarder.rs`: blob `9b4551770e807084c48c2cdbe94f15f2cf2358e0`

So the RPC write-admission and journal single-flusher findings still apply to that current upstream head.

## Evidence limits

- This receipt classifies a test-control result; it does not repair the upstream parallel-test issue.
- The candidate-focused run remains the acceptance surface for the RPC production change.
- Fire-and-forget daemon notifications remain a separate synchronous write-lane owner and are outside this control.
- Upstream remained read-only; no maintainer contact occurred.
