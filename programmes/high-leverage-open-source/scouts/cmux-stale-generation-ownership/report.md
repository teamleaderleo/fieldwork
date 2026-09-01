# cmux stale-generation ownership scout

State: `investigating`  
Fieldwork issue: #931  
Programme: #114  
Worker: `chatgpt:gpt-5.6-sol`  
Fieldwork base: `eda248dc8a752241ae9359962a467c2bfd2dbb8a`  
Target: `manaflow-ai/cmux`  
Pinned target revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Pinned at: 2026-09-01 17:27:07Z  
Evidence so far: `source-read` + `model-executed`  
Upstream contact authorized: `false`

## In simple words

Does an old cmux owner still get to act after a successor has taken over the same long-lived identity?

The strongest current candidate is the remote proxy broker. Tunnel A can fail and queue a fatal callback identified only by the durable transport key. If A is retired and tunnel B becomes ready at the same key before that callback reaches the broker queue, A's callback can stop B. The broker already has a generation token for delayed restart timers; fatal callbacks carry no corresponding generation identity.

A second candidate exists in the cloud CLI bridge: overlapping daemon generations use one stable Unix-socket pathname, and A's deferred cleanup can unlink B's pathname after B binds it. The remote PTY attachment replacement path provides a strong negative control: fresh stale input, resize, and detach are fenced by attachment object/token identity, while input already accepted before handoff is explicitly preserved in FIFO order.

The owned cmux fork is the next evidence surface. The broker candidate should receive a target-native regression first, then the smallest generation fence that makes that regression pass.

## Core invariant

> Once a successor becomes the authoritative owner of a long-lived resource, work from the retired owner must not mutate that resource unless the handoff contract explicitly preserves that work and the successor can account for it.

Old work occurring after detach is insufficient evidence for duplicate execution; duplication must be separately demonstrated.

## Identity and generation map

| Durable thing | Durable identity | Generation discriminator | Result |
| --- | --- | --- | --- |
| Remote proxy tunnel | broker transport key | current tunnel; restart timers also carry `restartToken` | candidate violation: fatal callback carries key only |
| Persistent PTY session | `sessionID` | hub session object / PTY process | survives attachment replacement |
| PTY attachment | `sessionID` + stable `attachmentID` | exact attachment object + fresh client token | fenced |
| Accepted PTY input | session FIFO item | accepted before replacement | explicit handoff semantics |
| Persistent per-slot daemon | slot | exclusive `flock` | fenced |
| Cloud CLI bridge | stable Unix-socket path | none across listener generations | candidate violation under overlap |
| RPC client process | reusable client object | current `Process` check is partial | evidence-limited seam |

## Main candidate: key-only tunnel failure can stop B

`RemoteProxyBroker.startEntryLocked` creates a tunnel whose fatal callback captures only the durable transport key. The callback later queues `handleTunnelFailureLocked(key:detail:)`. That handler checks only that the key still has some tunnel and then stops the current runtime. It never compares the callback's originating tunnel or a tunnel generation.

The broker already solves the same stale-work class for restart timers: each delayed wakeup carries a UUID `restartToken`, and `restartDelayElapsed` ignores a token that no longer matches the entry.

`RemoteDaemonProxyTunnel.failLocked` is one-shot, but one callback is enough. `stop()` and `stopPreservingPTYLifecycle()` synchronously enter the tunnel's serial queue, so a broker teardown can wait on A while A is frozen immediately before publishing its already-decided fatal callback.

### Smallest violating sequence

```text
A current for transport K
A enters failLocked; freeze before onFatalError enqueue
broker release(last lease) starts teardown and blocks on A queue
queue acquire(B, K) behind that broker operation
release A
A queues fatal(K) behind acquire(B)
broker removes A
broker installs B and publishes ready
A's fatal(K) runs and stops current tunnel B
```

### Deterministic discriminator

`artifacts/broker_stale_generation_probe.swift` models the two serial queues and that exact order. Swift 6.2.1 on x86_64 Linux produced:

```text
=== CURRENT_KEY_ONLY ===
A_ENTRY_REMOVED
B_READY
STALE_FATAL_STOPPED B: A transport failed
FINAL_CURRENT nil B_STOP_COUNT 1
```

With a generation guard under the same schedule:

```text
=== CONTROL_GENERATION_GUARD ===
A_ENTRY_REMOVED
B_READY
SAFE_DROP stale=A current=B
FINAL_CURRENT B B_STOP_COUNT 0
```

Consequence: **2. stale destructive effect**. A's failure can also publish an error after B reached ready, giving a **3. stale publication / UI lies** symptom. This evidence does not demonstrate duplicate remote command execution.

Surviving state: B's local tunnel and endpoint are torn down while daemon-side persistent PTY/process state may survive, followed by another broker retry cycle.

Repair owner: `RemoteProxyBroker`. Mint one tunnel-generation UUID per installed runtime, capture it in `onFatalError`, require it to match the entry's current generation before stop/publication, and clear or replace it on every runtime transition.

Evidence limit: source-read plus model-executed. A target-native `RemoteProxyBrokerTests` regression is required next.

## Negative control: remote PTY replacement is fenced

The PTY handoff explicitly preserves already-accepted input from A in the per-session FIFO. Fresh work from retired A is fenced:

- replacement installs a new attachment object;
- delayed detach compares exact attachment identity;
- by-ID write/resize/detach checks the client attachment token;
- every Swift `attachPTY` mints a fresh UUID token;
- timeout cancellation carries A's exact token.

Pinned tests distinguish the contract: `TestWebSocketPTYReplacedAttachmentCannotWriteInput` rejects stale fresh input/resize, while `TestWebSocketPTYReattachWritesAcceptedOldInputBeforeNew` deliberately observes `OLDNEW` for input accepted before replacement.

Classification: **6. expected handoff semantics** for accepted pre-handoff bytes.

## Adjacent candidate: cloud CLI listener cleanup can unlink B

`cloud_cli_bridge.go` defaults to `/tmp/cmux-cloud-cli.sock`. Startup removes the pathname then binds it; `acceptLoop` defers another unconditional remove.

```text
A binds path
B removes A pathname and binds same path
B becomes dialable
A closes
A deferred remove deletes B pathname
```

`artifacts/cloud_cli_socket_generation_probe.go` reproduced this on Go 1.23.2 / Linux. B's listener remains alive through its file descriptor while new dials fail with `ENOENT`. The paired control disables A's automatic unlink and removes only when the current inode still belongs to A; B remains dialable.

Consequence: **2. stale destructive effect**, with an unreachable surviving B listener resembling **4. leaked surviving resource** until B exits.

Reachability is narrower than the broker candidate because the normal Freestyle service tends to serialize ordinary restarts. Overlapping RPC-enabled daemon instances on one VM still share the machine-global CLI socket path.

## Adjacent safe owner

The persistent per-slot daemon acquires nonblocking exclusive `flock` ownership before becoming ready, so a second owner for the same slot cannot overlap. That is a direct safe comparison for machine-local Unix-socket ownership.

## Secondary seam

`RemoteDaemonRPCClient+Events.swift` checks whether a process-termination callback belongs to the current `Process` only for notification eligibility, then clears client state regardless. A reused client instance could let A clear B. Production proxy tunnels normally create a fresh RPC client, so retain this as evidence-limited until a production same-object restart caller is found.

## Ranked next branches

1. RemoteProxyBroker fatal-generation fence: target-native regression, minimal repair, focused test execution.
2. Cloud CLI bridge pathname ownership: independent Go regression after the broker branch settles or if target-native broker execution disproves the model.
3. Reusable RPC client process callback: promote only with a production same-instance restart caller.
4. Continue successor-boundary scouting after the first repair is bounded.

## Upstream boundary

`manaflow-ai/cmux` remained read-only. No upstream state was changed.