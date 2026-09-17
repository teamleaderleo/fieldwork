# Vercel AI SDK fixed-seed fanout scout

Issue: #870  
Programme: #13  
Target hub: #2  
Exact public Vercel AI revision: [`59d6defd09f1855ccd95687dcccb1dd0122815d8`](https://redirect.github.com/vercel/ai/commit/59d6defd09f1855ccd95687dcccb1dd0122815d8)  
Worker: `chatgpt:gpt-5.6-sol`  
Retrieval date: 2026-08-12  
Claim scope: interface and mechanism  
Upstream contact authorized: `false`

## Question

What should one top-level `seed` mean when `generateImage({ n })` automatically splits one public operation into several provider calls?

The copied-seed mechanism and deterministic-output consequence are established. The portable repair policy is still under comparison.

## Core behavior

[`packages/ai/src/generate-image/generate-image.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/ai/src/generate-image/generate-image.ts):

1. resolves `maxImagesPerCall` from the call override or provider model;
2. computes `callCount = ceil(n / maxImagesPerCall)`;
3. creates one child call count per chunk;
4. launches all children through `Promise.all`;
5. forwards the same top-level `seed` unchanged into every child's `doGenerate()` options.

The checked-in multi-call tests make this explicit: with a fixed seed, each expected child argument contains the same seed value.

## Public documentation contract pressure

[`content/docs/03-ai-sdk-core/35-image-generation.mdx`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/content/docs/03-ai-sdk-core/35-image-generation.mdx) says both:

- the SDK automatically calls the model as often as needed, in parallel, to generate the requested number of images;
- when supported by the model, the same seed always produces the same image.

Those statements are individually reasonable. Together with repeated child seeds they create a concrete multi-call ambiguity: a caller asks for several images while automatic batching can replay one deterministic request several times.

The v4 provider type is not more specific. [`ImageModelV4CallOptions`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/provider/src/image-model/v4/image-model-v4-call-options.ts) describes `seed` only as the seed for image generation and leaves provider defaults/ranges to implementations.

## Provider compositions

### Replicate

[`packages/replicate/src/replicate-image-model.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/replicate/src/replicate-image-model.ts):

- `maxImagesPerCall` is one for every model outside the Flux-2 family;
- `seed` is forwarded directly as `input.seed`;
- child `n` is forwarded as `num_outputs`.

The checked-in Replicate image-model test already proves an explicit SDK seed reaches the outgoing provider JSON unchanged.

Primary Replicate documentation retrieved on 2026-08-12 describes seeds as reproducibility controls. One current image model states that using the same seed and the same parameters yields an identical image each time. Several official Black Forest Labs models on Replicate describe the seed as a reproducible-generation input; one accelerated path explicitly documents that it is nondeterministic even with a seed, which is a useful negative control rather than evidence against the deterministic models.

### Black Forest Labs direct provider

[`packages/black-forest-labs/src/black-forest-labs-image-model.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/black-forest-labs/src/black-forest-labs-image-model.ts):

- `maxImagesPerCall = 1`;
- core `seed` is copied directly into the provider request body.

This shows the one-output repeated-seed pattern is not specific to one adapter.

### ByteDance negative control

Recent first-party Seedream image work explicitly treats standard `seed` as unsupported for that provider/model family and emits a warning rather than assigning invented semantics.

This is useful design evidence: the portable core seed surface already spans providers with materially different support contracts.

## Exact consequence

For a deterministic one-output-per-call model:

```text
caller
  n = 3
  seed = 1234

core
  child 0: n = 1, seed = 1234
  child 1: n = 1, seed = 1234
  child 2: n = 1, seed = 1234
```

If the provider's deterministic contract is request-local, all three child requests describe the same deterministic generation.

For a model whose provider can generate several images in one request, repeated seeds across chunks can instead restart a deterministic output sequence. The visible failure can therefore be duplicate single outputs or repeated chunks, depending on provider semantics.

No live paid generation is required to establish the request composition. A live provider call would only strengthen the exact visual/output consequence for one provider.

## Why arithmetic seed derivation is not yet justified

A tempting repair is `childSeed = seed + childOffset`.

That is not yet a portable rule because:

- provider seed ranges and accepted numeric domains can differ;
- provider implementations may normalize or truncate seed values;
- a provider generating several outputs in one request may use one seed to initialize one internal sequence rather than `seed + outputIndex`;
- changing the child seed is externally observable and can break existing reproducibility expectations;
- some providers ignore or reject the standard seed entirely.

Core should not invent a cross-provider random-number sequence without evidence that it preserves provider semantics better than the current behavior.

## Candidate policies

### A. Explicit limitation plus warning when fanout occurs

When a caller supplies `seed` and core must create more than one provider call, retain the current repeated seed but emit a warning explaining that automatic fanout reuses the seed and can repeat deterministic outputs.

Advantages:

- backward compatible request bytes;
- does not invent provider-specific seed arithmetic;
- makes the surprising lifetime visible at the point the SDK creates the fanout.

Weakness:

- still returns repeated outputs for deterministic one-output models;
- callers cannot fix the behavior through the current standard API except by changing provider options/model choice or making separate calls themselves.

### B. Reject fixed seed plus automatic multi-call fanout

Fail before provider dispatch when `seed != null && callCount > 1`.

Advantages:

- avoids silently returning duplicate deterministic outputs;
- makes the unsupported composition explicit.

Weakness:

- breaks a currently accepted input combination;
- some providers may intentionally produce useful distinct outputs despite repeated seed semantics.

### C. First child seeded, later children unseeded

Preserve the exact caller seed only for the first child and let providers choose default randomness for later children.

Advantages:

- first output remains exactly reproducible;
- likely avoids deterministic duplicates.

Weakness:

- aggregate output set is no longer reproducible across invocations;
- core silently changes a top-level caller setting for later children.

### D. Deterministic core-derived child seeds

Derive distinct child seeds from the caller seed.

Advantages:

- can preserve aggregate reproducibility and produce distinct requests.

Weakness:

- no portable derivation contract is established;
- provider ranges and internal multi-output RNG semantics differ;
- likely the highest compatibility risk despite looking elegant.

### E. Add explicit per-output/per-child seed input

Expose a seed sequence or seed factory so callers own the mapping.

Advantages:

- no invented semantics;
- supports deterministic distinct generations deliberately.

Weakness:

- new public API surface;
- complicates chunking because provider calls can produce several outputs at once;
- likely excessive unless demand exists beyond this edge.

### F. Document repeated-seed semantics with no runtime warning

Declare that `seed` applies to every provider call generated by core batching.

Advantages:

- exactly matches current source and tests;
- zero runtime behavior change.

Weakness:

- leaves a surprising `n > 1` outcome hidden unless callers read batching and seed documentation together;
- the top-level API still reads naturally as one generation request with one output count.

## Current ranking

1. **A — warning + explicit limitation** is the safest current direction if product policy wants to preserve request compatibility.
2. **B — reject the ambiguous combination** is stronger correctness but a breaking behavior change.
3. **E — explicit seed sequence** is the cleanest caller-controlled long-term capability if real demand justifies API growth.
4. **C** loses because it silently destroys aggregate reproducibility.
5. **D** loses provisionally because no portable numeric derivation has been established.
6. **F** is acceptable only if maintainers explicitly define seed as per-child-call and accept deterministic duplicate outputs as expected behavior.

This ranking is provisional and should lose if stronger history/provider evidence establishes a portable derivation contract.

## Existing tests as characterization evidence

A new core test is not required merely to prove repeated seed arguments: current multi-call `generateImage` tests already pin the same fixed seed in each child call.

A useful new target-native control would instead test any selected policy:

- warning/rejection only when `callCount > 1` and `seed != null`;
- no warning/rejection for one provider call;
- no warning/rejection when seed is absent;
- preserve provider warnings and ordinary aggregation;
- cover sync and async `maxImagesPerCall` resolution;
- cover an explicit call-level override that changes whether fanout occurs.

## Negative results

- Do not use ByteDance Seedream as the deterministic consequence proof; its current Vercel adapter explicitly treats standard seed as unsupported.
- Do not infer that every provider repeats output merely because it sees the same seed. The claim is bounded to providers whose own deterministic contract makes the repeated request equivalent.
- Do not equate one provider request producing `n > 1` outputs with several SDK-created provider requests. A provider may deliberately derive its own internal output sequence from one seed.
- Do not choose `seed + index` just because it produces different integers; that is an algorithm, not yet a portable contract.

## Overlap

No Fieldwork Vercel lane found under fixed-seed fanout / duplicate seeded output wording.

No matching public Vercel issue was found in the read-only overlap search at retrieval time. Treat that as a search result, not proof of absence.

Adjacent work:

- #868 — sibling lifetime after a fanout child fails;
- #454 — asynchronous task identity and retry/deadline ownership.

Neither owns successful deterministic fanout semantics.

## Evidence state

- source-confirmed: repeated seed is passed to every automatic child call;
- documented: SDK fanout and same-seed reproducibility statements;
- source-confirmed: at least two one-output first-party adapters forward the standard seed directly;
- vendor-documented: deterministic seed behavior exists for current provider models;
- target-test-prepared: selected policy controls described above;
- target-executed: not required for the already-checked-in repeated-seed mechanism; no selected repair has executed;
- integration-executed: no live paid generation performed.

## Recommendation

Do **not** implement seed arithmetic yet.

Treat the current behavior as a real interface ambiguity with a deterministic duplicate-output consequence for at least some supported models. If a product change is desired, start with a warning or explicit validation at the core fanout boundary because that owner knows both `seed` and `callCount` and can act without provider-specific guesses.

A broader per-output seed API should require demonstrated demand and a separate compatibility design.

No third-party upstream mutation occurred.
