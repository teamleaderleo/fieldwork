## In simple words

The #794 max-envelope repair is the wrong generic owner. It can make totals agree by moving tokens into the wrong category. Current Vercel AI already has a better pattern: keep the generic OpenAI-compatible converter close to OpenAI semantics and use provider-specific conversion when a provider or model uses a different accounting dialect.

The leading repair direction is therefore narrower: retire the generic `total - prompt` promotion, preserve the existing generic completion aggregate, and repair the observed Baseten/Kimi dialect at a model-aware boundary using `convertUsage` or equivalent provider code. A Baseten-wide rewrite is still too broad because Baseten serves several independent model families and arbitrary dedicated models.

## Lane identity

- Fieldwork lane: #890
- Parent campaign: #794
- Dependencies: #888 provider semantics, #889 accounting contract
- Programme: #13
- Target hub: #2
- Public Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- Retrieved: 2026-08-12
- Claim scope: mechanism and interface
- Upstream contact authorized: `false`

## Rejected generic invariants

### Raw-total equality

The earlier characterization asserted:

```text
normalized input + normalized output == raw total_tokens
```

The xAI cache-exclusive counterexample disproves this as a generic classifier. Its raw response can be balanced only after cached input is added to the prompt side. Using `raw total - raw prompt` moves cache into output.

### Reasoning floor as a universal semantic repair

`reasoning > completion` has at least two meanings in current source:

- xAI/Vertex-xAI/DeepInfra correction: completion can represent text while reasoning is additive;
- Baseten/Kimi incident: captured counters say reasoning exceeds a completion field that undercounts the generation.

The inequality alone cannot determine whether output is reasoning, completion + reasoning, or something else.

## Alternative A — generic OpenAI semantics plus provider/dialect conversion

**Status: leading direction.**

Current source precedent:

- OpenAI-compatible generic converter uses completion as output aggregate.
- `OpenAICompatibleChatConfig.convertUsage` is explicitly documented for providers with different token-accounting semantics.
- Google Vertex xAI uses `convertUsage` for additive reasoning.
- xAI has a dedicated converter for additive reasoning and cache-membership detection.
- DeepInfra has provider/model-specific repair logic for Gemini/Gemma.

This preserves a clear owner boundary: generic code implements the compatibility contract; adapters own deviations they know about.

### Baseten complication

`BasetenChatModelId` includes DeepSeek, Kimi, Qwen, GPT-OSS, GLM and `(string & {})`; custom dedicated deployment URLs are also accepted. One Baseten provider can therefore expose several accounting dialects.

A correction should use the narrowest reliable model/dialect discriminator rather than `provider == baseten`.

## Baseten/Kimi incident evidence

Retained provider response from the upstream fix:

```text
prompt_tokens      = 951
completion_tokens  = 6000
reasoning_tokens   = 6001
total_tokens       = 6952
cached_tokens      = 60
finish              = length
observed text       = none
```

The upstream incident description says the model spent its output budget on reasoning and hit the length stop before emitting text; it identifies completion as the undercounting field because `total = prompt + reasoning` for this response.

For this exact dialect, the defensible normalized output is:

```text
output total = 6001
text         = 0
reasoning    = 6001
```

That conclusion depends on incident/model evidence. It should not be generalized from arithmetic alone.

## Candidate Baseten owner choices

### A1. Model-aware `convertUsage`

Select a converter using the Baseten model identity and apply a Kimi-specific correction only for model families with retained evidence.

Pros:
- smallest semantic radius;
- uses the intended OpenAI-compatible extension point;
- leaves unrelated Baseten models unchanged.

Need:
- exact model family coverage evidence;
- generate + stream controls;
- negative control for unknown Baseten model with the same numeric inequality.

### A2. Expose a Baseten `convertUsage` setting for custom deployments

Dedicated Baseten deployments can serve arbitrary models. Letting callers supply a usage converter would preserve the generic default and give custom deployments a supported semantic override.

Pros:
- honest for arbitrary deployments;
- avoids guessing unknown model semantics.

Cost:
- new provider API surface;
- does not by itself repair the known default Kimi path.

### A3. Baseten subclass with dialect dispatch

A subclass can own model-aware correction if configuration plumbing makes `convertUsage` selection awkward. This follows DeepInfra precedent but adds more custom code than A1.

## Alternative B — generic non-reclassifying contradiction handling

Current generic behavior already clamps negative text to zero while keeping completion as aggregate. This avoids inventing output.

A stricter generic policy could suppress a reasoning detail that exceeds its aggregate:

```text
if reasoning > completion and provider semantics are unknown:
  output total = completion
  text = 0
  reasoning = undefined
  raw retains provider reasoning
```

This restores aggregate/detail consistency without reclassifying tokens, but loses normalized reasoning evidence on the known Baseten/Kimi case. It is therefore a fallback policy candidate, not the preferred known-dialect repair.

## Alternative C — explicit unknown aggregate

Provider V4 allows `outputTokens.total = undefined`, but AI core currently computes `totalTokens` with an additive helper that treats one missing side as zero. An unknown output with known input produces a partial public total.

A clean unknown representation would need a wider change so missing output makes all-in total unknown and telemetry semantics remain clear. This exceeds the smallest repair boundary for #794.

## Alternative D — guarded generic total-minus-prompt

**Rejected by current evidence.**

No predicate built only from `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, and `total_tokens` proves whether prompt includes cached input or whether total carries provider-specific categories. The xAI cache-exclusive case is a direct counterexample even when all values are non-negative and the total arithmetic is exact.

## Preferred invariant

```text
Every standardized token count must be backed by evidence that the
source tokens belong to that standardized category.

Consistency repair may clamp an impossible derived value, omit an
unsupported detail, or apply a provider-specific conversion. It may not
move tokens between input and output merely to make totals agree.
```

## Required regression set for a repaired implementation

1. Baseten/Kimi retained incident: `951 / 6000 / 6001 / 6952` -> known-dialect output `6001`, text `0`.
2. Ordinary OpenAI subset accounting remains completion aggregate.
3. xAI additive reasoning remains completion + reasoning under its adapter.
4. xAI cache-exclusive case `4142 / cache 4328 / completion 254 / total 8724` remains input `8470`, output `254`.
5. Unknown Baseten model with `reasoning > completion` receives no Kimi reinterpretation without model/dialect evidence.
6. Missing or contradictory raw total cannot force category movement.
7. Generate and stream paths produce identical usage normalization.

## Current design disposition

Retire #78 as an implementation direction. Keep its exact execution receipt as evidence that the max-envelope code behaves as designed, while classifying the design itself as semantically unsafe.

Proceed with Alternative A. First establish the exact Baseten/Kimi model-family evidence; then implement the narrowest model/dialect-aware converter. Keep Alternative B as a generic fallback question if the public contract requires impossible details to be suppressed.

## Remaining uncertainty

- The retained incident names Kimi-K3 while current Baseten model lists expose Kimi-K2 variants. Evidence is needed before assuming the same accounting behavior across Kimi generations.
- A dedicated deployment may return the same field shape with unrelated semantics.
- Provider docs may offer a stronger model-family contract and should be preferred before widening any adapter rule.

No third-party repository was modified.