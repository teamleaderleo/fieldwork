# cmux PTY timeout-isolation harness reduction — 2026-09-01

Owned fork: `teamleaderleo/cmux`  
Branch: `fieldwork/nonlinear-resource-collapse`  
Upstream contact authorized: `false`

## Why this reduction was needed

The event-delivery owner and downstream proxy-output owner each passed their focused gates. When both candidate stacks were layered into one checkout and the complete `CmuxRemoteDaemon` target ran with Swift Testing's default parallel execution, two existing PTY timeout-isolation tests missed short semaphore deadlines.

The failing assertions were scheduling observations:

- an existing PTY data callback did not arrive inside a 1-second wait;
- a helper block waiting on that callback did not enter the RPC write queue inside a 2-second wait;
- the expected transport termination was then delayed behind that missed synchronization.

The event-delivery ownership tests themselves passed in those same failing runs. The downstream proxy candidate does not modify `CmuxRemoteDaemon` source.

## Reproduction

Composition run `33570470640` failed the full daemon target twice with the same two timeout tests. Re-running the exact failed job did not change the result.

## Exact reduction

Run `33570851723`, job `100064267508`, head `e72176d74c6cf0d199de5ea0040dc42e34d4ca6a` applied the exact same event-delivery and proxy-output overlays, then executed:

1. `timedOutPTYAttachPreservesHealthyTransportState` three times alone;
2. `timedOutPTYAttachBoundsCancellationWrite` three times alone;
3. the two-test timeout-isolation suite three times together;
4. timeout-isolation plus the full event-delivery test suite.

Every discriminator passed.

Run `33571037040`, job `100064825707`, head `aa24cea17974d37c38722185172136b2f6ea5121` repeated those gates and added the entire `CmuxRemoteDaemon` package with `swift test --no-parallel`. Every step passed.

This isolates the failure to whole-target parallel test scheduling rather than a reproduced production-semantic regression in either candidate.

## Harness repair

Staged patch: `scripts/fieldwork/cmux-resource-collapse/timeout_isolation_harness_repair.patch`.

The second timeout test previously used a PTY data callback (`attach-read`) as the synchronization point for a test whose subject is the cancellation write lane. That couples callback scheduling to write-liveness behavior.

The repair changes the fake transport to create a marker file immediately after it reads the stalled `pty.attach`. The test waits for that transport-side marker, then inserts the write-queue blocker directly. The write-liveness test therefore synchronizes on the operation it actually needs: the fake daemon has received the stalled attach.

The first timeout test still verifies real subscription survival through a real PTY data event. Its callback wait is widened from 1 second to 3 seconds because callback dispatch latency is not the deadline under test; the RPC response and termination expectations remain unchanged.

## Current gate

The full default-parallel composition workflow has been updated to apply this test-only harness repair while leaving both production candidates unchanged. Run `33571263196` is the next acceptance gate:

- complete default-parallel `CmuxRemoteDaemon` package;
- complete `CmuxRemoteWorkspace` package;
- healthy 200-session downstream proxy control;
- 96 MiB per-session slow-reader breaker;
- 256 MiB process-wide slow-reader breaker.

Source promotion remains behind that gate.