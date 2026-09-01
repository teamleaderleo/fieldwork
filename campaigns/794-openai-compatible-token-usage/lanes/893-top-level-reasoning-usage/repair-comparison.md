## In simple words

The first attempted repair was too broad. A generic OpenAI-compatible fallback from nested reasoning to top-level `reasoning_tokens` would recover TogetherAI and SGLang details, but it would also assume that every compatible backend treats top-level reasoning as a subset of `completion_tokens`.

Gemini-compatible evidence breaks that assumption: Google token accounting separates candidate/completion tokens from thought tokens, and observed OpenAI-compatible responses can satisfy `total = prompt + completion + reasoning`. The same field name can therefore be additive on another provider.

TogetherAI supplies the narrower contract needed for a safe repair. Its current reasoning documentation says reasoning output is billed as completion tokens and reported as completion detail, while its compatibility documentation says the detail may appear outside OpenAI's normal nesting. The leading repair is therefore a Together-specific `convertUsage` rule.

## Comparison identity

- Fieldwork lane: #898
- Vercel AI public base: `8e9028317de6a72973971356283271aff44bba74`
- Current-behavior characterization: `teamleaderleo/ai#151@310bbb7401a6232292f2313a5af227b42c942af4`
- Losing generic candidate: `teamleaderleo/ai#152@3bd90b2327001e87d6a0a7b4c9a5d267b3009d70` — closed
- Losing generic carrier: `teamleaderleo/ai#153@c4b7b925443b5f3af9d42ffdbe7395f81e2d9270` — closed
- Provider-scoped candidate: `teamleaderleo/ai#154@4eee21141429608c62bd4da346ad57313425db75`
- Provider-scoped carrier: `teamleaderleo/ai#156@6241f188655d2010991a61e9b69642f2dbb98db1`
- Retrieved: 2026-08-12
- Upstream contact authorized: `false`

## Alternative A — generic alternate-field fallback

Rule:

```text
reasoning = nested reasoning ?? top-level reasoning_tokens ?? 0
output total = completion_tokens
text = completion_tokens - reasoning
```

### Why it was attractive

- OpenAI nested detail keeps first precedence.
- TogetherAI documents a top-level provider-specific reasoning field.
- SGLang independently emits top-level `reasoning_tokens` and counts completion from the generated output-token stream.
- No arithmetic reconciliation is needed.

### Reversing evidence

Google Gemini accounting exposes a different compatible dialect. Native `GenerateContent` usage separates generated candidate tokens from generated thought tokens and defines total as the sum of prompt, candidate, tool-use-prompt, and thought counts.

Observed Gemini/Vertex OpenAI-compatible responses likewise include cases where completion and reasoning are additive. Examples retained in provider-facing reports satisfy forms such as:

```text
prompt      14
completion  21
reasoning   78
total      113

14 + 21 + 78 = 113
```

and top-level-reasoning reports have shown the same additive relationship.

A generic fallback would therefore interpret an alternate field location as if it also established Together-style membership. It loses for the same reason #794's generic total reconciliation lost: field names and arithmetic position do not establish category membership across providers.

### Disposition

**Losing alternative.** PRs #152/#153 were closed before their queued execution could be used as promotion evidence.

## Alternative B — TogetherAI provider-scoped conversion

Rule:

```text
TogetherAI only:
reasoning = nested reasoning ?? top-level reasoning_tokens ?? 0
output total = completion_tokens
text = max(0, completion_tokens - reasoning)
```

### Provider contract

Together's current reasoning documentation states that reasoning output is billed as completion tokens and reports reasoning under completion usage detail. Its OpenAI-compatibility documentation separately warns that Together-specific fields such as reasoning and cache usage can appear outside OpenAI's standard nested detail objects.

Together therefore establishes both facts needed for a safe normalization:

1. membership: reasoning belongs inside completion usage;
2. location variance: the reasoning detail may appear at the top level.

### Implementation boundary

Candidate #154 leaves `@ai-sdk/openai-compatible` untouched. It adds a Together-local converter and wires it through the existing `OpenAICompatibleChatConfig.convertUsage` hook.

Nested detail retains first precedence so canonical OpenAI-shaped Together responses keep current behavior. Top-level reasoning is a Together-local fallback only.

### Raw fidelity

The converter returns the literal provider usage object in `raw`; it does not synthesize nested fields into raw data.

### Current evidence state

Target-executed current behavior is red on #151. Candidate #154 and execution carrier #156 are running; no green claim is made until exact candidate/carrier receipts complete.

## Alternative C — leave reasoning only in raw

Current behavior already preserves the top-level field in raw usage.

This avoids semantic inference but fails the standardized provider contract for Together, where the provider has documented both the detail's meaning and its alternate location. Public reasoning-token details and telemetry remain incomplete.

Disposition: weaker than provider-scoped conversion.

## Selected direction

**Alternative B — TogetherAI provider-scoped conversion.**

The reusable invariant remains:

```text
An alternate field location does not establish category membership.
Normalize provider-specific fields only where the provider contract
establishes both their location and their accounting meaning.
```

## Reopen triggers

Reopen the selection if:

- Together documents top-level `reasoning_tokens` as additive to completion for any supported chat family;
- candidate execution shows the loose OpenAI-compatible parser does not pass the field into `convertUsage` on real generate/stream paths;
- a narrower built-in Together usage representation already exists on current main;
- or current public source changes the provider conversion hook.

No third-party repository was modified.
