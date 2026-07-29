# Host and MCP Lifecycle Reconciliation Report

## In simple words

Codex currently has several refresh boundaries with different meanings.

- Ordinary reconciliation deliberately reuses an unchanged ready MCP connection.
- Explicit host MCP config reload is a stronger freshness action and now has a compiled owned-fork candidate that requests fresh connections.
- A server tool-list-change notification reaches Codex but is only logged.
- Cached regular MCP tools may be advertised before the replacement server is ready; call dispatch can later resolve the same tool name through a newer live binding.
- The Rust SDK protects its own cache from late stale relist writes, but its public result does not protect an application's published catalogue.

Campaign #84 must give each boundary a generation, equality decision, publication outcome, and request-authority rule.

## Assignment

- Fieldwork campaign: #84
- Parent research campaign: #31
- Programme: #14
- Target hub: #8
- Owned Fieldwork path: `campaigns/0004-host-mcp-lifecycle-reconciliation/`
- Owned Codex branch: `fieldwork/31-mcp-config-reload-reconnect`
- Owned draft Codex PR: `teamleaderleo/codex#5`
- Owned fork base: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Current public Codex recheck: `85c082ccccf6b5ac4d6c31d14f960057348b78f4`
- Official Rust SDK pin: `cb50ae7890d8a5daacae1a4ad95f395f06733c07`
- Claim scope: mechanism, interface, and focused compiled behavior
- Upstream contact authorized: `false`

## Evidence inherited

### L01 lifecycle provenance

Saved host dynamic tools and selected capability roots can remain thread-scoped across cold reconstruction. Public resume and fork inputs do not expose current-host replace or clear fields. Host preserve, replace, clear, and reject behavior requires an explicit contract.

### L04 MCP catalogue convergence

Ordinary refresh with unchanged connection configuration can reuse the ready client and its startup catalogue. Fresh thread, explicit reconnect, restart, and changed connection identity converge. Recomputed desired inputs alone do not prove that a live binding learned a changed remote catalogue.

### L06 effective-surface diagnostics

Catalogue, binding, model advertisement, executable path, completion, and client delivery are separate observations. A valid loader can still use stale saved provenance or a stale catalogue.

## Public source map

### Host-facing config reload

`codex-rs/app-server/src/mcp_refresh.rs` loads the current configuration and calls `CodexThread::refresh_mcp_config` for active threads.

`codex-rs/core/src/codex_thread.rs` exposes that host-facing MCP-only reload.

At the owned-fork base it applied config and marked MCP state dirty without requesting fresh connections.

### Ordinary runtime publication

`codex-rs/core/src/session/mcp.rs` claims refresh work, recomputes desired state, and publishes through the thread-owned runtime.

`codex-rs/codex-mcp/src/runtime.rs` reuses prior connections unless reconnect is requested.

`reconciliation_reuses_connection_without_relisting_regular_tools` protects this low-latency ordinary reuse contract.

### Explicit reconnect operation

`Op::RefreshMcpServers` already requests reconnect before runtime refresh. This provides a source precedent for treating an explicit freshness action differently from routine reconciliation.

### Tool-list-change notification

The RMCP client receives `notifications/tools/list_changed`. The Codex logging handler records the event and returns. No Codex relist, remote identity check, catalogue digest, revision increment, or thread publication follows.

### Cached-startup late binding

Current Codex can advertise cached regular-MCP tools while a replacement optional client remains pending.

The sampling step and `McpHandler` retain catalogue A for:

- model schema and description;
- search metadata;
- hook identity;
- initial request tool registration.

At call time, core dispatch waits for server startup and asks the thread runtime for the latest binding B. B supplies:

- prepared call;
- current client and server metadata;
- current approval policy and permission profile;
- file-input rewrite metadata;
- execution and result.

The current path can therefore plan as A and execute as B.

## First owned Codex candidate

The bounded source change calls `reconnect_on_next_refresh()` before applying the host-supplied MCP config:

```rust
pub async fn refresh_mcp_config(&self, next_config: crate::config::Config) {
    self.session
        .services
        .mcp_runtime
        .reconnect_on_next_refresh();
    self.session.refresh_mcp_config(next_config).await;
}
```

### Compiled result

Passing:

```text
cargo fmt --all -- --check
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
just test -p codex-mcp reconciliation_reuses_connection_without_relisting_regular_tools
```

The candidate proves:

- host MCP config reload creates a fresh ready client at the stable test endpoint;
- ordinary reconciliation still reuses an unchanged ready client without relisting regular tools.

The source and regression are committed in owned Codex PR #5.

### Broader limits

- Full `codex-core` encountered unrelated sandbox-dependent failures.
- The app-server MCP filter stopped at an existing test initializer missing `ItemCompletedEvent.started_at_ms`.

These are retained as baseline limits rather than candidate failures.

### Why this is only the first slice

The reconnect request is a boolean. An older publication can consume a reconnect request intended for a newer desired-state generation. `concurrency.md` defines the adversarial sequence and a generation-bound replacement.

The candidate also does not address notification relist, remote identity, catalogue equality, request authority, cold reconstruction policy, or failed reconnect outcomes.

## Codex request-authority conflict

The source history contains a policy change that needs an explicit decision.

### PR #34588 — captured catalogue revision

This change introduced request-scoped MCP bindings and stated that a model-step tool call must not reroute to a replacement client or run against a catalogue revision the model did not see.

### PR #34930 — current runtime at dispatch

Runtime centralization changed core dispatch to refresh MCP state and obtain the current binding before approval and execution. Its description continued to promise immutable bindings for model steps and tool calls.

### PR #35590 — cached A, live B

This change intentionally advertises cached catalogue A before server startup, waits for the selected server, and then prepares the call against live B.

Its integration test proves:

- inference receives process A's cached description;
- the same tool name executes on process B;
- a tool absent from B fails closed.

It does not test same-name changes to schema, approval, annotations, visibility, file-input metadata, hook metadata, or behavior.

### Approval-relaxation consequence

An already-sampled step can capture prompt-required A. Before its tool call dispatches, thread configuration can change to permissive B. Current dispatch can refresh to B and auto-approve under B.

A later policy may tighten an in-flight call. It should not relax the authority under which the call was sampled.

### Candidate authority rule

For a prepared call captured by the sampling step:

- execute the captured client, tool metadata, and approval authority;
- fail on the captured client rather than rerouting;
- apply current policy only as an added restriction;
- defer relaxation until a newly sampled step.

For a cached tool with no captured prepared call:

- wait for live B only as a bounded exception;
- compare A and B authority fingerprints;
- execute B only when equality is verified;
- otherwise fail closed and require a new sampling step.

The fingerprint should cover server identity, tool name, schemas, authority-relevant annotations, visibility, file-input metadata, plugin or connector provenance, and approval/execution metadata.

## Compiled Rust SDK relist result

A focused fixture against the pinned official SDK used two real overlapping `on_tool_list_changed` callback relists over an in-process duplex transport.

Controlled order:

```text
R1 captures older generation and waits
→ second notification invalidates again
→ R2 returns catalogue C and publishes first
→ R1 returns catalogue B late
```

Observed:

```text
sdk_cache=catalogue_c
naive_application=catalogue_b
ticketed_application=catalogue_c
requests=3
```

One test passed; zero failed.

The SDK cache correctly retained C because its private generation rejected R1's late write. R1 still returned `Ok(B)` to application code, so a naive publisher rolled back from C to B. An application notification-generation ticket retained C.

The fixture, lockfile, exact log, and validation record are retained on L01 amendment PR #74 under `artifacts/rmcp-relist-ordering/`.

### SDK implication

Calling `list_tools` from every list-change callback is insufficient under concurrent notifications.

A generic opt-in SDK helper needs one of:

- public relist ticket plus accepted-current result;
- internal notification coalescing with newest-result publication;
- watch or stream containing only accepted catalogue snapshots.

The helper should not silently replace application approval policy, request bindings, or model advertisements. Codex still owns those decisions.

## Unified refresh ticket

Host reload, user reconnect, auth change, server notification, and recovery should use one ticket vocabulary.

A ticket should contain:

- desired-state generation;
- source reason;
- per-server reconnect or relist requirement;
- configured connection identity;
- observed remote server identity;
- advertised and live catalogue digests;
- approval/config authority digest;
- supersession state;
- typed result.

Typed results should include:

- `unchanged`;
- `replaced`;
- `failed_retained_old`;
- `failed_unavailable`;
- `cancelled`;
- `superseded`;
- `identity_mismatch`;
- `catalogue_mismatch`;
- `advertisement_execution_revision_mismatch`.

Only a result accepted for the relevant current generation may publish.

## Required compiled matrix

### Host generation ownership

Hold publication A before replacement, install B and request reconnect, release A, then prove B—not A—owns the fresh client.

### Notification relist ordering

Delay an older relist until after a newer one publishes. Prove only the accepted-current result changes the thread catalogue revision.

### Captured approval

Sample under prompt-required A, apply permissive B before dispatch, then prove the A call still prompts or fails. Reverse the policies and prove B may tighten the call.

### Cached A/live B

Test:

- removed tool;
- same name, changed schema;
- same name, changed approval or annotations;
- same name, changed file-input or provenance metadata;
- verified equal fingerprint.

### Failed refresh

Test old-state retention, unavailable publication, partial per-server success, cancellation, timeout, and later recovery.

### Host reconstruction

Test `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` for dynamic tools and selected roots across resume and fork.

## CI harness rule

For Rust-only owned-fork changes:

- use `cargo fmt --all -- --check` and focused package tests;
- install `cargo-nextest` before `just test` when required;
- use repository-wide `just fmt` only when the full formatter set, including `uv` and `dotslash`, is installed;
- classify missing tools as `harness_unavailable`;
- classify unrelated existing compile failures as `baseline_compile_blocker`.

## Current conclusion

The first host-reload source slice is valid and compiled, but it is not the complete repair.

The next Codex implementation step should introduce generation ownership and preserve captured request authority. Notification-driven relist should consume the compiled SDK lesson: cache freshness does not automatically provide application publication freshness.

Public Codex and the official Rust SDK remained read-only. No upstream contact occurred.