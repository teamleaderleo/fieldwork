# Vercel AI SDK provider and server-tool scout — 2026-08-11

## In simple words

Two fresh branches survived this scout.

1. `@ai-sdk/google-vertex` sends Chirp 3 HD speech requests to the global Cloud Text-to-Speech host even when the provider is configured with `location: 'eu'` or `location: 'us'`. Current Google Cloud documentation says those regional endpoints exist for Chirp 3 HD, keep data within the selected continental boundary, and can be enforced by organization policy. This can defeat a caller's location intent and can fail outright where global endpoint use is blocked.
2. `@ai-sdk/xai` now exposes xAI's provider-executed image-generation tool, including edit mode, but self-managed message replay drops the generated-image call/result before the next request. Stateful continuation with `previousResponseId` works; local-history continuation cannot currently carry the generated image forward for another image edit. The implementation commit itself records this as future work.

A third suspicion around Google's enum conversion was challenged and killed. Numeric and boolean enum values being encoded as strings looks strange beside generic JSON Schema, but the current implementation was added specifically for Gemini's schema format, has focused regression coverage, and carries an end-to-end literal-output example that succeeds.

This scout stayed read-only against the public Vercel repository. Target-native characterization tests live only on the owned `teamleaderleo/ai` fork as a disposable verification carrier.

## Claim

- Fieldwork lane: #839
- Programme: #13
- Target hub: #2
- Worker: `chatgpt:gpt-5.6-sol`
- Public target: `vercel/ai`
- Pinned revision: `7d40fafc394a2c9033f931eb85c895e3817f4b58`
- Retrieval boundary: `2026-08-11`
- Scope: recent provider conversion, routing, and provider-executed tool behavior
- Upstream contact authorized: `false`
- Upstream mutation performed: `false`

## Scout map

### xAI Responses image generation

Primary files:

- `packages/xai/src/responses/xai-responses-language-model.ts`
- `packages/xai/src/responses/convert-to-xai-responses-input.ts`
- `packages/xai/src/responses/xai-responses-api.ts`
- `packages/xai/src/responses/xai-responses-language-model.test.ts`
- `packages/xai/src/responses/convert-to-xai-responses-input.test.ts`

Relevant implementation history:

- public commit `fa2c2bb004588407f085522be63408819071f0aa`

The response side converts `image_generation_call` into an SDK provider-executed tool call plus a tool result containing the base64 image and model-written image prompt. The request converter then skips provider-executed assistant tool calls and assistant tool results during replay.

### Google Vertex Chirp 3 HD

Primary files:

- `packages/google-vertex/src/google-vertex-provider-base.ts`
- `packages/google-vertex/src/google-vertex-cloud-tts-speech-model.ts`
- `packages/google-vertex/src/google-vertex-cloud-tts-speech-model.test.ts`

Relevant implementation history:

- public commit `6d9951bd08b5e76d4838ed412cdb31e82d223d23`

The provider knows `location` and builds region-aware Vertex URLs for its other model paths. The Chirp branch creates the regular speech config and then passes only provider name, headers, and fetch into a Cloud TTS model that hardcodes `https://texttospeech.googleapis.com/v1/text:synthesize`.

### Google enum conversion

Primary files:

- `packages/google/src/convert-json-schema-to-openapi-schema.ts`
- `packages/google/src/convert-json-schema-to-openapi-schema.test.ts`
- `examples/ai-functions/src/generate-text/google/output-object-literals.ts`

Relevant implementation history:

- public commit `da78d58ebac4393f2448bde307f15201a82f7f98`

This path was sampled because the converter emits string-valued enum members for numeric and boolean literals. The history and end-to-end example support the implementation, so this branch is recorded as a negative result.

## Finding 1 — Google Vertex Chirp bypasses configured location

### Current behavior

`GoogleVertexProviderSettings.location` feeds `loadBaseURL()` for Vertex calls, including special `eu` and `us` hosts. `createSpeechModel()` detects IDs beginning with `chirp`, creates a speech config, and constructs `GoogleVertexCloudTTSSpeechModel` without passing either the location or the derived base URL.

`GoogleVertexCloudTTSSpeechModel` owns a constant endpoint:

```text
https://texttospeech.googleapis.com/v1/text:synthesize
```

Its focused test explicitly expects that global host.

### External contract

Google Cloud's current Cloud Text-to-Speech endpoint documentation says:

- Cloud TTS offers global, US, EU, and regional endpoints;
- Chirp 3 HD is available on the US and EU multi-region endpoints;
- using a regional endpoint keeps data at rest and in use within the selected continental boundary;
- EU synthesis uses `https://eu-texttospeech.googleapis.com`;
- US synthesis uses `https://us-texttospeech.googleapis.com`;
- organization policy can restrict use of the global endpoint.

Reference: https://docs.cloud.google.com/text-to-speech/docs/endpoints

The page was last updated `2026-07-30 UTC` when retrieved for this scout.

### Consequence

A caller can configure:

```ts
createGoogleVertex({
  project: 'example-project',
  location: 'eu',
}).speech('chirp-3-hd');
```

and still send the speech text to the global Cloud TTS endpoint. That creates two concrete consequences:

1. the request does not honor the caller's continental endpoint intent;
2. an organization that blocks the global endpoint can reject a Chirp request that could have used the documented EU or US endpoint.

The same branch also ignores `GoogleVertexProviderSettings.baseURL`. That is a secondary interface mismatch worth testing separately because the option is documented as the base URL for Google Vertex API calls while Chirp targets Cloud TTS.

### Owning boundary

`@ai-sdk/google-vertex` speech routing and Cloud TTS model configuration.

A narrow candidate would begin with `location: 'eu'` and `location: 'us'`, where Google's endpoint mapping is explicit. Single-region mapping should follow the provider's documented support matrix instead of guessing from Vertex location names.

### Executable discriminator

Owned-fork characterization test:

- `packages/google-vertex/src/fieldwork-chirp-regional-routing.test.ts`
- carrier branch: `teamleaderleo/ai@fieldwork/839-provider-tool-probes`

The probe records the fetch URL for `location: 'eu'` and proves current main targets the global host. A second case proves a configured Vertex `baseURL` is also bypassed.

Negative control / reversing evidence:

- if a current target test showed `location: 'eu'` selecting `https://eu-texttospeech.googleapis.com`, this finding would be reversed;
- if the public provider contract explicitly declared `location` irrelevant to Chirp and exposed a separate Cloud TTS endpoint selector, the interface claim would need reframing;
- Google's current endpoint documentation supports the regional behavior and regulatory consequence.

### Recommendation

**Promote to a focused campaign.** Start with EU/US multi-region selection and a regression test that captures the request URL. Keep custom `baseURL` handling as a second question inside that campaign.

## Finding 2 — xAI image-generation replay loses generated images

### Current behavior

The new xAI image-generation server tool maps provider output into:

- a provider-executed SDK tool call; and
- an SDK tool result carrying the image base64 payload and model-written image prompt.

When the next request is built from self-managed messages, `convertToXaiResponsesInput()`:

- skips an assistant tool call when `providerExecuted` is true;
- skips assistant tool-result parts;
- keeps the assistant's ordinary text.

The xAI Responses input type union also lacks an `image_generation_call` input item on current main.

Existing converter tests already characterize the general server-tool behavior by dropping provider-executed tool calls from replay.

### Why image generation makes this consequential

The image-generation feature exposes `action: 'edit'` for editing images already in the conversation, including images generated by the model. The implementation commit's own end-to-end coverage exercises multi-turn image editing with `previousResponseId` and explicitly lists self-managed round-trip support as future work.

That gives this scout a crisp split:

- server-managed continuation via `previousResponseId`: supported and live-tested by the feature change;
- self-managed continuation by replaying local messages: generated-image call/result is removed before the provider request.

xAI's Responses documentation describes stateful continuation and also says callers who retain response history locally can pass that history in a later request. Reference: https://docs.x.ai/developers/model-capabilities/text/generate-text

### Consequence

An application that persists its own AI SDK message history cannot rely on replay to perform a later edit of an image generated by the xAI server tool. The local transcript still has the SDK tool result, but the xAI request converter removes the provider-executed image event/result from the provider payload.

This is especially relevant to durable chats, databases that persist AI SDK messages, migrations away from provider-side retention, and conversations that need to outlive provider response retention.

### Owning boundary

`@ai-sdk/xai` Responses input conversion and request-side API item types.

### Executable discriminator

Owned-fork characterization test:

- `packages/xai/src/responses/fieldwork-image-generation-roundtrip.test.ts`
- carrier branch: `teamleaderleo/ai@fieldwork/839-provider-tool-probes`

The test builds a local conversation containing a provider-executed `image_generation` call/result followed by a user request to edit it. The converter output contains the original user text, assistant text, and new user text while omitting the image-generation call/result.

Negative control:

- a normal client-executed function call is preserved as a `function_call` item.

Reversing evidence:

- support for `image_generation_call` request items plus a round-trip test that retains the generated image would reverse the current finding;
- a provider API restriction making image calls impossible to replay would change the candidate into a documentation/API-capability issue;
- current implementation history explicitly names this round-trip work as future work, which supports retention of the candidate.

### Recommendation

**Promote to a focused campaign or direct implementation lane.** The intended direction is already recorded in the feature history, so the next useful work is a current-head request-format probe and a failing regression around self-managed image edit replay.

## Negative result — Google primitive enum conversion

### Suspicion

The Google schema converter maps numeric and boolean enum values to strings and marks them with `format: 'enum'`. Seen in isolation, that can look like type corruption.

### Challenge

The change that introduced this behavior says the previous form caused a Gemini API error because the Google Schema form requires a type and represents enum members as strings. It adds regression cases for:

- number literals;
- integer enums;
- boolean literals;
- nullable primitive enums;
- untyped primitive enums;
- mixed-type rejection.

It also adds an end-to-end `generateText` example using a string literal, number literal, boolean literal, and number-literal union, with the commit recording that the previously failing schema now works.

### Disposition

**Kill this branch.** The odd-looking encoding is compatibility behavior with direct test and end-to-end evidence. Reopen only with a concrete Gemini request that accepts a better representation or rejects the current one.

## Additional sampled paths with no branch retained

### provider-utils fetch-less import

The recent `safe-node-fetch` change guards inspection of `globalThis.fetch` with a function-type check before calling `Function.prototype.toString`. Code inspection found the reported import crash addressed directly and no adjacent consequence strong enough for this scout.

### GMI Cloud nested error detail unwrapping

The new provider parses the proxy's JSON-encoded `error.details` with `secureJsonParse`, extracts a nested message when valid, and falls back to the outer message otherwise. Focused fallback behavior is visible in the implementation; no distinct branch survived this pass.

These are retained here as negative search results so later scouts can start beyond them.

## Target-native verification carrier

Owned repository: `teamleaderleo/ai`

Branch: `fieldwork/839-provider-tool-probes`

Pinned branch base: public target revision `7d40fafc394a2c9033f931eb85c895e3817f4b58`

Draft PR: `teamleaderleo/ai#88`

The fork's `main` branch is older than the pinned public target, so the draft PR has a deliberately noisy comparison. It exists only to trigger the target repository's native CI. It is not a delivery PR and should not be merged.

Characterization files:

- `packages/xai/src/responses/fieldwork-image-generation-roundtrip.test.ts`
- `packages/google-vertex/src/fieldwork-chirp-regional-routing.test.ts`

At report write time, the fork CI workflow was queued. Evidence status is therefore:

- source inspection: **executed**;
- focused existing tests/history inspection: **executed**;
- owned-fork characterization tests: **prepared, CI pending**;
- live provider request: **not executed by this scout**;
- external protocol/documentation check: **executed**.

The source-level discriminators are deterministic even before CI completes because both probes assert current request-conversion/routing code directly. CI completion should be attached to #839 when available.

## Ranked branches

| Rank | Branch | Consequence | Evidence strength | Likely owner | Next move |
| --- | --- | --- | --- | --- | --- |
| 1 | Google Vertex Chirp ignores `eu` / `us` endpoint intent | residency/compliance mismatch and possible request rejection under global-endpoint policy | source + focused tests + current official endpoint docs + prepared target-native probe | `@ai-sdk/google-vertex` | open focused campaign |
| 2 | xAI image generation cannot round-trip through self-managed history | durable/local-history image editing loses prior generated-image context | source + focused tests + feature history explicitly naming future work + prepared target-native probe | `@ai-sdk/xai` | open focused campaign or direct implementation lane |
| 3 | Google numeric/boolean enum stringification | suspicion disproved | source + regression suite + recorded end-to-end example | `@ai-sdk/google` | stop |

## Stop condition

Satisfied.

Three distinct recent boundaries were challenged against implementation, tests, history, and the current Fieldwork portfolio. Two survived with concrete consequences and executable discriminators. One attractive suspicion was disproved and recorded. Additional recent provider-utils and GMI Cloud paths were sampled without retaining weaker branches.

## Suggested handoff

1. Promote the Google Vertex Chirp regional-endpoint branch first.
2. Promote the xAI self-managed image-generation round-trip branch independently; it has a different owner and mechanism.
3. Preserve the Google enum result as a killed hypothesis.
4. Attach the owned-fork CI result to #839 once the queued run resolves.
5. Keep upstream contact disabled until a delivery lane reaches Fieldwork's upstream-contact gate.
