## In simple words

Current Vercel AI `main` contains a fresh usage-normalization edge that deserves its own bounded follow-up: when an OpenAI-compatible provider reports more reasoning tokens than completion tokens, the SDK now clamps text tokens to zero but can still publish an output total smaller than the reasoning count and a public total-token count smaller than the provider's own raw total.

Two other recent surfaces were worth chasing. The new deterministic harness bridge-token callback does make token derivation repeatable, but live attach still validates and consumes a serialized `bridge.token`; callers seeking durable resume without persisting that bearer value must currently reinsert it into resume state themselves or fall back to a respawn path. The new xAI image-generation server tool also drops its provider-executed call/result from self-managed history, but the introducing change explicitly records that limitation as future work and directs multi-turn editing through `previousResponseId` today.

The usage finding is the strongest distinct branch candidate. A one-file failing characterization is prepared on the owned `teamleaderleo/ai` fork. The harness token question stays research-active until a target-native lifecycle test proves the exact redaction/reattach consequence. The xAI item is retained as known upstream prior art, with no new campaign recommended.

## Scout identity

- Fieldwork lane: #783
- Programme: #13 (`sdk-integration-lifecycle`)
- Target hub: #2 (`vercel-ai`)
- Original broad scout checked for overlap: #17
- Cross-runtime run-authority scout checked for overlap: #528
- Fieldwork base: `2b5e3ce23236e98dbd4c209a70fdfcd03ece8a9a`
- Vercel AI source pin: [`fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`](https://github.com/vercel/ai/commit/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c)
- Retrieved: 2026-08-11
- Claim scope: mechanism and interface
- Upstream contact authorized: `false`

## Existing-work check

The target hub already owns or tracks streaming terminal settlement, explicit abort, resumable Stop/run identity, idle UI delivery, MCP transport/session behavior, WorkflowAgent continuation, async provider jobs/deadlines, framework callback settlement, realtime message processing, and related lifecycle work. #528 separately owns cross-runtime run authority and current async-video polling deadline authority.

This scout therefore avoided those active questions. Searches for `mintBridgeToken`, `BRIDGE_CHANNEL_TOKEN`, bridge credentials, and OpenAI-compatible reasoning-token consistency found no existing Fieldwork finding dedicated to the two retained boundaries below.

## Current-main map sampled

### Bridge-backed harnesses

Recent change: [`#18643`](https://github.com/vercel/ai/pull/18643), merged as the pinned source revision.

Relevant owners:

- `packages/harness-codex/src/codex-harness.ts`
- `packages/harness-codex/src/codex-harness.test.ts`
- `packages/harness-claude-code/src/claude-code-harness.ts`
- `packages/harness/src/agent/harness-agent.ts`
- `packages/harness/src/bridge/index.ts`
- `examples/ai-functions/src/lib/mint-bridge-token.ts`

The bridge server authenticates a WebSocket with `agent_bridge_token`, using `BRIDGE_CHANNEL_TOKEN` as the expected secret. The example deterministic mint is `HMAC-SHA256(secret, sandboxId)`.

### xAI Responses server-side tools

Recent change: [`fa2c2bb004588407f085522be63408819071f0aa`](https://github.com/vercel/ai/commit/fa2c2bb004588407f085522be63408819071f0aa), adding `xai.tools.imageGeneration()`.

Relevant owners:

- `packages/xai/src/responses/xai-responses-language-model.ts`
- `packages/xai/src/responses/convert-to-xai-responses-input.ts`

### OpenAI-compatible usage normalization

Recent fix: [`83e65105d67bc6f4f550c27c654a687342ca6911`](https://github.com/vercel/ai/commit/83e65105d67bc6f4f550c27c654a687342ca6911), PR [`#18614`](https://github.com/vercel/ai/pull/18614).

Relevant owners:

- `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts`
- `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.test.ts`
- `packages/provider/src/language-model/v4/language-model-v4-usage.ts`
- `packages/ai/src/types/usage.ts`

## Candidate 1 — normalized usage can remain arithmetically inconsistent

**Rank: 1 — retain and promote to bounded follow-up.**

### Source mechanism

The regression payload in #18614 is:

```json
{
  "prompt_tokens": 951,
  "completion_tokens": 6000,
  "total_tokens": 6952,
  "prompt_tokens_details": { "cached_tokens": 60 },
  "completion_tokens_details": { "reasoning_tokens": 6001 }
}
```

The change correctly prevents `text = completion - reasoning` from becoming `-1` by returning:

```text
outputTokens.total      = 6000
outputTokens.text       = 0
outputTokens.reasoning  = 6001
```

The PR itself identifies `completion_tokens` as the undercounting field because `total_tokens = prompt_tokens + reasoning_tokens` for the captured incident.

`packages/ai/src/types/usage.ts` then projects provider usage into the public `LanguageModelUsage` and computes:

```text
totalTokens = inputTokens + outputTokens
            = 951 + 6000
            = 6951
```

The raw provider value carried alongside it is `6952`.

So the clamp repairs non-negativity while leaving two public consistency failures on the recorded incident:

1. `outputTokenDetails.reasoningTokens > outputTokens` (`6001 > 6000`);
2. public `totalTokens` is `6951` while raw `total_tokens` is `6952` and prompt + reasoning is also `6952`.

`addLanguageModelUsage` sums public totals and detailed counts independently, so this disagreement can continue into multi-step aggregate usage instead of being confined to one raw provider record.

### Consequence

Consumers commonly use `totalTokens` / `outputTokens` for quota, accounting, telemetry, cost approximation, validation, and usage display. A provider-inconsistent response now avoids a negative field but can still expose an internally impossible vector and undercount the public total relative to the same response's raw evidence.

The consequence is bounded: this requires a provider payload whose completion aggregate undercounts a detailed reasoning field. The merged PR says this has been observed with Baseten/Kimi-K3 and that several recorded xAI fixtures contained the same class of inconsistency.

### Runnable evidence

`probe.mjs` models the exact current conversion and public projection. Executed output is retained in `execution.md`:

```text
usage-invariant: {"internal":{"total":6000,"text":0,"reasoning":6001},"publicTotalTokens":6951,"rawTotalTokens":6952,"delta":1}
```

A target-native one-file failing characterization is prepared on the owned fork:

- carrier: `teamleaderleo/ai#48`
- exact base: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`
- head: `ba9328997cd3a200c8bc4cec8df74320c7662b18`
- file: `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.fieldwork.test.ts`
- state at scout close: test prepared; no CI status registered yet

The carrier asserts both `outputTokens.total >= outputTokens.reasoning` and public `totalTokens === raw total_tokens` for the incident payload. No production repair is proposed there.

### Likely owning boundary

Primary: `convertOpenAICompatibleChatUsage` because it has the raw provider evidence and decides the normalized V4 usage vector.

Secondary: the public projection contract in `packages/ai/src/types/usage.ts` if the project deliberately wants raw provider aggregates preserved even when inconsistent.

### Repair directions to compare, not yet selected

1. **Reasoning floor:** set normalized `outputTokens.total = max(completion_tokens, reasoning_tokens)` when reasoning exceeds completion.
2. **Raw-total reconciliation:** when `total_tokens` is present and sane, derive the output total from `total_tokens - prompt_tokens`, while retaining the raw object.
3. **Provider-fidelity contract:** preserve the inconsistent aggregate exactly, but explicitly define detailed counts as independent observations and stop presenting the projected aggregate as arithmetically self-consistent. This direction would likely need documentation and downstream validation guidance.

A comparison should include inconsistent payloads where `total_tokens` itself is missing or contradictory so one bad aggregate is not blindly privileged over another.

### Reversing evidence

Downgrade this finding if the documented V4/public usage contract explicitly permits `reasoning > output total` and explicitly defines `totalTokens` as a literal recomputation from provider `completion_tokens` even when the raw response proves that field is undercounted. In that case this becomes a documentation/consumer-contract question rather than a normalization defect.

## Candidate 2 — deterministic bridge-token derivation does not by itself make live resume state secret-free

**Rank: 2 — retain as a narrow follow-up question; no campaign yet.**

### Source mechanism

PR #18643 says bridge-backed harnesses previously generated a random authentication token that had to be persisted with resume state and adds `mintBridgeToken(sandboxId)` so callers that deterministically derive a token can reconstruct resume state without storing that secret.

Current implementation establishes three relevant facts:

1. lifecycle bridge coordinates contain `token: string`;
2. `HarnessAgent.createSession()` validates `resumeFrom` against the harness lifecycle schema before handing it to the adapter;
3. on a live attach, bridge-backed adapters use `coords.token`; the new `mintBridgeToken` callback is called for spawn/respawn, not for the existing attach coordinates.

The new Codex unit test makes the intended current behavior explicit: a caller-minted token is included in `session.doDetach()` state, and attaching that state does not call `mintBridgeToken` a second time.

The HMAC example proves the caller can derive the same secret again from `sandboxId`. The lifecycle API, however, still requires the caller to materialize that value into `resumeState.data.bridge.token` before framework validation if the persisted copy was redacted.

### Consequence

An application that wants both:

- live bridge attach/replay semantics; and
- durable storage that excludes the bridge bearer token

must own an out-of-band rehydration step that patches the token back into resume state before `HarnessAgent.createSession()`. Supplying the configured `mintBridgeToken` function alone does not perform that reconstruction on attach.

Dropping bridge coordinates entirely allows a respawn path to mint again, but that can change the recovery rung and, for in-flight continuation, may trade a live attach for replay/rerun behavior.

### Runnable evidence

The local model, transcribed from the schema/attach branch, produced:

```text
bridge-secret-redaction: {"attachUsesPersistedToken":true,"redactedStateValidation":"bridge.token required by lifecycle state schema","derivationAvailableOutsideState":true}
```

This is **model-executed**, not target-executed.

### Next discriminator

Prepare one target-native harness test around the public `HarnessAgent.createSession()` boundary:

1. start with deterministic `mintBridgeToken`;
2. detach a live bridge;
3. persist a copy with `bridge.token` removed;
4. reconstruct a new agent with the same `mintBridgeToken` and pass that redacted state unchanged;
5. record whether validation rejects before the adapter can derive the token;
6. compare with an explicit caller-side rehydration of `bridge.token` and confirm live attach/replay is preserved.

That test decides whether the feature's public contract already provides secret-free reconstruction or merely provides a primitive callers must wire into their own serializer.

### Reversing evidence

Stop if public docs/examples already define caller-side state rehydration as the intended integration contract and a target-native example demonstrates it cleanly. In that case the implementation is behaving as designed and the only residual question is whether the docs make the two-step pattern discoverable.

## Candidate 3 — xAI image-generation self-managed history is a real gap with explicit upstream prior art

**Rank: 3 — stop as an independent Fieldwork campaign.**

The new xAI Responses implementation emits `image_generation_call` as a provider-executed tool call plus tool result. `convertToXaiResponsesInput` skips provider-executed assistant tool calls and does not serialize assistant tool results back into request input.

The executable model therefore converts the representative image-generation history to zero request items:

```text
xai-image-history: {"convertedItems":0,"requiresPreviousResponseIdForRoundTrip":true}
```

The introducing commit already says this directly under **Future Work**: round-trip `image_generation_call` in `convertToXaiResponsesInput` so multi-turn editing works with self-managed message history; today it needs `previousResponseId`, like the other xAI server-side tools.

This is useful target-map evidence, but it is neither novel nor an accidental regression hidden from maintainers. Retain the boundary and avoid opening a duplicate campaign unless the upstream direction stalls and a concrete SDK-level interoperability need appears.

## Negative results and rejected attractive hypotheses

### Custom Claude Code `env` does not overwrite bridge-process control variables

The new `createClaudeCode({ env })` setting looked like it might let caller values override `BRIDGE_CHANNEL_TOKEN` or `BRIDGE_WS_PORT` during bridge startup. Source rejects that hypothesis.

The bridge process spawn environment is built from resolved auth plus internal bridge control variables. `settings.env` is passed later inside the `start` control message, and the sandbox bridge merges it into the Claude Agent SDK query environment. It therefore configures the Claude runtime without replacing the host-to-bridge WebSocket credential used to establish the control channel.

Stop: no campaign.

### Sandbox-id-only HMAC does not establish a cross-session credential collision by itself

The example mint uses only `sandboxId`, which initially suggested that two sessions in one sandbox could share a bridge credential. `HarnessAgent` acquires a sandbox through `createSession({ sessionId })` or `resumeSession({ sessionId })` and separately leases bridge ports. The default contract therefore gives no source-backed evidence that independent live sessions share one `sandboxId`.

A provider-specific sandbox implementation could still reuse ids, but that requires separate evidence. Stop at the generic harness layer.

### Existing run-authority and polling deadline work remains owned elsewhere

Recent async video and harness continuation code overlaps #528. That scout already has exact-source tests and owned-fork carriers for deadline authority. This scout did not reopen those questions.

## Evidence classification

| Boundary | Evidence |
| --- | --- |
| OpenAI-compatible usage consistency | `source-read + model-executed + target-test-prepared` |
| Deterministic bridge-token redaction/attach | `source-read + model-executed` |
| xAI image-generation self-managed history | `source-read + model-executed`; maintainer-provided live-E2E context exists in introducing commit |
| Claude Code env override hypothesis | `source-read` negative result |
| Sandbox-id HMAC collision hypothesis | `source-read` negative result |

No item in this scout is classified `target-executed`, `integration-executed`, or `full-gate`.

## Recommendation

1. **Open a bounded finding/campaign for OpenAI-compatible usage consistency** if the target-native carrier reproduces the expected failures. Compare at least the reasoning-floor and raw-total reconciliation policies before choosing a production patch.
2. **Dispatch one focused harness lifecycle test** for deterministic-token resume-state redaction. Promote only if the public API rejects redacted state without an ergonomic reconstruction path and the consequence survives a real detach/reattach run.
3. **Stop xAI image history as duplicate/prior-art work** and keep the path on the target map for future changes.
4. Keep upstream contact disabled. All writes from this scout remain in Fieldwork and the owned `teamleaderleo/ai` fork.

## Source links

- Vercel AI pin: https://github.com/vercel/ai/commit/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c
- bridge-token feature: https://github.com/vercel/ai/pull/18643
- Codex adapter test: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness-codex/src/codex-harness.test.ts
- HarnessAgent lifecycle validation: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/agent/harness-agent.ts
- shared bridge auth: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/harness/src/bridge/index.ts
- HMAC mint example: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/examples/ai-functions/src/lib/mint-bridge-token.ts
- xAI image-generation feature: https://github.com/vercel/ai/commit/fa2c2bb004588407f085522be63408819071f0aa
- xAI input conversion: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/xai/src/responses/convert-to-xai-responses-input.ts
- usage-normalization fix: https://github.com/vercel/ai/pull/18614
- normalized usage converter: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts
- public usage projection/aggregation: https://github.com/vercel/ai/blob/fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c/packages/ai/src/types/usage.ts
- owned test carrier: https://github.com/teamleaderleo/ai/pull/48
