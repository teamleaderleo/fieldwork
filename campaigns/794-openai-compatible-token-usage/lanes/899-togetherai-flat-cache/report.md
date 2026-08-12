## In simple words

TogetherAI currently documents two cache-usage layouts. Reasoning models use OpenAI-style `prompt_tokens_details.cached_tokens`, while some non-reasoning models return `cached_tokens` flat at top-level `usage` with no detail objects. Together explicitly tells clients to fall back across both locations or they will silently report zero.

Current `@ai-sdk/togetherai` delegates chat usage to the generic OpenAI-compatible converter, which reads cache only from the nested OpenAI location. A documented flat-cache response therefore retains the literal cache count in raw usage while standardized cache-read usage becomes zero and no-cache input becomes too large.

This is a provider-local field-location defect with a clean accounting contract. The likely repair is a Together-specific usage converter that keeps nested OpenAI cache detail first and falls back to Together's flat `cached_tokens` only within the Together provider.

## Lane identity

- Fieldwork lane: #899
- Related campaign: #794
- Provider semantics: #888
- Programme: #13
- Target hub: #2
- Public Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- Current-behavior characterization: `teamleaderleo/ai#161@7f1b50a142c4026d26cd50ebfe02031bd4eac1d4`
- Retrieved: 2026-08-12
- Claim scope: mechanism and interface
- Upstream contact authorized: `false`

## Provider contract

Together's current OpenAI-compatibility documentation says:

```text
usage always includes:
  prompt_tokens
  completion_tokens
  total_tokens

reasoning models:
  cached input -> usage.prompt_tokens_details.cached_tokens
  reasoning    -> usage.completion_tokens_details.reasoning_tokens

some non-reasoning models:
  cached input -> usage.cached_tokens
  no *_details objects
```

The documentation names `meta-llama/Llama-3.3-70B-Instruct-Turbo` as a flat-cache example and warns that a client configured for only one usage layout will return zero for the others without an error. It gives this fallback pattern:

```text
nested cached_tokens OR top-level cached_tokens OR 0
```

Together's model catalog also distinguishes cached input pricing from ordinary input pricing on models that support caching.

## Current AI SDK path

`packages/togetherai/src/togetherai-provider.ts` creates `OpenAICompatibleChatLanguageModel` with `includeUsage: true` and no custom usage conversion.

The shared OpenAI-compatible usage schema is loose, so top-level `cached_tokens` survives parsing into raw provider usage.

`convertOpenAICompatibleChatUsage` currently computes:

```text
promptTokens    = usage.prompt_tokens ?? 0
cacheReadTokens = usage.prompt_tokens_details?.cached_tokens ?? 0
noCache         = promptTokens - cacheReadTokens
```

It never reads `usage.cached_tokens`.

## Concrete consequence

For a Together response:

```text
prompt_tokens      10
completion_tokens   5
total_tokens       15
cached_tokens       4
```

provider-documented normalized input is:

```text
input total = 10
cacheRead   = 4
noCache     = 6
```

Current generic conversion is expected to produce:

```text
input total = 10
cacheRead   = 0
noCache     = 10
raw.cached_tokens = 4
```

This preserves aggregate token totals while losing the input pricing/detail category.

## Why the owner should be TogetherAI

The #794 investigation established that field names and arithmetic relationships do not establish category membership across every OpenAI-compatible provider. A generic top-level `cached_tokens` fallback would therefore need independent cross-provider semantics.

Together itself establishes both facts needed here:

1. `cached_tokens` is cached **input** usage;
2. its location varies between nested and top-level layouts by model.

The existing `OpenAICompatibleChatConfig.convertUsage` hook provides the provider-local extension point.

## Falsifiable characterization

Owned-fork PR #161 adds exactly one test:

`packages/togetherai/src/togetherai-flat-cached-usage.fieldwork.test.ts`

It drives the real TogetherAI provider with the documented flat-cache layout and asserts:

```text
raw.cached_tokens = 4
input.total        = 10
input.cacheRead    = 4
input.noCache      = 6
```

CI run `31588668655` is queued on the exact characterization head. Until the relevant TogetherAI test job completes, evidence remains `target-test-prepared`.

## Candidate repair

If the characterization reproduces the loss, compare:

A. Together-local usage converter:

```text
cacheRead = nested cached_tokens ?? top-level cached_tokens ?? 0
```

while preserving existing completion/reasoning semantics and literal raw usage.

B. Generic alternate cache-location support, only if independent provider contracts prove the same membership semantics.

Current evidence favors A because the Together contract is explicit and the generic compatibility layer is intentionally provider-agnostic.

## Required controls

- flat Together cache detail maps to standardized cacheRead/noCache;
- nested OpenAI-style Together cache detail remains unchanged;
- nested detail has first precedence if both locations are present;
- raw provider fields remain literal;
- ordinary Together responses without cache usage remain unchanged;
- generate and stream paths use the same converter;
- the shared OpenAI-compatible converter remains untouched.

## Stop condition

Promote after target execution reproduces the documented flat-cache loss. Stop if current runtime parsing already maps the flat field through another provider-specific path.

No third-party repository was modified.
