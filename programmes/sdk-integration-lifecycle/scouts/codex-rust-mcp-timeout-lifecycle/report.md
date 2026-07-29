# Codex and Rust MCP timeout lifecycle

Date: 2026-07-30

Fieldwork scout: #130  
Programme: #13  
Primary target hub: #7  
Worker: ChatGPT GPT-5.6 Thinking  
Upstream contact authorized: `false`

## In simple words

Codex has a configurable time limit for MCP tool calls. In the default legacy MCP path, that limit currently wraps the whole Rust SDK operation from the outside.

When the Codex timer expires, Codex stops waiting and reports a timeout. The underlying `rmcp` request handle is simply dropped. The Rust SDK only sends MCP cancellation when its own request timeout fires or when `RequestHandle::cancel()` is called.

An executed `rmcp 3.0.0` probe confirms the consequence:

- Codex-style outer timeout: the server receives no cancellation and completes the delayed side effect;
- native Rust SDK request timeout: the server receives cancellation and the delayed side effect stops.

This is a concrete Codex integration lifecycle candidate. It is not evidence that every timeout or crash in Codex has one cause. Separate current reports cover transport recovery after server restart and Windows child-process cleanup.

## Verdict

**Confirmed default-legacy timeout/cancellation mismatch in the Codex integration.**

The strongest supported statement is:

> In Codex's default legacy MCP tool-call path, the caller-visible `tool_timeout_sec` deadline can expire without sending `notifications/cancelled` to the MCP server. A cooperative server can therefore continue and complete work after Codex has reported the tool call as timed out.

Ownership is primarily in Codex's `codex-rmcp-client` integration because:

- `rmcp 3.0.0` already exposes timeout-aware and explicit-cancellation request APIs;
- Codex creates the legacy request with `PeerRequestOptions::no_options()`;
- Codex then applies its own outer active-time timeout;
- the Rust SDK has no request-handle drop-cancellation contract.

The production fix should preserve Codex's elicitation-aware active-time accounting while explicitly retiring the underlying MCP request on timeout.

## Exact pins

- Codex source: `openai/codex@88d6c2b2b41b0790fa10c232f2a6be0e128cedd6`
- Codex Rust SDK dependency: `rmcp = "=3.0.0"`
- Rust SDK release inspected and executed: `modelcontextprotocol/rust-sdk@rmcp-v3.0.0`
- Rust SDK comparison revision: `modelcontextprotocol/rust-sdk@d82c94aa8ede23d7ee8c9caf539a92bd1c057e78`
- Fieldwork probe head: `teamleaderleo/fieldwork@35c7628e17451d9d7fc22bd93aa8c6bf74bb5662`
- Probe workflow run: `30490566255`
- Retrieval date: 2026-07-30

OpenAI Codex and the MCP Rust SDK remained read-only. No issue, pull request, comment, reaction, branch, or message was created upstream.

## Boundary map

| Layer | Current responsibility | Observed boundary |
| --- | --- | --- |
| Codex connection manager | Reads `tool_timeout_sec` and passes a duration into the managed client | Caller-visible policy source |
| Codex `RmcpClient` | Wraps service operations with `active_time_timeout` | Actual timeout owner in the default legacy path |
| Rust SDK `RequestHandle` | Tracks request ID, response receiver, progress timeout and explicit cancellation | Does not receive a timeout option from Codex's legacy call |
| Rust SDK service loop | Stores pending responder by JSON-RPC request ID | Entry remains until response, error, cancellation, send failure or transport teardown |
| MCP server handler | Receives `RequestContext::ct` when cancellation is propagated | Token does not fire for the Codex-style outer timeout |
| Application side effect | May commit independently of response delivery | Can complete after caller-visible timeout |

## Codex source path

### Default protocol mode

Codex's `McpProtocolMode` defaults to `Legacy`.

- legacy preferred version: `2025-06-18`;
- 2026 mode is opt-in;
- stdio remains legacy unless both the Codex modern mode and `CODEX_MCP_PROTOCOL_VERSION=2026-07-28` are selected.

The confirmed probe therefore matches the default Codex/stdio lifecycle rather than an unusual compatibility setting.

### Tool timeout configuration

`McpConnectionSet` stores one configured timeout per server using `tool_timeout_sec` or the default tool timeout. `call_tool()` passes that duration into the managed `RmcpClient`.

### Outer timeout

`RmcpClient::run_service_operation_once()` applies Codex's `active_time_timeout(duration, ..., operation(service))`.

This timer is intentionally aware of elicitation pauses. When it expires, it returns Codex's own `ClientOperationError::Timeout`.

### Legacy request construction

The legacy `tools/call` path creates:

```rust
let mut options = rmcp::service::PeerRequestOptions::no_options();
```

It sends the request and awaits the returned handle's response. No Rust SDK timeout is installed on that handle.

When the outer Codex timeout wins, the operation future and request handle are dropped.

## Rust SDK 3.0.0 source path

### Native timeout behavior

`RequestHandle::await_response()` checks `PeerRequestOptions.timeout` and `max_total_timeout`.

When its own timeout fires, it:

1. unregisters request subscription state;
2. sends `notifications/cancelled` with the request ID;
3. returns `ServiceError::Timeout`;
4. cleans progress-timeout state.

`RequestHandle::cancel()` provides the same explicit cancellation route.

### Drop behavior

No `Drop` implementation for ordinary `RequestHandle` cancels the remote request.

Dropping a handle therefore drops its response receiver but does not invoke `cancel()` and does not send a notification.

The service loop retains the corresponding responder until a later response/error, explicit cancellation, send failure, or transport shutdown removes it. If a late response arrives after the receiver was dropped, the service loop removes the entry and its attempt to deliver through the closed oneshot fails.

### Existing SDK control tests

The Rust SDK already tests that `PeerRequestOptions::with_timeout(...)` returns `ServiceError::Timeout`. Its cancellation tests also demonstrate that an explicit cancellation fires the server handler's `RequestContext::ct` and suppresses a late response.

The missing boundary is not native SDK timeout behavior. It is what an integrating application does when it imposes a separate outer timeout.

## Executed probe

### Fixture

The owned probe uses exact `rmcp 3.0.0` public APIs and a real in-memory async transport pair.

The server tool:

- marks handler entry;
- waits either for `RequestContext::ct` or a 250 ms delayed side effect;
- records whether cancellation arrived;
- records whether the side effect completed.

Two controls use the same client/server fixture.

### Case A: Codex-style external timeout

1. Send a request with `PeerRequestOptions::no_options()`.
2. Wrap `RequestHandle::await_response()` in a 50 ms `tokio::time::timeout`.
3. Allow the server another 300 ms.

Observed:

```json
{
  "cancellation_observed": false,
  "side_effect_completed": true
}
```

### Case B: native Rust SDK timeout

1. Send a request with `PeerRequestOptions::with_timeout(50 ms)`.
2. Await the request normally.
3. Allow cancellation propagation to the server.

Observed:

```json
{
  "cancellation_observed": true,
  "side_effect_completed": false
}
```

### Verification

Workflow `30490566255` passed. Fieldwork integrity and external-reference-policy checks also passed on the probe revision.

### What the probe proves

- external timeout and native request timeout have different cancellation semantics;
- the difference exists in the exact `rmcp` release used by the inspected Codex revision;
- a cooperative server can continue and complete a side effect after the Codex-style timeout;
- the Rust SDK's native timeout is a valid cancellation control.

### What the probe does not prove

- that every Codex timeout reaches the server;
- that every server cooperatively stops on cancellation;
- that modern 2026 HTTP request-stream closure behaves the same way;
- that the mismatch causes a process crash;
- that increasing `tool_timeout_sec` repairs the lifecycle mismatch;
- that late side effects are duplicated without an application retry.

## Issue and fix routing

### Confirmed new candidate: Codex outer timeout does not retire the MCP request

**Evidence:** source-observed and executed against exact dependency.

Suggested issue title:

> MCP tool timeout drops the rmcp request without sending cancellation

Proposed invariant:

> When Codex reports an MCP tool call as timed out, the underlying MCP request must also reach a terminal lifecycle state. For legacy MCP this means sending request cancellation; for modern per-request transports it means terminating the request stream. No server work should remain active solely because Codex stopped awaiting the response.

Fix design should remain open to maintainers. Plausible approaches include:

- retain the request handle and explicitly cancel it when Codex's active-time deadline expires;
- add an integration wrapper that combines elicitation-aware active-time accounting with request-handle cancellation;
- use native request options where their clock semantics can be reconciled with Codex's elicitation pause behavior;
- add a cancellation-on-drop guard at the Codex integration boundary rather than changing `rmcp`'s general `RequestHandle` contract.

A plain `tokio::time::timeout` replacement with a longer duration is not sufficient.

### Existing open Codex issue: remote server restart recovery

[Codex issue #22571 — MCP transport should recover after remote MCP server restart](https://redirect.github.com/openai/codex/issues/22571) remains open.

Reported sequence:

- tool works;
- remote server restarts;
- existing Codex session first times out, then reports `Transport closed`;
- fresh clients work;
- current session cannot recreate one MCP connection without a broader restart.

This is separate from request cancellation. It concerns connection-manager recovery and catalog refresh after terminal transport failure.

### Existing open Codex issue: Windows process-tree cleanup

[Codex issue #34614 — duplicate MCP suites and surviving Windows grandchildren](https://redirect.github.com/openai/codex/issues/34614) remains open.

It reports two process-lifecycle modes:

- complete MCP suites repeatedly spawned while older generations remain alive;
- `cmd.exe -> node.exe` grandchildren surviving attempted teardown.

Current Codex source explicitly terminates Unix process groups and uses `taskkill /PID ... /T /F` on Windows, but the live report indicates remaining Desktop/session-generation paths and process-tree cases need platform execution rather than source inference alone.

### Rust SDK session reinitialization hang: already fixed

[Rust SDK issue #912 — session reinitialization orphaned in-flight requests](https://redirect.github.com/modelcontextprotocol/rust-sdk/issues/912) described accepted Streamable HTTP requests hanging forever when 404 recovery aborted the response streams.

[Merged Rust SDK PR #914 — fail orphaned responses on reinitialization](https://redirect.github.com/modelcontextprotocol/rust-sdk/pull/914) tracks accepted request IDs and fails stale requests rather than silently replaying side-effecting calls.

The regression exists in the exact 3.0.0 source tree, so this is not a new Codex dependency gap at the inspected pin.

### Rust SDK stateless disconnect cancellation: already fixed in 3.0.0

[Rust SDK issue #857 — TCP disconnect did not cancel stateless tool handlers](https://redirect.github.com/modelcontextprotocol/rust-sdk/issues/857) was fixed by [merged PR #967](https://redirect.github.com/modelcontextprotocol/rust-sdk/pull/967).

The exact 3.0.0 release includes the disconnect-cancellation regression test. The fix intentionally applies to stateless one-shot HTTP requests. Stateful resumable disconnects remain a separate design problem because disconnect is not automatically cancellation when replay is possible.

### Rust SDK stdio EOF response loss: already fixed

[Rust SDK issue #753 — stdio server dropped in-flight responses on stdin EOF](https://redirect.github.com/modelcontextprotocol/rust-sdk/issues/753) was fixed by [merged PR #759](https://redirect.github.com/modelcontextprotocol/rust-sdk/pull/759).

Do not reuse this closed server-side EOF defect to explain current Codex client timeouts without a new reproduction.

### Historical Codex reports

- [Codex issue #5770](https://redirect.github.com/openai/codex/issues/5770) was traced to a server emitting unsupported SSE event framing. The response appeared in raw logs but was discarded before JSON-RPC routing. This is an interoperability/framing example, not the confirmed outer-timeout mechanism.
- [Codex issue #6127](https://redirect.github.com/openai/codex/issues/6127) reported a tool side effect completing while the caller waited indefinitely and eventually timed out. It was closed as outdated without a precise mechanism. It is symptom support, not duplicate proof.
- [Codex issue #13831](https://redirect.github.com/openai/codex/issues/13831) reported 120-second timeouts followed by `Transport closed`, destroyed stdin and an unavailable Codex process while direct server probes remained healthy. It is a multi-stage host failure report and was closed; the mechanisms were not separated.

## Ranked campaign candidates

### 1. Codex timeout-to-cancellation ownership

**Rank:** highest  
**Status:** confirmed candidate  
**Owner:** Codex integration  
**Why:** exact dependency probe shows caller timeout while server side effect continues.

Next evidence:

1. add a Codex-native regression test around `RmcpClient::call_tool` rather than the extracted ownership model;
2. capture the outbound `notifications/cancelled` count;
3. confirm a subsequent request remains usable;
4. test a never-completing handler to bound pending responder retention;
5. preserve elicitation pause accounting;
6. run stdio and legacy Streamable HTTP controls.

### 2. Codex connection recovery after terminal MCP transport failure

**Rank:** high  
**Status:** existing upstream issue #22571  
**Owner:** Codex connection manager  
**Why:** an otherwise healthy restarted server remains unusable in the existing session.

Next evidence:

1. owned stdio bridge and direct HTTP server fixture;
2. server restart at idle, during `tools/list`, and during `tools/call`;
3. record process identity, connection identity, catalog revision and recovery action;
4. distinguish respawn, session reinitialize and catalog refresh;
5. verify no duplicate side effect is replayed automatically.

### 3. Codex Windows stdio process-tree teardown

**Rank:** high for Windows users  
**Status:** existing upstream issue #34614  
**Owner:** Codex Desktop/process launcher  
**Why:** current report describes duplicate connection generations and surviving command grandchildren.

Next evidence:

1. controlled Windows runner or owned host;
2. `npx` wrapper tree with PID/PPID snapshots;
3. one session replacement and one normal shutdown;
4. verify `taskkill /T` results and Job Object ownership;
5. separate repeated spawning from failed descendant termination.

### 4. Modern 2026 timeout stream-close control

**Rank:** medium  
**Status:** untested scope  
**Owner:** Codex plus `rmcp` integration  
**Why:** modern protocol cancellation uses per-request stream termination rather than legacy notification semantics.

Next evidence:

1. opt Codex and server into `2026-07-28`;
2. time out a streaming HTTP request;
3. record body drop, server request token and handler completion;
4. compare outer timeout with native modern request cancellation;
5. keep conclusions separate from the default legacy result.

### 5. Stateful HTTP disconnect grace and cancellation

**Rank:** medium  
**Status:** design question, not a simple bug packet  
**Owner:** protocol/SDK/application boundary  
**Why:** immediate cancellation on disconnect conflicts with valid resumption; unlimited continuation wastes work.

A useful trial needs explicit reconnect grace, durable acceptance and idempotency rather than treating every dropped socket as cancellation.

## Negative and narrowed results

1. The confirmed Codex timeout mismatch does not demonstrate a Codex process crash.
2. It does not mean the Rust SDK's native timeout is broken; the native control worked.
3. It does not mean every direct server response should be accepted; #5770 was invalid/unsupported SSE event framing.
4. The Rust SDK reinitialization orphan, stateless disconnect cancellation and stdio EOF response loss all have merged fixes.
5. Increasing `tool_timeout_sec` changes when the mismatch occurs but does not make timeout retire the underlying request.
6. A server may ignore cooperative cancellation, so correct client cancellation is necessary but not sufficient for destructive-operation safety.
7. Application idempotency remains required because a user or agent can submit a new request after an ambiguous timeout.

## Recommended immediate action

Promote the confirmed Codex timeout/cancellation mismatch into a dedicated Fieldwork candidate issue with this order:

1. run one Codex-native regression fixture;
2. verify legacy stdio and legacy Streamable HTTP;
3. add the modern 2026 control;
4. search current Codex issues once more using the final observed wording;
5. prepare an issue-first packet owned by Codex integration;
6. keep upstream contact held for explicit authorization.

Treat #22571 and #34614 as existing upstream tracks that deserve owned reproductions and evidence contributions, not duplicate issues.

## Handoff

State: ready for synthesis after the Codex-native follow-up lane is dispatched.

Durable artifacts:

- this report;
- Fieldwork issue #130;
- Fieldwork PR #131;
- exact `rmcp 3.0.0` probe;
- workflow run `30490566255`;
- TypeScript candidates #127 and #128 for cross-SDK comparison.

No upstream contact occurred.
