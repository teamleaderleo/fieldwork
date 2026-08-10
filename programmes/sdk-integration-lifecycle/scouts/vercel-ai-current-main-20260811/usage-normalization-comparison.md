## In simple words

Current OpenAI-compatible usage normalization can publish internally impossible totals for provider responses whose aggregate counters disagree. Two candidate policies repair the captured Baseten/Kimi incident, but only the conservative envelope also reconciles the repository's existing generic xAI-style fixtures with their own raw `total_tokens`.

Candidate A uses reasoning as a lower bound for output total. It fixes `6000 < 6001` on the incident, but it still undercounts generic xAI-style responses where `completion_tokens` excludes reasoning rather than including it.

Candidate C treats normalized output total as a conservative envelope over `completion_tokens`, `reasoning_tokens`, and valid `total_tokens - prompt_tokens`. It never lowers the provider completion count and keeps literal provider fields in `raw`. This handles both observed accounting dialects without pretending the detailed text/reasoning split is complete when the provider fields disagree.

Current recommendation: retain Candidate C as the leading comparison, execute its package/Baseten gates, and keep Candidate A as a documented losing alternative unless new compatibility evidence reverses the result.

## Target

Public Vercel AI source family: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c` through current head `cfc587bdfd8fd1996dd902edd14143be6e034baf`  
Fieldwork campaign: #794  
Characterization: `teamleaderleo/ai#48`  
Candidate A: `teamleaderleo/ai#53`  
Candidate A carrier: `teamleaderleo/ai#54`  
Candidate C: `teamleaderleo/ai#58`  
Candidate C carrier: `teamleaderleo/ai#59`  
Upstream contact authorized: `false`

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
reasoning           = 6001
normalized all-in  = 6951
raw all-in         = 6952
```

Exact target execution on Node and Edge proved both discriminators:

```text
6000 >= 6001   -> false
6951 == 6952   -> false
```

See `execution.md` and campaign #794.

## Candidate A — reasoning floor

Rule:

```text
output total = max(completion_tokens, reasoning_tokens)
text = max(0, completion_tokens - reasoning_tokens)
```

For the incident:

```text
output total       = 6001
reasoning          = 6001
normalized all-in  = 6952
```

This is the smallest local repair under OpenAI-style accounting, where `completion_tokens` is normally the aggregate that already contains reasoning.

### Exact execution

Carrier #54 run `31424188815`:

- OpenAI-compatible type-check: PASS;
- focused Fieldwork incident controls: PASS inside the full Node run;
- Node suite: 235 pass / 5 snapshot failures;
- later gates did not run after Node failure.

The five failures all come from existing generic xAI-style fixtures whose normalized output totals intentionally changed under the candidate:

```text
fixture                        before   Candidate A
text generate                     2        320
tool-call generate               26        255
usage inline                      2        320
text stream                       2        340
tool-call stream                 26        227
```

These are expected semantic-output changes, not unrelated failures. They expose the candidate's limit because the same fixtures carry all-in provider totals that show additional output beyond the reasoning floor.

## Existing generic xAI-style discriminator

The repository's generic OpenAI-compatible `xai-text` fixture reports:

```text
prompt_tokens      = 12
completion_tokens  = 2
reasoning_tokens   = 320
total_tokens       = 334
```

The accounting implied by the raw response is:

```text
output from all-in total = 334 - 12 = 322
completion + reasoning   = 2 + 320 = 322
```

Candidate A publishes output total `320`, so normalized input + output becomes `332`, two tokens below the raw all-in total.

This is reversing evidence for Candidate A as the general default converter repair. It fixes the Baseten incident while remaining inconsistent for a different provider dialect already retained in the same package's compatibility fixtures.

## Candidate C — conservative consistency envelope

Rule:

```text
outputFromAllIn =
  total_tokens is present and total_tokens >= prompt_tokens
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

### Existing generic xAI-style fixture

```text
completion       = 2
reasoning        = 320
all-in delta     = 322
output total     = 322
```

The typed detail does not invent the missing two text tokens; `text` remains the conservative existing derived value. The normalized aggregate can legitimately exceed the sum of represented detail fields when the provider's detailed accounting dialect is ambiguous.

### Negative controls on Candidate C

The candidate source includes controls that:

1. preserve ordinary OpenAI-style `prompt=10, completion=20, total=30, reasoning=5` as output total `20`;
2. repair the captured Baseten/Kimi incident to output total `6001`;
3. refuse to lower valid completion `20` when a contradictory `total_tokens=25` would imply output `15`;
4. preserve output represented by an xAI-style all-in aggregate;
5. fall back to completion/reasoning when `total_tokens` is absent.

Candidate C execution carrier #59 runs OpenAI-compatible and Baseten type-check plus Node/Edge suites. Exact execution remains pending at this record.

## Why the generic converter needs a conservative policy

`OpenAICompatibleChatConfig` already allows a provider-specific `convertUsage` override for known accounting dialects. The dedicated xAI provider uses its own converter and can model xAI semantics precisely.

The default generic converter still serves providers such as Baseten without a usage override and is also tested against xAI-shaped compatible responses. A default repair therefore needs to survive contradictory or dialect-dependent counters without silently choosing one provider's detailed accounting convention for every compatible backend.

## Current comparison

| Criterion | Candidate A | Candidate C |
| --- | --- | --- |
| Baseten incident `total >= reasoning` | pass | pass |
| Baseten incident all-in total | pass | pass |
| ordinary OpenAI-style accounting | unchanged | unchanged |
| generic xAI-style all-in aggregate | still undercounts | reconciles aggregate |
| lowers provider completion count | no | no |
| uses `total_tokens` already parsed by response schema | no | yes |
| semantic radius | narrower | wider |
| literal provider fields retained in `raw` | yes | yes |

## Current recommendation

Candidate C is the provisional leader because Candidate A has concrete reversing evidence in an existing target fixture. Selection still waits for Candidate C target execution and any newly exposed compatibility failures.

If Candidate C's full package/Baseten execution reveals a provider contract where using a larger sane all-in delta is harmful, reopen Candidate A or move reconciliation into a provider-specific `convertUsage` path instead.
