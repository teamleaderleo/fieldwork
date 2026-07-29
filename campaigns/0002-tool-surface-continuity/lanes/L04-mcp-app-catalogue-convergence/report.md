# L04: MCP and app catalogue convergence

State: `complete`

Issue: #39  
Campaign: #31  
Owned path: `campaigns/0002-tool-surface-continuity/lanes/L04-mcp-app-catalogue-convergence/`  
Upstream contact authorized: `false`

## In simple words

A running thread can keep the tool list it learned when an MCP connection first started. The server can later replace an offline stub with its real catalogue while keeping the same endpoint and credentials. Global inspection and direct calls can see the real server, yet the thread still builds its router and model-visible declarations from the old client snapshot.

The first stale layer in the controlled transition is the thread-owned live client and the binding captured from it. Router registration and model advertisement then remain mutually consistent with that stale binding. A benign call to the removed stub tool fails, while a raw call over the same healthy connection reaches a newly available real tool.

Fresh thread creation, explicit reconnect, full restart, and a connection-configuration identity change all rebuild the client and converge every measured layer.

## Assignment

Trace the path from the installed/authenticated MCP or app catalogue to the current thread binding, compare the global catalogue, runtime binding, router, model advertisement, and execution, then run a harmless stub-to-real transition across refresh, reconnect, fresh thread, and restart controls.

## Source and experiment boundary

- Public source revision: [`openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Source retrieval: 2026-07-29 through 2026-07-30
- Fixture runtime: Python 3.13 on Linux
- Resources: local temporary files and local stdio subprocesses only
- External publication or modification: none

Evidence labels used below:

- **Documented** — direct public source behavior.
- **Observed** — retained fixture output.
- **Inferred** — consequence joining source and fixture behavior.
- **Unknown** — a boundary the retained evidence cannot resolve.

## Path from global catalogue to execution

| Layer | Public source path | Finding |
| --- | --- | --- |
| Runtime catalogue assembly | [`core/src/mcp.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/mcp.rs), blob `5ae3315e70931575918cdd006618b130577f07c6` | **Documented:** `McpManager::runtime_config_for_step` combines configured servers, extension contributions, selected plugins, connector sources, app enablement, and current step context. |
| Thread owner | [`core/src/state/service.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/state/service.rs), blob `463abea8af802b6442eb77afedc9d4b677fb76ec` | **Documented:** each session owns one `Arc<McpRuntime>` as the live MCP connection owner for the thread. |
| Runtime publication | [`core/src/session/mcp_runtime.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mcp_runtime.rs), blob `01f5ce4a265f140fb609c6fc256331af57bd207d` | **Documented:** current config, auth, environments, selected roots, and effective servers become `McpRuntimeInput`; publication calls `McpRuntime::replace`. |
| Refresh trigger | [`core/src/session/mcp.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mcp.rs), blob `0b90712229f57f8f714cb046423c74e74a0d8127` | **Documented:** ordinary step capture refreshes only after MCP state becomes dirty. Auth changes and selected-root changes mark it dirty. The inspected path contains no remote catalogue-digest comparison. |
| App-server config refresh | [`app-server/src/mcp_refresh.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/app-server/src/mcp_refresh.rs), blob `405f575c16706ef75cfd9fe91f19d1c71e512b03` | **Documented:** config reload walks active threads and applies refreshed MCP config. Its tests cover config replacement and thread overrides. |
| Connection reuse | [`codex-mcp/src/runtime.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/runtime.rs), blob `c0acaf1b03e495868385685a480a25a321918499`; [`codex-mcp/src/connection_manager.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/connection_manager.rs), blob `34a0f35613ece5bfcc103833f45c5689eac17e46` | **Documented:** `McpRuntime::replace` supplies the previous connection set unless reconnect was requested. A ready, open client is reused when its connection identity matches. |
| Connection identity | [`codex-mcp/src/server.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/server.rs), blob `0811d80435809430823d0d7331fab1eba81b8832` | **Documented:** identity includes transport, environment, credentials, selected environment-variable values, runtime auth, cache context, and elicitation capabilities. Remote `serverInfo` and a catalogue digest are absent. |
| Startup snapshot | [`codex-mcp/src/rmcp_client.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/rmcp_client.rs), blob `3f4ca26efa4bab50d98b76d0f0f82e3e48427472` | **Documented:** startup initializes the server, runs `tools/list`, then stores `server_info` and `client_tools` in `ManagedClient`. Ready-client listing clones that stored tool vector, except the dedicated Apps cache path. |
| Process catalogue cache | [`codex-mcp/src/tool_catalog_cache.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/tool_catalog_cache.rs), blob `15c3ae3d59813ea31ae31b11fc0f101c063403f6` | **Documented:** regular stdio MCP definitions can be retained process-wide for 30 minutes under a configuration-derived cache identity. HTTP catalogues skip this shared cache. A server can disable the cache through the experimental capability. |
| Step binding | [`codex-mcp/src/binding.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/binding.rs), blob `6cec4cb393da5d08c0470538df3715be93b4a705`; [`connection_manager/tool_catalog.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/connection_manager/tool_catalog.rs), blob `0a3447e56c9ed9e8bdc5312354951faf58f6e940` | **Documented:** one binding freezes tools and exact prepared calls from ready clients. Apps hard refresh increments a catalogue revision; prepared calls reject execution after an in-place catalogue revision change. |
| Router and model declaration | [`core/src/session/step_context.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/step_context.rs), blob `13dde96fde7b4b55860d5721cbdc14698858b7e9`; [`core/src/tools/router.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/router.rs), blob `73c98dec1125aed7671050a509b7b2ed8ad95b7d`; [`core/src/tools/spec_plan.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs), blob `5ff9e392f3ebec0a510efd11305752133944ceda` | **Documented:** the exact binding enters `ToolRouter::from_context`; one finalized router holds both the registry and model-visible specifications for the sampling request. |
| Sampling and dispatch | [`core/src/session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs), blob `57691ab81a216834b60666e7976828b380dae68e` | **Documented:** each sampling loop captures one step so context, advertised tools, and calls share one request view. |
| Raw control-plane execution | [`core/src/codex_thread.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/codex_thread.rs), blob `63f2c69afff2c0744a8ac8b5bb271fd0bfbb5202`; [`codex-mcp/src/connection_manager.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-mcp/src/connection_manager.rs) | **Documented:** `call_mcp_tool` refreshes dirty state and calls the latest live client by server/tool name. This route does not require the tool to appear in the current sampling-step binding. |

## Controlled fixture

Artifacts:

- `artifacts/stub_real_mcp.py`
- `artifacts/catalogue_transition_probe.py`
- `artifacts/test_catalogue_transition.py`
- `artifacts/results/latest.json`
- `artifacts/results/probe-output.txt`
- `artifacts/results/test-output.txt`

Run:

```bash
cd campaigns/0002-tool-surface-continuity/lanes/L04-mcp-app-catalogue-convergence/artifacts
python3 catalogue_transition_probe.py --output results/latest.json
python3 -W error::ResourceWarning -m unittest -v test_catalogue_transition.py
```

The server implements a small MCP-shaped JSON-RPC stdio surface: `initialize`, `tools/list`, `tools/call`, and `shutdown`. Every request reads a disposable state file. The thread client performs initialization and listing once, stores server information and tools, and follows the source reuse rule when connection configuration remains equal. A fresh global probe opens a separate client for each checkpoint.

The transition uses harmless tools only:

- stub: `offline_status`
- real: `catalogue_version`, `echo`, `health`
- catalogue-only addition: `new_read_only_tool`

## Results

Retained test result: seven tests passed in 10.863 seconds.

| Checkpoint | Global catalogue | Bound catalogue | Refresh action | Router/model | Benign execution result |
| --- | --- | --- | --- | --- | --- |
| `01-stub-baseline` | `offline_status`, digest `2f248f05f5cb106b` | same | initial | same | stub call succeeds |
| `02-server-became-real-before-refresh` | real tools, digest `d22cc55e351c2c2a` | stub digest `2f248f05f5cb106b` | none | stub | removed stub call returns `unknown tool`; raw `echo` succeeds |
| `03-ordinary-refresh-same-config` | real | stub | `reused` | stub | divergence persists |
| `04-fresh-thread` | real | real | new thread runtime | real | all real smoke calls succeed |
| `05-explicit-reconnect` | real | real | `reconnected` | real | all real smoke calls succeed |
| `06-full-restart` | real | real | new process runtime | real | all real smoke calls succeed |
| `07-identity-only-ordinary-refresh` | identity `real-3-identity-only` | identity `real-2` | `reused` | catalogue unchanged | calls succeed against the newer server while bound identity remains old |
| `07b-identity-reconnect-control` | identity `real-3-identity-only` | same | `reconnected` | same | converged |
| `08-catalogue-only-ordinary-refresh` | adds `new_read_only_tool`, digest `38e3ca4d6c6fe10e` | prior digest `d22cc55e351c2c2a` | `reused` | prior catalogue | router lacks the new handler; raw call succeeds |
| `09-connection-config-change` | expanded catalogue | same | `reconnected` | same | all smoke calls succeed |

## First stale layer

**Observed:** immediately after the server changes from stub to real, the fresh global probe reports the real server and real catalogue. The active thread still holds the startup `server_info` and tool vector from the stub.

**Observed:** the router registry and model-visible declaration agree with that stale binding. The request-scoped router invariant works as designed; it faithfully carries the older snapshot.

**Observed:** execution splits into two useful checks:

1. the model/router path cannot call newly added tools because handlers are absent;
2. the model/router path still offers the removed stub tool, and the server rejects it as unknown;
3. a raw control-plane call over the same live client reaches the new real tool successfully.

**Conclusion:** the first stale layer is the current thread runtime binding source: the reused ready client and its startup-captured catalogue. Router registration and model advertisement are downstream stale layers. The server transport and provider execution path remain healthy in this reproduction.

## Refresh, reconnect, fresh thread, and restart

- **Ordinary refresh:** reuses the ready client when connection configuration matches. It preserves the stale server identity and catalogue.
- **Explicit reconnect:** starts a fresh client, repeats initialization and `tools/list`, and converges all measured layers.
- **Fresh thread:** creates a new thread-owned runtime and converges all measured layers.
- **Full restart:** creates a new runtime and converges all measured layers.
- **Connection-config change:** changes the reuse identity, forces startup, and converges all measured layers.

## Server identity and catalogue digest

### Server identity only

With the same endpoint, credentials, and catalogue, changing `serverInfo.version` from `real-2` to `real-3-identity-only` leaves the active bound identity at `real-2` after ordinary refresh. Calls still execute against the updated server. This demonstrates stale diagnostic identity even when the callable names remain compatible.

### Catalogue digest only

After reconnecting to the new identity, adding `new_read_only_tool` without changing `serverInfo` leaves the bound digest at `d22cc55e351c2c2a` while the global digest becomes `38e3ca4d6c6fe10e`. The raw call succeeds and the router lacks the handler.

### Source connection

**Inferred:** the controlled outcome follows the public reuse key. `McpServerConnectionIdentity` compares connection and authorization inputs while omitting remote server information and catalogue digest. Reusing `ManagedClient` therefore reuses its startup-captured tool vector.

## Negative findings and controls

- **Negative result:** router registration and model advertisement never diverged within one captured step in the fixture.
- **Negative result:** fresh thread, reconnect, restart, and connection-config change all restored the larger catalogue.
- **Negative result:** the failure does not require broken transport, expired credentials, or an unreachable server; raw real-tool calls succeeded during the stale-thread checkpoints.
- **Negative result:** server identity can remain stale while calls still succeed, so identity mismatch alone does not prove execution failure.
- **Negative result:** the inspected Apps hard-refresh path already provides stronger semantics than ordinary configured-MCP refresh: it starts fresh connections and increments the Apps catalogue revision.
- **Boundary:** the generic stdio catalogue cache may affect startup and display observations for up to 30 minutes. The ready binding in this fixture isolates live-client reuse from that cache.
- **Unknown:** no live `tools/list_changed` reconciliation path was located in the inspected files. A protocol-notification integration test would settle that branch.
- **Unknown:** private ChatGPT host catalogue assembly and Remote behavior remain outside public Codex source.
- **Boundary:** this lane produced a source-grounded owned fixture. A compiled Codex regression test remains a candidate implementation task.

## Candidate repair contract

### 1. Refresh has an explicit freshness result

Every requested refresh should return one typed outcome per server:

- `reused_same_catalogue`
- `catalogue_relisted_same`
- `catalogue_changed_rebound`
- `server_identity_changed_reconnected`
- `connection_config_changed_reconnected`
- `refresh_failed_kept_previous`
- `refresh_failed_unbound`

The receipt should include privacy-safe digests for connection identity, server identity, normalized model-visible catalogue, selected roots, required servers, router registration, model advertisement, and executable smoke status.

### 2. Explicit refresh validates live catalogue state

For a ready configured MCP connection, explicit refresh should perform one of these actions:

1. run a live `tools/list`, compare the normalized catalogue digest, and publish a new catalogue revision when it changes; or
2. reconnect and initialize again when live relisting has weaker safety guarantees.

A successful refresh cannot report completion while preserving an unverified startup catalogue.

### 3. Server identity participates in diagnostics and reconnection policy

Capture the remote `serverInfo` digest at startup and after an explicit relist or reconnect. A changed identity should force reconnection when identity affects protocol, authorization, or tool semantics. Compatible identity changes can retain the connection only with an explicit `identity_changed_catalogue_verified` outcome.

### 4. Publication keeps request-scoped consistency

Continue deriving router handlers and model-visible specifications from one immutable step binding. When a live catalogue changes in place, increment the catalogue revision before publishing the new binding so prepared calls from the earlier revision fail with the existing typed stale-catalogue error.

### 5. Generic MCP receives a hard-refresh seam

Provide configured MCP with a refresh operation equivalent in strength to the current Apps `replace_fresh` path. The operation should be callable by app-server refresh, reconnect UI, tests, and diagnostics without altering unrelated thread settings.

### 6. Cache use stays visible

Record whether each tool vector came from:

- live startup listing;
- live explicit relist;
- Apps shared cache;
- generic stdio cache;
- pending-startup cached metadata.

A refresh receipt should expose cache age and the server’s cacheability decision. A cached vector can support display or startup continuity; model execution after explicit refresh should require a verified live client and a current catalogue revision.

### 7. Recovery preserves older step authority

A new catalogue publication should leave already-running step bindings immutable. New sampling requests use the newer binding. Calls prepared under an invalidated in-place catalogue revision receive a typed rejection. Consequential callers can then stop or reconcile instead of guessing.

## Candidate implementation seams

1. Extend `McpServerConnection::reusable_client` or its caller with a refresh mode that requests live catalogue verification.
2. Add a generic `McpRuntime::replace_fresh`/`hard_refresh_server` operation returning server identity and catalogue digests.
3. Store a normalized catalogue digest beside `ManagedClient.server_info` and `ManagedClient.tools`.
4. Increment and expose catalogue revision for every accepted live catalogue replacement, beyond the Apps-only override.
5. Add app-server tests for stable endpoint plus changed identity/catalogue across existing thread, fresh thread, and restart controls.
6. Feed the typed refresh receipt into campaign lane L06 diagnostics.

## Proposed regression matrix

| Transport/cache | Transition | Existing thread ordinary refresh | Existing thread explicit reconnect | Fresh thread | Restart |
| --- | --- | --- | --- | --- | --- |
| stdio, cache disabled by server | stub → real | must relist or report stale-preserved failure | converge | converge | converge |
| stdio, shared cache enabled | stub → real | verify live digest; record cache source | converge | converge with live verification | converge |
| streamable HTTP | stable endpoint, identity change | verify identity and catalogue | converge | converge | converge |
| streamable HTTP | stable identity, catalogue change | publish new revision | converge | converge | converge |
| Apps | hard refresh | publish new revision and reject earlier prepared calls | converge | converge | converge |

Each row should assert global, bound, registered, advertised, router-executable, raw control-plane, and displayed inventories separately.

## Handoff

Strongest supported finding: public source permits ordinary runtime publication to reuse a ready client whose connection configuration matches, while that client retains startup-captured server information and tools. The owned live fixture reproduces a stable-endpoint stub-to-real transition where global and raw execution see the real server and the active thread remains bound to the stub until reconnect, fresh thread, restart, or connection-config change.

Recommended next decision: accept the candidate repair contract and dispatch a compiled Codex regression test at the connection-reuse boundary. Preserve the request-scoped binding/router invariant.
