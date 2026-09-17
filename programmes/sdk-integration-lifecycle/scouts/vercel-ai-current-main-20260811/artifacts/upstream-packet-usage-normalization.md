# Upstream Packet: Reconcile contradictory OpenAI-compatible usage totals

Campaign: #794  
Target: Vercel AI SDK  
State: `candidate — current behavior executed; preferred repair awaiting exact candidate gates`

> This packet is preparation-only. A human must perform any Vercel upstream interaction manually outside Fieldwork automation.

## In simple words

The default OpenAI-compatible usage converter can now prevent a negative derived text-token count while still returning a normalized usage object whose own totals disagree.

On a provider payload already retained by AI SDK's regression tests, normalized output is `total: 6000, reasoning: 6001`, and public all-in usage becomes `6951` while the same response's parsed raw `total_tokens` is `6952`.

Node and Edge target tests reproduced both contradictions beside 238 passing ordinary package tests. A narrow reasoning-floor repair fixes that incident but loses against existing generic xAI-style fixtures. The current preferred direction uses a conservative envelope over completion, reasoning, and a sane `total_tokens - prompt_tokens` delta while preserving every literal provider counter in `raw`.

Vercel's current contribution guide explicitly encourages high-quality issue/reproduction-first bug reports. This packet is therefore written so the problem can be reviewed independently of the still-executing candidate patch.

## Proposal

I propose defining normalized `outputTokens.total` so it cannot be smaller than output evidence already present in the same provider response, while leaving the provider's literal counters unchanged in `raw`.

For the default OpenAI-compatible converter, the candidate rule is:

```text
allInOutput =
  prompt_tokens and total_tokens are both present
  and total_tokens >= prompt_tokens
    ? total_tokens - prompt_tokens
    : 0

outputTokens.total = max(
  completion_tokens,
  reasoning_tokens,
  allInOutput,
)
```

`text` keeps the existing conservative derivation:

```text
text = max(0, completion_tokens - reasoning_tokens)
```

## Current and proposed behavior

Captured provider incident already present in the target test suite:

```text
prompt_tokens      = 951
completion_tokens  = 6000
reasoning_tokens   = 6001
total_tokens       = 6952
```

Current normalized result:

```text
input total        = 951
output total       = 6000
text               = 0
reasoning          = 6001
public all-in      = 6951
raw all-in         = 6952
```

Preferred candidate:

```text
input total        = 951
output total       = 6001
text               = 0
reasoning          = 6001
public all-in      = 6952
raw all-in         = 6952
```

The target's generic xAI-style fixture supplies a second accounting dialect:

```text
prompt_tokens      = 12
completion_tokens  = 2
reasoning_tokens   = 320
total_tokens       = 334
```

Its all-in response proves output `322`. A reasoning-only floor would publish `320`; the conservative envelope publishes `322` without inventing a detailed category for the remaining two tokens.

## Consequence

The current normalized object can violate its own public field meanings: `outputTokens.total` can be smaller than `outputTokens.reasoning`.

AI SDK core also derives public all-in `totalTokens` from normalized input plus normalized output. For the retained incident, that produces `6951` even though the same parsed response contains raw total `6952`.

Consumers that validate non-negative/self-consistent usage, aggregate usage across steps, emit telemetry, or use normalized counts for accounting can receive a believable but internally contradictory vector.

## Reproduction

```text
source revision: fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c
environment: Ubuntu 24.04 / Node 22.23.1
owned characterization: teamleaderleo/ai branch research/usage-consistency-fc3baaf
execution run: 31423425063
fixture: retained Baseten/Kimi provider-usage payload
```

Executed result:

```text
@ai-sdk/openai-compatible type-check: PASS
Node ordinary package tests: 238 PASS
Node discriminator 1: FAIL — expected 6000 >= 6001
Node discriminator 2: FAIL — expected 6951 == 6952
Edge ordinary package tests: 238 PASS
Edge discriminator 1: FAIL — expected 6000 >= 6001
Edge discriminator 2: FAIL — expected 6951 == 6952
```

Deterministic: yes for the mocked/retained provider payload.

The reproduction preserves the SDK's actual response schema and usage conversion boundary. It does not establish how every OpenAI-compatible provider defines its counters.

## Cause

The response schema parses all three aggregate signals:

```text
prompt_tokens
completion_tokens
total_tokens
```

and the detailed reasoning count.

The default converter currently chooses `completion_tokens` as normalized output total unconditionally, even when the same response proves that aggregate is smaller than one of its own output components or smaller than the valid all-in delta.

## Invariant

```text
Normalized output total must never be lower than a valid output count
already present in the same provider response.
```

Literal provider values remain available in `raw` so normalization does not rewrite source evidence.

## Scope

Included:

- default OpenAI-compatible chat usage conversion;
- contradictory aggregate/detail counters;
- sane all-in reconciliation when both prompt and total are present;
- preservation of raw provider payload;
- core behavior where aggregate totals may exceed classified detail categories.

Excluded:

- redefining provider-specific `convertUsage` overrides;
- inventing missing text/reasoning classifications;
- cost estimation from ambiguous provider counters;
- speculative input-cache reconciliation without an observed failing payload.

## Candidate implementation

```text
owned fork: teamleaderleo/ai
candidate PR: #58
base revision: fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c
candidate source generation: 9835c28c19687fff69fbae846190a954c70a2338 plus tightened converter/test commits retained on the branch
changed product component: packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts
```

The candidate also carries target controls for ordinary OpenAI-style accounting, a too-small raw all-in total, missing prompt totals, missing total tokens, xAI-style all-in output, and AI core's independent aggregate/detail usage contract.

Exact candidate verification is still pending because the owned-fork hosted runner queue remains queued. Do not describe the candidate as executed or ready yet.

## Verification and alternatives

### Losing alternative — reasoning floor

```text
output total = max(completion, reasoning)
```

It fixed the Baseten incident but remained inconsistent on existing generic xAI-style fixtures. Exact execution moved five retained snapshot totals and still undercounted their raw all-in totals. The alternative was retired.

### Preferred alternative — conservative envelope

The first execution generation passed 238 ordinary Node assertions plus the Fieldwork controls; five usage snapshots changed as expected. Each changed value tracked the fixture's valid raw all-in output rather than merely the reasoning floor.

A tightened generation adds the missing-prompt negative control and core aggregate/detail contract. Full Edge/Baseten/core candidate gates remain pending.

## Tradeoffs

The conservative envelope has a wider semantic reach than a reasoning-only floor because it uses a parsed all-in aggregate when that provides additional output evidence.

It deliberately permits normalized output aggregate to exceed the sum of currently represented `text` and `reasoning` details. AI SDK core already treats aggregate and detail categories independently; the candidate carries an explicit regression for that contract.

A provider with a known incompatible accounting dialect can still supply `convertUsage`. The generic fallback should remain conservative when its input counters disagree.

## Recovery

The change is isolated to normalized usage conversion and can be reverted without stored-state migration. Provider literal counters remain in `raw` throughout.

## AI assistance

AI systems performed source inspection, hypothesis generation, owned-fork test preparation, candidate comparison, and evidence synthesis. Claims promoted here are tied to exact source revisions and retained target execution receipts. A human must review every proposed source line and run/confirm the final filing-head verification before any public submission.

The current Vercel contribution guide and PR template contain no dedicated AI-assistance disclosure field found in this review. A human submitter should recheck policy at submission time.

## Human accountability

```text
reproduced problem:           yes
reviewed every final change:  pending human review
can defend implementation:    pending human review
ran final candidate gates:    pending
checked current policy:       yes, 2026-08-11
automated upstream write:     no
```

## Maintainer decision requested

For contradictory OpenAI-compatible usage counters, should the normalized V4 usage object preserve a self-consistent conservative aggregate while keeping literal provider counters in `raw`, or is the intended contract that normalized aggregate/detail fields may contradict each other and callers should reconcile through `raw` themselves?
