## In simple words

OpenAI-compatible token fields do not carry one universal accounting meaning. Current Vercel AI source contains adapters where reasoning is a subset of completion, adapters where reasoning is additive to completion, and an xAI path where cached input can be either included in or additional to the prompt count. A generic `total_tokens - prompt_tokens` rule can therefore move input tokens into output while still making the arithmetic add up.

The safest generic rule is category fidelity: normalize a token into input, output, text, reasoning, or cache only when a provider contract or provider-specific adapter establishes that membership. The repository already exposes `convertUsage` specifically for OpenAI-compatible providers with different token-accounting semantics.

## Lane identity

- Fieldwork lane: #888
- Parent campaign: #794
- Programme: #13
- Target hub: #2
- Public Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- Retrieved: 2026-08-12
- Claim scope: mechanism and interface
- Evidence class: source-read, plus retained observed provider history where named
- Upstream contact authorized: `false`

## Dialect matrix

| Provider/path | Input/cache semantics in current adapter | Output/reasoning semantics in current adapter | Implication for generic fallback |
| --- | --- | --- | --- |
| OpenAI chat | cached reads and cache writes are members of `prompt_tokens`; no-cache subtracts both | `completion_tokens` is output aggregate; reasoning is a subset | OpenAI-style subset accounting |
| Groq | cached input is a prompt subset | completion is aggregate; reasoning is subset | OpenAI-style subset accounting |
| Alibaba | source explicitly says cache reads and writes are included in prompt | completion is aggregate; reasoning is subset | OpenAI-style subset accounting; unmodeled fields remain in `raw` |
| DeepSeek | prompt cache hits are subtracted from prompt | completion is aggregate; reasoning is subset | OpenAI-style subset accounting |
| MoonshotAI | cached tokens are subtracted from prompt | completion is aggregate; reasoning is subset | OpenAI-style subset accounting |
| Perplexity | prompt is input aggregate; no cache detail mapped | completion is aggregate; separate reasoning is treated as subset | OpenAI-style output accounting |
| Mistral | multiple cache field spellings are treated as prompt subsets | completion is aggregate; no reasoning detail mapped | raw total is unnecessary for output derivation |
| xAI chat | dialect-dependent: cache may be included in prompt or additional to prompt | completion is text; reasoning is additive; output is completion + reasoning | generic OpenAI arithmetic is unsafe |
| Google Vertex xAI | cache treated as prompt subset on this path | completion is text; reasoning is additive | uses `convertUsage` to override generic semantics |
| DeepInfra Gemini/Gemma | OpenAI-like input conversion | provider-specific repair says completion can be text-only and reasoning additive | model/provider-specific correction required |
| Baseten | generic OpenAI-compatible input conversion | generic OpenAI-compatible output conversion | semantics unknown across the provider as a whole; Baseten fronts several model families and arbitrary dedicated models |

## Source map

Current source paths inspected:

- `packages/openai/src/chat/convert-openai-chat-usage.ts`
- `packages/groq/src/convert-groq-usage.ts`
- `packages/alibaba/src/convert-alibaba-usage.ts`
- `packages/deepseek/src/chat/convert-to-deepseek-usage.ts`
- `packages/moonshotai/src/convert-moonshotai-chat-usage.ts`
- `packages/perplexity/src/convert-perplexity-usage.ts`
- `packages/mistral/src/convert-mistral-usage.ts`
- `packages/xai/src/convert-xai-chat-usage.ts`
- `packages/google-vertex/src/xai/google-vertex-xai-provider.ts`
- `packages/deepinfra/src/deepinfra-chat-language-model.ts`
- `packages/baseten/src/baseten-provider.ts`
- `packages/baseten/src/baseten-chat-options.ts`
- `packages/openai-compatible/src/chat/openai-compatible-chat-language-model.ts`

## Concrete counterexample to total-minus-prompt

Retained xAI compatibility history in Vercel AI commit `7ccb9025499b15271cea6e30d1943a02db77d508` records models where `prompt_tokens` excludes cached tokens. The current regression contains:

```text
prompt_tokens      = 4142
cached_tokens      = 4328
completion_tokens  = 254
total_tokens       = 8724
```

The xAI adapter classifies:

```text
input total  = 4142 + 4328 = 8470
output total = 254
```

The rejected generic policy from #794 derives:

```text
total_tokens - prompt_tokens = 4582
```

That produces a numerically balanced response while moving all `4328` cached-input tokens into normalized output. This is a direct counterexample to treating `total >= prompt` as sufficient evidence that `total - prompt` is output.

## Reasoning has two incompatible meanings in current source

Subset family:

```text
OpenAI
Groq
Alibaba
DeepSeek
MoonshotAI
Perplexity

completion = output aggregate
reasoning  = member of completion
```

Additive family:

```text
xAI chat
Google Vertex xAI
DeepInfra Gemini/Gemma correction

completion = text or non-reasoning output
reasoning  = additional output
```

The visible condition `reasoning_tokens > completion_tokens` therefore cannot select one universal repair.

## Baseten is a routing boundary, not one model dialect

Current Baseten model identifiers include DeepSeek, Kimi, Qwen, GPT-OSS, GLM and an open string escape hatch for other or dedicated models. The package also accepts custom deployment URLs. The retained Kimi incident establishes one Baseten-served model response, not a Baseten-wide accounting contract.

A provider-wide Baseten rewrite would therefore need additional evidence. A model/dialect-aware rule is the narrower owner.

## Generic blast radius

Current source search finds direct `OpenAICompatibleChatLanguageModel` consumers including Baseten, Fireworks, TogetherAI, Vercel, GMI Cloud, Cerebras, DeepInfra and custom-provider users. Some of these providers support reasoning controls while retaining the generic converter. A generic arithmetic repair changes all of them even though their accounting semantics are independently owned.

## Invariant

```text
A normalized token count may enter a category only when the adapter has
provider-contract evidence, provider-specific source knowledge, or an
observed dialect discriminator establishing membership in that category.

Arithmetic equality alone cannot establish category membership.
```

## Current conclusion

The repository already provides the right extension point: `OpenAICompatibleChatConfig.convertUsage` is documented as the optional usage converter for providers with different token-accounting semantics. Current xAI/Vertex-xAI/DeepInfra code demonstrates the same architectural direction through dedicated conversion or subclass repair.

The generic fallback should remain aligned with its declared OpenAI-compatible contract. Divergent dialects should be normalized at a provider/model-aware boundary.

## Remaining uncertainty

- The matrix records adapter semantics. Provider documentation still needs to carry any claim that a source rule is a stable external contract rather than a repository interpretation.
- The exact Kimi family predicate for Baseten needs retained provider evidence beyond the single Kimi-K3 incident before widening to other Kimi models.
- Other generic OpenAI-compatible consumers may contain contradictory retained payloads that warrant their own provider rule.

No third-party repository was modified.