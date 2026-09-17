# Vercel AI SDK harness bridge lifecycle and auth

## In simple words

The new AI SDK harness layer has two bridge-owned boundaries worth promoting.

First, the public `runBridge()` runtime accepts an empty WebSocket credential when callers supply neither `options.token` nor `BRIDGE_CHANNEL_TOKEN`. Its fallback value becomes the empty string, and a client connecting with `?agent_bridge_token=` passes the equality check. The first-party bridge-backed adapters generate a token, so their ordinary path carries a secret. The public `@ai-sdk/harness/bridge` subpath leaves a misconfigured bridge reachable with an empty credential.

Second, the bridge creates pending promises for host tool results and approval decisions. An inbound `abort` only aborts the turn signal. Those promises remain registered until a matching result or approval arrives. A turn that directly awaits one of them can therefore remain pending after abort, and the resolver stays retained. The host adapter can already have rejected the caller-facing turn by then, which splits caller settlement from bridge cleanup.

A third branch remains promising: cross-process attach gets one initial connection attempt. Any exception falls through to bridge respawn. A transient port-URL or WebSocket-open failure against a live bridge can therefore turn into a spawn collision instead of a bounded reattach retry. This branch needs a target-native injected-failure test before promotion.

Two early ideas lost enough support to stop here. Deterministic `mintBridgeToken(sandboxId)` does not create ordinary cross-session credential reuse because `HarnessAgent` normally creates or resumes one sandbox per session. The bridge-port lease registry is explicitly process-local and documents cross-process coordination as caller-owned.

## Assignment and source boundary

- Fieldwork issue: #786
- Programme: `sdk-integration-lifecycle` (#13)
- Target hub: `vercel-ai` (#2)
- Owned path: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-harness-bridge-lifecycle/`
- Pinned target revision: [`vercel/ai@fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`](https://github.com/vercel/ai/commit/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c)
- Retrieval date: 2026-08-11
- Target interaction: read-only
- Provider credentials: none
- Execution: model-owned Node 22 discriminator plus pinned-source inspection through the GitHub connector
- Environment limit: a target-native clone could not be established because the execution sandbox could not resolve `github.com`; source inspection remained available through the GitHub connector

Evidence labels in this report are **Source-established**, **Observed**, **Inferred**, **Negative result**, and **Unknown**.

## Bottom line

### A — empty bridge token authenticates

**Source-established:** `runBridge()` resolves the expected credential with:

```ts
const expectedToken = options.token ?? procEnv.BRIDGE_CHANNEL_TOKEN ?? '';
```

The WebSocket connection handler accepts a socket when:

```ts
url.searchParams.get('agent_bridge_token') === expectedToken
```

With no configured token, `?agent_bridge_token=` produces the empty string and passes. A missing query parameter produces `null` and fails.

**Observed in the model discriminator:** empty query credential was accepted under the no-token fallback; missing and wrong credentials were rejected. Supplying a real token restored the expected check.

**Reachability:** `@ai-sdk/harness` publicly exports `./bridge`, including `runBridge()`. The first-party Codex/Claude Code/OpenCode/DeepAgents/ACP adapters create a random token by default, so ordinary first-party starts avoid the empty fallback. The exposed low-level bridge API and any misconfigured custom bridge remain affected.

**Candidate fix:** require a non-empty credential before listening. Throw during `runBridge()` startup when both sources resolve to an empty value. Add negative-auth tests for absent, empty, and incorrect values plus the existing positive case.

### B — abort leaves bridge-owned host waits pending

**Source-established:** `requestToolResult(toolCallId)` and `requestToolApproval(approvalId)` create promises whose resolve callbacks are stored in maps. Matching inbound result/approval frames delete and resolve them. The `abort` branch only calls `turnAbort?.abort()`.

**Observed in the model discriminator:** a turn awaiting `requestToolResult()` remained pending after abort, and its resolver stayed in the pending map.

**Source-established at the host adapter:** Codex sends `{ type: 'abort' }` and immediately rejects the caller-facing turn. This means the consumer can see an aborted operation while bridge-owned async work remains alive.

**Source-established in relay users:** Codex and OpenCode host-tool relays await `requestToolResult()`. ACP's host-tool relay also awaits the bridge-owned result promise. The Codex turn driver closes its local relay in `finally`, yet the shared bridge map owns the actual result waiter.

**Historical precedent:** Vercel AI SDK PR [#16595](https://github.com/vercel/ai/pull/16595) fixed the same lifecycle class in MCP: aborting an in-flight request had left a promise pending and a response handler registered. The repair added abort-driven rejection and cleanup.

**Candidate fix:** make pending bridge waits turn-scoped deferreds with both resolve and reject. On abort, reject every pending result/approval wait owned by the active turn and clear the maps. Ignore late result/approval frames after cleanup. Add tests for tool-result waits, approval waits, late frames, and a clean next turn.

### C — initial attach has no retry budget

**Source-established:** `SandboxChannel.open()` performs a single `connectThunk()` call on initial open. Reconnect retry logic only starts after an already-open socket drops.

**Source-established:** bridge-backed adapters attempt live attach from persisted coordinates inside a `try`. Any thrown error falls through to spawn-based recovery. If the previous bridge is still alive on its leased port, that fallback can collide with the live listener.

**Historical precedent:** Vercel AI SDK PR [#16122](https://github.com/vercel/ai/pull/16122) fixed bridge startup hanging on `EADDRINUSE`; a live old bridge makes this failure mode concrete.

**Inferred:** one transient `getPortUrl()` or WebSocket-open failure can skip an otherwise viable live attach and reach respawn. A bounded retry around initial attach would preserve the existing transparent reconnect intent.

**Promotion gate:** target-native injected failure: live bridge, first attach dial fails once, second succeeds. Current behavior should be measured across at least Codex and one other shared-runtime adapter.

## Code and test map

| Boundary | Pinned source | Relevant behavior |
|---|---|---|
| Shared bridge runtime | [`packages/harness/src/bridge/index.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/bridge/index.ts) | WebSocket auth, active-socket replacement, turn state, replay log, pending tool/approval maps, abort/stop/destroy controls |
| Shared bridge tests | [`packages/harness/src/bridge/index.test.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/bridge/index.test.ts) | Positive authenticated connection, replay, host tool result, warnings/errors, stop/destroy; no empty-token or abort-waiter coverage |
| Public package exports | [`packages/harness/package.json`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/package.json) | Exports `@ai-sdk/harness/bridge` publicly |
| Sandbox channel | [`packages/harness/src/utils/sandbox-channel.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/utils/sandbox-channel.ts) | Single initial open; retry loop after an established connection drops; replay cursor |
| Bridge readiness | [`packages/harness/src/utils/bridge-ready.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/utils/bridge-ready.ts) | Startup marker, stdout/metadata readiness, timeout/abort kill |
| Codex host adapter | [`packages/harness-codex/src/codex-harness.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-codex/src/codex-harness.ts) | Live attach, spawn fallback, bridge token minting, host-side abort settlement |
| Codex bridge driver | [`packages/harness-codex/src/bridge/index.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-codex/src/bridge/index.ts) | Abort-aware Codex stream plus host-tool relay lifecycle |
| Codex tool relay | [`packages/harness-codex/src/bridge/tool-relay.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-codex/src/bridge/tool-relay.ts) | Emits host tool call and waits on bridge `requestToolResult()` |
| Codex relay auth | [`packages/harness-codex/src/bridge/tool-relay-auth.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-codex/src/bridge/tool-relay-auth.ts) | One-shot short-lived command authorization and in-flight dedupe |
| OpenCode relay | [`packages/harness-opencode/src/bridge/tool-relay.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-opencode/src/bridge/tool-relay.ts) | Same shared bridge result-wait boundary |
| ACP host relay | [`packages/harness-acp/src/v1/bridge/host-tool-relay.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-acp/src/v1/bridge/host-tool-relay.ts) | Credentialed localhost relay, request validation, awaits active-turn result promise |
| Agent session acquisition | [`packages/harness/src/agent/harness-agent.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/agent/harness-agent.ts) | Fresh sandbox per session or resume by session id; lifecycle validation |
| Agent turn guard | [`packages/harness/src/agent/harness-agent-session.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/agent/harness-agent-session.ts) | Rejects a second prompt while a turn is active |
| Bridge port registry | [`packages/harness/src/agent/internal/bridge-port-registry.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/agent/internal/bridge-port-registry.ts) | Provider-instance keyed, process-local port leases; cross-process coordination delegated to caller |
| Token mint example | [`examples/ai-functions/src/lib/mint-bridge-token.ts`](https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/examples/ai-functions/src/lib/mint-bridge-token.ts) | HMAC(secret, sandboxId) deterministic token example |

## Lifecycle traces

### Fresh bridge start

1. The host adapter creates a random token unless a caller supplies `mintBridgeToken`.
2. The token enters the bridge process as `BRIDGE_CHANNEL_TOKEN`.
3. The bridge binds its WebSocket server and advertises the bound port.
4. The host asks the sandbox provider for a dialable WebSocket URL.
5. The host appends `agent_bridge_token` and opens the channel.
6. The bridge compares the query value against its expected token.
7. An authorized socket becomes the active socket; a later authorized socket replaces it.

The low-level `runBridge()` API can skip step 1 entirely. Its empty fallback creates finding A.

### Host tool result

1. The sandbox runtime initiates a host tool call.
2. The adapter or relay emits a `tool-call` frame.
3. The bridge creates a promise and stores its resolver under `toolCallId`.
4. The host executes the user tool.
5. The host sends a matching `tool-result` frame.
6. The bridge deletes the resolver and settles the promise.
7. The relay returns the value to the sandbox runtime.

### Abort during a host tool wait

1. Steps 1–3 above complete.
2. Caller aborts the host turn.
3. Host adapter sends bridge control `{ type: 'abort' }` and rejects its caller-facing result.
4. Shared bridge aborts `turn.abortSignal`.
5. The pending result resolver remains in `pendingToolResults`.
6. Code directly awaiting `requestToolResult()` still waits until a later result frame arrives.

The same ownership split exists for `requestToolApproval()`.

### Cross-process attach

1. Detach returns live bridge coordinates: port, token, and replay cursor.
2. A new process resumes the sandbox by session id.
3. The adapter asks the provider for the old bridge port URL.
4. `SandboxChannel.open()` performs one initial connection attempt.
5. Success reconnects to the live bridge; continuation can request replay after the saved cursor.
6. Any thrown error causes the adapter's attach rung to fall through to spawn recovery.
7. A still-running old bridge can still own the port when the new spawn starts.

## Model discriminator

Artifact: `probe.mjs`

Captured output: `probe-output.json`

The probe uses the exact two load-bearing predicates from the pinned source without external packages:

- expected-token fallback plus `URLSearchParams.get()` comparison;
- pending result resolver plus abort-signal-only cleanup.

Observed output:

```json
{
  "auth": {
    "missingParam": false,
    "emptyParam": true,
    "wrongParam": false,
    "explicitTokenCorrect": true,
    "explicitTokenEmptyParam": false
  },
  "abort": {
    "signalAborted": true,
    "onStartOutcomeAfterAbort": "still-pending",
    "retainedPendingResolver": true
  }
}
```

This establishes the branch semantics while keeping execution synthetic. The next validation step for both promoted candidates is to transplant equivalent regression tests into an owned Vercel AI fork or a target-native checkout and run the package test matrix.

## Existing coverage and overlap check

### Shared bridge auth

Current shared bridge tests always start with `token: 'test-token'` and connect with that token. I found no test exercising absent or empty token configuration.

GitHub issue searches at the pinned date found no open Vercel AI SDK issue for `BRIDGE_CHANNEL_TOKEN`, empty `agent_bridge_token`, or an empty-token `runBridge()` path.

Historical relay-auth PR [#16432](https://github.com/vercel/ai/pull/16432) concerns a different boundary: token material for local Codex/OpenCode host-tool relays was visible to the sandbox agent. Its fix moved those relays to short-lived observed-call authorization. The shared WebSocket bridge still uses `agent_bridge_token` as its intended gate.

### Abort-owned pending waits

Current bridge tests cover successful `requestToolResult()` settlement. I found no shared bridge test for abort while a result or approval promise is pending.

GitHub issue searches found no open issue matching bridge `requestToolResult` plus abort or host-tool relay abort. The closest precedent is merged PR [#16595](https://github.com/vercel/ai/pull/16595), which fixed an MCP request promise and handler that survived in-flight abort.

## Candidate branches

| Rank | Branch | Evidence | Reach | Next discriminator | Disposition |
|---:|---|---|---|---|---|
| 1 | Empty credential accepted by public `runBridge()` | Source-established + model-observed | Public low-level bridge API; first-party adapters normally pass a secret | Native regression test with missing/empty token, assert startup fails closed | **Promote** |
| 2 | Abort leaves host result/approval waits registered | Source-established + model-observed + analogous merged fix | Shared bridge runtime; Codex/OpenCode/ACP consume result-wait boundary | Native bridge tests for abort, late result, next-turn cleanliness | **Promote** |
| 3 | One-shot attach failure falls into live-port respawn | Source-established + inferred | Bridge-backed adapters with cross-process detach/attach | Inject one transient initial dial failure while old bridge stays alive | **Keep active** |
| 4 | Low-level second `start` can overlap an active turn | Source-established | Direct bridge clients; high-level `HarnessAgentSession` blocks prompt reentry | Raw bridge test sends second `start` during a gated first turn | **Hold** |
| 5 | Deterministic token causes ordinary cross-session auth sharing | Weakened by agent sandbox ownership | Ordinary agent path gives sessions distinct sandbox ids | None | **Negative result** |
| 6 | Port lease registry itself is a fresh cross-process bug | Explicitly documented limitation | Custom cross-process callers | None | **Negative result** |

## Weakened and killed branches

### Deterministic `mintBridgeToken` as cross-session credential reuse

The newest target commit added caller-minted bridge tokens, with an HMAC example keyed by `sandboxId`. At first glance this looked like every bridge in one sandbox could share a credential.

The higher-level agent flow changes the reachability: fresh sessions call the sandbox provider's `createSession()`, while resume uses `resumeSession({ sessionId })`. In the ordinary path, one agent session owns one sandbox session, so `HMAC(secret, sandboxId)` is effectively scoped to that sandbox/session pair.

The current attach tests also persist the bridge token in resume state and reuse it. The new hook enables deterministic reconstruction; it does not automatically remove the token from lifecycle state.

Disposition: useful design caveat for custom providers that multiplex several harness sessions into one sandbox, insufficient as a broad SDK bug.

### Cross-process bridge-port registry

The registry is process-wide and keyed by provider instance. Its source comment explicitly says separate provider instances receive independent registries and cross-process coordination belongs to callers who need it.

Disposition: documented boundary. A provider or future orchestration layer could offer stronger coordination, but this scout should not relabel the stated contract as a fresh defect.

### Concurrent `start` at raw bridge level

The shared bridge handles `start` without checking `currentTurnState`; a raw authorized client can send another `start`, reset the abort controller and replay log, and invoke `onStart` again. That is a real low-level hardening gap.

`HarnessAgentSession.requirePromptableTurn()` rejects a second prompt while the current turn is active, so the normal high-level path blocks this sequence. Abort timing could potentially reopen reachability if the host settles before the bridge finishes unwinding, but this scout has not established that chain.

Disposition: hold behind the two promoted boundaries and the attach probe.

## Proposed test cases

### Empty-token auth

1. `runBridge({ token: undefined })` with `BRIDGE_CHANNEL_TOKEN` absent should reject startup with a credential-configuration error.
2. `token: ''` should reject startup.
3. `BRIDGE_CHANNEL_TOKEN=''` should reject startup.
4. A non-empty `token` should accept the exact token and reject empty/wrong values.
5. Adapter-level smoke test confirms random default remains a 32-byte hex token.

### Abort-owned pending waiters

1. `onStart` awaits `turn.requestToolResult('tc1')`; host sends `abort`; `onStart` settles and pending map becomes empty.
2. Same for `requestToolApproval('a1')`.
3. A late `tool-result` after abort is ignored and does not affect the next turn.
4. A late approval after abort is ignored.
5. Start a clean next turn using the same bridge and reuse the same id; no prior resolver receives the result.
6. Repeat through Codex/OpenCode relay path to ensure the HTTP request is closed or rejected promptly.

### Initial attach retry

1. Start and detach a live bridge.
2. Resume sandbox by session id.
3. Make the first `getPortUrl()` or WebSocket connect fail transiently.
4. Let the second dial succeed.
5. Assert no bridge spawn occurs and continuation replays from the saved cursor.
6. Exhaust retry budget and then verify spawn-based recovery behavior separately.

## Verification status

- Pinned source inspected across shared bridge, channel, agent session, readiness helper, Codex/OpenCode/ACP relays, newest token-mint commit, and relevant tests.
- Model Node 22 discriminator executed successfully; output is committed beside this report.
- Upstream issue overlap searches performed for both promoted findings; no matching open issue found at retrieval time.
- Historical related fixes reviewed: relay auth #16432, bridge bind error #16122, MCP abort-handler leak #16595.
- No upstream write or contact performed.
- No external side effect or provider credential used.
- Target-native package tests remain unexecuted in this environment because the execution sandbox could not resolve GitHub for a clone.

## Handoff

Two branches deserve campaigns or owned-fork regression drafts now:

1. fail closed when bridge authentication resolves to an empty credential;
2. make bridge-owned host result/approval waits abort-aware and clean them before the caller-facing turn can be considered fully settled.

The attach one-shot fallback should get one focused injected-failure experiment before campaign promotion. The remaining branches can stay parked unless those tests expose a stronger chain.