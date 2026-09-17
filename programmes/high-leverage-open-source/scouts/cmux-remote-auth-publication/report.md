# cmux remote authorization publication and lease-rotation scout

Date: 2026-09-01  
Issue: #929  
Programme: #114 / high-leverage-open-source  
Target: `manaflow-ai/cmux`  
Worker: `chatgpt:gpt-5.6-sol`  
Claim scope: mechanism / interface / recovery  
Upstream contact authorized: `false`

## In simple words

cmux's legacy cloud WebSocket daemon stores attach authorization in fixed files under `/tmp/cmux`. A single-use PTY connection reads one lease, authenticates it, then removes the pathname. The admin installer can replace that same pathname at the same time because installation does not participate in the consumer mutex.

That produces a concrete stale-owner failure:

```text
lease A at path
  -> consumer locks, reads A, authenticates A
  -> installer writes replacement B to the same path
  -> old consumer removes the path while finishing A
  -> B is gone
```

The current publisher also truncates files in place, so readers can see an empty file during replacement. A successful admin install publishes PTY auth, RPC auth, and RPC-client metadata as three separate writes, so interruption or concurrent installs can leave a mixed authorization set.

The smallest source-level defect is the stale single-use deletion race. A copied-function Go probe pauses immediately before the production `os.Remove`, proves B exists byte-for-byte, releases A, and observes the pathname disappear. The negative control lets A settle first and then publishes B; B survives byte-for-byte.

## Exact source state

Pinned upstream `main`: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Resolved and rechecked: 2026-09-01  
Commit time: 2026-09-01T18:12:25Z  
Repository: https://github.com/manaflow-ai/cmux

The first source pass used `eaa899cb20bd411019744fbd2bdedeb397f3070b`. Before retention, `main` advanced by six commits. GitHub compare from that first pin to `8ef183f1...` changes only:

- `cmux-tui/crates/cmux-tui/src/app.rs`
- `cmux-tui/crates/cmux-tui/src/ui/mod.rs`

The relevant source blobs stayed byte-identical across that advance:

- `daemon/remote/cmd/cmuxd-remote/ws_pty.go`: `cbf6bb9c7053df86c1c1b166f482fef3ce5c92d1`
- `web/services/vms/drivers/freestyle.ts`: `b75b662f57e0a69b8c88fea2327c52e3af878a33`
- `web/services/vms/drivers/wsLease.ts`: `8eda593f43958e1bc3ff67cd9ab6953043e9ac17`

Upstream remained read-only. No issue, pull request, comment, review, reaction, label, branch, or other mutation was made in `manaflow-ai/cmux`.

## Invariant

**Installing a new authorization generation must preserve that generation as a complete, readable authorization. Work belonging to an older generation must never consume or delete the replacement.**

For a logical PTY + RPC + RPC-client installation, readers should observe one coherent generation. Failure before the commit point should leave the prior coherent generation available; success should leave the new coherent generation available.

## Operation owners and authority boundary

| Operation | Owner | Durable effect / observation | Synchronization |
| --- | --- | --- | --- |
| Mint PTY and RPC credentials | `web/services/vms/drivers/wsLease.ts` + Freestyle provider | random raw token/session; daemon lease stores token SHA-256 | caller-local only |
| Admin install | `handleWebSocketLeaseInstall` in `ws_pty.go` | PTY lease, then RPC lease, then `/tmp/cmux/attach-rpc-client.json` | no `wsLeaseMu` |
| Lease write | `writeLeaseFile` -> `writeJSONFile` | `json.Marshal` + newline -> `os.WriteFile(path, ..., 0600)` | in-place pathname write |
| Legacy Freestyle PTY publication | `FreestyleProvider.openWebSocketPty` | shell `printf ... | base64 -d > <pty path>` | external shell write |
| Legacy Freestyle RPC publication | `openWebSocketPty` / `openReusableRpcDaemon` | RPC lease then RPC-client JSON using shell `>` | external shell writes joined with `&&` |
| PTY authentication | `handleWebSocketPTY` -> `consumeWebSocketLease` | reads PTY lease; removes pathname for `single_use` | `wsLeaseMu` across read/auth/remove |
| RPC authentication | `handleWebSocketRPC` -> `consumeWebSocketLease` | reads RPC lease | same `wsLeaseMu` |
| RPC credential reuse | `readReusableRpcLease` | requires RPC and client files nonempty; parses only client JSON | no shared daemon lock |
| Health state | `/healthz` | `os.Stat` of PTY lease path; missing path means locked | no shared daemon lock |

The installation authority boundary is the admin bearer-token SHA-256 or Ed25519 public key configured on the daemon. Once admin authentication succeeds, the handler has authority to publish VM-local PTY/RPC authorization. User PTY/RPC connections prove possession of a raw token; the daemon compares its SHA-256 to the lease file.

## File identities and generation model

`wsLease` contains `version`, `TokenSHA256`, `ExpiresAtUnix`, `SessionID`, and `SingleUse`. RPC-client metadata contains the raw `Token`, `SessionID`, and `ExpiresAtUnix`.

There is no shared authorization-generation ID across PTY lease, RPC lease, and RPC-client metadata. Freestyle mints PTY and RPC credentials independently, so their session IDs also differ during a normal admin-backed attach. File path plus lease version therefore cannot identify one logical three-artifact generation.

## Writers

### Daemon admin endpoint

`POST /admin/leases` accepts optional PTY lease, RPC lease, and RPC-client metadata. After admin authentication it writes:

```text
PTY lease
RPC lease
RPC-client metadata
```

Each successful write becomes a separate pathname update before the next write starts. An error returns immediately. Earlier writes stay in place. There is no set-level rollback or commit marker.

The HTTP server can serve `/admin/leases`, `/terminal`, and `/rpc` concurrently. The admin handler does not acquire `wsLeaseMu`.

### Freestyle legacy exec publisher

When the admin endpoint is unavailable, `openWebSocketPty` writes the PTY lease with shell redirection. When it needs a fresh reusable RPC credential, it appends RPC-lease and RPC-client redirections to the same `&&` command chain.

`openReusableRpcDaemon` has the same two-write RPC publication sequence. Shell `>` truncates the destination before writing replacement bytes. A failing command stops the remaining `&&` chain and leaves earlier writes in place.

Within the current legacy WebSocket path searches, these are the production writers found for the three authorization files. Current E2B, Daytona, and Blaxel providers use the newer `cmux-remote` session transport; Freestyle legacy machines retain the WebSocket lease route.

## Consumers

### PTY and RPC authentication

Both `/terminal` and `/rpc` call `consumeWebSocketLease`. One global `wsLeaseMu` serializes consumers with each other:

```go
wsLeaseMu.Lock()
data := os.ReadFile(path)
json.Unmarshal(data, &lease)
authenticate(lease, presentedToken)
if lease.SingleUse {
    os.Remove(path)
}
wsLeaseMu.Unlock()
```

The consumer authenticates values read from one file image, then removes by pathname. The removal carries no generation or inode identity check.

### RPC-client reuse

Freestyle's `readReusableRpcLease` executes:

```text
test -s <rpc lease path>
test -s /tmp/cmux/attach-rpc-client.json
cat /tmp/cmux/attach-rpc-client.json
```

It parses client metadata and checks its fields and expiry. It never parses the RPC lease or checks that `SHA256(client.token)`, session ID, or a generation identity matches the durable RPC lease.

A surviving `RPC=B / client=A` pair can therefore be returned as reusable A metadata and then rejected by the daemon enforcing B.

## Synchronization and publication

The consumer mutex protects consumer-versus-consumer races only. Neither production publisher participates in it.

`os.WriteFile` replaces an existing regular file in place: the open-for-write path truncates before the replacement write completes. The legacy shell `>` path has the same property. Neither path uses a temporary sibling followed by rename.

The three admin artifacts also lack a group commit point. Per-file atomicity, if added alone, still permits a PTY file from X to coexist with RPC/client files from Y.

## Smallest failure sequence

The stale deletion race is the smallest established violation:

```text
1. path contains single-use lease A
2. consumer acquires wsLeaseMu
3. consumer reads A and authenticates token A
4. consumer pauses immediately before os.Remove(path)
5. admin writer, outside wsLeaseMu, writes complete lease B to path
6. inspection reads complete B bytes from path
7. consumer resumes and executes os.Remove(path) as cleanup for A
8. consumer returns success for A
9. path is absent; B was deleted by work belonging to A
```

No malformed input, crash, or write failure is required.

## Distinguishing probes

Retained runner: `artifacts/lease_race_test.go`  
Raw output: `artifacts/harness-results.txt`  
Manifest: `artifacts/EVIDENCE.txt`

Command:

```sh
GO111MODULE=off go test -v -count=1 ./...
```

Environment: `go1.23.2 linux/amd64`; upstream daemon module declares Go 1.22.

The probe copies the relevant lease types and functions from the pinned source. The stale-delete test adds one hook immediately before the production `os.Remove`; read, parse, token comparison, locking, and removal follow the copied source.

### Old A removes replacement B

Immediately before releasing A, the pathname contained complete B JSON bytes. After A resumed, the pathname was absent. **Invariant violated.**

### Negative control

A consumed and removed its own pathname first. B was then published. B remained and its bytes matched the expected serialization byte-for-byte.

### Reader racing in-place publication

A reader repeatedly called `os.ReadFile` while the writer alternated valid leases through the copied `writeJSONFile` path. Last retained run observed:

```text
invalid reads=20
empty reads=20
first invalid length=0
```

The empty image becomes `errWSLeaseForbidden` in `consumeWebSocketLease` because JSON parsing fails.

Atomic-rename control: **0 invalid JSON reads during 20,000 replacements.**

### Failure after first artifact

Starting from `PTY=A / RPC=A / client=A`, PTY B publishes and the RPC write is forced to fail. Surviving state is:

```text
PTY=B
RPC=A
client=A
```

No rollback restores PTY A.

### Failure after second artifact

Starting from A/A/A, PTY B and RPC B publish and the client write is forced to fail. Surviving state is:

```text
PTY=B
RPC=B
client=A
```

A fresh reuse read selects client A; fresh daemon-style RPC authentication rejects it against RPC B.

### Concurrent X/Y installs

Two unmodified three-write helpers ran concurrently with independently recognizable credentials. The retained run reached:

```text
PTY=X
RPC=Y
client=Y
```

at iteration 5. Every surviving file contained valid JSON, but the set belonged to two installs.

A second probe used temp-file + atomic rename for each artifact independently and still reached `PTY=X / RPC=Y / client=Y`.

### Repair discriminators

Atomic rename alone left the stale-delete race intact: B was atomically renamed into the canonical pathname, then old A removed that canonical pathname.

A writer taking the same `wsLeaseMu` as the old consumer waited for A to settle and then published B; B survived.

## Restart behavior

Lease authorization is read from disk at connection authentication time; the daemon does not preload a durable generation into an in-memory owner. The retained interruption probes therefore model the persistent-state side of restart by discarding operation-local state, re-reading surviving files, and making a fresh auth/reuse decision.

An actual `cmuxd-remote` process restart was **not executed** in this run. Process-level restart remains a hardening step for any candidate repair. A same-VM service restart ordinarily leaves `/tmp/cmux` available; VM reboot/replacement lifetime belongs to adjacent scout #927.

## Concurrent install behavior

The daemon's `net/http` handler permits admin requests to overlap. With no install mutex, each request owns only its next file write. The harness found a mixed final set under the ordinary scheduler without an explicit interleaving hook.

## Revocation behavior

PTY revocation is consumption: successful single-use authentication removes its pathname. That removal lacks generation identity, producing the stale-delete defect.

RPC rotation overwrites the reusable RPC lease file. That invalidates the old raw token for future RPC connection authentication. An RPC WebSocket connection that already passed authentication continues under its established connection; the lease file is not rechecked for every RPC request.

The `/admin/leases` path has no delete/revoke operation. Reusable RPC credentials otherwise age out by expiry, replacement, or destruction of the enclosing VM.

## Observed surviving state

| Probe | Final state | Evidence |
| --- | --- | --- |
| old A paused, B published, A released | PTY pathname absent | model-executed |
| negative control | complete B bytes | model-executed |
| in-place replacement race | transient zero-byte reads | model-executed |
| failure after PTY | B / A / A | model-executed |
| failure after RPC | B / B / A | model-executed |
| concurrent X/Y install | X / Y / Y in retained run | model-executed |
| per-file atomic X/Y install | X / Y / Y in retained run | model-executed |
| atomic rename read control | 0 malformed reads / 20,000 replacements | model-executed |
| shared-lock stale-delete control | complete B survives | model-executed |

## Consequence

Established at mechanism/interface scope:

1. A complete replacement write can be deleted by an older authenticated PTY consumer.
2. A reader can reject a credential during the truncate window while complete valid bytes exist immediately before and after it.
3. Interrupted multi-artifact installation can persist a split authorization set.
4. Concurrent installers can finish with individually valid files from different credential generations.
5. `RPC=B / client=A` can be selected as reusable A metadata and then rejected by the daemon.

Freestyle mints the credentials returned to its caller before publishing them. On the admin-backed path it sends PTY, RPC, and RPC-client data in one request and expects a successful response to install that credential set. The daemon has no generation-level durable commit point for that caller-visible operation.

No live Freestyle VM was used in this run, so production frequency and incident prevalence remain `Unknown`.

## Repair boundary comparison

### Shared locking

Acquire the same daemon lock for the full admin install and lease consumption.

Provides:

- A settles before B publication, or B publication wins before a consumer reads;
- daemon admin installs serialize with PTY/RPC consumers;
- if held across PTY/RPC/client writes, concurrent daemon admin installs finish wholly X or wholly Y at process-concurrency scope.

Leaves open:

- Freestyle's shell writer bypasses a Go-process mutex;
- process death or a later write error can still leave B/A/A or B/B/A;
- RPC-client readers outside the daemon do not share the mutex;
- in-place writes remain visible to readers outside the mutex.

The shared-lock control leaves B intact after A settles.

### Temp file + atomic rename per artifact

Provides complete old or complete new bytes for one pathname. The read control produced zero malformed JSON reads in 20,000 replacements.

Leaves open stale deletion: old A still removes canonical pathname B after B is renamed into place. It also leaves cross-artifact mixing and interruption between independent renames.

### Generation-qualified filenames

Example:

```text
leases/<generation>/pty.json
leases/<generation>/rpc.json
leases/<generation>/rpc-client.json
current -> <generation>
```

When a consumer retains the selected generation identity, A cleanup can target A's PTY artifact while B remains untouched, and cross-file correlation becomes explicit. This still needs one atomic selector/manifest commit.

### Transactional/bundled publication

Stage every artifact for generation G, validate the complete set, then atomically switch one current-generation manifest/pointer to G.

This can make restart observe the old complete generation or the new complete generation, keep concurrent installs coherent, and let RPC-client metadata verify the same generation as daemon auth. Single-use PTY consumption still needs generation-aware cleanup so consuming PTY G does not revoke reusable RPC G.

## Smallest repair versus full invariant

For the two smallest proven daemon races, a narrow candidate can:

1. serialize `/admin/leases` against `consumeWebSocketLease`; and
2. publish each file through a temporary sibling plus atomic rename.

That combination closes stale deletion for daemon-admin writes through serialization and closes torn reads for readers outside the mutex.

It does not provide crash-consistent PTY/RPC/client publication. The full invariant reaches the authorization-generation boundary: explicit generation identity plus one atomic commit point for the logical set.

A broad redesign should wait until a target-native regression captures the smallest stale-delete proof and the product decides whether PTY + RPC + RPC-client are contractually one generation. Current Freestyle admin usage strongly treats them as one operation; the on-disk schema does not encode that contract.

## Failed hypotheses and negative results

- **Atomic rename alone fixes stale deletion:** disproved; old A still deletes canonical B.
- **Per-file atomic rename makes the three-artifact install coherent:** disproved; concurrent X/Y still mixed.
- **The consumer mutex already protects replacement:** disproved; publishers do not acquire it.
- **The first source pin became stale in this area when main advanced:** disproved by compare and identical relevant blobs.
- **A fully settled A threatens later B:** the negative control disproved this; B survives when publication begins after A's remove completes.

## Evidence labels and limits

**source-read**

- current upstream handler, writer, consumer, lease schema, Freestyle publisher, and reuse reader;
- exact current revision and relevant blob identities;
- source continuity from the earlier pin.

**model-executed**

- stale deletion and negative control;
- in-place torn read and atomic-rename control;
- first/second artifact failure injection;
- concurrent X/Y installs;
- atomic-rename-only and shared-lock repair discriminators.

**Unknown / unexecuted**

- actual daemon-process restart after each interruption point;
- target-native `go test` inside a complete upstream checkout;
- live Freestyle VM interleavings;
- filesystem-specific rates outside the retained Linux environment;
- production frequency or observed user incidents.

The harness copies the exact low-level source needed for the invariant and adds one explicit pause hook before `os.Remove`. It does not claim target-native execution.

## Branch candidates

1. **Focused regression / repair candidate:** target-native deterministic test for old A authenticating, B installing, then A finishing. First candidate boundary: shared install/consume serialization plus atomic file replacement. Keep the multi-artifact limitation explicit.
2. **Generation-commit campaign:** decide and encode whether PTY, RPC, and RPC-client metadata form one logical generation. If yes, stage generation-qualified artifacts and atomically publish one generation selector; cross-check client metadata against that identity.
3. **Legacy external-writer cleanup:** route all Freestyle legacy publication through one publication owner or give the external writer the same generation/atomic protocol. A Go mutex cannot protect shell `>`.
4. **Restart hardening:** execute actual `cmuxd-remote` restart after each interrupted state and verify old/new generation selection before widening recovery claims.

Recommendation: **retain this as a finding and promote the stale-delete/file-publication repair as the first bounded candidate; keep multi-artifact transactional publication as a separate decision-bearing branch.**

## Exact reopen trigger

Refresh this scout when any of these occurs:

- `daemon/remote/cmd/cmuxd-remote/ws_pty.go` changes from blob `cbf6bb9c7053df86c1c1b166f482fef3ce5c92d1`;
- `web/services/vms/drivers/freestyle.ts` changes from `b75b662f57e0a69b8c88fea2327c52e3af878a33`;
- `web/services/vms/drivers/wsLease.ts` changes from `8eda593f43958e1bc3ff67cd9ab6953043e9ac17`;
- Freestyle legacy machines stop using `cmuxd-remote serve --ws` and these lease files;
- a target-native regression identifies a different owner than the copied-function model;
- a generation/manifest/compare-before-delete mechanism appears in the active path;
- a real process restart contradicts the persisted-state model.

Adjacent scout #927 owns broader persistent-generation compatibility across restart, upgrade/downgrade, daemon identity, and cloud lifecycle. This report owns the narrower legacy WebSocket authorization publication/rotation boundary.
