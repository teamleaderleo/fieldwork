## In simple words

Some OpenAI-compatible providers report reasoning usage as `usage.reasoning_tokens` at the top level. Current AI SDK parsing preserves that literal field in `raw` but the generic normalized converter reads reasoning only from `completion_tokens_details.reasoning_tokens`, so the standardized reasoning count becomes zero or absent even when the provider supplied a real count.

TogetherAI is a direct SDK package affected by this contract mismatch: Together documents top-level provider-specific `reasoning_tokens`, while `@ai-sdk/togetherai` delegates chat usage to the generic OpenAI-compatible converter without a custom usage converter. SGLang independently emits the same top-level field in its OpenAI-compatible usage schema.

This is a separate compatibility defect from #794's contradictory-total policy question. The likely repair is additive parsing support for the alternate field location, with a precedence rule when both nested and top-level fields exist.

## Lane identity

- Fieldwork lane: pending issue materialization
- Related campaign: #794
- Programme: #13
- Target hub: #2
- Public Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- SGLang source pin: `b3bffef70aa17733b48af91e4b529e72c913bc6e`
- Retrieved: 2026-08-12
- Claim scope: mechanism and interface
- Upstream contact authorized: `false`

## Current AI SDK path

`openaiCompatibleTokenUsageSchema` is a loose object. It explicitly parses:

```text
prompt_tokens
completion_tokens
total_tokens
prompt_tokens_details.cached_tokens
completion_tokens_details.reasoning_tokens
completion_tokens_details.accepted_prediction_tokens
completion_tokens_details.rejected_prediction_tokens
```

Because the object is loose, undeclared fields such as top-level `reasoning_tokens` survive into the parsed raw object.

`convertOpenAICompatibleChatUsage` then derives normalized reasoning only from:

```text
usage.completion_tokens_details?.reasoning_tokens ?? 0
```

So a response such as:

```json
{
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30,
    "reasoning_tokens": 8
  }
}
```

produces standardized output reasoning `0` even though `raw.reasoning_tokens` remains `8`.

## TogetherAI contract

Together's current OpenAI-compatibility documentation states that usage includes `prompt_tokens`, `completion_tokens`, and `total_tokens`, and that Together-specific fields such as `cached_tokens` and `reasoning_tokens` can appear on supporting models outside OpenAI's nested detail objects.

The current TogetherAI provider constructs `OpenAICompatibleChatLanguageModel` with `includeUsage: true` and no `convertUsage` override. A recent live Kimi-K3 verification in Vercel AI also records Together returning completion usage plus provider-specific cached/reasoning fields once usage is requested.

Consequence: the provider package can receive a documented Together reasoning counter and expose it only in raw provider usage, while standardized `outputTokenDetails.reasoningTokens` reports zero.

## SGLang contract

Current SGLang defines OpenAI-compatible `UsageInfo` with:

```text
prompt_tokens
total_tokens
completion_tokens
prompt_tokens_details
reasoning_tokens
```

Its usage processor populates the top-level `reasoning_tokens` field and defines total usage as prompt plus completion. Its scheduler records completion from the generated output token ids and reasoning separately.

This gives an independent implementation of the same top-level field dialect.

## Consequence

Normalized reasoning usage feeds public AI SDK usage, telemetry, harnesses, and user accounting/detail displays. A zero normalized reasoning count can therefore erase provider-supplied information while raw usage still proves it existed.

The aggregate completion and total counts can remain correct, so ordinary total-usage tests may miss this defect.

## Likely owner

Two plausible repair boundaries:

1. **Generic alternate-field support:** extend the OpenAI-compatible usage schema/converter to accept top-level `reasoning_tokens` as an alternate reasoning-detail location. This fits multiple compatible implementations but needs an explicit precedence rule when both locations are present.
2. **Together-specific `convertUsage`:** map Together's documented top-level field in `@ai-sdk/togetherai`. This has a smaller provider radius but leaves SGLang/custom-compatible users with the same loss.

Given independent provider evidence for the same field location, generic alternate-field parsing is the leading hypothesis, provided it preserves nested OpenAI semantics and raw fidelity.

## Falsifiable characterization

Replay a Together/SGLang-style usage response through the real TogetherAI/OpenAI-compatible chat path:

```text
prompt=10
completion=20
total=30
top-level reasoning=8
```

Expected standardized usage under the provider contract:

```text
output total = 20
reasoning    = 8
text         = 12
raw reasoning_tokens = 8
```

Current generic behavior should retain raw `reasoning_tokens=8` while publishing normalized reasoning `0` and text `20`.

Negative controls:

- nested OpenAI-style reasoning continues to work;
- when both nested and top-level reasoning are present and equal, normalization remains stable;
- when both are present and disagree, preserve both in raw and use a documented precedence rule rather than arithmetic reconciliation.

## Stop condition

Promote to a repair only after a source-native characterization reproduces the loss through the TogetherAI package and the precedence rule is justified from provider contracts or compatibility convention.

No third-party repository was modified.
