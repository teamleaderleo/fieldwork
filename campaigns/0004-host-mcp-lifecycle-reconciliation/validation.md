# Host and MCP Lifecycle Reconciliation Validation

## Evidence summary

Campaign #84 currently rests on four different evidence classes. They must remain separate.

### Target-executed owned Codex reconnect primitive

Owned draft: `teamleaderleo/codex#5`

Passing focused checks:

```text
cargo fmt --all -- --check
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
just test -p codex-mcp reconciliation_reuses_connection_without_relisting_regular_tools
```

Supported conclusion:

- explicit host MCP configuration reload can request a fresh ready client;
- ordinary reconciliation retains the existing unchanged-client reuse behavior.

Missing proof:

- generation ownership;
- catalogue replacement;
- accepted-current publication;
- request authority;
- timeout and active-call interaction.

### Target-executed Rust SDK relist ordering

Pinned dependency revision: `cb50ae7890d8a5daacae1a4ad95f395f06733c07`

Observed:

```text
sdk_cache=catalogue_c
naive_application=catalogue_b
ticketed_application=catalogue_c
requests=3
```

Supported conclusion:

- the SDK cache rejects an older late write;
- an older successful callback result can still be published by application code;
- application publication needs its own accepted-current decision.

Rust MCP SDK 3.0.1 does not alter this result. Its release changes authentication resource selection, protocol-header handling, stateless initialize negotiation, and graceful subscription metadata.

### Target-executed public Codex schema transition

Public Codex revision: `a5082373f18119dc5d3eb993267c97f37880935d`

- workflow run: `30488803287`;
- job: `90701186402`;
- artifact: `8739076993`;
- digest: `sha256:f759a6b2e0a75bd8b2e2cfb8ef23c42a9d5e4e259473ae121a3b7614089e3148`.

Observed:

```text
A advertises echo(message: string)
→ model emits {"message":"hello"}
→ B exposes echo(count: integer)
→ current dispatch invokes B
→ B rejects the A-shaped arguments
→ Codex returns B's error
```

Supported conclusion:

- current Codex does not compare A and B before invocation;
- the server parser, rather than Codex, contained this particular mismatch.

Classification: `advertisement_execution_revision_mismatch`.

### Adjacent target-executed Codex timeout behavior

Fieldwork #134 and owned Codex PR #22 exercise the real Codex MCP client.

Current legacy result:

```text
caller reports timeout
MCP cancellation is not observed
server mutation completes later
follow-up request remains usable
```

Supported conclusion:

- a local timeout is not remote terminal evidence;
- persisting the timeout output does not prove the operation stopped;
- a refresh may occur while the original operation remains live.

The expanded timeout comparison workflow at owned Codex head `7b1a5f8bf71de0df169b1eae83d3eaa43da2f315` was queued at the latest observation. Native-timeout, pause-aware explicit-cancel, cancellation-failure, ignored-cancellation, and modern transport conclusions remain pending that retained execution.

## Merged Campaign #83 prerequisites

Campaign #83 has now merged the relevant shared owner and direct evidence paths:

- canonical session-scoped receipt ownership;
- selected runtime effect before dispatch;
- certain pre-dispatch failure closure;
- authoritative direct result persistence;
- ambiguity after persistence failure or conflicting observations.

Campaign #84 must reuse those receipts. It needs one additional typed dimension for post-dispatch execution certainty, such as confirmed terminal versus `MayStillRun`.

## Next validation gates

1. **Generation-bound publication** — older refresh or relist completion cannot publish after a newer accepted result.
2. **Captured call authority** — prepared A stays on A; current B may tighten policy but cannot relax or reroute.
3. **Cached late binding** — equality is checked before rewrite, approval, or execution.
4. **Cancellation delivery** — distinguish requested, delivered, remotely observed, ignored, failed, and unknown.
5. **Modern transport terminal state** — split stateless one-shot closure from stateful or resumable disconnect.
6. **Timed-out A during B publication** — late results and all receipts remain attached to A.
7. **Mutation retry control** — session recovery and fallback do not replay an uncertain mutation.
8. **Host reconstruction** — preserve, replace, clear, and reject behavior across resume and fork.

## Decision

The mapping phase has produced a coherent implementation direction. Do not add another independent lifecycle ledger or another generic refresh boolean.

The next accepted source work should connect:

- Campaign #83's operation receipt;
- a typed execution-certainty result from the timeout work;
- Campaign #84's generation and A/B authority decisions.

Public Codex and the official Rust MCP SDK remain read-only.
