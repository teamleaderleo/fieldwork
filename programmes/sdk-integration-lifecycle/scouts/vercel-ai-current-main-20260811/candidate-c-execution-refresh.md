## In simple words

Candidate C has now passed the tightened comparison gate on the exact owned-fork carrier. The first carrier generation had a harness-only red because its core-contract command accidentally invoked the full `ai` package suite. The repaired generation isolated the intended core contract and then completed the remaining Baseten gates successfully.

The result supports Candidate C as the selected technical direction for clean-source preparation. It does not yet establish current-main delivery readiness: expected snapshot updates still need to be materialized on the canonical source, the candidate needs a patch changeset and a clean restack on current public main, and exact-head review must be renewed afterward.

## Candidate and carrier

- Fieldwork campaign: #794
- candidate: `teamleaderleo/ai#58`
- candidate source head: `9835c28c19687fff69fbae846190a954c70a2338`
- execution carrier: `teamleaderleo/ai#59`
- failed carrier head: `f8b65b62c44471e9c1efb3317518ef12e3535b94`
- failed workflow run: `31428318082`
- failed workflow job: `93585277185`
- repaired carrier head: `0c14035cf87ec1676fb56adc9cbc38ffdb458ddd`
- successful workflow run: `31441670391`
- successful workflow job: `93627486548`
- runner: Ubuntu 24.04, Node `22.23.1`
- upstream contact authorized: `false`

## Failed generation classification

Run `31428318082` already proved the OpenAI-compatible package behavior:

```text
OpenAI-compatible type-check: PASS
Node snapshot-renewal run: 244 / 244 PASS
Fieldwork usage controls: 2 / 2 PASS
semantic file fence: PASS
OpenAI-compatible Edge: 244 / 244 PASS
```

Exactly five semantic snapshots moved:

```text
text generate           2 -> 322
function/tool generate 26 -> 281
text stream             2 -> 342
tool stream            26 -> 253
inline text case        2 -> 322
```

The original core command was:

```text
pnpm -C packages/ai test:node -- usage-detail-contract.fieldwork.test.ts
```

That package script loaded the full `ai` test graph. The intended `src/types/usage-detail-contract.fieldwork.test.ts` still passed 2/2, but unrelated unbuilt `@ai-sdk/gateway` resolution and one batch type assertion made the enclosing command red. Baseten gates were skipped after that harness failure.

Classification: **harness/setup failure after the intended core discriminator passed**.

## Repaired exact execution

The carrier changed only the core execution command:

```text
pnpm -C packages/ai exec vitest --config vitest.node.config.js --run src/types/usage-detail-contract.fieldwork.test.ts
```

Run `31441670391` / job `93627486548` completed successfully:

```text
OpenAI-compatible type-check: PASS
OpenAI-compatible Node: 244 / 244 PASS
expected snapshot renewals: 5
semantic file fence: PASS
OpenAI-compatible Edge: 244 / 244 PASS
core aggregate/detail contract: 2 / 2 PASS, no type errors
Baseten type-check: PASS
Baseten Node: 51 / 51 PASS
Baseten Edge: 51 / 51 PASS
```

The five renewed totals are identical to the prior generation and remain confined to the expected OpenAI-compatible language-model test/snapshot files.

## Current-main relation

The latest public Vercel AI head checked after the green carrier is `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`, eleven commits after the original `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c` pin.

That delta does not touch:

- `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts`;
- its usage tests or snapshots;
- the Baseten usage path;
- `packages/ai/src/types/usage.ts`.

Applicability therefore remains intact at source-read scope, while final delivery execution still belongs on a clean branch based on current public main.

## Evidence class

- Candidate C converter and incident/negative controls: `target-executed` on Node and Edge.
- Five expected semantic snapshot movements: `target-executed` and fenced.
- Core aggregate/detail contract: `target-executed` on the isolated intended file.
- Baseten compatibility: `target-executed` for type-check plus Node and Edge package suites.
- Current-main applicability through `74556f7`: `source-read`.

No integration-executed or full-gate claim follows from this receipt.

## Next transition

1. materialize only the five expected snapshot updates on the canonical source branch;
2. add a patch changeset for `@ai-sdk/openai-compatible` if Candidate C remains selected;
3. create one clean source branch on current public main without Fieldwork-only characterization or carrier files;
4. rerun focused Node/Edge package gates and the relevant ordinary repository gates on that exact head;
5. renew complete-diff and independent review;
6. retire execution carriers after evidence transfer.
