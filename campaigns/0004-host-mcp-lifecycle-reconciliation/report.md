# Host and MCP Lifecycle Reconciliation Report

## In simple words

Codex has several MCP lifecycle boundaries with different meanings.

- Ordinary reconciliation deliberately reuses an unchanged ready connection.
- Explicit host MCP config reload is a stronger freshness action and now has a compiled owned-fork candidate that requests fresh connections.
- A server tool-list-change notification reaches Codex but is only logged.
- Cached regular MCP tools may be advertised before a replacement server is ready; call dispatch can later resolve the same tool name through a newer live binding.
- The Rust SDK protects its own cache from late stale relist writes, but its public result does not protect an application's published catalogue.
- A Codex-style outer timeout can stop the local wait without sending MCP cancellation, leaving the server operation active while refresh or replacement continues.

Campaign #84 must give refresh, publication, call authority, and timed-out live work explicit generations, identities, outcomes, and ownership rules.

## Assignment

- Fieldwork campaign: #84
- Parent research campaign: #31
- Programme: #14
- Target hub: #8
- Owned Fieldwork path: `campaigns/0004-host-mcp-lifecycle-reconciliation/`
- Owned Codex branch: `fieldwork/31-mcp-config-reload-reconnect`
- Owned draft Codex PR: `teamleaderleo/codex#5`
- Owned fork base: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Public Codex schema-drift pin: `a5082373f18119dc5d3eb993267c97f37880935d`
- Official Rust SDK relist pin: `cb50ae7890d8a5daacae1a4ad95f395f06733c07`
- Claim scope: mechanism, interface, and focused compiled behavior
- Upstream contact authorized: `false`

## Evidence inherited

### L01 lifecycle provenance

Saved host dynamic tools and selected capability roots can remain thread-scoped across cold reconstruction. Public resume and fork inputs do not expose current-host replace or clear fields. Host preserve, replace, clear, and reject behavior requires an explicit contract.

### L04 MCP catalogue convergence

Ordinary refresh with unchanged connection configuration can reuse the ready client and its startup catalogue. Fresh thread, explicit reconnect, restart, and changed connection identity converge. Recomputed desired inputs alone do not prove that a live binding learned a changed remote catalogue.

### L06 effective-surface diagnostics

Catalogue, binding, model advertisement, executable path, completion, result persistence, client delivery, and display are separate observations.

### Campaign #83 operation receipts

Campaign #83 accepted a bounded session-scoped live receipt owner in owned Codex. It separates operation effect, terminal execution, authoritative result persistence, client delivery, and display. #84 should consume that owner for MCP call lifecycle evidence instead of inventing another receipt system.

### Scout #130 timeout ownership

A focused `rmcp 3.0.0` probe compared Codex-style outer timeout with the SDK's native request timeout.

```text
external outer timeout: cancellation=false, side effect completed=true
native SDK timeout:     cancellation=true,  side effect completed=false
```

Timeout mechanism remains owned by Scout #130/#131. Campaign #84 owns how a timed-out but still-live operation relates to captured binding A and a newer published binding B.

## Public source map

### Host-facing config reload

`codex-rs/app-server/src/mcp_refresh.rs` loads current configuration and calls `CodexThread::refresh_mcp_config` for active threads.

`codex-rs/core/src/codex_thread.rs` exposes that host-facing MCP-only reload. At the owned-fork base it applied config and marked MCP state dirty without requesting fresh connections.

### Ordinary runtime publication

`codex-rs/core/src/session/mcp.rs` claims refresh work, recomputes desired state, and publishes through the thread-owned runtime.

`codex-rs/codex-mcp/src/runtime.rs` reuses prior connections unless reconnect is requested.

`reconciliation_reuses_connection_without_relisting_regular_tools` protects this low-latency ordinary reuse contract.

### Explicit reconnect operation

`Op::RefreshMcpServers` already requests reconnect before runtime refresh. This is the source precedent for treating explicit freshness differently from routine reconciliation.

### Tool-list-change notification

The RMCP client receives `notifications/tools/list_changed`. The Codex logging handler records the event and returns. No Codex relist, remote identity check, catalogue digest, revision increment, or thread publication follows.

### Cached-startup late binding

Current Codex can advertise cached regular-MCP tools while a replacement optional client remains pending.

The sampling step retains catalogue A for:

- model schema and description;
- search metadata;
- hook identity;
- initial request tool registration.

At call time, core dispatch waits for server startup and asks the thread runtime for current binding B. B supplies:

- prepared call;
- current client and server metadata;
- current approval policy and permission profile;
- file-input rewrite metadata;
- execution and result.

The path can therefore plan as A and approve or execute as B.

### Tool invocation still carries the captured step

Every `ToolInvocation` already contains its request's `StepContext`. The MCP handler does not need a new transport to recover the sampling-step binding. The smallest repair can use the captured binding first and enter late binding only for cached tools that had no prepared call at sampling time.

## First owned Codex candidate

The bounded source change calls `reconnect_on_next_refresh()` before applying host-supplied MCP config:

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

These are baseline limits rather than candidate failures.

### Why this is only the first slice

Reconnect intent is a boolean. An older publication can consume a reconnect request intended for a newer desired-state generation. `concurrency.md` defines the adversarial sequence and a generation-bound replacement.

The candidate also does not address notification relist, remote identity, catalogue equality, request authority, timed-out live work, cold reconstruction policy, or failed reconnect outcomes.

## Codex request-authority conflict

The source history contains a policy change that needs an explicit decision.

### Captured catalogue revision

The captured-binding change stated that a model-step tool call must not reroute to a replacement client or run against a catalogue revision the model did not see.

### Current runtime at dispatch

Runtime centralization changed core dispatch to refresh MCP state and obtain current binding before approval and execution, while still describing bindings as immutable for model steps and calls.

### Cached A, live B

The cached-startup change intentionally advertises cached catalogue A before server startup, waits for the selected server, and then prepares the call against live B.

Its original integration test proves:

- inference receives process A's cached description;
- the same tool name executes on process B;
- a tool absent from B fails closed.

It did not test same-name schema or authority changes.

## Compiled same-name schema result

A focused public-Codex test changed the existing cache fixture so that:

```text
catalogue A: echo(message: string)
→ A is cached and advertised to inference
→ model emits {"message":"hello"}
→ replacement B starts with echo(count: integer)
→ current dispatch invokes B
```

Observed:

- the request advertised A's required `message` field;
- the request advertised no `count` field;
- B received the A-shaped call;
- B rejected it with `echo schema v2 requires integer count`;
- Codex returned B's schema error to the model-visible function-call output;
- Codex did not report an A/B revision mismatch before invocation.

Validation:

- public Codex pin: `a5082373f18119dc5d3eb993267c97f37880935d`;
- workflow run: `30488803287`;
- job: `90701186402`;
- evidence artifact: `8739076993`;
- artifact digest: `sha256:f759a6b2e0a75bd8b2e2cfb8ef23c42a9d5e4e259473ae121a3b7614089e3148`;
- one focused integration test passed, zero failed.

The test passed because it asserted current behavior. It is a successful reproduction, not a passing repair.

Classification: `advertisement_execution_revision_mismatch`.

The server's argument rejection is a useful negative control. It is not a general safety guarantee. Another same-name implementation could accept, ignore, or reinterpret A's fields.

Exact patch, log, and result note are retained under:

`campaigns/0004-host-mcp-lifecycle-reconciliation/artifacts/codex-cached-schema-drift/`

## Approval-relaxation consequence

An already-sampled step can capture prompt-required A. Before its tool call dispatches, thread configuration can change to permissive B. Current dispatch can refresh to B and auto-approve under B.

A later policy may tighten an in-flight call. It should not relax the authority under which the call was sampled.

## Candidate authority rule

For a prepared call captured by the sampling step:

- execute the captured client, tool metadata, and approval authority;
- fail on the captured client rather than rerouting;
- apply current policy only as an added restriction;
- defer relaxation until a newly sampled step.

For a cached tool with no captured prepared call:

- wait for live B only as a bounded exception;
- compare A and B authority fingerprints before argument rewrite, approval, or execution;
- execute B only when equality is verified;
- otherwise fail closed with a typed revision-mismatch result and require a new sampling step.

The fingerprint should cover server identity, tool name, input and relevant output schemas, authority-relevant annotations, visibility, file-input metadata, plugin or connector provenance, hook identity, and approval/execution metadata.

## Compiled Rust SDK relist result

A focused fixture against the pinned official SDK used two real overlapping `on_tool_list_changed` callback relists over an in-process duplex transport.

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

The SDK cache retained C because its private generation rejected R1's late write. R1 still returned `Ok(B)` to application code, so a naive publisher rolled back from C to B. An application notification-generation ticket retained C.

The fixture, lockfile, exact log, and validation record are retained on L01 amendment PR #74.

### SDK implication

Calling `list_tools` from every list-change callback is insufficient under concurrent notifications.

A generic opt-in SDK helper needs one of:

- public relist ticket plus accepted-current result;
- internal notification coalescing with newest-result publication;
- watch or stream containing only accepted catalogue snapshots.

The helper should not silently replace application approval policy, request bindings, or model advertisements. Codex owns those decisions.

## Timed-out live calls

The adjacent timeout probe establishes a new transition that #84 must test:

```text
call begins under binding A
→ Codex outer timeout ends local wait
→ no MCP cancellation is sent
→ server operation remains active
→ refresh publishes binding B
→ A operation later completes or fails
```

Required rules:

- the operation keeps A's identity and authority;
- B cannot claim the late result;
- local timeout remains distinct from terminal execution and result persistence;
- automatic mutation retry or fallback stays blocked while the A outcome is ambiguous;
- refresh receipts record that an older live operation remains attached to A.

Timeout and cancellation mechanics remain under Scout #130. Durable operation and persistence receipts remain under Campaign #83. Fallback authority remains under #86.

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
- `timed_out_live_call_retained`;
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

The same-name changed-input-schema transition is compiled. Remaining cases:

- verified equal fingerprint;
- changed output schema;
- changed approval or annotations;
- changed visibility;
- changed file-input or provenance metadata;
- changed hook identity or behavior;
- typed mismatch before B execution.

### Timed-out live call

Let an A call time out locally without cancellation, publish B, and prove the eventual A terminal or persistence result remains attached to A and blocks ambiguous replay.

### Failed refresh

Test old-state retention, unavailable publication, partial per-server success, cancellation, timeout, and later recovery.

### Host reconstruction

Test `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` for dynamic tools and selected roots across resume and fork.

## CI harness rule

For Rust-only owned-fork changes:

- use `cargo fmt --all -- --check` and focused package tests;
- install `cargo-nextest` before `just test` when required;
- build helper binaries required by integration tests before invoking filtered test targets;
- use repository-wide `just fmt` only when the full formatter set, including `uv` and `dotslash`, is installed;
- classify missing tools as `harness_unavailable`;
- classify unrelated existing compile failures as `baseline_compile_blocker`.

## Current conclusion

The first host-reload source slice is valid and compiled, but it is not the complete repair.

The mixed-revision call path is now compiled for same-name input-schema drift. Current Codex calls B and relies on B's parser rather than verifying A/B equality. The next request-authority change should use the captured step binding first and make cached-startup late binding conditional on a verified authority fingerprint.

Notification-driven relist should consume the SDK ordering lesson: cache freshness does not automatically provide application publication freshness.

Timed-out live work must remain attached to its original operation identity and authority while newer MCP state publishes.

Public Codex and the official Rust SDK remained read-only. No upstream contact occurred.
