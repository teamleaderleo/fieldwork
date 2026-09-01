# cmux stale-generation fork status

State: `investigating`  
Fieldwork issue: #931  
Original pinned target: `manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Current checked upstream main: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## In simple words

The remote-proxy broker stale-owner failure is proven on exact current upstream and has a small generation-fenced repair with target-native red/green evidence.

The cloud CLI Unix-socket stale-unlink failure is also real. Its first lifetime-lock repair passed the ownership regression, but review found a second boundary introduced by that repair: the predictable lock pathname was opened with plain `os.OpenFile`, so symlink, FIFO, and hard-link cases were outside the ownership contract. The canonical cloud branch has therefore been rewritten to a new two-commit red/green candidate that hardens the lock by file descriptor. Its previous green receipt is historical mechanism evidence only; fresh execution is required for the rewritten head.

Remote PTY attachment replacement, workspace/session coordinator replacement, and production RPC-client replacement remain useful negative controls.

## Core invariant

Once a successor becomes the authoritative owner of a long-lived resource, work from the retired owner must not mutate that resource unless the handoff contract explicitly preserves that work and the successor can account for it.

## Remote proxy broker — target-executed repaired candidate

Canonical owned-fork PR: `teamleaderleo/cmux#6`.

Exact current chain:

```text
6044a8b3f43152d2e6fc17f771fd4b277b393118
  -> e9ea500cebfba753444e961e2ef9d6af079ec096  RED regression only
  -> 8daa014321001d9aec128a9112720fb74e2ae11d  GREEN generation fence
```

Execution run `33554543666`, job `100012026075`, completed successfully on macOS 15.7.7 arm64 with Xcode 26.3 / Swift 6.2.4:

- ancestry and red-only diff fence: PASS;
- RED `staleFatalCallbackCannotStopSuccessor`: fails at `cmux.remote.pty` code 40, `remote daemon tunnel is not ready`;
- GREEN same test: PASS;
- current-owner `fatalFailureRestarts` negative control: PASS;
- full `CmuxRemoteWorkspace` package: **95 tests in 18 suites PASS**.

Evidence class: **`target-executed`**.

Repair: one UUID per installed tunnel runtime, captured in that runtime's fatal callback, stored only when the tunnel becomes current, required to match before destructive failure handling/publication, and cleared on teardown.

Consequence: **2. stale destructive effect**, plus **3. stale publication / UI lies**. No duplicate command effect is claimed.

Review note: the run emits an existing Swift 6.2 Sendable warning in the managed-cloud refresh path; the candidate does not introduce that capture.

## Cloud CLI Unix-socket ownership — proven mechanism, candidate under fresh execution

Canonical owned-fork PR: `teamleaderleo/cmux#10`.

Mechanism:

```text
A binds stable socket pathname
B removes A pathname and binds the same name
B becomes dialable
A closes later
A cleanup removes the stable name
B listener FD survives but future dials fail ENOENT
```

Consequence: **2. stale destructive effect**, with an unreachable surviving listener resembling **4. leaked surviving resource** until B exits.

### Review defect in the first repair

The first lifetime-lock implementation serialized A/B ownership and passed the overlap regression, but it opened the predictable `<socket>.lock` path with plain `os.OpenFile`. That follows symlinks and does not establish regular-file type, link count, owner, or nonblocking behavior before `flock`. A planted FIFO can turn lock acquisition into a blocking startup boundary; a symlink or shared inode can redirect ownership to an unintended object.

That finding invalidated the earlier candidate disposition even though its ownership-only run was green.

### Rewritten two-commit candidate

```text
6044a8b3f43152d2e6fc17f771fd4b277b393118
  -> 3fcfdc334a2459ea353dc6316d5325be48a20e40  RED tests only
  -> 2df7cd900dd038bdd18b4c7c35dcd809878f1344  GREEN hardened lock
```

RED now covers:

- overlapping B cannot replace live A;
- a symlinked lock pathname is rejected without touching its target;
- a FIFO lock is rejected without blocking before type validation;
- a hard-linked lock is rejected without chmod side effects;
- a single-link lock owned by the effective UID is migrated to mode `0600`.

GREEN opens the lock with `O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC`, validates regular-file type, single link, effective-UID ownership and private mode through the opened descriptor, then acquires nonblocking `flock`. The lock remains held until listener cleanup removes the retiring socket pathname.

The remote-daemon release builder targets Darwin/Linux arm64+amd64, so the implementation uses the existing `golang.org/x/sys/unix` dependency and the fresh verifier includes cross-build coverage.

Evidence class for the rewritten head: **`target-test-prepared`** until the fresh execution carrier completes. Previous runs remain historical evidence for the stale-unlink mechanism and singleton handoff semantics, not acceptance evidence for this changed head.

## Remote PTY attachment replacement — negative control

Classification: **6. expected handoff semantics**.

A stable attachment ID is supplemented by exact attachment object identity and a fresh client token. Delayed cleanup checks the retired object/token before mutation. Bytes already accepted from A before replacement remain deliberately owned by the session FIFO and may drain before B's bytes; fresh A input/resize/detach after B is current is fenced.

## Remote session coordinator replacement — negative control

App-facing publication is fenced by controller UUID. Reverse-relay process callbacks compare exact process identity, delayed restart carries a UUID token, and workspace transitions await `stopAndWait` before creating the successor. Cleanup failure for the same persistent namespace blocks successor start.

Disposition: negative result for normal workspace replacement. Reopen if a production caller replaces a coordinator outside the serialized workspace transition.

## RemoteDaemonRPCClient same-object restart — production negative result

`handleProcessTermination(_:)` has an isolated same-object stale-termination hazard, but the production proxy path creates a fresh `RemoteDaemonRPCClient` for every fresh one-shot tunnel. A stopped tunnel cannot restart. Reopen if production begins reusing the same client object across transport generations.

## NativeSSH control-master ownership — reachability unresolved

`NativeSSHControlMasterOwnershipRegistry` can reject a shared retain while another owner holds exclusive cleanup authorization, while `NativeSSHConnectionBroker.retainWorkspace` historically discarded that Boolean result and could record a local lease anyway. Production reachability remains unproven because no macOS production retain caller was established during the scout.

Do not promote this seam until the production caller/order is found or the ownership machinery is shown to be dormant.

## Next gate

1. Keep proxy PR #6 unchanged at its exact target-executed head.
2. Complete fresh red/green execution for rewritten cloud PR #10; any head movement invalidates the candidate disposition again.
3. After deterministic evidence is current, perform complete-diff review. Consequential ownership repairs still need independent final review before a human-facing upstream submission decision.
4. Continue adjacent scouting only after these canonical candidates are coherent; NativeSSH/control-master reachability remains the leading unresolved seam.
5. Third-party upstream remains read-only unless a fresh bounded human greenlight names one exact interaction.

Third-party upstream remained read-only throughout these fork operations.
