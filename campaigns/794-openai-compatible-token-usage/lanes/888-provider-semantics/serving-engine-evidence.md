## In simple words

Current Kimi K3 serving evidence points away from a Kimi-specific additive-completion accounting rule. Moonshot's own verifier treats `completion_tokens` as the API's completion/output count, and both recommended serving engines inspected here count completion from the generated token stream while carrying reasoning as a detail. A response where `reasoning_tokens > completion_tokens` is therefore a serving/accounting contradiction on these paths.

This strengthens the #794 review result: the retained Baseten/Kimi-K3 `6000 / 6001` payload should not be generalized into a Kimi-family converter without evidence about the exact Baseten serving stack. The safer generic policy remains category fidelity, and the safest treatment of this incident is as contradictory provider evidence.

## Evidence identity

- Parent provider-semantics lane: #888
- Parent campaign: #794
- Vercel AI pin: `8e9028317de6a72973971356283271aff44bba74`
- Moonshot Kimi Vendor Verifier pin: `ca0415af385618c5ae197c909ec72f7896b500b8`
- vLLM pin: `8c011da6d0a45f2c9316ea3c658da754f770a178`
- SGLang pin: `b3bffef70aa17733b48af91e4b529e72c913bc6e`
- Retrieved: 2026-08-12
- Claim scope: mechanism and interface
- Upstream contact authorized: `false`

## Moonshot K3 verifier

Moonshot's `Kimi-Vendor-Verifier` is expressly intended to compare K3 vendors and OpenAI-compatible endpoints. Its BEAM generation path records `completion.usage.completion_tokens` directly as the response's completion-token count even when the request enables thinking. The K3 tokenization tests separately establish exact prompt-token semantics against Moonshot tokenism.

The verifier contains no current invariant that declares reasoning additive to completion. Its usage treatment instead uses completion as the API output count.

## vLLM

Kimi K3 lists vLLM as a supported serving engine.

Current vLLM OpenAI chat serving counts completion independently of response parsing:

```text
streaming:
  previous_num_tokens += len(output.token_ids)
  completion_tokens = sum(previous_num_tokens)
  total_tokens = prompt_tokens + completion_tokens

non-streaming:
  parse output.text/token_ids -> reasoning, content, tool calls
  num_generated_tokens = sum(len(output.token_ids))
  completion_tokens = num_generated_tokens
  total_tokens = prompt_tokens + num_generated_tokens
```

The reasoning parser therefore partitions presentation of tokens after the generated-token count already defines completion usage. Reasoning tokens are members of generated completion accounting on this path.

## SGLang

Kimi K3 also lists SGLang as a supported serving engine, and current SGLang contains K3-specific chat encoding support.

Its scheduler records:

```text
reasoning_tokens  = req.reasoning_tokens
completion_tokens = len(req.output_ids_through_stop)
```

Its OpenAI usage processor then returns:

```text
prompt_tokens     = prompt_tokens
completion_tokens = completion_tokens
total_tokens      = prompt_tokens + completion_tokens
reasoning_tokens  = reasoning_tokens
```

This again treats completion as the generated output aggregate and reasoning as a separately reported detail. The K3-specific prompt-token adjustment subtracts the three-token assistant generation stub from reported prompt usage; it does not alter output aggregation.

## TogetherAI cross-provider evidence

A recent Vercel TogetherAI fix records a direct live Kimi-K3 streaming response with `prompt_tokens: 86` and `completion_tokens: 16`, plus Together-specific cached/reasoning usage fields when `include_usage` is requested. The same change was required because missing usage made AI Gateway cost accounting return zero.

Together's current OpenAI-compatibility documentation says usage contains prompt/completion/total and that provider-specific `cached_tokens` and `reasoning_tokens` may appear outside OpenAI's nested detail objects. Its reasoning guide says `max_tokens` caps total output and must accommodate both reasoning and answer content.

This is consistent with completion as the all-output budget/count, while reasoning is a detailed component.

## Revised classification of the Baseten incident

Retained incident:

```text
prompt_tokens      951
completion_tokens  6000
reasoning_tokens   6001
total_tokens       6952
finish              length
text output         none
```

The earlier repair comparison treated a possible Kimi-specific rule as an open implementation direction. Current primary/source evidence weakens that direction substantially.

For vLLM and SGLang serving semantics, `reasoning_tokens > completion_tokens` is internally impossible because completion counts the generated output stream that contains reasoning. Together's current reasoning contract also treats the output budget as covering reasoning plus answer output.

Therefore the strongest current classification is:

- **Observed:** Baseten/Kimi-K3 produced contradictory counters.
- **Documented/source-backed:** supported K3 serving paths count completion as the generated output aggregate.
- **Unknown:** the exact backend/version responsible for the retained Baseten response and why its completion counter was one token low.
- **Unsupported:** a Kimi-family rule that redefines completion as text-only or promotes reasoning to output total from arithmetic alone.

## Consequence for #890

The next repair should not install a Kimi-family arithmetic converter from this incident. A provider/model-specific conversion remains appropriate only when the provider contract establishes a divergent dialect. For this particular K3 response, current evidence favors preserving the contradiction in `raw` and using a generic non-reclassifying policy if the SDK needs normalized aggregate/detail consistency.

One candidate generic fallback is to keep the provider completion aggregate and suppress a reasoning detail that exceeds it from standardized detail fields, while preserving the literal reasoning count in `raw`. That policy still needs an explicit contract decision because it trades detailed visibility for internal consistency.

No third-party repository was modified.
