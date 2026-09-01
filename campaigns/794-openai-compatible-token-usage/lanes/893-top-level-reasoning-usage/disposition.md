## Final lane disposition

**STOP — mechanism reproduced; Together-specific production premise withdrawn.**

This file supersedes the provider-applicability and repair-selection portions of `report.md` and `repair-comparison.md` for Fieldwork #898.

## What remains verified

The exact owned-fork characterization `teamleaderleo/ai#151@310bbb7401a6232292f2313a5af227b42c942af4` proved on target CI that a top-level `usage.reasoning_tokens` field survives the loose OpenAI-compatible parser into `usage.raw` while the generic converter omits it from standardized reasoning details.

Run/job: `31586785811` / `94083470768`.

Received standardized output:

```text
total      20
text       20
reasoning   0
```

while raw usage retained:

```text
reasoning_tokens 8
```

This is valid mechanism evidence for compatible endpoints that emit that field location.

## Corrected TogetherAI applicability

Current Together OpenAI-compatibility documentation is more specific than the earlier broad summary:

- reasoning models put reasoning usage at `usage.completion_tokens_details.reasoning_tokens`;
- those reasoning models also put cached prompt usage at `usage.prompt_tokens_details.cached_tokens`;
- some non-reasoning models instead put **cached** usage at top-level `usage.cached_tokens` with no detail objects;
- Together's explicit cross-location fallback example is for cached tokens.

Therefore the synthetic #151 response was useful to prove the generic normalization mechanism, but current provider documentation does not establish top-level reasoning as an active Together chat response contract.

## Why no generic repair follows

SGLang source establishes a real compatible implementation with top-level `reasoning_tokens`, but compatible providers do not share one reasoning-membership rule. Gemini/Vertex evidence includes accounting where thought/reasoning tokens are additive to candidate/completion tokens.

A generic rule that interprets top-level reasoning as a subset of completion would therefore assign one provider dialect to another.

`createOpenAICompatible` already exposes `convertUsage`, allowing a custom SGLang/Gemini-compatible provider integration to supply its own accounting semantics.

## Retired alternatives

- #152 / #153 — generic top-level reasoning fallback: retired after cross-provider semantic counterexample.
- #154 / #156 — Together-specific top-level reasoning fallback: retired after current Together response-shape documentation removed the provider-specific premise.

## Successor

Fieldwork #899 owns the stronger adjacent finding: Together explicitly documents top-level `cached_tokens` for some non-reasoning models and gives a fallback rule across nested/flat cache locations, while current AI SDK normalized cache accounting reads only the nested location.

No third-party repository was modified.
