# cmux stale-generation fork status

State: `investigating`  
Fieldwork issue: #931  
Pinned target: `manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## In simple words

The remote-proxy broker finding has one canonical owned-fork candidate with a test-only red commit followed by a minimal generation fence. The cloud CLI Unix-socket branch remains useful research, but its current lifetime-lock repair is held because it changes daemon-overlap semantics and introduces an adjacent lock pathname that still needs hardening.

This file owns live fork dispositions for scout #931 and supersedes older execution-carrier status text in `report.md` when the two disagree.

## Remote proxy broker — canonical candidate

Owned-fork PR: `teamleaderleo/cmux#6`  
Base: `eaa899cb20bd411019744fbd2bdedeb397f3070b`

Two-commit history:

1. RED `f1a91ab9090295f04d6b8fffef7bf6a4cfdd0371` — behavioral regression only.
2. GREEN `6cb48b5d96a9c2ce36cd699c5be3ca64050d52a0` — tunnel-generation fence in `RemoteProxyBroker` (+17/-3 source lines).

The provider contract says `onFatalError` is invoked once after the tunnel has stopped itself and may fire on any queue. It gives the broker no cancellation guarantee for an already-issued callback after replacement. Routing that callback by transport key alone therefore cannot prove current ownership.

Adjacent broker audit at the pinned revision:

- restart wakeups compare a per-entry `restartToken`;
- ready-operation completion compares captured `Entry` identity;
- managed-cloud endpoint refresh compares captured `Entry` identity before publication;
- stale lease release carries a subscriber UUID and cannot remove a different subscriber;
- fatal tunnel failure is the lone key-only mutation in this replacement cluster.

Execution carrier: owned-fork PR `teamleaderleo/cmux#8`. Its workflow was moved from the unavailable `macos-14` label to `macos-15` without changing the canonical source branch. Current run `33550818558` remains queued. Queue admission is not execution evidence.

Evidence class remains `source-read` + `model-executed` + `target-fix-prepared` until the focused red/green run actually executes.

## Remote PTY attachment replacement — negative control

Classification: **6. expected handoff semantics**.

The stable attachment ID is supplemented by exact attachment object identity and a fresh client token. Delayed cleanup checks the retired object/token before mutation. Bytes already accepted from A before replacement remain deliberately owned by the session FIFO and may drain before B's bytes; fresh A input/resize/detach after B is current is fenced.

## RemoteDaemonRPCClient same-object restart — production negative result

The reusable RPC client has an isolated stale-termination seam: `handleProcessTermination(_:)` compares the terminating `Process` with `self.process` only when deciding whether to notify, then clears client transport state. Reusing one `RemoteDaemonRPCClient` object for A -> B before A's delayed termination callback would therefore be unsafe.

The production proxy replacement path does not reuse that object at the pinned revision:

- every `RemoteDaemonProxyTunnel.start()` constructs a fresh `RemoteDaemonRPCClient`;
- `RemoteDaemonProxyTunnel.stopLocked` permanently sets `isStopped = true` and `start()` rejects a stopped tunnel;
- broker replacement creates a new tunnel, so the client object is replaced with the tunnel generation.

Disposition: retain as an API-level implementation hazard and a production negative result for this scout. Reopen if a production caller starts the same `RemoteDaemonRPCClient` object more than once or if tunnel restart semantics change to reuse the client.

## Cloud CLI Unix-socket ownership — finding retained, repair HOLD

Owned-fork research PR: `teamleaderleo/cmux#10`  
Current exploratory red/green head: `5f8d17ca28410d6077a7fc66a646668f752c156e`

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

1. `runWebSocketPTYServer` treats cloud-bridge startup failure as fatal. Holding a lock for A's entire listener lifetime converts overlapping B startup from replacement into daemon-start rejection. Source/history establish a normal one-daemon-per-machine service, but do not yet establish that overlap must be rejected as policy.
2. The candidate uses a new adjacent regular lock pathname opened with plain `os.OpenFile`. The pinned target revision itself hardens another start lock against symlinks, non-regular files, foreign ownership, and hard links. A retained lock-file design needs equivalent ownership checks.

A narrower repair, if overlap is intended, is generation-aware pathname publication/cleanup: serialize the name mutation across processes, disable automatic Unix-listener unlink, and remove the stable name only when it still names the retiring generation. If the bridge is explicitly a machine-wide singleton, a lifetime ownership lock may be appropriate after its lock-file boundary is hardened.

The cloud execution carrier was retired before execution; no target-native receipt is claimed.

## Next gate

1. Obtain actual macOS red/green execution for `teamleaderleo/cmux#6` and retain the exact run/log identity.
2. If green, run/retain the current-owner fatal-failure negative control and full `CmuxRemoteWorkspace` package suite, then request independent review for the ownership repair.
3. Keep cloud socket repair on HOLD until singleton-vs-replacement semantics are established; retain the stale-unlink mechanism regardless.
4. Continue adjacent production-reachable successor scouting in session/controller, hook/event-producer, agent-session, and descendant cleanup boundaries while runner capacity is unavailable.

Third-party upstream remained read-only throughout these fork operations.
