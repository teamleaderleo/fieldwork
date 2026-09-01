# cmux nonlinear resource-collapse scout

Date: 2026-09-01  
Programme: high-leverage-open-source  
Worker: ChatGPT  
Claim scope: mechanism / operational  
Upstream contact authorized: `false`

## In simple words

This scout asks a specific scaling question about `manaflow-ai/cmux`: when sessions, reconnects, attachments, subscriptions, proxy operations, and remote work rise from a handful to dozens or hundreds, does resource use continue to grow in a controlled way, and does cleanup return owned resources close to baseline?

The source pass found two strong amplification candidates and several useful controls.

The strongest candidate is the managed session-journal forwarder. All subscribed sessions feed one shared pending buffer and one shared POST worker. When one POST enters retry, producers continue appending into the shared pending pool. The nominal 100-record threshold no longer drains while `flushing == true`; it only sets `flush_again`. This turns the system into a queue with aggregate producer rate `lambda = sum(session rates)` and one retrying consumer with service rate `mu`. During an outage, `mu = 0`, so retained records grow with `lambda * outage_duration`. After recovery, settling requires `mu > lambda`; settle time rises sharply as the rates approach each other.

The second candidate is the macOS remote-daemon synchronous RPC path over SSH/stdio. Calls register in the pending-call registry, then enter one global `writeQueue`, and only after the write finishes do they start their ordinary response timeout. The stdio path uses synchronous `FileHandle.write` without its own write deadline. If the remote helper stays alive but stops reading, one large write can block the global write lane. Later RPC callers can register and wait behind that lane before their advertised 4–12 second response deadlines even begin. The non-WebSocket keepalive uses the same write lane and arms its watchdog only after admission, so it cannot preempt a writer already stuck in `writePayload`.

PTY bridge replacement can multiply the second failure. Each bridge creates its own RPC queue and performs synchronous `pty.attach`. The lifecycle registry limits distinct generations to 256, but an existing generation can collect additional `bridgeID`s. A bridge stopped while `isAttaching` delays its final stop notification until the attach returns. Repeated reconnect/restore for the same logical attachment can therefore retain multiple bridge owners behind one stalled daemon write lane while the tunnel remains alive.

The source also exposes useful negative controls. Journal-hook delivery uses one dispatcher and a 4–32 worker pool, with admission limited by worker capacity and per-hook `max_parallel`. Machine-provider subprocesses run in dedicated process groups and cleanup escalates SIGTERM to SIGKILL, waits for the child, and joins the stderr worker. `SharedLiveAgentIndex` explicitly limits overlapping loader replacement and caps executable-watch installation work and watch descriptors. Terminal hosts have explicit per-client and parser byte caps. These are the kinds of owners that should converge under the same harness.

The next step is red-first owned-fork execution. No production patch is justified until the fork probes establish the resource curve, first non-converging owner, cleanup behavior, and a small-scale negative control.

## Question

Where does current cmux first violate this invariant?

> Increasing the number of sessions, attachments, reconnects, watchers, hooks, or remote operations should increase resource use in a controlled way, and teardown should return owned resources close to baseline.

The target is specifically a nonlinear knee: behavior that looks ordinary at 1–5 instances, then crosses a threshold where retries, queues, subprocesses, sockets, tasks, or retained state amplify each other.

## Assignment boundary

Expected deliverable: exact current revision, source ownership map, executable scaling probes, baseline and cleanup controls, measured failure threshold where the owned-fork environment supports it, surviving state after load stops, and a ranked implementation thesis.  
Owned output path: `programmes/high-leverage-open-source/scouts/cmux-nonlinear-resource-collapse/report.md`  
Owned testbed: `teamleaderleo/cmux`  
Target upstream: `manaflow-ai/cmux`  
Target revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Retrieval boundary: GitHub source reads on 2026-09-01.  
Intended claim scope: mechanism and operational behavior only.  
Stop condition: red-first fork probes identify the first non-converging owner or establish bounded behavior for the candidate; a clean-shutdown control is included; upstream remains read-only.  
Upstream-contact authorization: `false`.

## Exact source state

Pinned upstream main: `8ef183f1e5de765b183aec9d1799f17a0848ae84` (`perf(cmux-tui): avoid per-frame sidebar layout clone`, 2026-09-01T18:12:25Z).

The audit initially pinned parent `eaa899cb20bd411019744fbd2bdedeb397f3070b`; upstream advanced once during the pass. The final pin moved to `8ef183f...`. The merge touched sidebar rendering files. Critical journal/remote files inspected before and after the move retained identical blobs.

Owned fork default branch at scout creation: `teamleaderleo/cmux` `e0f447b45af20e6e32d67074db31a0c4d730b683`. The experiment branch should start from the exact upstream target revision instead of inheriting unrelated fork-main verification commits.

## Source ownership map

### Managed journal forwarding

Owner: `cmux-tui/crates/chatmux-relay/src/journal_forwarder.rs`

Relevant constants and owners:

- `MAX_BATCH_RECORDS = 100`
- `MAX_BATCH_BODY_BYTES = 4 MiB`
- HTTP request timeout: 30 seconds
- POST retry backoff: 1 second rising to 60 seconds, with no retry-count ceiling
- discovered session cap: 128
- one `PoolState` shared by every session worker
- one `run_flusher` task shared by every session worker
- one pending buffer containing `PendingSession.records`
- one `flush_again` boolean, not a queue of flush requests

The critical branch is `enqueue_pending`. While a POST is in flight, the 100-record threshold stops being a drain boundary. When `pool.flushing` is true and total pending records reach the threshold, the function sets `flush_again = true` and returns. Subsequent records continue to append.

`post_with_retry` keeps the current batch while retrying. Network errors and retryable HTTP responses have no maximum-attempt count. Consequently one batch can remain owned indefinitely while `pool.pending` grows behind it.

A second subtle effect follows after recovery: `flush_cycle` takes the entire pending vector when it runs again. The 100-record constant is therefore not an aggregate retained-record cap and is not necessarily a post-retry batch-count cap. The 4 MiB HTTP body check can split large serialized bodies later, but retained `serde_json::Value` memory has already accumulated by then.

### Remote daemon RPC admission and write serialization

Owners:

- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+RPC.swift`
- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Registry/RemoteDaemonPendingCallRegistry.swift`
- `Packages/macOS/CmuxRemoteDaemon/Sources/CmuxRemoteDaemon/Client/RemoteDaemonRPCClient+TransportKeepalive.swift`

Call order is:

1. `pendingCalls.register()`
2. encode payload
3. `writeQueue.sync { writePayload(payload) }`
4. `waitForCall(... timeout:)`

The pending registry has no admission count ceiling. `waitForCall` owns the response timeout, which means the timeout starts after the global write finishes.

For WebSocket transport, `writePayload` blocks on a send-completion semaphore. WebSocket transport also owns a separate ping watchdog, so a total transport stall has another potential breaker.

For SSH/stdio and local socket-forward transport, `writePayload` uses synchronous `FileHandle.write`. No write deadline surrounds those calls. The non-WebSocket keepalive invokes `callIfIdle` through `writeQueue`; its watchdog is armed by an `onAdmitted` callback only after it acquires the write lane. This leaves a clear pre-timeout window: a real RPC blocked inside `FileHandle.write` prevents both later application calls and the keepalive from reaching their timeout-owning code.

### PTY bridge retention during a stalled attach

Owners:

- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/PTYBridge/RemotePTYBridgeSession.swift`
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Tunnel/RemotePTYLifecycleRegistry.swift`
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Tunnel/RemoteDaemonProxyTunnel+PTYBridge.swift`
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Broker/RemoteProxyBroker.swift`

Each bridge session owns a distinct serial `rpcQueue`. Authentication submits synchronous `attachBridgePTY` on that queue. If the bridge closes while `isAttaching`, `close()` cancels local network state but returns before notifying its owner. `finishAttach` later performs that notification.

`RemotePTYLifecycleRegistry` caps distinct lifecycle generations at 256. For an existing generation with the same attachment ID, `registerBridge` adds another `bridgeID` to that generation instead of applying a per-generation count cap.

`RemoteProxyBroker.withReadyTunnel` increments `activeReadyTunnelOperationCount`; last-subscriber release defers entry teardown while this count is positive. A stuck synchronous tunnel operation can therefore delay the cleanup that would otherwise stop the RPC client.

The remote Go daemon has an independent cap of 32 concurrent `pty.attach` requests per RPC connection. Calls parked client-side before the write finishes do not consume those server slots, so this server bound does not cap the macOS pending-call population.

### SSH reconnect reachability probe

Owners:

- `Packages/macOS/CmuxRemoteSession/Sources/CmuxRemoteSession/Session/RemoteSessionCoordinator+Reconnect.swift`
- `Packages/macOS/CmuxRemoteSession/Sources/CmuxRemoteSession/Reachability/RemoteHostReachabilityProbe.swift`
- `Packages/macOS/CmuxFoundation/Sources/CmuxFoundation/Process/CommandRunner.swift`

Reconnect timers themselves are replacement-owned: old retry tasks are cancelled and token checks drop stale wakeups.

Reachability evaluation increments a generation and starts a new probe. Each probe launches detached work for `ssh -G` resolution. Generation checks suppress stale results, but they do not cancel stale work. One probe can own an `ssh -G` child and pipes, an optional second `ssh -G` for ProxyJump, an `NWConnection`, and its timeout task.

The work is bounded in lifetime: each config-resolution command has a 3 second timeout with deterministic process teardown, and TCP probing has a 2.5 second timeout. Approximate worst-case stale lifetime is about 5.5 seconds for direct resolution followed by TCP timeout, and about 8.5 seconds for two near-deadline ProxyJump resolutions followed by TCP timeout. This is a transient storm candidate, not the strongest persistent-retention lead.

### Proxy stream remote-to-local sends

Owner: `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Tunnel/RemoteDaemonProxySession.swift`

PTY bridge output has explicit pending-send count and byte caps. Proxy stream output forwards every `proxy.stream.data` chunk through `NWConnection.send` without a parallel application-level pending-send count or byte budget. A remote source combined with a local consumer that stops reading is therefore worth measuring for retained send-completion state. Network.framework may impose its own practical backpressure; source alone does not establish the resulting memory curve.

## Strong negative controls

### Journal hooks

Owner: `cmux-tui/crates/cmux-tui-core/src/journal_hooks.rs`

- one dispatcher claim per session
- 4–32 delivery workers derived from available parallelism
- admission refuses work after active + selected reaches worker capacity
- each hook also respects `exec.max_parallel`
- shutdown closes the job sender and joins every worker

### Machine provider / cloud subprocesses

Owner: `cmux-tui/crates/cmux-tui/src/machine_provider_transport.rs`

- each command/SSH endpoint gets a dedicated process group
- stderr drain has one owned worker
- cleanup sends SIGTERM to the process group
- after 250 ms grace, cleanup sends SIGKILL if the group remains alive
- direct child is waited
- stderr worker is joined
- private SSH control directory is retained by process guards and removed on final drop

### Agent index watchers and loader replacement

Owner: `Sources/SharedLiveAgentIndex.swift`

- one active index loader
- at most one retired timed-out loader plus one replacement attempt
- executable-watch install work capped at 8 concurrent operations
- watch-source ceiling 64
- file-descriptor budgeting keeps 128 descriptors in reserve

### Terminal hosts

Owner: `cmux-tui/crates/cmux-tui-core/src/terminal_host_runtime.rs`

- live client output budget: 8 MiB plus bounded state overhead
- smart retained history: 8 MiB / 4096 frames
- parser queue: 256 frames / 16 MiB
- hosts intentionally outlive a mux crash, so process survival after mux death is expected and must be separated from cleanup leaks

## Scaling experiments

### Experiment A — journal single-consumer collapse

Synthetic managed-events endpoint modes:

1. healthy 200 + cursor ACK
2. accepted connection with stalled response
3. immediate retryable 503
4. recovery to healthy mode

Synthetic cmux-tui journal producers: N = `1, 10, 50, 128, 200` with fixed per-session event rates and fixed payload sizes.

Measure:

- relay RSS
- relay FD count
- Unix-domain socket count
- session-worker count
- total generated events
- HTTP attempts
- total ACKed events
- `generated - ACKed` backlog
- settle time after production stops
- resources after relay cancellation

A useful normalized scenario is 10 records/s/session, 2 KiB encoded records, 60 seconds of POST outage. Payload-only retained data predicted from the source is approximately:

- N=1: ~1.0 MiB after accounting for the first 100-record batch
- N=10: ~11.5 MiB
- N=50: ~58.4 MiB
- N=128: ~149.8 MiB
- N=200: still ~149.8 MiB because discovery caps active producers at 128

These numbers are illustrative encoded payload only; real RSS includes `serde_json::Value`, strings, vector capacity, allocator metadata, tasks, HTTP state, and source-socket buffering.

Smallest amplification sequence:

1. enqueue 100 records
2. flusher takes that batch and enters a retrying POST
3. enqueue 100 more while `flushing == true`
4. enqueue record 101 behind the in-flight batch

At step 4 the shared pending pool has exceeded the nominal record threshold and no drain can occur until the current POST leaves its retry loop.

Negative control: same producer schedule against a healthy ACK endpoint, then cancel the forwarder. Session workers should be aborted and joined, flusher should terminate, sockets should close, and RSS/FDs should settle close to baseline.

### Experiment B — stdio write-lane stall

Use the existing `transportExecutableOverride` seam in `CmuxRemoteDaemon` tests. The fake SSH helper should:

1. read and answer the initial `hello`
2. optionally answer setup RPCs
3. stop reading stdin while remaining alive
4. exit only after a long safety deadline

Drive one large `proxy.write`/RPC sufficient to fill the pipe, then launch `1, 10, 50, 200` additional synchronous RPC callers.

Measure:

- submitted/completed caller counts
- blocked caller threads/work items
- process RSS
- FD count
- elapsed time relative to each operation's nominal response timeout
- pending-call population if a test-only observation seam is later justified
- behavior after direct `client.stop()`
- behavior after helper exit

Distinguishing result: secondary callers remain blocked beyond their nominal response timeout because they have not reached `waitForCall` yet. The first owner that stops converging is the global `writeQueue` lane, with pending registry entries accumulating before it.

Negative control: helper continuously reads and responds. Caller count should affect latency roughly linearly through one serialized write lane while every call completes and cleanup returns to baseline.

### Experiment C — same-lifecycle PTY replacement

With the fake RPC transport stalled as in B:

1. start one bridge for a stable `(sessionID, lifecycleID, attachmentID)`
2. authenticate the local bridge client so `pty.attach` begins
3. close/recreate the bridge while attach remains blocked
4. repeat replacement 1 / 10 / 50 times

Measure bridge server count, local loopback sockets, live RPC queues/threads, pending calls, lifecycle generation count, bridge IDs inside the active generation if exposed by test code, and cleanup time.

Expected source-level discriminator: generation count stays at one while bridge ownership grows. Full tunnel teardown should be the stronger breaker.

### Experiment D — reachability overlap

Inject or wrap a command runner whose `ssh -G` consumes nearly its full 3 second deadline. Trigger reconnect-policy evaluation/replacement 1 / 10 / 50 times inside that interval.

Measure descendant process count, pipe FDs, TCP sockets, task count where available, and decay after triggering stops.

Expected curve: transient live resource count approximately equals launch rate multiplied by probe lifetime, followed by convergence after the 3s/2.5s deadlines.

Negative control: instant `ssh -G` plus immediate reachable TCP result.

### Experiment E — slow local proxy consumer

Drive N proxy sessions against a remote TCP source that continually emits data. Complete SOCKS/CONNECT setup, then stop local reads.

N = `1, 10, 50, 200`.

Measure RSS, outstanding local socket send buffers (`netstat`/`lsof`/platform tools), connection count, remote stream count, and teardown convergence. Run the same source with active local readers as the negative control.

This experiment remains a candidate until Network.framework behavior is measured.

## Measurement recipe for macOS fork execution

External measurements should come before adding production instrumentation:

- process tree / descendants: `ps -axo pid=,ppid=,rss=,command=`
- RSS: `ps -o rss= -p <pid>` plus `vmmap -summary <pid>` when useful
- threads: `ps -M <pid>` or sample tooling
- FDs and sockets: `lsof -nP -p <pid>`
- listener/socket inventory: `lsof -nP -a -p <pid> -i` plus Unix-socket rows
- stuck stacks: `sample <pid>` after a knee appears
- settle time: periodic sampling for at least one full retry/timeout interval after load stops

Internal counters should be added only after an external curve reproduces, and should be minimal enough to avoid perturbing the owner being measured.

## Evidence labels

- Exact source revision and ownership map: **Observed** from pinned source.
- Journal producer/consumer topology and retry behavior: **Observed**.
- Journal retained-memory values above: **Illustrative**, calculated from explicit rates and encoded sizes rather than measured RSS.
- Stdio RPC pre-timeout write-lane hole: **Observed** in control flow; exact runtime blocked-write behavior on macOS remains **Unknown** until the fork test executes.
- PTY same-generation bridge multiplication: **Observed** in ownership logic; runtime thread/RSS threshold remains **Unknown**.
- Reachability stale-work overlap: **Observed**, with timeout-derived lifetime **Inferred** from sequential worst-case stages.
- Proxy local-send retention: **Inferred candidate** pending runtime measurement.
- Hook/provider/agent/terminal bounds: **Observed** source controls.

## Competing explanations and discriminators

1. **Journal buffering is intentionally durable enough elsewhere to absorb the pool.** Discriminator: inspect the session-stream server's bounded delivery behavior and run a real socket producer. Even if upstream source backpressures, the forwarder's own pending `Value`s should stop at a measurable bound to satisfy the invariant.
2. **Closing the stdio transport interrupts a blocked `FileHandle.write` immediately.** Discriminator: red-first fake-transport test and direct `client.stop()` timing. This would reduce surviving-state severity, while the pre-timeout accumulation still exists until stop is invoked.
3. **libdispatch does not dedicate one kernel thread per blocked bridge queue.** Discriminator: measure OS threads separately from queued work and retained bridge/session owners. The bug claim concerns retained operations and delayed cleanup; thread count is one consequence, not the invariant itself.
4. **Network.framework applies strict internal send backpressure.** Discriminator: experiment E with RSS and socket-buffer measurements. If retained bytes plateau cleanly, retain this as a negative result.
5. **Repeated PTY replacement is rejected by a higher owner before bridge creation.** Discriminator: exercise the actual broker/tunnel entry points with one stable lifecycle ID and count accepted bridge registrations. If a caller-level replacement fence exists, narrow the PTY claim accordingly.

## Ranked implementation thesis

1. **Journal forwarder:** strongest candidate for a bounded-ingress repair. A correct repair should preserve lossless cursor semantics while preventing unlimited in-memory records during one retrying POST. Backpressure to the journal stream is preferable to dropping records. Any cap should include both record count and retained bytes.
2. **Remote daemon RPC:** add a write-phase deadline/cancellation owner that begins before or around entry to the physical write, then prove queued calls and keepalive cannot wait forever before their normal response deadlines. The exact implementation needs a macOS behavior test first because `FileHandle` cancellation semantics determine the safest primitive.
3. **PTY bridge replacement:** after the RPC write owner is bounded, consider a per-lifecycle replacement policy so a new bridge replaces or waits for the prior bridge instead of accumulating bridge IDs while an attach is unresolved.
4. **Reachability:** retain as a secondary transient-pressure candidate. Cancellation ownership could be tightened later, but existing process and TCP deadlines already guarantee eventual convergence.
5. **Proxy output:** promote only if runtime measurements show meaningful retained send state.

## Current action

Create an owned-fork branch directly from `8ef183f1e5de765b183aec9d1799f17a0848ae84`. Add red-first probes without production fixes:

- a `CmuxRemoteDaemon` test proving whether queued RPCs outlive their nominal deadlines while a physical stdio write is blocked;
- a journal-forwarder scaling probe/model that records the 1/10/50/128/200 producer curve and cleanup control;
- supporting notes/scripts for macOS resource sampling where they can run without changing product behavior.

Only after the probes produce a discriminating result should the branch add a production repair.
