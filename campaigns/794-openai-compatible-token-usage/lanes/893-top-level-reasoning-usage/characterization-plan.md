## In simple words

This plan turns the top-level reasoning-usage discovery into one source-native failing test on the owned Vercel AI fork. It changes no production code and makes no upstream claim beyond the provider contracts already recorded in the lane report.

## Exact target

- Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- package: `packages/togetherai`
- intended owned-fork branch: `research/togetherai-top-level-reasoning-usage-20260812`
- intended test file: `packages/togetherai/src/togetherai-reasoning-usage.fieldwork.test.ts`
- claim scope: mechanism
- upstream contact authorized: `false`

## Test thesis

Construct `createTogetherAI` with a synthetic fetch response shaped like Together's documented usage:

```json
{
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30,
    "reasoning_tokens": 8
  }
}
```

Drive the returned chat model through `doGenerate` and assert:

```text
usage.outputTokens.total      == 20
usage.outputTokens.reasoning  == 8
usage.outputTokens.text       == 12
usage.raw.reasoning_tokens    == 8
```

Current source is expected to fail the reasoning/text assertions because the generic converter reads only nested `completion_tokens_details.reasoning_tokens`.

## Why package-level characterization

A direct converter unit test would prove only the shared helper. The TogetherAI package is a real SDK provider whose current documented upstream response dialect places reasoning at the top level, so exercising `createTogetherAI` verifies the actual provider wiring and avoids a hypothetical compatibility-only case.

## Negative controls for a later repair

- nested `completion_tokens_details.reasoning_tokens` remains supported;
- equal nested and top-level counts normalize identically;
- conflicting nested/top-level counts preserve literal raw fields and use an explicit precedence rule;
- generate and stream paths normalize the same usage payload consistently.

## Evidence class

Until executed on the exact branch, this is `target-test-prepared` only.
