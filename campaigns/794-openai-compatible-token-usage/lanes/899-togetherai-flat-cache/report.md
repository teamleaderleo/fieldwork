## In simple words

TogetherAI currently documents two cache-usage layouts. Reasoning models use OpenAI-style `prompt_tokens_details.cached_tokens`, while some non-reasoning models return `cached_tokens` flat at top-level `usage` with no detail objects. Together explicitly tells clients to fall back across both locations or they will silently report zero.

Current `@ai-sdk/togetherai` delegates chat usage to the generic OpenAI-compatible converter, which reads cache only from the nested OpenAI location. A documented flat-cache response therefore retains the literal cache count in raw usage while standardized cache-read usage becomes zero and no-cache input becomes too large.

This is a provider-local field-location defect with a clean accounting contract. The selected candidate is a Together-specific usage converter that implements the provider's published nested-or-flat fallback while leaving shared OpenAI-compatible conversion untouched.

## Lane identity

- Fieldwork lane: #899
- Related campaign: #794
- Provider semantics: #888
- Programme: #13
- Target hub: #2
- Public Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- Current-behavior characterization: `teamleaderleo/ai#161@7f1b50a142c4026d26cd50ebfe02031bd4eac1d4`
- Canonical repair candidate: `teamleaderleo/ai#162@45de2c4d53f8f808584ae8c88270b7d1c150b9c1`
- Exact execution carrier: `teamleaderleo/ai#172@9e6dbb51a0e01e42c4ffc721fbb938770fec198e`
- Dedicated carrier workflow run: `31590555255`
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

The truthy `OR` is relevant: a nested `0` falls through to a nonzero flat count if both locations appear. Together's model catalog also distinguishes cached input pricing from ordinary input pricing on models that support caching.

## Current AI SDK path

`packages/togetherai/src/togetherai-provider.ts` creates `OpenAICompatibleChatLanguageModel` with `includeUsage: true` and no custom usage conversion on the public base.

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

## Why the owner is TogetherAI

The #794 investigation established that field names and arithmetic relationships do not establish category membership across every OpenAI-compatible provider. A generic top-level `cached_tokens` fallback would therefore need independent cross-provider semantics.

Together itself establishes both facts needed here:

1. `cached_tokens` is cached **input** usage;
2. its location varies between nested and top-level layouts by model.

Current Fireworks documentation uses the normal nested cache location, so it does not establish a cross-provider flat-field convention. Current `@ai-sdk/moonshotai` provides positive source precedent for provider-local flat/nested cache normalization.

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

Broad CI run `31588668655` is in progress on the exact characterization head. Evidence for current behavior remains `target-test-prepared` until a TogetherAI package result is observed.

## Canonical candidate

PR #162 changes exactly four source files:

```text
.changeset/together-cached-usage.md
packages/togetherai/src/convert-togetherai-chat-usage.ts
packages/togetherai/src/convert-togetherai-chat-usage.test.ts
packages/togetherai/src/togetherai-provider.ts
```

Provider-local policy:

```text
cacheRead = nested cached_tokens || flat cached_tokens || 0
input total = prompt_tokens
noCache = prompt_tokens - cacheRead
```

Existing nested reasoning accounting is retained; raw usage remains literal; shared `@ai-sdk/openai-compatible` code is unchanged.

Candidate controls cover:

- flat cached tokens when nested details are absent;
- nonzero nested cache detail taking first precedence;
- nested `0` falling through to a nonzero flat cache count, matching Together's documented truthy fallback;
- existing nested reasoning accounting;
- null usage.

## Exact execution carrier

The first carrier generation against source `753e7082...` was expired after provider-doc review exposed the nested-zero/flat-nonzero fallback edge.

Fresh two-layer carrier #172 is exact for source `45de2c4d...`:

- workflow-only base: `b244ef011130b0e8a52413868d5a6506a8350d72`;
- test-only head: `9e6dbb51a0e01e42c4ffc721fbb938770fec198e`;
- dedicated workflow run: `31590555255`.

Its workflow verifies the public-base/candidate diff fence, workflow-only base fence, and test-only head fence, then runs repository consistency, TogetherAI type-check, complete Node and Edge package suites, and package build.

No execution result is claimed while that workflow remains queued.

## Stop condition

Promote after target execution reproduces the current flat-cache loss and the corrected candidate passes the exact provider package gate. Reopen if Together changes its response contract or if a cross-provider contract justifies moving the fallback into shared conversion.

No third-party repository was modified.
