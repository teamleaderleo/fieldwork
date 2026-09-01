# cmux stale-generation candidate self-review

## In simple words

The scout has two consequential owned-fork candidates. Both have deterministic test-only RED commits, bounded GREEN repairs, target-native execution, negative controls, and clean complete diffs. A first cloud-lock repair was rejected during self-review and replaced with the current descriptor-hardened version.

Upstream advanced after the execution runs from `6044a8b3f43152d2e6fc17f771fd4b277b393118` to `594eb0461e0ae4d57a99180e19097cea5e5091e0`. The two intervening commits touch browser-skill and `cmux-tui` client files only. The upstream owner files for both findings are byte-identical across that movement, so the executed behavioral evidence remains applicable within this explicit fence. The owned-fork PRs still require a final restack onto then-current upstream before a human-facing submission packet can be treated as current.

Disposition: **HOLD for human-facing upstream submission**. Clearing conditions: final independent complete-diff review, then final restack/current-head validation. No second-model review was launched because cmux requires explicit user opt-in for that step.

Upstream contact authorized: `false`.

## Reviewed inputs

### Proxy candidate

Canonical fork PR: `teamleaderleo/cmux#6`

```text
base   6044a8b3f43152d2e6fc17f771fd4b277b393118
RED    e9ea500cebfba753444e961e2ef9d6af079ec096
GREEN  8daa014321001d9aec128a9112720fb74e2ae11d
```

Complete diff:

- `Packages/macOS/CmuxRemoteWorkspace/Tests/CmuxRemoteWorkspaceTests/RemoteProxyBrokerStaleGenerationTests.swift` — regression only;
- `Packages/macOS/CmuxRemoteWorkspace/Sources/CmuxRemoteWorkspace/Broker/RemoteProxyBroker.swift` — +one runtime-generation field, generation capture/match, teardown clear.

Execution: run `33554543666`, job `100012026075`; RED fails for the stale-owner assertion, GREEN passes, current-owner fatal restart passes, full package passes 95 tests in 18 suites.

No unrelated cleanup appears in the candidate diff.

### Cloud CLI candidate

Canonical fork PR: `teamleaderleo/cmux#10`

```text
base   6044a8b3f43152d2e6fc17f771fd4b277b393118
RED    3fcfdc334a2459ea353dc6316d5325be48a20e40
GREEN  2df7cd900dd038bdd18b4c7c35dcd809878f1344
```

Complete diff:

- `daemon/remote/cmd/cmuxd-remote/cloud_cli_bridge_generation_test.go` — five regression/negative-control cases;
- `daemon/remote/cmd/cmuxd-remote/cloud_cli_bridge.go` — lifetime lock plus descriptor hardening.

Execution: run `33560606934`, job `100031891608`; five separate RED markers proven; combined GREEN set passes 25 times; Darwin/Linux arm64+amd64 builds pass; Darwin arm64 test target cross-compiles; full `daemon/remote` package passes.

The first candidate that used plain `os.OpenFile` on the lock path was rejected during this same lane. The retained GREEN uses `O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC`, descriptor `fstat`, single-link/UID/private-mode checks, then `flock`.

No unrelated cleanup appears in the current candidate diff.

## Upstream movement after execution

Latest upstream checked during this review:

`594eb0461e0ae4d57a99180e19097cea5e5091e0`

Compared with executed base `6044a8b3f43152d2e6fc17f771fd4b277b393118`, upstream is two commits ahead. Changed paths are limited to browser-skill workflow/docs/tests and `cmux-tui/crates/cmux-remote/src/client.rs`.

The exact upstream owner blobs remain unchanged:

- `RemoteProxyBroker.swift`: `efdb05374e725727efd346684e5cc0ff1d15cb76` at both executed base and latest checked upstream;
- `cloud_cli_bridge.go`: `299d90d1ae1b440146670a7f490ea37390a95ec5` at both executed base and latest checked upstream.

Neither package manifest nor candidate test/support path changed in the intervening compare. This preserves the executed result as source-continuous evidence; it does not turn the old fork base into the latest upstream coordinate.

## Competing explanations rechecked

### Proxy

- "The callback is one-shot, therefore safe" — rejected. One queued A callback is sufficient.
- "The callback can only stop A" — rejected by target-native RED: B becomes current and is removed.
- "A current-owner failure would be suppressed by the generation fence" — rejected by the passing current-owner restart control.

### Cloud CLI

- "A's listener close only affects A's file descriptor" — incomplete. Unix pathname unlink is independent of B's listener descriptor; original model showed B surviving unreachable.
- "Already serialized by normal systemd restart" — ordinary service restart reduces overlap but does not make the machine-global bridge self-owning; overlapping RPC-enabled daemon instances were accepted by source before the repair.
- "Any flock file is enough" — rejected during self-review because the first predictable lock path followed symlinks and lacked FIFO/hard-link/owner semantics.

## Negative controls

- Remote PTY attachment replacement: expected handoff semantics; accepted A bytes may drain, fresh stale A input/resize/detach are fenced.
- Workspace/session controller replacement: serialized cleanup and controller/process/token identity fences.
- Same-object `RemoteDaemonRPCClient` termination: isolated seam; production replacement uses fresh one-shot client/tunnel instances.
- NativeSSH ControlMaster: local retain bookkeeping can transiently disagree with cross-process ownership, but foreground handoff, coordinator startup, and cleanup each recheck authority before consequence-producing use. Recorded separately as a negative result.

## Evidence limits

The proxy repair has target-native macOS package execution. The cloud repair has target-native Linux execution plus Darwin/Linux cross-build coverage; it does not have a Darwin runtime test because the contested socket/lock semantics were executed on Linux and Darwin compilation was the practical owned-fork gate used here.

Neither candidate has independent final review. Neither candidate is rebased onto `594eb046…`; source continuity is proven instead. Any final upstream packet should restack onto then-current upstream, recheck the full diff, and rerun the smallest relevant gates if restack changes a reviewed input.

No upstream issue, PR, comment, review, reaction, branch, or file was mutated during this scout.
