## In simple words

The top-level reasoning-usage loss is now target-executed on the exact owned-fork characterization. The provider's literal `reasoning_tokens: 8` survives in `usage.raw`, while standardized output usage reports reasoning `0` and text `20` instead of reasoning `8` and text `12`.

The failing assertion is isolated to the Fieldwork characterization: the other 43 TogetherAI Node assertions in the same package run passed.

## Exact execution

- Fieldwork lane: #898
- Owned-fork PR: `teamleaderleo/ai#151`
- Public source/base: `8e9028317de6a72973971356283271aff44bba74`
- Authored characterization head: `310bbb7401a6232292f2313a5af227b42c942af4`
- PR merge test commit: `1bb17cfb595d87855b9c859a7d948682ca6eff87`
- Workflow run: `31586785811`
- Discriminator job: `94083470768` — `Test (26)`
- Runner: Ubuntu 24.04.4
- Node: `26.7.0`
- Test fence: `packages/togetherai/src/togetherai-reasoning-usage.fieldwork.test.ts`

## Result

The root CI invoked `pnpm test:ci`, which included `@ai-sdk/togetherai`. The TogetherAI package ran its Node suite.

Existing package tests:

```text
togetherai-provider.test.ts                 14 PASS
togetherai-image-model.test.ts              17 PASS
togetherai-reranking-model.test.ts          12 PASS
```

Fieldwork discriminator:

```text
togetherai-reasoning-usage.fieldwork.test.ts  1 FAIL
```

Package total before the expected red:

```text
43 passed
1 failed
```

The exact failure was:

```text
Expected:
{
  total: 20,
  text: 12,
  reasoning: 8
}

Received:
{
  total: 20,
  text: 20,
  reasoning: 0
}
```

The preceding assertion that `usage.raw` contains `reasoning_tokens: 8` passed. The failure therefore distinguishes raw response survivability from standardized-detail loss.

## Classification

Evidence class for the mechanism: **target-executed**.

The red is candidate-owned and intentional: the only failing TogetherAI assertion is the characterization of current behavior. Existing TogetherAI Node coverage passed 43/43.

The broader root `Test (26)` job is red because Turbo propagates the TogetherAI package failure. Other package lines that subsequently print lifecycle failure text are not classified as independent source failures from this job; the root failure owner is explicitly reported as `@ai-sdk/togetherai#test`.

Build Packages, TypeScript, lint/format, code-consistency, load-time checks, and the AI/codemod shards observed in the same workflow completed successfully. These do not replace the focused provider discriminator.

## Reproduced invariant break

```text
provider supplied reasoning detail = 8
raw reasoning detail               = 8
standardized reasoning detail      = 0
standardized text detail           = 20
completion aggregate               = 20
```

The aggregate remains plausible, so this defect can evade total-token accounting checks while erasing a provider-supplied output detail.

## Next repair discriminator

Compare two repairs:

1. generic OpenAI-compatible fallback: nested OpenAI reasoning detail first, then top-level `reasoning_tokens` when nested detail is absent;
2. Together-specific `convertUsage` mapping.

The generic fallback has independent SGLang evidence and preserves the canonical OpenAI nested field as first precedence. It should lose if another compatible provider uses top-level `reasoning_tokens` with a different membership meaning.

No third-party repository was modified.
