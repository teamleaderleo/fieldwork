# L02 — Responses transport and startup-prewarm tool continuity

State: `complete`

Issue: #37  
Campaign: #31  
Draft synthesis base: #51  
Owned path: `campaigns/0002-tool-surface-continuity/lanes/L02-responses-transport-prewarm/`  
Worker: GPT-5.6 Thinking operating as `@teamleaderleo`  
Upstream contact authorized: `false`

## In simple words

HTTP and WebSocket build the same logical Responses request. The first deterministic transport difference appears later, when WebSocket startup prewarm is reused through `previous_response_id`.

For ordinary Responses requests, tools remain in the top-level `tools` field, so an incremental WebSocket request repeats them. For Responses Lite, tools are encoded as an `additional_tools` item at the front of `input`. A clean startup-prewarm handoff can remove that already-sent prefix from the first real turn and send only the compacted history plus new user input. HTTP, a fresh WebSocket thread, a reconnect, and a restart send the `additional_tools` item directly.

That makes the first real Responses Lite turn depend on the server retaining the tool declaration from a `generate=false` prewarm response. The public client source also permits this reuse while changing request metadata from `prewarm` to `turn`, because `client_metadata` is deliberately excluded from the reuse comparison.

The client source rejects reuse when the tool list changes, clears reuse state on reconnect, and sends the full request after restart. The remaining live question is whether the affected server or host route fails to carry the prewarm tool state into the first generated response, or whether the normal turn's logical request was already reduced before transport selection. Full effective-tool digests at the shared request-builder boundary will separate those cases.

## Question and supported claim scope

**Question:** Can startup prewarm, `previous_response_id`, request reuse, sticky routing, or `additional_tools` serialization retain an empty or reduced capability surface for one thread while HTTP or a fresh WebSocket thread builds the expected surface?

**Supported scope:**

- **Mechanism, observed from public source:** request construction, incremental reuse, serialization, reconnect reset, and startup-prewarm handoff.
- **Interface, reproduced by retained fixture:** the HTTP/full-WebSocket versus prewarm-incremental wire difference for Responses Lite.
- **Server consequence, inferred:** tool loss follows if a `generate=false` prewarm response fails to retain inherited `additional_tools` state.
- **Operational cause in the reported IDE case, unknown:** the public issue lacks full sanitized `additional_tools`, logical-request digests, response-routing identifiers, and server traces.

## Revisions and retrieval boundary

| Item | Revision / boundary | Retrieval date |
|---|---|---|
| Fieldwork synthesis base | `teamleaderleo/fieldwork@aa72bd513f6664dc67517dabd9b03b4f051d8460` (draft PR #51 head) | 2026-07-29 |
| Public Codex source | [`openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc) | 2026-07-29/30 |
| Owned Codex comparison | [`teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`](https://github.com/teamleaderleo/codex/commit/2b7b93081361b77f8ddaceaf362a09765b4153bf) | 2026-07-30 |
| Public symptom report | [`openai/codex#35751`](https://redirect.github.com/openai/codex/issues/35751) | 2026-07-30 |

The owned comparison revision has the same startup-prewarm file blob (`abffe19313943de4f493466bc906a54100313774`) and the same sampled reuse predicate. Its full `client.rs` blob differs, so conclusions remain pinned to the declared public revision and only use the owned revision as a corroborating snapshot.

## Source path map

### 1. Startup prewarm builds a separate prompt snapshot

[`codex-rs/core/src/session_startup_prewarm.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session_startup_prewarm.rs#L252-L333)

- Creates a startup turn context with `INITIAL_SUBMIT_ID`.
- Captures a startup `StepContext` and its tool router before `run_turn`.
- Builds a prompt with empty conversation history.
- Marks metadata as `CodexResponsesRequestKind::Prewarm`.
- Sends a WebSocket `response.create` with `generate=false` and returns the populated `ModelClientSession`.

### 2. The first regular turn consumes the prewarmed client session

[`codex-rs/core/src/tasks/regular.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tasks/regular.rs#L40-L95)

A ready prewarm session is passed into `run_turn`. A cancelled or unavailable prewarm produces the regular fresh-session path.

### 3. The normal turn captures a fresh step and tool router

[`codex-rs/core/src/session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L155-L216)

`run_turn` reuses the transport session, then separately captures the real first-turn `StepContext`, including required MCP servers. Later sampling clones conversation history and builds the prompt from that normal step. The startup router object is never reused as the normal turn router.

### 4. HTTP and WebSocket share one logical request builder

[`codex-rs/core/src/client.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/client.rs#L838-L932)

`build_responses_request` is called by both transports.

- Responses Lite: prepend `ResponseItem::AdditionalTools` and a developer instruction to `input`; set top-level `tools` to `None`.
- Other Responses requests: place tools in the top-level `tools` field.

Therefore `top-level tools_count=0` is expected for Responses Lite and cannot establish a missing effective tool surface.

### 5. WebSocket reuse compares the logical tool surface before taking a delta

[`codex-rs/core/src/client.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/client.rs#L307-L360)

The non-input reuse predicate compares model, instructions, top-level tools, tool choice, parallel-tool setting, reasoning, store, stream, include, service tier, cache key, and text. It deliberately ignores `client_metadata` and `stream_options`.

[`codex-rs/core/src/client.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/client.rs#L1180-L1260)

The input check requires the current input to start with the prior request plus server-returned output. For Responses Lite, the `AdditionalTools` item participates in this prefix comparison. A changed tool list therefore rejects reuse and causes a full request.

### 6. Incremental WebSocket creation is the first deterministic wire divergence

[`codex-rs/core/src/client.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/client.rs#L1529-L1701)

After the shared request is built, WebSocket may attach `previous_response_id` and replace `input` with only the incremental suffix. `ResponseCreateWsRequest::from(&request)` preserves all non-input fields.

[`codex-rs/codex-api/src/common.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/codex-api/src/common.rs#L253-L331)

For non-Lite requests, top-level tools are repeated even during incremental creation. For Responses Lite, tool declarations live in the input prefix and can disappear from the first real turn's direct wire payload when inherited through `previous_response_id`.

### 7. Prewarm and turn metadata differ while reuse remains eligible

[`codex-rs/core/src/responses_metadata.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/responses_metadata.rs#L121-L179)

Metadata explicitly distinguishes `Prewarm` and `Turn`, and carries `code_mode_tool_names`. The reuse predicate ignores `client_metadata`, so this request-kind transition does not force a full first-turn request.

### 8. Reconnect and fallback clear request-reuse state

[`codex-rs/core/src/client.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/client.rs#L1317-L1364)

When the socket is closed or absent, connection setup clears the prior request, prior response receiver, and warmup marker before reconnecting. HTTP fallback also replaces the cached WebSocket session with a default session.

## Existing public tests

The pinned suite already establishes several parts of the mechanism:

- [`responses_websocket_request_prewarm_reuses_connection`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/tests/suite/client_websockets.rs#L466-L544) asserts a `generate=false` prewarm followed by `previous_response_id=warm-1` and an empty incremental input when the prompt is unchanged.
- [`responses_websocket_forwards_turn_metadata_on_initial_and_incremental_create`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/tests/suite/client_websockets.rs#L1734-L1815) shows different turn metadata can accompany an incremental request.
- [`responses_websocket_creates_when_non_input_request_fields_change`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/tests/suite/client_websockets.rs#L1941-L1974) asserts changed compared fields force a full request.
- [`responses_websocket_v2_after_error_uses_full_create_without_previous_response_id`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/tests/suite/client_websockets.rs#L2056-L2145) covers a failed connection followed by a full request on a new connection.
- [`websocket_model_switch_to_responses_lite_omits_top_level_tools`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/tests/suite/agent_websocket.rs#L27-L128) verifies that Responses Lite sends no top-level tools and begins full input with a nonempty `additional_tools` item.
- [`websocket_first_turn_uses_startup_prewarm_and_create`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/tests/suite/agent_websocket.rs#L180-L235) exercises startup prewarm and confirms the real turn carries populated top-level tools in the non-Lite configuration.

No pinned public test combines all four properties: resumed compacted history, Responses Lite `additional_tools`, startup prewarm inheritance, and a benign tool call.

## Retained same-history fixture

Files:

- `artifacts/same_history_transport_fixture.py`
- `artifacts/fixtures/same_history.json`
- `artifacts/results/latest.json`

The fixture models the exact source-defined request transformation. It does not emulate private OpenAI service behavior.

Commands run from this lane directory:

```bash
python3 artifacts/same_history_transport_fixture.py \
  --fixture artifacts/fixtures/same_history.json \
  --output artifacts/results/latest.json
python3 -m py_compile artifacts/same_history_transport_fixture.py
sha256sum artifacts/same_history_transport_fixture.py \
  artifacts/fixtures/same_history.json \
  artifacts/results/latest.json
```

Recorded SHA-256 values:

```text
82f45fb7dde94a75803f1dba319ad7e2b85a939eff9315ec8daca90d10d79d8b  artifacts/same_history_transport_fixture.py
c351cf4459258773ad9f747360bb8a6ec04545315cdf118a4d9b6807bb15a619  artifacts/fixtures/same_history.json
55635fd332c06180bbf59593897d9b0717c49e81040232dadd34e405c05a150c  artifacts/results/latest.json
```

### Control matrix

| Case | `previous_response_id` | Tools directly present on wire | Result |
|---|---:|---|---|
| Same-history HTTP, Lite | absent | `additional_tools: [exec, file_edit]` | benign probe `TOOL_OK` |
| Fresh-thread WebSocket, Lite | absent | `additional_tools: [exec, file_edit]` | benign probe `TOOL_OK` |
| Clean-prewarm WebSocket, Lite | `warm-lite` | none; compacted history and user item only | `TOOL_OK` only when inherited prewarm state holds |
| Changed-tools WebSocket, Lite | absent | full updated `additional_tools` | reuse rejected; benign probe `TOOL_OK` |
| Reconnect WebSocket, Lite | absent | full `additional_tools` | benign probe `TOOL_OK` |
| Restart WebSocket, Lite | absent | full `additional_tools` | benign probe `TOOL_OK` |
| Clean-prewarm WebSocket, non-Lite | `warm-non-lite` | top-level `[exec, file_edit]` | benign probe `TOOL_OK` |

The clean-prewarm Responses Lite case is the only control whose first generated turn carries no direct tool declaration. Its logical tool digest remains `3444399af101141c`, while its direct-wire tool digest is the empty-list digest `4f53cda18c2baa0c`.

## Earliest divergence and defect separation

### Earliest deterministic divergence

**Point:** `ModelClientSession::prepare_websocket_request` / `stream_responses_websocket`, after the shared logical request has been built.

**Difference:** HTTP sends full input. A clean prewarmed Responses Lite WebSocket request sends `previous_response_id` plus only the input suffix, omitting the `AdditionalTools` and developer-instruction prefix.

### Client request construction

No request-construction defect was established at the pinned revision. HTTP and WebSocket call the same builder, and direct WebSocket serialization preserves the request fields. A changed logical tool surface blocks reuse.

### Client state reuse

A real compatibility dependency is established:

1. Responses Lite places tools in input.
2. Startup prewarm creates a server response with `generate=false`.
3. The first real turn can inherit that input through `previous_response_id`.
4. Request-kind and other client metadata differences do not participate in reuse eligibility.

This can be treated as a client-side repair boundary even when the ultimate failure resides in server state retention.

### Server routing or response-state reuse

Server behavior remains unknown from public evidence. The reported symptom follows if either condition holds:

- `generate=false` response state does not retain Responses Lite `additional_tools` for later `previous_response_id` use; or
- a prewarm route/profile associated with the previous response overrides or loses the real turn's code-mode capability metadata.

Those are inferences. The public source and issue do not expose the server implementation or complete request/response traces.

### Earlier client/host tool construction

A second branch remains open: the affected resumed thread may build a reduced normal `StepContext` before transport. This branch is falsified when HTTP and WebSocket logical-request tool digests match at `build_responses_request`. The issue's existing top-level tool count cannot perform that comparison for Responses Lite.

## Negative findings

- The startup tool router object is not reused as the real turn's tool router.
- A changed top-level tool list blocks incremental reuse.
- A changed Responses Lite `AdditionalTools` item breaks the input prefix and forces a full request.
- Non-Lite incremental WebSocket requests repeat top-level tools.
- Reconnect and restart controls clear or lack the previous response chain and send full requests.
- WebSocket serialization itself preserves supplied top-level tools.
- A zero top-level tool count is expected for Responses Lite and does not measure the effective tool surface.
- The retained fixture reproduces the inheritance dependency, not the private service failure.

## Repair candidates

1. **Targeted client mitigation:** For the first generated Responses Lite turn after startup prewarm, send a full request without `previous_response_id`, or retransmit the `AdditionalTools` prefix. This removes reliance on `generate=false` state retention while preserving later incremental reuse.
2. **Regression test:** Add a startup-prewarm test using Responses Lite, compacted replacement history, a nonempty `additional_tools` manifest, and a benign shell/tool call. Assert both the request sequence and successful tool execution.
3. **Reuse-contract check:** Include the `Prewarm` → `Turn` request-kind transition in reuse eligibility unless the server contract explicitly guarantees that prewarm response state is capability-complete and reusable.
4. **Server repair:** Guarantee that `generate=false` response state retains Responses Lite tool declarations and applies the current turn metadata when resolving `previous_response_id`.
5. **Diagnostics:** Record a canonical effective-tool digest at the shared logical request boundary and a second digest for direct wire declarations, together with transport, request kind, `previous_response_id`, connection reuse, model, and response id. This cleanly distinguishes request construction from inherited server state.

## Public report comparison

The public report states that the same compacted history fails on resumed WebSocket, works over HTTP, and works in a fresh WebSocket thread. That pattern matches the inheritance-only seam identified here. The report also cautions that top-level tools may be empty for Responses Lite. Since the raw rollout and complete payloads remain private, this lane cannot establish whether the affected logical `AdditionalTools` manifest was complete before incremental preparation.

## Handoff

- **Strongest finding:** Responses Lite startup-prewarm reuse creates a deterministic wire-level capability dependency: the first generated WebSocket turn may omit `AdditionalTools` and inherit them from a `generate=false` response, while HTTP and all clean-state controls transmit them directly.
- **Durable artifacts:** this report, fixture, fixture input, and recorded output under the owned L02 path.
- **Unresolved uncertainty:** whether the private server loses inherited tool state, or the affected host constructs a reduced logical request before transport.
- **Decision:** retain for campaign synthesis and prioritize a targeted full-first-turn Responses Lite control plus paired logical/wire tool digests.
- **Upstream contact:** unauthorized and untouched.
