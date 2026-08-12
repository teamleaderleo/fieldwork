# Vercel AI xAI video reference routing scout

## In simple words

Current Vercel AI main added `grok-imagine-video-1.5` and treats it as capable of text-to-video, image-to-video, editing, extension, and reference-to-video. Current xAI documentation gives that model a narrower contract: image-to-video is the highlighted 1.5 path, the model page says text-to-video is unsupported, and the reference-to-video guide explicitly says 1.5 does not support that mode.

The same Vercel change also introduced first-class `inputReferences` handling. That path has a separate precedence edge: any non-empty first-class list takes ownership over legacy `referenceImageUrls`, even if every first-class entry is unusable for reference-to-video. A valid legacy image list can therefore disappear from the outgoing request.

A third gap is representational rather than a local defect: xAI now accepts private Files API `file_id` inputs anywhere Imagine accepts URL/base64, including mixed reference-to-video inputs. Vercel's generic video file type and xAI provider options currently have no way to retain that file identity; the introducing Vercel commit names `file_id` support as future work.

The strongest next campaign is the 1.5 capability matrix because the public provider contract and the emitted request disagree about which remote operations exist. File-id support is a distinct missing capability. The mixed-reference precedence question should stay narrower until the target characterization settles and project intent is reviewed.

## Assignment

- Fieldwork issue: #863
- Programme: #13 — SDK behaviour and integration
- Target hub: #2 — Vercel AI SDK
- Worker: `chatgpt:gpt-5.6-sol`
- Pinned public Vercel AI revision: `dcf33e816a75de7fd4fad0637e1c1f370b21e7f7`
- Retrieval date: 2026-08-12
- Claim scope: mechanism and interface
- Owned target characterization: `teamleaderleo/ai#108`
- Upstream contact authorization: `false`

## Code map

Primary implementation:

- `packages/xai/src/xai-video-model.ts`
  - `resolveReferences()` gives any non-empty first-class `inputReferences` list precedence over `providerOptions.xai.referenceImageUrls`.
  - non-image first-class references are warned and discarded.
  - `resolveVideoMode()` can select reference-to-video from usable first-class images or legacy reference URLs.
  - request construction permits reference-to-video for every xAI video model id.
  - reference voices become `reference_audios` only in reference-to-video mode.
  - reference-to-video `1080p` is downgraded to `720p`.
  - `grok-imagine-video` receives a warning for `1080p`; `grok-imagine-video-1.5` does not.

Provider options:

- `packages/xai/src/xai-video-model-options.ts`
  - reference image URLs: 1–7 non-empty strings;
  - reference voice ids: at most 3 non-empty strings;
  - runtime `referenceImageUrls` is optional even when explicit mode is selected;
  - public explicit R2V type requires `referenceImageUrls`.

Generic video file identity:

- `packages/provider/src/video-model/v4/video-model-v4-file.ts`
  - a video input is either `{ type: 'file', data, mediaType }` or `{ type: 'url', url, mediaType? }`;
  - there is no provider-reference/file-id variant.

Tests:

- `packages/xai/src/xai-video-model.test.ts`
  - expects 1.5 text-only request construction;
  - expects 1.5 reference-to-video request construction and R2V 1080p downgrade;
  - covers invalid reference voices, audio/video reference filtering, frame-image precedence, and ordinary reference URLs;
  - does not cover an unusable first-class list coexisting with usable legacy reference URLs.

## Recent-change context

Introducing revision `8edc7753b54ef28f36c0590d9603fa97d2e8720c` says:

- 1.5 adds native 1080p for text-to-video and image-to-video;
- reference-to-video remains available but capped at 720p;
- first-class reference routing should avoid selecting R2V for lists with no image;
- `reference_images` accepting `file_id` remains future work.

The same change updated Vercel's provider/core docs to list 1.5 with text-to-video, image-to-video, editing, extension, and R2V.

Evidence label: **Documented** for Vercel's own implementation intent.

## Branch 1 — 1.5 capability matrix disagrees with xAI's current contract

### Vercel behavior

At the pinned head, `XaiVideoModel` accepts `grok-imagine-video-1.5` for the same mode selection used by `grok-imagine-video`.

The test suite explicitly constructs:

```text
1.5 + prompt only
    -> POST /videos/generations
    -> model: grok-imagine-video-1.5

1.5 + reference-to-video + reference_images
    -> POST /videos/generations
    -> reference_images retained

1.5 + R2V + 1080p
    -> downgrade to 720p
    -> request still sent
```

The Fieldwork characterization in `teamleaderleo/ai#108` also asserts that 1.5 emits a reference-to-video request containing both `reference_images` and `reference_audios`.

Evidence label: **Observed/source-confirmed**; target execution for the new focused characterization is pending at report write time.

### xAI contract

Primary xAI sources retrieved 2026-08-12:

- Model page: `https://docs.x.ai/developers/models/grok-imagine-video-1.5`
  - lists image/video modalities;
  - says the model currently does not support text-to-video.
- Reference-to-video guide: `https://docs.x.ai/developers/model-capabilities/video/reference-to-video`
  - explicitly says `grok-imagine-video-1.5` does not support reference-to-video;
  - examples use `grok-imagine-video`.
- Imagine overview: `https://docs.x.ai/developers/model-capabilities/imagine`
  - presents 1.5 as the Image-to-Video model;
  - says reference-to-video requires `grok-imagine-video`.
- Video generation guide: `https://docs.x.ai/developers/model-capabilities/video/generation`
  - says 1080p is supported on 1.5 for image-to-video generation;
  - text-to-video examples use `grok-imagine-video`.
- Pricing: `https://docs.x.ai/developers/pricing`
  - describes 1.5 as Image → Video while `grok-imagine-video` covers Text, Image, Video → Video.

Evidence label: **Documented**.

### Consequence

Vercel can construct and send operations that xAI currently documents as unsupported for 1.5. This is more consequential than an inaccurate capability table: a valid-looking AI SDK call can cross the network with an unsupported model/mode combination and fail remotely instead of being rejected or redirected at the provider boundary.

No live paid xAI request was made, so the exact remote error body and billing behavior are unclaimed.

### Competing explanation challenged

The introducing Vercel change may reflect a newer provider capability than the public xAI docs. That possibility remains the strongest reversing evidence. It does not currently explain why several independent xAI pages, including the model page, capability guide, overview, and pricing table, agree on the narrower 1.5 contract while the Vercel change landed later.

### Recommended next question

Does the provider need a model/mode compatibility guard so 1.5 accepts its documented image-to-video path while text-only and reference-to-video calls receive a local unsupported/invalid argument result?

Promotion: **open bounded campaign after target characterization receipt**.

## Branch 2 — xAI file-id inputs cannot retain their identity in the AI SDK video boundary

### Provider capability

Primary xAI sources retrieved 2026-08-12:

- `https://docs.x.ai/developers/model-capabilities/imagine/files`
- `https://docs.x.ai/developers/model-capabilities/imagine/files/inputs`
- `https://docs.x.ai/developers/model-capabilities/video/reference-to-video`

xAI documents `file_id` as a private Files API substitute anywhere Imagine accepts public URL/base64. Reference-to-video can mix `{ file_id }` and `{ url }` entries in one `reference_images` array. The official Python SDK exposes `reference_image_file_ids`.

Evidence label: **Documented**.

### Vercel boundary

`VideoModelV4File` can retain bytes or a URL. `XaiVideoModel.fileToXaiUrl()` therefore emits only URL/data-URI identity. `XaiVideoModelOptions` has `referenceImageUrls` but no file-id counterpart.

The introducing 1.5 commit itself records `reference_images` file-id support as future work.

Evidence label: **Source-confirmed / Documented**.

### Consequence

A caller that already owns a private xAI Files API asset cannot pass that durable provider identity into current AI SDK xAI video generation. They need another representation, such as a public URL or re-sent bytes, losing the Files API's private reuse path and its upload/bandwidth advantage.

This is a missing interface capability, not evidence of malformed behavior for supported URL/data inputs.

### Recommended next question

Choose the smallest provider-specific representation that can carry `file_id` for start image, source video, and reference images without forcing a cross-provider generic API change before other providers need reference identity.

Promotion: **retain finding / small compatibility campaign**.

## Branch 3 — unusable first-class references can shadow valid legacy references

### Current sequence

```text
providerOptions.xai.referenceImageUrls = [usable image]
inputReferences = [video/audio only]

resolveVideoMode()
  -> legacy URL selects reference-to-video

resolveReferences()
  -> sees non-empty inputReferences
  -> discards every non-image first-class reference
  -> returns undefined
  -> never consults legacy referenceImageUrls

request
  -> reference_images omitted
  -> warning says R2V has no usable references
```

The same legacy request without the unusable first-class list sends its reference image normally.

`teamleaderleo/ai#108` contains a target-native characterization plus that negative control.

Evidence label: **Source-confirmed; target-test-prepared** at report write time.

### Competing explanation

The code comment intentionally says first-class `inputReferences` win over legacy `referenceImageUrls`. A strict replacement policy could intentionally make presence of the new API suppress the old API.

The open question is narrower: should a list that produces zero usable first-class images still count as an authoritative replacement? The current behavior converts an otherwise valid legacy R2V request into a reference-less request while also warning that the new list was unusable.

### Recommended next question

Compare two policies:

1. strict presence precedence — current behavior;
2. usable-value precedence — first-class references replace legacy URLs only when at least one usable image survives classification.

Use mixed image+video first-class lists as the positive control so fallback does not accidentally merge two owners when the new API has a real image.

Promotion: **retain pending target receipt and compatibility judgment**.

## Negative results and boundaries

### Reference voice validation is already bounded

`referenceVoiceIds` is runtime-validated as at most three non-empty strings. Existing tests cover one, three, four, empty string, empty list, and outside-R2V warning behavior. No separate validation branch is justified from this scout.

### Generic non-image filtering received a recent repair

The introducing 1.5 change already fixed the prior behavior where any non-empty `inputReferences` list could select R2V and emit an empty `reference_images` array. Current code selects automatic R2V only when at least one image survives. The retained precedence branch concerns mixed old/new ownership, not that superseded bug.

### R2V 1080p downgrade is secondary

If xAI's documented model matrix is authoritative, 1.5 R2V should be rejected before resolution policy matters. Treat the 1080p downgrade as evidence of the larger capability assumption rather than a separate bug.

## Ranked branch candidates

1. **1.5 capability matrix guard** — highest consequence and clearest contract disagreement. Likely owner: xAI video model mode validation. Evidence needed: target characterization receipt, current xAI contract refresh, current-main/overlap refresh, then model/mode negative controls.
2. **Files API reference identity** — clear provider capability missing from the current adapter and explicitly acknowledged as future work. Likely owner: xAI video provider options plus request input representation.
3. **Usable-value precedence for mixed reference APIs** — concrete local behavior with a compatibility/design choice. Likely owner: `resolveReferences()`. Evidence needed: target receipt and review of desired old/new precedence semantics.

## Probe

Owned characterization: `teamleaderleo/ai#108@c7ed99fee4229a2ec8242f90875f25ebb8d2ae53`.

It asserts current behavior for:

- 1.5 reference-to-video plus preset voice;
- unusable first-class reference shadowing a usable legacy URL;
- legacy-only negative control.

Repository CI was queued when this report was materialized. Until it executes, classify these assertions as `target-test-prepared`, while the same mechanics remain `source-confirmed` from the pinned implementation/tests.

## Recommendation

Promote the 1.5 capability mismatch into one bounded campaign after the characterization executes for the intended reason. Retain file-id support as a separate compatibility finding/campaign because its design boundary differs. Keep mixed-reference precedence in the scout until the prepared target test executes and a compatibility policy is selected.

No production credentials, provider calls, private payloads, or third-party upstream mutations were used.
