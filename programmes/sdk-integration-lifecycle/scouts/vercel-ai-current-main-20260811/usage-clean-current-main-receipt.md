## In simple words

The selected OpenAI-compatible usage repair now exists as one clean five-file candidate based directly on the current public Vercel AI head. Its generated expectations were materialized under a hard file fence, and the exact resulting source head passed the relevant OpenAI-compatible, core-usage, and Baseten gates on Node and Edge.

The builder's complete-diff self-review found no blocking defect. Because the builder created and materially shaped the candidate, this receipt does not accept it; the exact head is ready for independent technical review.

## Exact review fence

- Fieldwork campaign: #794
- owned source PR: `teamleaderleo/ai#78`
- branch: `candidate/usage-consistency-current-main`
- public base: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`
- exact candidate head: `ae0ef90ba83c49c0fa1e3bb156fb751f7d438b00`
- current public `vercel/ai:main` checked after execution: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`
- work class: upstream-fork research / clean human-review candidate
- upstream contact authorization: `false`

Complete changed-file fence:

1. `.changeset/calm-usage-totals.md`;
2. `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts`;
3. `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.test.ts`;
4. `packages/openai-compatible/src/chat/openai-compatible-chat-language-model.test.ts`;
5. `packages/openai-compatible/src/chat/__snapshots__/openai-compatible-chat-language-model.test.ts.snap`.

No Fieldwork-only characterization, temporary workflow, or execution-carrier file appears on the candidate head.

## Change thesis

Current OpenAI-compatible conversion can publish an internally contradictory normalized usage vector when provider counters disagree. The retained Baseten/Kimi response says:

```text
prompt_tokens      951
completion_tokens  6000
reasoning_tokens   6001
total_tokens       6952
```

Current public conversion produces output total `6000` with reasoning `6001`, and public input + output total `6951` despite raw all-in total `6952`.

The candidate selects normalized output total as:

```text
max(
  completion_tokens,
  reasoning_tokens,
  total_tokens - prompt_tokens when both totals exist and total >= prompt,
)
```

It keeps literal provider fields unchanged in `raw`, preserves the existing non-negative text derivation, and does not alter input/cache accounting.

## Exact-head execution receipt

Execution carrier: `teamleaderleo/ai#80`  
Carrier generation: `314cb0e62faa34911c3574fa45131bea147d2eca`  
Workflow run/job: `31442391041` / `93629617678`  
Environment: Ubuntu 24.04, Node `22.23.1`

The carrier began from source head `aee8f21477dd13becba4ff05691fe12fa4c8b3d6`, generated exactly the two expected language-model expectation files, verified the remote source generation had not moved, committed those expectations as `ae0ef90ba83c49c0fa1e3bb156fb751f7d438b00`, and continued validation from that exact commit.

Executed results:

```text
OpenAI-compatible pre-renew type-check        PASS
snapshot renewal                              9 files / 242 tests PASS
snapshot changes                              exactly 5
expected generated-file fence                 PASS
OpenAI-compatible exact-head type-check       PASS
OpenAI-compatible Node                        9 files / 242 tests PASS
OpenAI-compatible Edge                        9 files / 242 tests PASS
core aggregate/detail contract                2 / 2 PASS, no type errors
Baseten type-check                             PASS
Baseten Node                                   51 / 51 PASS
Baseten Edge                                   51 / 51 PASS
final exact-head + clean-working-tree fence   PASS
```

Evidence class for the converter behavior, package regressions, core aggregate/detail contract, and Baseten compatibility: `target-executed`.

The carrier is execution machinery, not the canonical source. Its receipt is transferred here and onto PR #78.

## Generated expectation audit

Exactly five normalized aggregate outputs changed under the selected policy:

```text
text generate            2 -> 322
function/tool generate  26 -> 281
text stream              2 -> 342
tool stream             26 -> 253
inline text case          2 -> 322
```

The complete PR diff shows no generated movement outside the two expected language-model test/snapshot files.

## Complete-diff self-review

### Production boundary

The production change adds `total_tokens` to the converter's accepted usage shape, computes one candidate total from a sane all-in/prompt pair, and takes the maximum of completion, reasoning, and that derived count. The converter remains provider-generic and preserves the existing raw payload.

### Negative controls

The ordinary regression file establishes:

- normal OpenAI-style accounting remains unchanged;
- a too-small `total_tokens` value cannot lower a valid completion count;
- absent `total_tokens` falls back to completion/reasoning evidence;
- absent `prompt_tokens` disables total-minus-prompt reconciliation;
- a larger sane all-in total can preserve output that detailed counters do not classify.

### Cross-layer contract

Core usage projection and aggregation were exercised separately with an aggregate output total larger than text + reasoning details. Both the projection and double-aggregation controls passed. This supports the existing contract that aggregate and detailed counters may be independently meaningful rather than requiring detail sums to equal the aggregate.

### Compatibility surface

Baseten type-check and complete Node/Edge package suites passed. Existing OpenAI-compatible Node and Edge package suites also passed after the five expected expectation renewals. No active equivalent upstream implementation was found in the refreshed overlap search.

### Current-main relation

Public `vercel/ai:main` remained exactly `74556f7946cdf50aa41c01c5d5b3bd2b733acc86` after exact-head execution. The candidate therefore has no current-main drift at this receipt generation.

### Uncertainty

This evidence does not establish every OpenAI-compatible provider's billing semantics or require providers to make their raw counters mutually consistent. The change instead defines a conservative normalized aggregate while preserving literal provider evidence in `raw`.

A broader provider-specific semantic objection, or evidence that normalized output total must equal the exposed detail sum, would reopen the selected policy.

## Self-review disposition

Builder self-review: **READY FOR INDEPENDENT REVIEW**.

The author is not eligible to issue the final `ACCEPT` disposition for this consequential implementation. The next transition is admission of exact head `ae0ef90ba83c49c0fa1e3bb156fb751f7d438b00` to Fieldwork review queue #213 with the five-file fence and the execution receipt above.

No public upstream interaction occurred.
