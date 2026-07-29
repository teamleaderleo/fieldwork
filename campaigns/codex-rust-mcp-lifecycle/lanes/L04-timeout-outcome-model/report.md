# L04 — MCP timeout outcome model

State: `claimed`

Programme: `sdk-integration-lifecycle`

Campaign: #133

Parent candidate: #134

Worker: `chatgpt:gpt-5.6-thinking`

Owned Codex implementation: `teamleaderleo/codex#29`

Superseded validation surface: `teamleaderleo/codex#28`

Owned Codex base: `f7265553ea1510304f3091833dcbce65ef21f10c`

Public upstream contact authorized: `false`

## In simple words

An MCP timeout currently arrives at the model as an ordinary failed tool result. That message says Codex stopped waiting. It does not prove that the request stopped, that cancellation reached the server, or that a remote mutation did not commit.

This lane retains those distinctions as typed internal evidence before any retry, compaction, refresh, or fallback policy consumes them.

## Exact question

What is the smallest internal representation that lets Codex distinguish a local `tools/call` deadline from a settled remote result without changing the public tool-call schema or model-visible output?

## Source path

Pinned owned Codex source establishes this path:

```text
codex-rmcp-client::RmcpClient::call_tool
  -> run_service_operation("tools/call", timeout, ...)
  -> private ClientOperationError::Timeout
  -> anyhow::Error

codex-mcp::PreparedMcpCall::call_with_preparation
  -> adds tool/server context while retaining the cause chain

codex-core::handle_approved_mcp_tool_call
  -> converts the error to a string
  -> emits a failed McpToolCallItem
  -> converts it into CallToolResult

codex-core::McpHandler
  -> returns Ok(McpToolOutput)
  -> registry lifecycle can observe a normal returned output
```

The information loss occurs when the typed `anyhow` cause is converted to a string before core retains execution certainty. Public MCP items then have only `inProgress`, `completed`, or `failed`, with an error message.

## Confirmed evidence

The parent #134 probe shows current legacy behavior:

```text
caller deadline reached
cancellation observed by server = false
delayed effect completed = true
follow-up request remained usable = true
```

Therefore:

- a local timeout is not a remote terminal receipt;
- a persisted failed tool output is not proof of non-execution;
- a handler returning a failed `CallToolResult` can still look lifecycle-completed;
- generic string matching is not a safe authority boundary.

## First internal model

Owned Codex PR #29 proposes four states:

```rust
NotDispatched
RemoteResultReceived
LocalFailureUnclassified
LocalTimeoutOutcomeUnknown
```

### `NotDispatched`

Used when core knows the remote call did not start, including invalid local arguments, unavailable prepared binding, disabled policy, and approval decline or cancellation before execution.

### `RemoteResultReceived`

Used only when `PreparedMcpCall` returns a remote `CallToolResult`. This records response receipt. It does not reinterpret the tool's application-level `isError` field.

### `LocalFailureUnclassified`

Conservative state for other local or transport failures whose dispatch and settlement facts have not yet been typed.

### `LocalTimeoutOutcomeUnknown`

Used when the retained `anyhow` cause chain contains `ClientOperationError::Timeout { label: "tools/call" }`.

It means:

```text
Codex stopped waiting after the local active-time deadline.
Remote execution may still be running or may already have committed an effect.
```

## Why the classifier belongs below string conversion

`PreparedMcpCall` adds `anyhow::Context`, but the original typed timeout remains in the cause chain. PR #29 classifies that cause before `handle_approved_mcp_tool_call` formats the error for existing public output.

This avoids:

- parsing localized or reformatted messages;
- coupling receipt safety to telemetry text;
- treating every failure containing the word “timeout” as an MCP execution timeout;
- losing the distinction between `tools/list`, handshake, and `tools/call` deadlines.

## Behavior-neutral first slice

PR #29 deliberately does not change:

- model-visible function-call output;
- Code Mode result JSON;
- `McpToolCallItem` public status or error schema;
- app-server or SDK generated schemas;
- retry behavior;
- compaction readiness;
- session-expiry recovery;
- MCP refresh or rebinding;
- fallback selection.

The candidate includes a regression requiring identical direct and Code Mode outputs for the same failed result tagged as ordinary local failure or timeout outcome-unknown.

## Relationship to adjacent work

### #134 — cancellation mechanics

#134 owns whether legacy cancellation is sent, whether modern request-stream closure is terminal, whether cancellation delivery is bounded, and what the server observes.

This lane does not infer those facts. It only provides a typed place to retain them.

### #83 — mutation identity and compaction

#83 may later map `LocalTimeoutOutcomeUnknown` to an ambiguous or may-still-run receipt. It must not consume this candidate until the exact source head passes and transport evidence from #134 is available.

### Codex PR #25 — generic terminal semantics

PR #25 conservatively maps handler-executed failures and unconfirmed aborts to ambiguity. It does not cover an MCP timeout returned as a normal failed output. PR #29 supplies the missing MCP-specific evidence.

## Retry and authority rules

The first slice authorizes no retry.

Future policy must satisfy all of these:

1. Preserve the original call and authority identity.
2. Do not trust arbitrary-server `readOnlyHint` or `idempotentHint` as proof.
3. Require a host trust policy, durable idempotency contract, or reconciliation read before replaying a potential mutation.
4. Treat cancellation delivery as a fact, not proof that the effect did not commit.
5. Require a new sampled step after runtime or authority changes.

## Negative results

- No public schema extension is justified by this first slice.
- No distinct public `timedOut` status is proposed yet.
- No cancellation-delivered state is claimed before #134 completes its transport matrix.
- No automatic retry is safe merely because the local failure is typed.
- No upstream issue, PR, comment, reaction, branch, or message was created.

## Validation plan

Owned Codex PR #29 runs:

```text
codex-rmcp-client typed cause classification
core execution-state mapping
behavior-neutral direct and Code Mode output
Rust formatting
git diff --check
```

The branch remains draft until a source-only head replaces its temporary validation carrier and the exact Rust diff is reviewed. PR #28 remains closed and contains no accepted implementation result.

## Next bounded steps

1. Finish and review the behavior-neutral internal type.
2. Consume #134 results for cancellation requested, delivered, observed, and transport-terminal facts.
3. Add a typed core outcome that can carry those facts without exposing arguments, output bodies, credentials, or resource names.
4. Map the typed outcome into #83 receipt terminal certainty.
5. Only then evaluate whether public protocol consumers need structured error detail or a new status.

## Stop condition

Stop this lane when compiled owned-fork tests prove that local MCP timeouts remain outcome-unknown internally while existing public/model output stays compatible, and the resulting type can be consumed by receipt logic without string parsing or unsafe replay.
