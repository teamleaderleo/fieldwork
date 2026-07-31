# Current MCP timeout retirement ownership

Date: 2026-07-31  
Worker: lane L  
Fieldwork issue: #134  
Public Codex source: `4642370542739d5dd080b0c87a9de06a6435d3db`  
RMCP SDK source: `3240b6e7828ed4146041d32dd0ce4ced7c04e411`  
Public upstream interaction: none

## Question

Which current Codex objects already own enough identity to retire a timed-out MCP connection safely, and which missing facts still require source work?

## Current identity already present

### `PreparedMcpCall`

`codex-rs/codex-mcp/src/binding.rs` retains:

- the exact `Arc<McpConnectionSet>` that produced the call;
- the exact `Arc<ManagedClient>` selected for the server;
- the exact `ToolInfo`;
- catalogue revision and revision source;
- exact configuration and server metadata.

The fields are currently private, but pointer identity already distinguishes the old client and connection set from any replacement. A delayed timeout task does not need to guess by server name alone.

### `McpRuntime`

`codex-rs/codex-mcp/src/runtime.rs` publishes an immutable `PublishedMcpRuntime` through `ArcSwap`. The current snapshot owns one `Arc<McpConnectionSet>`. Existing bindings retain older snapshots independently.

Current explicit reconnect is an `AtomicBool` named `reconnect_pending`. When claimed, the next `replace` passes no previous connection set and therefore creates fresh connections for all configured servers.

### `Session`

`codex-rs/core/src/session/mcp.rs` owns the refresh semaphore, dirty-state claim, desired-state reconstruction, runtime input construction, publication, and loop that consumes invalidations arriving during refresh. This is the layer that can turn a retirement decision into replacement and catalogue republication.

## Current timeout path

`codex-rs/rmcp-client/src/rmcp_client.rs` applies Codex's elicitation-aware active-time timeout around the whole service operation. Legacy `tools/call` creates an RMCP `RequestHandle` with no native timeout options and awaits it inside that outer timer. When the outer timer fires, the future is dropped and Codex returns a local timeout error.

The current path therefore does not retain:

- request-scoped cancellation requested;
- cancellation delivery completed, failed, or timed out;
- exact service/client retirement action;
- manager replacement receipt;
- external-effect settlement.

The RMCP SDK already supports explicit `RequestHandle::cancel` and timeout-triggered cancellation notifications carrying the request ID. Its stateless HTTP server tests also prove a disconnect can trigger cooperative server cancellation. Those facts establish delivery mechanisms, not remote-effect absence.

## Minimal ownership design

### 1. Opaque exact-client token

Expose an opaque token from `PreparedMcpCall` containing pointer identity for:

- connection set;
- managed client / RMCP client;
- server name;
- optional publication generation when available.

The token must not expose mutable client internals to core.

### 2. Typed timeout and cancellation receipt

Replace string-only timeout interpretation with a typed receipt that separates:

- caller deadline reached;
- request dispatched;
- cancellation requested;
- cancellation delivery `delivered | failed | timed_out | not_supported`;
- transport state `healthy | retired | replacement_pending | unknown`;
- remote effect `unknown` unless a stronger result or reconciliation proves otherwise.

### 3. Generation-checked targeted retirement

Add a runtime operation equivalent to:

```text
retire_server_if_current(exact_client_token)
```

It must compare the token with the runtime's current connection set and current server client by pointer identity. If either differs, the old timeout is stale and must not close or invalidate the replacement.

If both match and cancellation delivery failed or stalled:

1. mark that exact server/client retired;
2. close the exact unhealthy client;
3. request targeted reconnect for that server;
4. mark the session MCP runtime dirty;
5. reconstruct desired state and publish a replacement;
6. retain the timeout operation as outcome-unknown;
7. never replay the original call automatically.

### 4. Targeted reconnect request

The current `AtomicBool` forces all servers fresh. Timeout escalation should not restart unrelated healthy servers. Replace or extend it with a reconnect request that can represent:

- none;
- all servers, for explicit host configuration reload;
- a set of exact server names, for targeted retirement.

Claim/drop behavior must preserve unconsumed requests if publication fails or is superseded.

### 5. Publication composition

The owned publication-generation candidate proves that a slow older refresh must not overwrite a newer published runtime. Targeted retirement should compose with that invariant:

- an old timeout token cannot retire a newly published client;
- an older replacement candidate cannot publish after a newer desired state;
- active calls keep their captured client until they complete or receive typed invalidation.

Pointer identity is sufficient for safe stale-retirement rejection. A numeric publication generation remains useful for diagnostics, receipts, and publication ordering.

## Why direct client shutdown remains rejected

Closing `RunningService` inside `RmcpClient::call_tool` cannot prove it still owns the current server client. A timeout from an old call could close a replacement service or bypass manager-owned catalogue republication. It also cannot choose a targeted policy for unrelated calls.

## Why successful cancellation delivery does not require automatic retirement

A delivered request-scoped cancellation can leave the transport healthy. The server may cooperate, ignore cancellation, or commit before observing it. The receipt must keep remote effect unknown, but manager retirement should be reserved for failed/stalled delivery or a separately observed unhealthy transport. This preserves unrelated healthy requests without pretending delivery settled the mutation.

## Required controls

1. cooperative cancellation delivery prevents the synthetic delayed effect and preserves the exact client;
2. ignored cancellation commits later, keeps effect unknown, and does not trigger replay;
3. stalled cancellation returns within the caller bound and retires only the exact current server client;
4. an older timeout cannot retire a newer replacement client;
5. another server's concurrent call completes during targeted retirement;
6. a same-server unrelated call receives explicit typed invalidation or a documented bounded failure;
7. replacement reconnects, reinitializes, republishes the catalogue, and becomes callable;
8. publication race controls still reject stale replacement candidates;
9. modern stateless disconnect and resumable request-stream behavior remain separate.

## Evidence classes and limits

- `target-executed`: merged Fieldwork PR #163's candidate matrix at historical Codex head `e322eb92a6745616953bc00a3db8046c499dc6a7`.
- `source-read`: current Codex runtime, binding, session refresh, and RMCP client at `464237...`.
- `source-read`: RMCP SDK request handle and stateless disconnect tests at `3240b6...`.
- `inferred design`: pointer-identity retirement and targeted reconnect composition.
- `unknown`: no current-source manager-layer implementation has executed these controls.

## Next transition

Build a manager-layer prototype on current Codex source that introduces only the opaque identity token, typed cancellation receipt, current-client comparison, and targeted reconnect request. Run stale-token, unrelated-server, stalled-delivery, replacement-publication, and no-replay controls before selecting a production source candidate.
