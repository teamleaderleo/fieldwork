# cmux stale-generation fork status

State: `ready-for-synthesis`  
Fieldwork issue: #931  
Original pinned target: `manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Executed candidate base: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Latest upstream checked: `594eb0461e0ae4d57a99180e19097cea5e5091e0`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## In simple words

The scout found two consequential successor-ownership failures and closed the strongest adjacent lookalikes with explicit negative controls.

The remote proxy broker lets a retired tunnel's queued fatal callback target successor B by durable transport key. The cloud CLI bridge lets old listener A unlink successor B's machine-global Unix-socket pathname. Both now have clean two-commit owned-fork candidates and target-native red/green evidence.

The NativeSSH ControlMaster path was the last serious split-owner candidate. Its local and cross-process owner books can briefly disagree, but foreground adoption, coordinator startup, and destructive cleanup each recheck cross-process authority before acting, so it closes as a negative result under the traced production paths.

Upstream advanced two disjoint commits after the execution runs. The two affected upstream owner files are byte-identical through latest checked `main`; the executed evidence remains source-continuous, while a final contribution packet would still restack onto then-current upstream.

## Core invariant

Once a successor becomes the authoritative owner of a long-lived resource, work from the retired owner must not mutate that resource unless the handoff contract explicitly preserves that work and the successor can account for it.

## Remote proxy broker — target-executed repaired candidate

Canonical owned-fork PR: `teamleaderleo/cmux#6`.

```text
6044a8b3f43152d2e6fc17f771fd4b277b393118
  -> e9ea500cebfba753444e961e2ef9d6af079ec096  RED regression only
  -> 8daa014321001d9aec128a9112720fb74e2ae11d  GREEN generation fence
```

Execution run `33554543666`, job `100012026075`, macOS 15.7.7 arm64 / Xcode 26.3 / Swift 6.2.4:

- ancestry and red-only diff fence: PASS;
- RED `staleFatalCallbackCannotStopSuccessor`: fails at `cmux.remote.pty` code 40, `remote daemon tunnel is not ready`;
- GREEN same test: PASS;
- current-owner `fatalFailureRestarts` negative control: PASS;
- full `CmuxRemoteWorkspace`: **95 tests in 18 suites PASS**.

Evidence class: **`target-executed`**. Receipt: `proxy-execution-receipt-33554543666.md`.

Repair: one UUID per installed tunnel runtime; fatal callbacks carry that generation and destructive failure handling requires it to remain current.

Consequence: **2. stale destructive effect**, plus **3. stale publication / UI lies**. Duplicate command execution was not demonstrated and is not claimed.

## Cloud CLI Unix-socket ownership — target-executed repaired candidate

Canonical owned-fork PR: `teamleaderleo/cmux#10`.

Original failure:

```text
A binds stable socket pathname
B removes A pathname and binds the same name
B becomes dialable
A closes later
A cleanup removes the stable name
B listener FD survives; future dials fail ENOENT
```

Consequence: **2. stale destructive effect**, with an unreachable surviving listener carrying a bounded **4. leaked surviving resource** characteristic until B exits.

The first lifetime-lock implementation was rejected in self-review because plain `os.OpenFile` on a predictable lock path followed symlinks and did not establish FIFO/hard-link/owner semantics. The retained chain is:

```text
6044a8b3f43152d2e6fc17f771fd4b277b393118
  -> 3fcfdc334a2459ea353dc6316d5325be48a20e40  RED tests only
  -> 2df7cd900dd038bdd18b4c7c35dcd809878f1344  GREEN hardened lock
```

RED covers live-owner overlap, symlink lock, FIFO lock, hard-linked lock, and owned-mode migration. GREEN opens the lock with `O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC`, validates regular-file type, one link, effective-UID ownership and private mode through the descriptor, then acquires nonblocking `flock`. The lock remains held until retiring listener cleanup removes the socket pathname.

Execution run `33560606934`, job `100031891608`, Ubuntu 24.04.4 / Go 1.24.13:

- all five RED cases fail separately at their exact markers;
- combined GREEN set: **25 consecutive passes**;
- daemon cross-build: Darwin arm64 PASS, Darwin amd64 PASS, Linux arm64 PASS, Linux amd64 PASS;
- Darwin arm64 Go test target cross-compile: PASS;
- full `daemon/remote` `go test ./...`: PASS.

Evidence class: **`target-executed`**. Receipt: `cloud-cli-execution-receipt-33560606934.md`. Review history: `cloud-cli-lock-review.md`.

## Upstream movement after execution

Latest checked upstream: `594eb0461e0ae4d57a99180e19097cea5e5091e0`, two commits ahead of the executed base.

The intervening compare touches browser-skill workflow/docs/tests and `cmux-tui/crates/cmux-remote/src/client.rs`; neither candidate package is changed.

Byte continuity:

- upstream `RemoteProxyBroker.swift` remains blob `efdb05374e725727efd346684e5cc0ff1d15cb76`;
- upstream `cloud_cli_bridge.go` remains blob `299d90d1ae1b440146670a7f490ea37390a95ec5`.

The exact self-review fence is retained in `self-review.md`. The fork PRs intentionally remain on their executed base until the independent-review/submission gate; a final packet must restack and revalidate any reviewed input that moves.

## Remote PTY attachment replacement — negative control

Classification: **6. expected handoff semantics**.

A stable attachment ID is supplemented by exact attachment object identity and a fresh client token. Delayed cleanup checks the retired object/token before mutation. Bytes already accepted from A before replacement remain deliberately owned by the session FIFO and may drain before B's bytes; fresh A input/resize/detach after B is current is fenced.

## Remote session coordinator replacement — negative control

App-facing publication is fenced by controller UUID. Reverse-relay process callbacks compare exact process identity, delayed restart carries a UUID token, and workspace transitions await `stopAndWait` before creating the successor. Cleanup failure for the same persistent namespace blocks successor start.

## RemoteDaemonRPCClient same-object restart — production negative result

`handleProcessTermination(_:)` has an isolated same-object stale-termination hazard, but the production proxy path creates a fresh one-shot `RemoteDaemonRPCClient` for every tunnel generation. Reopen if production begins reusing one client object across transport generations.

## NativeSSH ControlMaster split-owner candidate — negative result

`retainWorkspace` can mint a local generation and populate `ownerLeases` even if the cross-process ownership registry rejects the exact ControlPath retain. That is suspicious bookkeeping, but the traced effect boundaries are independently fenced:

- foreground authentication uses `beginControlMasterAdoption` and requires `completeControlMasterAdoption` before proceeding;
- restore/reconnect/fork coordinators call `prepareControlMasterOwnershipLocked` before bootstrap/proxy/reverse-relay work, which re-runs `retainResolvedControlMasterLease` and rejects a busy owner;
- last-owner `ssh -O exit` requires fresh `beginCleanup` authorization;
- the only startup side effect before the ownership recheck kills PPID-1 relay/stdio orphan children, not the shared ControlMaster process.

Disposition: negative result for stale-generation mutation under current production paths. Durable record: `native-ssh-ownership-negative.md`.

## Current gate

1. Scout reconnaissance is complete enough for synthesis: two target-executed findings plus neighboring negative controls and one expected-handoff case.
2. Deterministic self-review is complete. See `self-review.md`.
3. Consequential ownership repairs remain **HOLD for human-facing upstream submission** until an independent complete-diff final review occurs. cmux's local instructions require explicit user opt-in before launching a second-model review, and that opt-in has not been given.
4. Before any human-facing submission packet is treated as current, restack the selected candidate onto then-current upstream and re-run the smallest invalidated gates.
5. Third-party upstream remains read-only. Any upstream issue/PR/comment requires a fresh bounded human greenlight for that exact interaction.

Third-party upstream remained read-only throughout this scout.
