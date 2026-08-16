## In simple words

Some OpenAI-compatible APIs report reasoning usage at `usage.reasoning_tokens`. AI SDK's generic response parser preserves that field in raw usage but its normalized converter reads only `completion_tokens_details.reasoning_tokens`, so standardized reasoning can become zero even when the provider returned a real count.

TogetherAI documents this top-level provider-specific field and the current `@ai-sdk/togetherai` package uses the generic converter with no usage override. SGLang independently emits the same usage field. The aggregate completion count can remain correct, which lets this detail loss slip past ordinary total-token checks.

## Assignment

- Related campaign: #794
- Programme: #13
- Target hub: #2
- Public source pin: `8e9028317de6a72973971356283271aff44bba74`
- Owned report path: `campaigns/794-openai-compatible-token-usage/lanes/893-top-level-reasoning-usage/`
- Claim scope: mechanism and interface
- State: `investigating — target characterization prepared`
- Upstream contact authorized: `false`

## Concrete current behavior

A Together/SGLang-style usage body can contain:

```text
prompt_tokens      10
completion_tokens  20
total_tokens       30
reasoning_tokens    8   # top-level
```

The generic schema is loose, so `raw.reasoning_tokens` survives. Normalized reasoning reads only the nested OpenAI location and therefore becomes zero; normalized text remains 20 instead of 12.

## Consequence

Public reasoning-token detail and telemetry can erase provider-supplied usage while aggregate output remains plausible. Callers inspecting standardized details see different information from the provider's literal usage record.

## Likely owner

`packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts` plus its accepted usage shape, with `packages/togetherai` as the concrete provider path.

A generic alternate-field mapping is preferable only if precedence between nested and top-level reasoning is explicit. A Together-specific converter is the smaller fallback.

## Falsifiable evidence path

One source-native TogetherAI package test should replay a documented top-level reasoning response through the real chat model and assert normalized reasoning `8`, text `12`, total output `20`, while raw remains literal. Current source is expected to fail the reasoning/text assertions.

## Stop condition

Promote to repair after target execution reproduces the loss and a precedence rule for dual-field responses is supported by provider contracts. Stop or narrow if current target execution already maps the top-level field through another path.

No third-party upstream mutation is authorized.
