## In simple words

Candidate C has passed the OpenAI-compatible package boundary on the tightened comparison, including the two incident controls and the five expected semantic snapshot changes. The first execution carrier then failed because its core-contract command accidentally invoked the full `ai` package suite without building package dependencies. The dedicated core usage contract itself passed 2/2 before unrelated `@ai-sdk/gateway` resolution and batch-type failures made the wrapper command red.

The carrier has been repaired to invoke only the intended core contract file. Baseten gates remain after that discriminator. This receipt records the failed generation as a harness result rather than a Candidate C product failure.

## Candidate and carrier

- Fieldwork campaign: #794
- candidate: `teamleaderleo/ai#58`
- candidate source head reviewed by the failed generation: `9835c28c19687fff69fbae846190a954c70a2338`
- execution carrier: `teamleaderleo/ai#59`
- failed carrier head: `f8b65b62c44471e9c1efb3317518ef12e3535b94`
- failed workflow run: `31428318082`
- failed workflow job: `93585277185`
- repaired carrier head: `0c14035cf87ec1676fb56adc9cbc38ffdb458ddd`
- replacement workflow run: `31441670391`
- upstream contact authorized: `false`

## What executed successfully on run 31428318082

The target package portion reached the intended semantics:

```text
OpenAI-compatible type-check: PASS

Node snapshot-renewal run:
  10 test files PASS
  244 tests PASS
  Fieldwork usage controls: 2/2 PASS
  exactly five semantic snapshots renewed

Semantic file fence: PASS
  only the expected OpenAI-compatible usage test/snapshot files changed

OpenAI-compatible Edge:
  10 test files PASS
  244 tests PASS
  Fieldwork usage controls: 2/2 PASS
```

The five renewed totals are the expected comparison outputs:

```text
text generate        2 -> 322
function/tool generate 26 -> 281
text stream          2 -> 342
tool stream         26 -> 253
inline text case     2 -> 322
```

These values follow the candidate rule's larger sane aggregate evidence rather than the smaller raw completion count.

## Core gate classification

The carrier used:

```text
pnpm -C packages/ai test:node -- usage-detail-contract.fieldwork.test.ts
```

That package script expands to the package-wide Vitest invocation. The extra filename did not isolate execution, so Vitest loaded the full `ai` test graph.

Within that run, the intended file executed and passed:

```text
src/types/usage-detail-contract.fieldwork.test.ts: 2 PASS
```

The command still returned red because unrelated suites could not resolve unbuilt `@ai-sdk/gateway`, and an unrelated batch type assertion also failed. Those failures sit outside Candidate C's three-file source fence and do not contradict the usage aggregate/detail contract.

Classification: **harness/setup failure after the intended core discriminator passed**.

Baseten type-check and Node/Edge tests were skipped only because the workflow stops on the red core wrapper step.

## Carrier repair

The repaired carrier changes only the execution workflow and now scopes the core step directly:

```text
pnpm -C packages/ai exec vitest --config vitest.node.config.js --run src/types/usage-detail-contract.fieldwork.test.ts
```

This removes the accidental package-wide execution while retaining the exact core contract that already passed in the failed generation.

Replacement carrier head: `0c14035cf87ec1676fb56adc9cbc38ffdb458ddd`.

Replacement run `31441670391` was queued when this receipt was written. Treat it as pending, not executed evidence.

## Current evidence class

- Candidate C OpenAI-compatible converter and incident controls: `target-executed` on Node and Edge for the failed carrier generation.
- Expected five semantic snapshot movements: `target-executed` and fenced.
- Core aggregate/detail contract: the target test itself executed and passed, while its enclosing command was a harness failure; keep the overall gate pending until the repaired isolated command completes cleanly.
- Baseten compatibility: pending on the replacement carrier.

No integration-executed or full-gate claim follows from this receipt.
