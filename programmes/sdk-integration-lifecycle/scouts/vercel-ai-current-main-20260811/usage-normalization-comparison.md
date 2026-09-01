## In simple words

Current OpenAI-compatible usage normalization can publish internally impossible totals for provider responses whose aggregate counters disagree. Two candidate policies repair the captured Baseten/Kimi incident, but the reasoning-only floor loses against other provider dialects already retained in the repository.

Candidate A uses reasoning as a lower bound for output total. It fixes `6000 < 6001` on the Baseten incident, but it still undercounts generic xAI-style responses and an older observed DeepInfra dialect where `completion_tokens` excludes reasoning rather than including it.

Candidate C treats normalized output total as a conservative envelope over `completion_tokens`, `reasoning_tokens`, and a sane `total_tokens - prompt_tokens` delta. It never lowers the provider completion count and keeps literal provider fields in `raw`. This handles the observed accounting dialects without pretending the detailed text/reasoning split is complete when the provider fields disagree.

Current recommendation: retain Candidate C as the leading comparison, execute its tightened package/core/Baseten gates, and keep Candidate A as a documented losing alternative unless new compatibility evidence reverses the result.

## Target

Public Vercel AI source family: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c` through public head `05a3679dc166edfa864bba00d7fb5247f723e5df`  
Fieldwork campaign: #794  
Current-behavior characterization: retired owned-fork PR #48  
Candidate A: retired owned-fork PR #53  
Candidate C: `teamleaderleo/ai#58`  
Candidate C carrier: `teamleaderleo/ai#59`  
Upstream contact authorized: `false`

The public commits after the original pin do not touch the default OpenAI-compatible usage converter, Baseten provider path, or core usage helpers used by this campaign.

## Established current behavior

Captured Baseten/Kimi incident:

```text
prompt_tokens      = 951
completion_tokens  = 6000
reasoning_tokens   = 6001
total_tokens       = 6952
```

Current normalization:

```text
input total        = 951
output total       = 6000
text               = 0
reasoning          = 6001
normalized all-in  = 6951
raw all-in         = 6952
```

Exact target execution on Node and Edge proved both discriminators:

```text
6000 >= 6001   -> false
6951 == 6952   -> false
```

See `execution.md` and campaign #794.

## Candidate A — reasoning floor — losing alternative

Rule:

```text
output total = max(completion_tokens, reasoning_tokens)
text = max(0, completion_tokens - reasoning_tokens)
```

For the Baseten incident:

```text
output total       = 6001
reasoning          = 6001
normalized all-in  = 6952
```

### Exact execution

Carrier #54 run `31424188815`:

- OpenAI-compatible type-check: PASS;
- focused Fieldwork incident controls: PASS inside the full Node run;
- Node suite: 235 pass / 5 expected semantic snapshot failures;
- later gates did not run after Node failure.

The five changed generic xAI-style totals were:

```text
fixture                        before   Candidate A
text generate                     2        320
tool-call generate               26        255
usage inline                      2        320
text stream                       2        340
tool-call stream                 26        227
```

These values still undercount the same fixtures' valid raw all-in output totals.

## Existing generic xAI-style discriminator

The repository's generic OpenAI-compatible `xai-text` fixture reports:

```text
prompt_tokens      = 12
completion_tokens  = 2
reasoning_tokens   = 320
total_tokens       = 334
```

The raw response implies:

```text
output from all-in total = 334 - 12 = 322
completion + reasoning   = 2 + 320 = 322
```

Candidate A publishes output total `320`, so normalized input + output becomes `332`, two tokens below the raw all-in total.

The generic tool-call fixture supplies the same dialect:

```text
prompt_tokens      = 307
completion_tokens  = 26
reasoning_tokens   = 255
total_tokens       = 588
all-in output      = 281
```

Candidate A publishes `255`, again below the response's own all-in output evidence.

## Historical DeepInfra provider precedent

Merged Vercel PR #12242 added a provider-specific DeepInfra correction for the same visible inequality because DeepInfra Gemini/Gemma had different semantics: `completion_tokens` represented text-only tokens and did not include reasoning.

That workaround is still present on current public main in `packages/deepinfra/src/deepinfra-chat-language-model.ts`.

One observed DeepInfra payload was:

```text
prompt_tokens      = 9
completion_tokens  = 1124
reasoning_tokens   = 1541
total_tokens       = 2674
```

Its accounting is:

```text
total_tokens - prompt_tokens = 2665
completion + reasoning       = 2665
```

The correct output aggregate for that dialect is therefore `2665`, not the reasoning floor `1541`.

This is important comparison evidence because the same predicate (`reasoning > completion`) now has at least two observed meanings in target history:

```text
DeepInfra: completion is text-only; output = completion + reasoning
Baseten:   completion undercounts; all-in output = reasoning
```

A generic fix cannot safely assume one detailed-counter interpretation merely from the inequality.

## Candidate C — conservative consistency envelope

Current rule:

```text
outputFromAllIn =
  prompt_tokens is present
  and total_tokens is present
  and total_tokens >= prompt_tokens
    ? total_tokens - prompt_tokens
    : 0

output total = max(
  completion_tokens,
  reasoning_tokens,
  outputFromAllIn,
)

text = max(0, completion_tokens - reasoning_tokens)
```

Literal provider counters remain unchanged in `raw`.

### Baseten incident

```text
completion       = 6000
reasoning        = 6001
all-in delta     = 6001
output total     = 6001
```

### Generic xAI-style fixture

```text
completion       = 2
reasoning        = 320
all-in delta     = 322
output total     = 322
```

### Historical DeepInfra dialect

```text
completion       = 1124
reasoning        = 1541
all-in delta     = 2665
output total     = 2665
```

The typed detail does not invent a category for output that the provider did not classify. The aggregate may therefore exceed the sum of represented `text` and `reasoning` details when the provider's detailed accounting is incomplete or contradictory.

AI SDK core already stores and aggregates the aggregate and detailed categories independently. Candidate C carries a dedicated core control proving that an output aggregate `322` with represented detail `0 + 320` remains public output `322`, all-in `334`, and aggregates independently across calls.

## Candidate C negative controls

The current candidate requires:

1. ordinary OpenAI-style `prompt=10, completion=20, total=30, reasoning=5` stays output `20`;
2. the Baseten/Kimi incident becomes output `6001`;
3. a too-small raw `total_tokens` cannot lower a valid completion count;
4. a generic xAI-style all-in aggregate can preserve otherwise-unclassified output;
5. missing `total_tokens` falls back to completion/reasoning;
6. `total_tokens` is ignored for output reconciliation when `prompt_tokens` is missing, preventing a partial all-in counter from being mistaken for output-only usage.

An adjacent cache-read arithmetic question (`cached_tokens > prompt_tokens`) remains a reopen trigger. No retained failing provider payload established that input-side contradiction in this pass, so it is outside the current campaign.

## Candidate C execution state

The first Candidate C run reached target semantics:

- OpenAI-compatible type-check: PASS;
- 238 ordinary Node assertions: PASS;
- both Fieldwork incident controls: PASS;
- five usage snapshots changed to totals that follow each fixture's raw all-in accounting.

The tightened generation adds the missing-prompt and core aggregate/detail controls. Carrier #59 is configured to renew only the expected usage snapshots in its workspace under a hard file fence, then run OpenAI-compatible Edge, core usage, and Baseten Node/Edge gates.

That renewed hosted execution remains queued. Do not describe the tightened candidate as executed or ready yet.

## Why the generic converter needs a conservative policy

The dedicated OpenAI converter treats `completion_tokens` as the output aggregate and ignores raw `total_tokens` for normalization.

Known provider dialects can implement stronger semantics in provider-specific code. DeepInfra already does this; `OpenAICompatibleChatConfig` also provides a `convertUsage` escape hatch.

The default generic converter still needs to survive contradictory counters from backends without a custom override. The conservative envelope uses the provider's own aggregate evidence without rewriting literal source values or assuming whether `completion_tokens` includes reasoning.

## Current comparison

| Criterion | Candidate A | Candidate C |
| --- | --- | --- |
| Baseten `total >= reasoning` | pass | pass |
| Baseten all-in total | pass | pass |
| ordinary OpenAI-style accounting | unchanged | unchanged |
| generic xAI-style all-in aggregate | undercounts | reconciles |
| historical DeepInfra-style output | undercounts | reconciles |
| lowers provider completion count | no | no |
| uses sane parsed `total_tokens` evidence | no | yes |
| requires both prompt + total for all-in delta | n/a | yes |
| literal provider fields retained in `raw` | yes | yes |
| semantic radius | narrower | wider |

## Current recommendation

Candidate C remains the provisional leader because Candidate A has concrete reversing evidence across target fixtures and provider history.

Selection still waits for the tightened Candidate C execution generation. If that execution reveals a backend where the larger sane all-in delta is demonstrably outside output accounting, move reconciliation into a provider-specific path for that dialect instead of silently broadening the generic rule.
