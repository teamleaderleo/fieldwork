# Vercel AI xAI video reference routing scout

## In simple words

Current Vercel AI main added `grok-imagine-video-1.5` plus new reference-routing behavior. The first pass found an apparent capability disagreement because current xAI documentation describes 1.5 as image-to-video and says both text-to-video and reference-to-video are unsupported.

The text-to-video suspicion is now a **negative result**. The introducing Vercel pull request contains a retained live xAI run where `grok-imagine-video-1.5` generated a 1080p text-to-video result successfully. That execution is stronger evidence for live T2V behavior than the current documentation wording. Do not open a T2V-blocking campaign from this scout.

Reference-to-video remains unresolved: Vercel constructs 1.5 R2V requests and has extensive local tests, while current xAI docs explicitly say 1.5 does not support R2V. I found no equivalent live 1.5 R2V receipt in the introducing pull request, so this is a compatibility uncertainty rather than a proven defect.

Two independent branches remain stronger. First, xAI supports private Files API `file_id` inputs anywhere Imagine accepts URL/base64, including mixed reference-to-video inputs, while the AI SDK video boundary can retain only bytes or URLs. Second, an unusable first-class `inputReferences` list can take precedence over otherwise usable legacy `referenceImageUrls`, removing the reference image from the outgoing request.

## Assignment

- Fieldwork issue: #863
- Programme: #13 — SDK behaviour and integration
- Target hub: #2 — Vercel AI SDK
- Worker: `chatgpt:gpt-5.6-sol`
- Pinned public Vercel AI revision: `dcf33e816a75de7fd4fad0637e1c1f370b21e7f7`
- Retrieval date: 2026-08-12
- Claim scope: mechanism and interface
- Owned target characterization: `teamleaderleo/ai#108`
- Execution carrier: `teamleaderleo/ai#109`
- Upstream contact authorization: `false`

## Code map

Primary implementation: `packages/xai/src/xai-video-model.ts`.

- `resolveReferences()` gives any non-empty first-class `inputReferences` list precedence over `providerOptions.xai.referenceImageUrls`.
- Non-image first-class references are warned and discarded.
- `resolveVideoMode()` can select reference-to-video from usable first-class images or legacy reference URLs.
- Request construction permits reference-to-video for every xAI video model id.
- Reference voices become `reference_audios` only in reference-to-video mode.
- Reference-to-video `1080p` is downgraded to `720p`.
- `grok-imagine-video` receives a warning for `1080p`; `grok-imagine-video-1.5` does not.

Provider options: `packages/xai/src/xai-video-model-options.ts`.

- Reference image URLs: 1–7 non-empty strings.
- Reference voice ids: at most 3 non-empty strings.
- Runtime `referenceImageUrls` is optional even when explicit mode is selected.
- Public explicit R2V type requires `referenceImageUrls`.

Generic video identity: `packages/provider/src/video-model/v4/video-model-v4-file.ts`.

- A video/image input is either `{ type: 'file', data, mediaType }` or `{ type: 'url', url, mediaType? }`.
- There is no provider-reference/file-id variant.

Tests: `packages/xai/src/xai-video-model.test.ts`.

- Constructs 1.5 text-only requests.
- Constructs 1.5 reference-to-video requests and R2V 1080p downgrade behavior.
- Covers invalid reference voices, audio/video reference filtering, frame-image precedence, and ordinary reference URLs.
- Does not cover an unusable first-class list coexisting with usable legacy reference URLs.

## Recent-change and live-evidence context

Introducing revision `8edc7753b54ef28f36c0590d9603fa97d2e8720c` says:

- 1.5 adds native 1080p for text-to-video and image-to-video;
- reference-to-video remains available but capped at 720p;
- first-class reference routing should avoid selecting R2V for lists with no image;
- `reference_images` accepting `file_id` remains future work.

The same change updated Vercel's provider/core docs to list 1.5 with text-to-video, image-to-video, editing, extension, and R2V.

A review comment on the introducing PR records an end-to-end live xAI run:

```text
grok-imagine-video-1.5
text-to-video
1080p
-> generated a real video successfully
```

The reviewer also reports 430/430 xAI package tests and clean TypeScript at that generation. The live receipt names T2V specifically; it does not claim a live 1.5 R2V run.

Evidence labels:

- Vercel source/tests and PR intent: **Documented / source-confirmed**.
- Vercel retained live T2V receipt: **Observed externally by the target project**; Fieldwork did not execute the paid provider call itself.

## Negative result — do not block 1.5 text-to-video from current docs alone

### Initial suspicion

Current xAI primary pages retrieved 2026-08-12 say:

- the 1.5 model currently does not support text-to-video;
- 1.5 is presented primarily as image-to-video;
- the pricing table describes 1.5 as Image → Video.

### Reversing evidence

The introducing Vercel PR contains a live 1.5 T2V 1080p execution with a generated output file and ffprobe result.

This directly overturns the proposed local T2V capability guard. The public xAI documentation appears stale, narrower than the live service, or otherwise incomplete for this behavior.

Disposition: **NEGATIVE RESULT / STOP T2V DEFECT CLAIM**.

Reopen only if a newer live provider run fails consistently or xAI publishes an authoritative removal/deprecation notice that explains the earlier live success.

## Branch 1 — 1.5 reference-to-video remains a bounded compatibility uncertainty

### Current Vercel behavior

At the pinned head, `XaiVideoModel` accepts `grok-imagine-video-1.5` for reference-to-video and can emit:

```text
model: grok-imagine-video-1.5
reference_images: [...]
reference_audios: [{ voice_id: ... }]
```

The existing xAI test suite also expects 1.5 R2V behavior and a 1080p-to-720p downgrade in R2V mode.

`teamleaderleo/ai#108` adds a small characterization of that exact request construction.

Evidence label: **Source-confirmed; target-test-prepared** until the focused carrier executes.

### Current xAI documentation

Primary xAI pages retrieved 2026-08-12:

- Reference-to-video guide explicitly says `grok-imagine-video-1.5` does not support R2V and uses `grok-imagine-video` in examples.
- Imagine overview says reference-to-video requires `grok-imagine-video`.
- 1.5 model/pricing pages present a narrower model role than Vercel's capability table.

Evidence label: **Documented**.

### Challenge result

The introducing Vercel PR's live verification proves T2V, not R2V. The same review calls the R2V routing implementation well-tested, which establishes local confidence but does not answer the remote capability question.

I found no retained live 1.5 R2V receipt in that PR discussion.

### Recommendation

Retain as a compatibility finding. A paid/live provider call would distinguish stale xAI docs from an unsupported Vercel request, but Fieldwork did not incur provider cost for this scout.

Do not implement a model/mode block until one of these appears:

1. a retained live 1.5 R2V failure on current xAI;
2. explicit maintainer/provider confirmation that 1.5 R2V is rejected;
3. another authoritative xAI source that resolves the contradiction despite the live T2V evidence showing docs can lag capability.

Disposition: **RETAIN / LIVE DISCRIMINATOR OPTIONAL**.

## Branch 2 — xAI Files API identity is missing from the AI SDK video boundary

### Provider capability

Primary xAI sources retrieved 2026-08-12:

- `https://docs.x.ai/developers/model-capabilities/imagine/files`
- `https://docs.x.ai/developers/model-capabilities/imagine/files/inputs`
- `https://docs.x.ai/developers/model-capabilities/video/reference-to-video`

xAI documents `file_id` as a private Files API substitute anywhere Imagine accepts public URL/base64. Reference-to-video can mix `{ file_id }` and `{ url }` entries in one `reference_images` array. The official Python SDK exposes `reference_image_file_ids`.

Evidence label: **Documented**.

### Vercel boundary

`VideoModelV4File` can retain bytes or a URL. `XaiVideoModel.fileToXaiUrl()` therefore emits only URL/data-URI identity. `XaiVideoModelOptions` has `referenceImageUrls` but no file-id counterpart.

The introducing 1.5 commit explicitly records `reference_images` file-id support as future work.

Evidence label: **Source-confirmed / Documented**.

### Consequence

A caller that already owns a private xAI Files API asset cannot pass that durable provider identity into current AI SDK xAI video generation. They need another representation, such as a public URL or re-sent bytes, losing the Files API private reuse path and its upload/bandwidth advantages.

This is a missing interface capability, not malformed behavior for supported URL/data inputs.

### Recommended next question

Choose the smallest provider-specific representation that can carry `file_id` for start image, source video, and reference images without forcing a cross-provider generic API change before other providers need reference identity.

Disposition: **PROMOTE / SMALL COMPATIBILITY CAMPAIGN**.

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

Evidence label: **Source-confirmed; target-test-prepared** at this revision.

### Competing explanation

The code comment intentionally says first-class `inputReferences` win over legacy `referenceImageUrls`. A strict replacement policy could intentionally make presence of the new API suppress the old API.

The open question is narrower: should a list that produces zero usable first-class images still count as an authoritative replacement? The current behavior converts an otherwise valid legacy R2V request into a reference-less request while also warning that the new list was unusable.

### Recommended next question

Compare two policies:

1. strict presence precedence — current behavior;
2. usable-value precedence — first-class references replace legacy URLs only when at least one usable image survives classification.

Use mixed image+video first-class lists as the positive control so fallback does not accidentally merge two owners when the new API has a real image.

Disposition: **RETAIN PENDING TARGET RECEIPT + COMPATIBILITY JUDGMENT**.

## Negative results and boundaries

### Reference voice validation is already bounded

`referenceVoiceIds` is runtime-validated as at most three non-empty strings. Existing tests cover one, three, four, empty string, empty list, and outside-R2V warning behavior. No separate validation branch is justified.

### Generic non-image filtering already received a recent repair

The introducing 1.5 change fixed the prior behavior where any non-empty `inputReferences` list could automatically select R2V and emit an empty `reference_images` array. Current automatic mode selection requires at least one image. The retained precedence branch concerns mixed old/new ownership, not that superseded bug.

### 1.5 T2V docs mismatch is closed by stronger live evidence

Do not convert documentation lag into a production restriction when the target project retained a successful live provider run.

### R2V 1080p downgrade is secondary

Its value depends on whether 1.5 R2V is actually accepted remotely. Keep it inside the R2V compatibility question.

## Ranked branch candidates

1. **Files API reference identity** — clear provider capability missing from the current adapter and explicitly acknowledged as future work. Likely owner: xAI video provider options/request conversion. No paid provider call is required to establish the missing representation.
2. **Usable-value precedence for mixed reference APIs** — concrete local behavior with a compatibility choice. Likely owner: `resolveReferences()`. Target characterization is prepared.
3. **1.5 R2V capability** — real source/docs contradiction, but T2V taught us that xAI docs may lag the live service. Keep as a compatibility uncertainty until live/provider evidence distinguishes it.

Stopped branch: **1.5 T2V capability guard** — rejected by retained live xAI success.

## Probe

Canonical characterization: `teamleaderleo/ai#108@c7ed99fee4229a2ec8242f90875f25ebb8d2ae53`.

Execution carrier: `teamleaderleo/ai#109@ee82214d7dfb55b0a707fca9f9a76a4fa87be519`.

The characterization asserts current request construction for:

- 1.5 reference-to-video plus preset voice;
- unusable first-class reference shadowing a usable legacy URL;
- legacy-only negative control.

The dedicated carrier runs frozen install, xAI type-check/build, focused controls, and the full xAI Node suite. Classify the characterization as `target-test-prepared` until that dedicated receipt settles.

## Recommendation

Promote Files API identity into a bounded compatibility campaign. Keep mixed-reference precedence in the scout until the prepared target test executes and a precedence policy is selected. Keep 1.5 R2V as a compatibility uncertainty instead of a defect claim. Preserve the successful live 1.5 T2V result as a negative control against over-trusting stale provider documentation.

No production credentials, paid provider calls, private payloads, or third-party upstream mutations were used by Fieldwork.
