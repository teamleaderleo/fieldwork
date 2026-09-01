# cmux stale-generation fork status

State: `investigating`  
Fieldwork issue: #931  
Original pinned target: `manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Current checked upstream main: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Owned fork: `teamleaderleo/cmux`  
Upstream contact authorized: `false`

## In simple words

Two successor-ownership failures are now proven on exact current upstream and have clean two-commit owned-fork candidates with target-native red/green evidence.

The remote proxy broker needed a per-runtime generation on fatal callbacks. The cloud CLI bridge needed one lifetime owner for its stable Unix-socket pathname; review then found that the first ownership lock was itself under-specified, so that candidate was rewritten and re-executed with symlink, FIFO, hard-link, owner/mode, Darwin-build, and Linux runtime coverage.

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

Evidence class: **`target-executed`**. Exact receipt: `proxy-execution-receipt-33554543666.md`.

Repair: one UUID per installed tunnel runtime, captured in that runtime's fatal callback, stored only when the tunnel becomes current, required to match before destructive failure handling/publication, and cleared on teardown.

Consequence: **2. stale destructive effect**, plus **3. stale publication / UI lies**. No duplicate command effect is claimed.

Review note: the run emits an existing Swift 6.2 Sendable warning in the managed-cloud refresh path; the candidate does not introduce that capture.

## Cloud CLI Unix-socket ownership — target-executed repaired candidate

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

### Review defect and repair

The first lifetime-lock implementation serialized A/B ownership and passed the overlap regression, but it opened the predictable `<socket>.lock` path with plain `os.OpenFile`. That followed symlinks and did not establish regular-file type, link count, owner, or nonblocking behavior before `flock`. Review therefore invalidated that earlier green candidate.

The rewritten exact-current chain is:

```text
6044a8b3f43152d2e6fc17f771fd4b277b393118
  -> 3fcfdc334a2459ea353dc6316d5325be48a20e40  RED tests only
  -> 2df7cd900dd038bdd18b4c7c35dcd809878f1344  GREEN hardened lock
```

RED covers:

- overlapping B cannot replace live A;
- a symlinked lock pathname is rejected without touching its target;
- a FIFO lock is rejected without blocking before type validation;
- a hard-linked lock is rejected without chmod side effects;
- a single-link lock owned by the effective UID is migrated to mode `0600`.

GREEN opens the lock with `O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC`, validates regular-file type, single link, effective-UID ownership and private mode through the opened descriptor, then acquires nonblocking `flock`. The lock remains held until listener cleanup removes the retiring socket pathname.

Execution run `33560606934`, job `100031891608`, completed successfully on Ubuntu 24.04.4 / Go 1.24.13:

- ancestry and red-only diff fence: PASS;
- all five RED tests failed separately at their exact distinguishing markers;
- combined GREEN hardened regression set: **25 consecutive passes**;
- `cmuxd-remote` cross-build: Darwin arm64 PASS, Darwin amd64 PASS, Linux arm64 PASS, Linux amd64 PASS;
- Darwin arm64 Go test target cross-compile: PASS;
- full `daemon/remote` `go test ./...`: PASS.

Evidence class: **`target-executed`**. Exact receipt: `cloud-cli-execution-receipt-33560606934.md`. Review history: `cloud-cli-lock-review.md`.

Fresh read-only issue/PR searches found no exact-mechanism upstream work. Earlier ownership-only runs remain historical mechanism evidence and are superseded for candidate acceptance by this hardened receipt.

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

## Current gate

1. Keep proxy PR #6 and cloud PR #10 fixed at the exact target-executed heads above; any head movement invalidates the reviewed execution coordinates.
2. Deterministic self-review is complete, including the cloud lock-path repair. Consequential ownership changes still require independent complete-diff final review before a human-facing upstream submission decision.
3. Upstream remains read-only. A human-facing packet may be prepared, but any upstream issue/PR/comment requires a fresh bounded human greenlight for that exact interaction.
4. If scouting continues before submission review, NativeSSH/control-master reachability is the leading unresolved adjacent seam.

Third-party upstream remained read-only throughout these fork operations.
