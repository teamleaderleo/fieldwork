# Lane L evidence — current MCP authority, publication, reconnect, and timeout read

Date: 2026-07-31  
Worker: GPT-5.6 Thinking via the active `teamleaderleo` repository session  
Public Codex revision: `3016671bb077c43448b8fa88f3edfa9772e17058`  
MCP Rust SDK revision: `3240b6e7828ed4146041d32dd0ce4ced7c04e411`  
Public upstream interaction: none

## Scope

This note retains the primary-source read behind `findings/F84-mcp-call-authority/finding.md`.

Questions:

1. Which MCP authority is captured for a model step?
2. Which authority is used when the call executes?
3. Why does the current path rebind live?
4. Which publication and reconnect candidates remain unabsorbed?
5. What does a Codex MCP timeout prove about cancellation and remote effects?

## Current source inventory

### Request-scoped authority

`codex-rs/core/src/session/step_context.rs`

- `StepContext.mcp: Arc<McpBinding>` is documented as the exact MCP connections, configuration, and catalogue captured for the step.
- `StepContext.mcp_tools` is the fixed MCP list used for the exact sampling request.

`codex-rs/codex-mcp/src/binding.rs`

- `McpBinding` owns frozen tools and a `(server, tool) -> PreparedMcpCall` map.
- `PreparedMcpCall` owns the exact client, config, catalogue revision and source, `ToolInfo`, server metadata, plugin identity, and selected-plugin state.
- `call_with_preparation` holds a read lock on the catalogue revision, rejects stale revision, performs irreversible preparation, and dispatches on the retained client.

### Current execution path

`codex-rs/core/src/tools/handlers/mcp.rs`

- `McpHandler` owns the `ToolInfo` used to create the model-visible declaration.
- The handler currently passes only raw server and tool names into `handle_mcp_tool_call`.

`codex-rs/core/src/mcp_tool_call.rs`

- The function receives `StepContext` but does not use `step_context.mcp` for call preparation.
- It calls `sess.refresh_mcp_if_dirty()`.
- It obtains `mcp_runtime.current_binding_for_call(server)`.
- It prepares the call from that current binding.
- Approval metadata, hooks, file rewriting, and execution therefore use the newest live prepared call.

This is the advertisement/execution revision seam.

## Upstream precedent reconciliation

### PR #34588 — captured catalogue revisions

URL: `https://github.com/openai/codex/pull/34588`

Merged head: `65f8bf68533332628b7fc213eade2a91d18d36ee`

Intent recorded by the PR:

- one sampling request captures ready clients, visible tools, resources, and server metadata;
- a call uses the captured client;
- a changed catalogue revision rejects the call before preparation/execution finishes;
- replacement connections must not receive a call from an earlier model step.

### PR #35590 — cached definitions before startup

URL: `https://github.com/openai/codex/pull/35590`

Merged head: `3bbf1fe75701c97fb190e0867002ba2d9dbda5db`

Intent recorded by the PR:

- cached tools can reach inference before the server is ready;
- cached tools intentionally have no prepared call;
- execution waits for startup and prepares against a refreshed live binding;
- a cached tool absent from the live catalogue returns a model-visible unavailable error.

### Reconciliation

The two intents compose cleanly with a branch on whether the captured binding has a prepared call:

```text
captured prepared call exists
→ use captured call

captured prepared call absent and advertised tool came from cache
→ wait for live startup
→ compare advertised and live callable authority
→ use live call only on equality
```

Applying live rebinding to both cases discards the first PR's invariant. Applying captured-only execution to both cases discards the second PR's cached startup feature.

## Authority fingerprint criteria

The comparison should answer whether live execution has the same callable authority as the cached advertisement. Candidate fields:

### Include

- raw MCP server name;
- raw MCP tool name;
- model-visible namespace and callable name;
- input schema;
- annotations that affect scheduling, approval, destructive/open-world interpretation, or display of risk;
- connector ID used by app policy;
- provided-file optional-field map used by argument rewriting;
- selected-plugin and server approval authority when those can change between captures;
- server origin or environment identity when they participate in authority or routing.

### Classify explicitly

- connector name;
- namespace description;
- plugin display names;
- tool description/title.

Those values can affect presentation and approval explanation. Some may belong in the fingerprint; the implementation should decide with focused controls instead of inheriting full serialized equality accidentally.

## Owned authority approach #79

Carrier head: `d96bcf0b8d9b254474c1d27739bd40ee5c6a04fa`  
Workflow: `fieldwork-84-mcp-authority-a01a`  
Run: `30584093534`

Approach:

- pass the `McpHandler` advertisement into `handle_mcp_tool_call`;
- prepare against the current live binding;
- serialize advertised and live `ToolInfo` and require complete JSON equality;
- reject drift before approval metadata, hooks, file rewriting, or dispatch.

Value:

- demonstrates a conservative fail-closed comparison;
- directly covers schema and connector changes.

Repair needed:

- use the captured prepared call for ordinary requests;
- reserve live rebind for cached-only advertisements;
- move callable-authority selection/comparison into `codex-mcp`;
- replace broad serialization equality with a deliberate fingerprint;
- add integration controls proving exact client dispatch and pre-dispatch rejection.

## Publication evidence

Source PR: `teamleaderleo/codex#75`  
Source head: `c3373c717f3138ff5f0a979d12836f60800d2bcf`  
Carrier PR: `teamleaderleo/codex#77`  
Carrier head: `0fb2e6b09a6ff03bcfcbd665b187cadb64d36b4b`  
Run: `30584055792`  
Job: `91011123543`

Executed controls:

1. `publication_state_rejects_older_generation`
2. `publication_state_carries_freshness_across_overlapping_refreshes`
3. `publication_state_rejects_candidate_when_freshness_advances`
4. `publication_state_keeps_stale_candidate_gate_closed`
5. `publication_gate_opens_only_for_the_winning_candidate`

Receipt:

```text
FIELDWORK_MCP_PUBLICATION_EXACT=5/5
complete codex-mcp package: passed
```

Evidence class: `target-executed`.

Limits:

- tests exercise the publication state and gate directly;
- the production Session path currently serializes ordinary and fresh replacement;
- no source receipt yet demonstrates a live slow-A/fast-B caller overlap;
- accepted-result identity and reconnect composition remain open.

## Reconnect source

Source PR: `teamleaderleo/codex#76`  
Source head: `7e9d80c4965a76b802f02d7bace17ea1c4a8931c`  
App-server carrier PR: `teamleaderleo/codex#82`  
Carrier head: `fee6e8350673b2fb87841dfb7b96d3c2ea8def0d`  
Run: `30584136349`

Current public source:

- `CodexThread::refresh_mcp_config` installs MCP config without requesting fresh connections.
- protocol operation `refresh_mcp_servers` requests reconnect before refresh.
- app-server `reload_mcp_config` loads every strict refresh plan before applying any thread refresh.

Required controls:

- ordinary unchanged runtime refresh reuses the ready client;
- explicit host MCP reload reconnects exactly once;
- public app-server `mcpServer/refresh` reaches the reconnect boundary;
- strict planning failure creates zero reconnect attempts and zero partial publication.

## Timeout and cancellation source read

### Current Codex client

`codex-rs/rmcp-client/src/rmcp_client.rs`

- `call_tool` creates a legacy `RequestHandle` with `PeerRequestOptions::no_options()` plus optional metadata.
- modern protocol uses the convenience `service.call_tool` path.
- both paths run inside `run_service_operation`.
- `run_service_operation_once` wraps the complete operation future in `active_time_timeout`.
- expiry returns `ClientOperationError::Timeout` from the outer Codex timer.

For the legacy path, the RMCP `RequestHandle` itself has no timeout option. The outer future is dropped at local expiry. The source does not record a cancellation-notification receipt or remote settlement receipt.

### RMCP SDK capability

`modelcontextprotocol/rust-sdk/crates/rmcp/src/service.rs`

- `RequestHandle::await_response` sends `notifications/cancelled` when its native timeout expires;
- progress-reset and maximum-total timeout paths send the same notification with a typed reason;
- `RequestHandle::cancel` sends explicit cancellation;
- request IDs are retained in the cancellation notification.

`crates/rmcp/tests/test_streamable_http_disconnect_cancel.rs`

- stateless SSE and JSON disconnects fire the server request context cancellation token;
- the source explicitly distinguishes stateful/resumable streams, where a disconnect may recover.

### Certainty classification

```text
local Codex timeout
→ caller deadline expired
→ RMCP cancellation delivery: unobserved in current Codex path
→ server cancellation acknowledgement: unobserved
→ remote effect settlement: unknown
```

A future implementation can improve transport cancellation delivery by using native request options or retaining and cancelling the request handle. It must continue reporting mutation outcome as unknown until a stronger settlement or idempotency receipt exists.

## Latest public drift

Lane-L candidates use base `a01a2d91461a57809e944de7758477b92617ab01`.

Current public head is `3016671bb077c43448b8fa88f3edfa9772e17058`.

The one-commit delta adds Enterprise automation account-plan support across authentication, rate limits, protocol schema, app-server state, and UI tests. It does not touch:

- `codex-rs/codex-mcp/src/runtime.rs`;
- `codex-rs/codex-mcp/src/binding.rs`;
- `codex-rs/codex-mcp/src/connection_manager.rs`;
- `codex-rs/core/src/codex_thread.rs`;
- `codex-rs/core/src/mcp_tool_call.rs`;
- `codex-rs/core/src/tools/handlers/mcp.rs`;
- `codex-rs/rmcp-client/src/rmcp_client.rs`.

The relation is mechanically clean and semantically file-disjoint. Exact-head policy still expires the earlier current/proposal-ready classifications.

## Smallest next experiments

### Authority integration matrix

1. ready captured A; publish B; invoke A call; require A client receives it;
2. cached-only A; live A; invoke; require live A receives it;
3. cached-only A; live B schema drift; require zero approval, hook, rewrite, and MCP dispatch;
4. cached-only A; live B connector/policy drift; require the same rejection;
5. captured A; catalogue revision changes while approval waits; require rejection before dispatch;
6. identical callable authority with presentation-only change; determine whether dispatch remains eligible.

### Timeout integration matrix

1. native timeout sends cancellation notification with matching request ID;
2. cooperative server cancellation produces a transport-cancelled receipt;
3. server ignores cancellation; local result remains outcome unknown;
4. stateless disconnect cancels request context;
5. stateful resumable disconnect remains potentially recoverable;
6. mutation replay remains blocked without idempotency or settlement proof.

## Disposition

- Publication: target-executed at its exact head; current-head renewal and live-overlap composition remain.
- Reconnect: execution pending.
- Authority #79: executable conservative approach, disposition `REPAIR`.
- Retained authority direction: captured-first plus authority-checked cached fallback.
- Timeout: source finding confirms an available native cancellation path and a separate remote-effect certainty gap.
- Non-delegable human decision: none.
