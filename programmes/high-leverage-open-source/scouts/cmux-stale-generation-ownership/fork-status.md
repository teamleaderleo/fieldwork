# cmux stale-generation fork status

State: `investigating`  
Fieldwork issue: #931  
Original pinned target: `manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## In simple words

The remote-proxy broker stale-owner failure is now target-executed with a red regression, a minimal generation fence, an ordinary-current-owner negative control, and the full package suite green. The executed base and current-main check use the same `RemoteProxyBroker.swift` blob as the original scout pin.

The cloud CLI Unix-socket stale-unlink mechanism remains retained while its current lifetime-lock repair is HOLD. Session/controller, remote PTY, and production RPC-client replacement provide negative controls around neighboring successor boundaries.

This file owns live fork dispositions for scout #931 and supersedes older execution-carrier status text in `report.md` when the two disagree.

## Remote proxy broker — proven repaired candidate

Owned-fork PR: `teamleaderleo/cmux#6`.

Original source pin: `eaa899cb20bd411019744fbd2bdedeb397f3070b`.

Executed restack:

```text
2ead47750ab2f47c13972d0709d99cdcbaa8ad73
  -> 80c54e08917a02ae91436a1495fe6296ea6c2bda  RED regression only
  -> 3f11ef644ce14d43e8086edb346dc4659a3e0c32  GREEN generation fence
```

Target execution receipt: `proxy-execution-receipt-33552198922.md`.

Run `33552198922`, job `100004099358`, on GitHub-hosted macOS 15 completed successfully:

- ancestry and red-only diff fence: PASS;
- RED focused stale-owner test: executed and failed at `cmux.remote.pty` code 40, `remote daemon tunnel is not ready`;
- GREEN focused test: PASS;
- current-owner `fatalFailureRestarts` negative control: PASS;
- full `CmuxRemoteWorkspace` package: **95 tests in 18 suites PASS**.

Evidence class: **`target-executed`**.

The production repair is +17/-3 lines in `RemoteProxyBroker`: one UUID per installed tunnel runtime, captured in that runtime's fatal callback, stored when the tunnel becomes current, required to match before failure handling, and cleared on teardown.

The provider contract says `onFatalError` is invoked once after the tunnel has stopped itself and may fire on any queue. It gives the broker no cancellation guarantee for an already-issued callback after replacement. Routing that callback by transport key alone therefore cannot prove current ownership.

Adjacent broker audit:

- restart wakeups compare a per-entry `restartToken`;
- ready-operation completion compares captured `Entry` identity;
- managed-cloud endpoint refresh compares captured `Entry` identity before publication;
- stale lease release carries a subscriber UUID and cannot remove a different subscriber;
- fatal tunnel failure was the lone key-only mutation in this replacement cluster.

Current-source continuity: checked upstream `main` at `6044a8b3f43152d2e6fc17f771fd4b277b393118`. `RemoteProxyBroker.swift` has blob SHA `efdb05374e725727efd346684e5cc0ff1d15cb76` at the original pin, executed base, and checked current main. The three intervening upstream commits after the executed base touched only cmux-tui/workflow/docs surfaces.

Consequence: **2. stale destructive effect**, plus **3. stale publication / UI lies**. No duplicate remote-command effect is claimed.

Remaining gate: independent complete-diff/current-source review if explicitly requested or required for later promotion. No second-model review has been launched.

## Remote PTY attachment replacement — negative control

Classification: **6. expected handoff semantics**.

The stable attachment ID is supplemented by exact attachment object identity and a fresh client token. Delayed cleanup checks the retired object/token before mutation. Bytes already accepted from A before replacement remain deliberately owned by the session FIFO and may drain before B's bytes; fresh A input/resize/detach after B is current is fenced.

## Remote session coordinator replacement — negative controls

The workspace/controller handoff is explicitly generation-aware at the original pinned revision.

App-facing publication is fenced by controller UUID. `WorkspaceRemoteSessionHostAdapter` captures the coordinator's immutable `controllerID` and, after hopping to the main queue, checks `workspace.activeRemoteSessionControllerID == controllerID` before applying connection state, daemon status, proxy endpoint, port snapshot, heartbeat, or bootstrap-TTY publication. A retired coordinator cannot publish UI/state through that seam after B becomes active.

Reverse-relay process callbacks are also fenced:

- standalone relay readiness requires exact `reverseRelayProcess === process`;
- relay termination requires exact process identity;
- delayed relay restart carries a UUID `reverseRelayRestartToken` and compares it before launching.

Persistent relay metadata cleanup initially looked like a cross-generation hazard because persistent restores deliberately rotate credentials while using the durable daemon slot as ownership identity. The workspace transition closes that race. `enqueueRemoteSessionTransition` serializes transitions, `performRemoteSessionTransition` awaits each conflicting old controller's `stopAndWait`, and a successor is started only after that cleanup succeeds. `stopAndWait` resumes only after `stopAllLocked`, which synchronously executes `stopReverseRelayLocked`; the remote relay/slot cleanup command therefore finishes before B exists. Cleanup failure for the same persistent or relay namespace blocks successor start instead of allowing two owners.

Disposition: negative result for normal workspace replacement. Reopen if a caller constructs/replaces `RemoteSessionCoordinator` outside `Workspace.performRemoteSessionTransition`, or if cleanup becomes detached from `stopAndWait`.

## RemoteDaemonRPCClient same-object restart — production negative result

The reusable RPC client has an isolated stale-termination seam: `handleProcessTermination(_:)` compares the terminating `Process` with `self.process` only when deciding whether to notify, then clears client transport state. Reusing one `RemoteDaemonRPCClient` object for A -> B before A's delayed termination callback would therefore be unsafe.

The production proxy replacement path does not reuse that object at the original pin:

- every `RemoteDaemonProxyTunnel.start()` constructs a fresh `RemoteDaemonRPCClient`;
- `RemoteDaemonProxyTunnel.stopLocked` permanently sets `isStopped = true` and `start()` rejects a stopped tunnel;
- broker replacement creates a new tunnel, so the client object is replaced with the tunnel generation.

Disposition: retain as an API-level implementation hazard and a production negative result. Reopen if a production caller starts the same `RemoteDaemonRPCClient` object more than once or if tunnel restart semantics change to reuse the client.

## NativeSSH control-master ownership — API seam under reachability review

`NativeSSHControlMasterOwnershipRegistry` correctly refuses a new shared lease while another owner holds exclusive cleanup authorization. `NativeSSHConnectionBroker.retainWorkspace`, however, discards the registry's Boolean result and records the workspace lease locally anyway. In isolation this can create split ownership: A holds exclusive cleanup authority while B is broker-visible without a cross-process shared lease.

Existing broker tests cover stale release generations, delayed cleanup cancellation, retries, and shared/exclusive registry locking, but do not cover a successor retain colliding with already-authorized exclusive cleanup.

Production reachability is unresolved. Repository code search has not found a macOS production caller of the broker's `retainWorkspace`; app-target `retainWorkspace` matches inspected so far are unrelated helpers, while `releaseWorkspace` is wired into remote-session lifecycle. The lease generation itself can only be minted by the broker retain path. Do not promote this seam until the production caller/order is found or the ownership machinery is shown to be dormant.

## Cloud CLI Unix-socket ownership — finding retained, repair HOLD

Owned-fork research PR: `teamleaderleo/cmux#10`.

Mechanism established by the retained Go model:

```text
A binds stable socket pathname
B removes A pathname and binds the same name
B becomes dialable
A closes later
A cleanup removes the stable name
B listener FD survives but future dials fail ENOENT
```

Consequence: **2. stale destructive effect**, with an unreachable surviving listener resembling **4. leaked surviving resource** until B exits.

The current lifetime-lock repair is on HOLD for two reasons:

1. `runWebSocketPTYServer` treats cloud-bridge startup failure as fatal. Holding a lock for A's entire listener lifetime converts overlapping B startup from replacement into daemon-start rejection. Source/history establish a normal one-daemon-per-machine service, but do not establish that overlap must be rejected as policy.
2. The candidate uses a new adjacent regular lock pathname opened with plain `os.OpenFile`. The original pinned target itself hardens another start lock against symlinks, non-regular files, foreign ownership, and hard links. A retained lock-file design needs equivalent ownership checks.

A narrower repair, if overlap is intended, is generation-aware pathname publication/cleanup: serialize the name mutation across processes, disable automatic Unix-listener unlink, and remove the stable name only when it still names the retiring generation. If the bridge is explicitly a machine-wide singleton, a lifetime ownership lock may be appropriate after its lock-file boundary is hardened.

No target-native cloud repair receipt is claimed.

## Next gate

1. Preserve the proxy candidate at its executed head and avoid unrelated fork edits.
2. Continue source scouting for a second production-reachable stale-owner boundary, prioritizing NativeSSH/control-master reachability, hook/event-producer identity, agent-session identity, and descendant cleanup.
3. Keep cloud socket repair on HOLD until singleton-vs-replacement semantics are established; retain the stale-unlink mechanism regardless.
4. Keep third-party upstream read-only unless a fresh bounded human greenlight names one exact interaction.

Third-party upstream remained read-only throughout these fork operations.
