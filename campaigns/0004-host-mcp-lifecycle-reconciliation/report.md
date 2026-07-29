# Host and MCP Lifecycle Reconciliation Report

## In simple words

Codex has two refresh meanings that currently overlap.

Ordinary runtime reconciliation is optimized to reuse an unchanged ready MCP connection. That contract has an explicit regression test: refreshing desired state with the same connection configuration should avoid another `tools/list` request.

A host MCP config reload is a stronger user-facing action. It loads a new config snapshot, installs the MCP inputs into every thread, marks each runtime dirty, and schedules prewarming. At the inspected revision, the public `CodexThread::refresh_mcp_config` entrypoint does not request a fresh connection before that publication. A remote server at the same endpoint can therefore keep the client, server identity, and tool catalogue captured at startup.

The first candidate draws a narrow boundary: explicit host config reload requests reconnect; ordinary per-turn reconciliation continues to reuse its connection.

## Assignment

- Fieldwork campaign: #84
- Parent research campaign: #31
- Programme: #14
- Target hub: #8
- Owned Fieldwork path: `campaigns/0004-host-mcp-lifecycle-reconciliation/`
- Owned Codex branch: `fieldwork/31-mcp-config-reload-reconnect`
- Owned draft Codex PR: `teamleaderleo/codex#5`
- Owned fork base: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Claim scope for this stage: mechanism and interface
- Upstream contact authorized: `false`

## Evidence inherited

### L01 lifecycle provenance

Saved host dynamic tools and selected capability roots can remain thread-scoped across cold reconstruction. Public resume and fork inputs do not expose an equivalent current-host replacement field. Host preserve, replace, clear, and reject behavior therefore requires an explicit contract.

### L04 MCP and app catalogue convergence

The retained stable-endpoint fixture changes a local MCP-shaped server from one stub tool to a different real catalogue. Ordinary refresh with unchanged connection configuration reuses the ready client and its startup catalogue. Router registration and model advertisement stay mutually consistent with that stale binding. Fresh thread, reconnect, restart, and connection-identity change converge.

### L06 effective-surface diagnostics

A stale-binding receipt needs both tool-set and server-identity or provenance digests. Tool names alone miss identity-only changes. Diagnostics remain observational and separate from repair.

## Public source map

### Host-facing config reload

`codex-rs/app-server/src/mcp_refresh.rs`

- loads the latest configuration;
- resolves a thread-specific refresh snapshot;
- calls `CodexThread::refresh_mcp_config` for each active thread.

`codex-rs/core/src/codex_thread.rs`

- exposes `refresh_mcp_config` as the public host-facing MCP-only reload;
- delegates to the session at the inspected revision;
- does not request reconnect.

`codex-rs/core/src/session/mod.rs`

- applies only MCP-related config inputs;
- marks the thread MCP runtime dirty;
- schedules MCP prewarming.

### Ordinary runtime publication

`codex-rs/core/src/session/mcp.rs`

- claims pending refresh work;
- recomputes current desired MCP state and projection;
- publishes into the thread-owned runtime;
- loops when another invalidation arrives during publication.

`codex-rs/codex-mcp/src/runtime.rs`

- `replace` reuses prior connections unless the reconnect flag was claimed;
- `reconnect_on_next_refresh` forces the next publication to start fresh connections;
- existing request-scoped bindings retain their exact captured connections.

`codex-rs/codex-mcp/src/connection_manager_tests.rs`

- `reconciliation_reuses_connection_without_relisting_regular_tools` protects ordinary reuse and avoids a blocking relist.

### Explicit reconnect operation

`codex-rs/core/src/session/handlers.rs`

- `Op::RefreshMcpServers` calls `reconnect_on_next_refresh`;
- then requests MCP runtime refresh.

This establishes a source precedent: an explicit refresh action may request fresh connections while ordinary reconciliation remains reusable.

## First candidate

Change `CodexThread::refresh_mcp_config` to request reconnect before applying the caller-supplied MCP config:

```rust
pub async fn refresh_mcp_config(&self, next_config: crate::config::Config) {
    self.session
        .services
        .mcp_runtime
        .reconnect_on_next_refresh();
    self.session.refresh_mcp_config(next_config).await;
}
```

### Intended effect

- app-server MCP config reload produces a fresh client for each enabled configured server;
- startup negotiation and tool listing run again at the stable endpoint;
- the new publication receives current remote identity and catalogue;
- older captured request bindings retain their exact client and authority;
- future steps capture the new binding;
- ordinary per-turn reconciliation retains the established reuse contract.

### Deliberate exclusions

- no live relist on a reused connection;
- no server identity or catalogue digest comparison yet;
- no catalogue revision field yet;
- no host reconstruction policy yet;
- no automatic repair from diagnostic receipts;
- no fallback rerouting;
- no change to request-scoped router/model consistency.

## Focused source-native regression

The existing Apps MCP test server has an initialization counter and a stable endpoint. The candidate regression:

1. starts a thread with the Apps MCP server;
2. waits until the server is ready;
3. records initialization attempts;
4. calls `CodexThread::refresh_mcp_config` with the current config;
5. requires one additional initialization attempt within five seconds.

This tests fresh-client behavior directly. It does not rely on tool-name output or model behavior.

The existing connection-manager regression remains unchanged and continues to prove that ordinary reconciliation can reuse a ready connection without relisting regular tools.

## Validation commands

Run from `codex-rs/`:

```bash
cargo fmt --all
cargo fmt --all -- --check
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
just test -p codex-core
just test -p codex-app-server
```

The owned CI runner also installs `cargo-nextest`, which the repository `just test` recipe requires.

## Validation history

### Repository-wide formatter attempt

The first ephemeral run applied the Rust candidate and then invoked the repository-wide formatter. That command reached unrelated Python and Bazel formatters and stopped because `uv` and `dotslash` were unavailable. No Rust test ran. The branch retained only the temporary workflow.

### Rust-only formatter attempt

The second ephemeral run applied the same source candidate and regression. Rust formatting passed. The focused test command stopped before compilation because `cargo-nextest` was unavailable. No source commit was created.

### Current attempt

The third run preserves the same candidate and regression, installs `cargo-nextest`, and runs the focused and scoped suites. The temporary workflow deletes itself and commits the source only after every command succeeds.

## Tool-list-change notification finding

The current MCP client service forwards server notifications to `LoggingClientHandler`. Its `on_tool_list_changed` implementation records a log entry and returns. Codex does not translate the signal into a thread-owned relist request, accepted catalogue revision, or new runtime publication.

The RMCP client already exposes a typed `list_tools` operation. The missing work belongs above that primitive:

- identify the server and current client generation;
- request a relist;
- compute server identity and catalogue digests;
- reject late results from older generations;
- publish a new revision only after validation;
- preserve older request-scoped bindings;
- provide a typed outcome for unchanged, replaced, failed, cancelled, or superseded refresh.

This notification path is the next independent #84 slice. It should remain separate from the host-config reconnect candidate because one is an explicit host action and the other is a server-originated live change.

## Competing candidates

### Reconnect every ordinary reconciliation

Rejected for this stage. It removes the source-defined reuse optimization and adds startup latency to routine step capture.

### Relist every ordinary reconciliation

Rejected for this stage. The existing regression explicitly protects against a blocking regular-tools relist, and relisting alone does not validate server identity or update all retained application state.

### Add remote identity and catalogue digest to connection reuse identity

Promising larger candidate. It needs live or cached remote observations before reuse can be decided and must define failed-validation behavior.

### Host reload requests reconnect

Selected first slice. It uses an existing runtime control, matches the explicit refresh precedent, and leaves ordinary reconciliation unchanged.

## Risks and open questions

- Reconnecting every active thread during host config reload can be expensive when many threads share the same server.
- A reload using an unchanged config may still represent a deliberate catalogue freshness request; the candidate treats it that way.
- Failed reconnect publication needs a typed decision: retain old state, publish unavailable, or reject the reload.
- Concurrent host reload and tool-list-change notification require generation ordering.
- Apps-specific cache refresh and generic configured-MCP refresh have different current paths and should converge on one per-server outcome vocabulary.
- Host preserve, replace, clear, and reject semantics remain unresolved for cold resume and fork.

## Current conclusion

The stale catalogue behavior is partly intentional: ordinary reconciliation reuses ready connections by design. The defect candidate sits at the stronger host action. `refresh_mcp_config` currently looks like a reload boundary while permitting the old client catalogue to survive. A reconnect request at that entrypoint is the smallest coherent correction and now has a source-native regression under owned-fork validation.

The server-notification gap is separately source-confirmed: a tool-list-change signal is logged and discarded at the application boundary. Campaign #84 should pursue that after the host reload slice reaches a compiled result.
