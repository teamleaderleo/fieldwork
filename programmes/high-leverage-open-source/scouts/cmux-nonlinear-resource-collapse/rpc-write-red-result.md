# cmux remote-daemon RPC write-lane red result

## In simple words

The first macOS execution confirmed the source-level write-admission failure. A healthy fake SSH transport handled 200 concurrent RPC callers and completed the control in under one second. When the helper stayed alive but stopped reading stdin, one deliberately oversized physical write occupied the daemon client's single `writeQueue`. A later RPC with a 50 ms response timeout was still waiting behind that physical writer after 750 ms.

That is the requested bend in ownership: the response timeout does not govern time spent waiting to enter or finish the physical write. The failure appears with one queued RPC caller; increasing caller count is an amplification dimension rather than the first threshold.

The initial red harness then received SIGPIPE while its finite fake-helper safety breaker was cleaning up the stalled pipe, so the same run did not execute the 10 / 50 / 200 cases. The fork test has been hardened to ignore SIGPIPE inside the serialized test and to use an explicit `client.stop()` cleanup control after each red case. This keeps cleanup behavior separate from the invariant failure and lets later runs collect the full sequence.

## Execution receipt

Owned fork: `teamleaderleo/cmux`  
Experiment branch: `fieldwork/nonlinear-resource-collapse`  
Workflow run: https://github.com/teamleaderleo/cmux/actions/runs/33551061330  
macOS job: `macos-rpc-write-admission`  
Job ID: `100000324906`  
Checked-out head: `ea0338c56b9bab22b8a37e794ed34ecbca907deb`  
Target ancestry base: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Runner: macOS 15.7.7, arm64  
Swift: Apple Swift 6.1.2

## Negative control

Test: `responsive stdio transport settles 200 concurrent RPC callers`

Result: **passed** in **0.727 seconds**.

The fake helper continuously read stdin and answered every RPC. Two hundred concurrent callers therefore exercised the same synchronous client and global write queue without a stalled physical writer. This is the small/healthy-path control showing that the harness itself can cleanly carry a large caller burst.

## Failure sequence

1. Start a fake SSH helper and complete the normal daemon `hello` handshake.
2. The helper remains alive and stops reading stdin.
3. On a separate queue, enter the real `RemoteDaemonRPCClient.writeQueue` and call `writePayload` with 4 MiB so Darwin pipe capacity is exhausted.
4. Confirm the physical write remains blocked for at least 150 ms.
5. Launch an ordinary `client.call(method: "hello", timeout: 0.05)`.
6. Wait 750 ms for that caller to finish.

Observed result at step 6:

> `1 queued RPC callers remained behind one physical write beyond their 50ms response timeout`

The test recorded the expectation failure at `RemoteDaemonRPCClientWriteAdmissionScalingTests.swift:107`.

## Why the curve bends

The current RPC call order is:

1. register a pending call;
2. encode request bytes;
3. synchronously enter the global write queue and physically write;
4. only after the write returns, call `waitForCall(... timeout:)`.

One stalled physical writer takes the write lane's service rate to zero. Every later application caller can retain its pending-call owner while waiting behind that lane. Their advertised response deadlines have not begun yet. The saturation resource is therefore the single serialized physical writer first, followed by queued caller contexts and pending-call registry entries.

The smallest observed amplification sequence is one stalled physical write plus one ordinary RPC caller. No large caller population is required to trigger the invariant failure.

## Consequence

Primary consequence: **remote tunnel outage / stranded synchronous operations**.

Amplified consequences at larger caller counts are expected to include retained pending-call entries, semaphores, blocked GCD work, delayed PTY/tunnel cleanup, and thread pressure. The hardened follow-up run is intended to measure 10 / 50 / 200 callers and explicit clean-stop convergence.

## Harness limit and repair

The original helper exited after two seconds to ensure a red run eventually unwound. Closing its pipe caused the standalone Swift test host to receive SIGPIPE before the test could advance past N=1.

Fork harness commit `40eff2091e7e2763db7a305ee26c8a56103c8222` changes the probe so:

- the serialized stalled-write test temporarily ignores SIGPIPE and restores the prior handler afterward;
- the fake helper's safety lifetime is ten seconds;
- after each failed bounded-settle assertion, `client.stop()` is invoked immediately;
- queued callers and the blocked writer must both release within one second after that clean stop.

This is a harness repair, not production evidence.

## Production repair under test

Fork commit `843accd73070a441ae4d24aa88e1a21bbbe02bc7` changes ordinary daemon RPC calls so their configured timeout becomes an absolute call deadline covering:

- waiting for the global write lane;
- the physical transport write;
- the response wait.

The physical write is queued asynchronously while the synchronous caller waits on a completion semaphore until the absolute deadline. If that write phase misses the deadline, the caller removes its own pending call first, stops the transport, and returns the existing RPC timeout error. Stopping the transport closes the physical handle and is intended to release the stalled writer plus all other queued calls.

This repair remains **candidate code** until the post-fix macOS run is green and surrounding timeout/isolation tests are exercised.

## Evidence labels

- Responsive 200-caller control: **Executed / Observed**.
- Stalled N=1 deadline violation: **Executed / Observed**.
- Full N=10/50/200 pre-fix curve: **Unknown** because the initial process hit SIGPIPE during cleanup.
- Clean-stop release under the hardened harness: **Unknown** until the next run finishes.
- Candidate production repair efficacy: **Unknown** until the post-fix run finishes.

Upstream remains read-only. Upstream contact authorization remains `false`.
