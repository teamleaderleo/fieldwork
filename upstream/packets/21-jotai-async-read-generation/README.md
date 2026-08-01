# Unit 21 — fix(utils): fence stale async JSON reads by per-key generation

## In simple words

Jotai's JSON storage adapter reuses parsed values so unchanged serialized data can preserve object identity. Unit 20 changes that cache to one entry per key. On that selected base, asynchronous reads can still settle out of order and let an older read replace the shared cache identity chosen by a newer read or a completed removal.

Unit 21 adds one read generation per key. Reads capture authority when they start; valid and malformed completions may change shared cache state only while their generation remains current; completed removal advances the same authority before invalidation.

The accepted repair passed focused target tests on Node 22, 24, and 26. This packet adds rejected-read and same-string controls, proves the patch must stack after unit 20, and preserves public drafts. Direct source materialization remains blocked by the absent unit-20 clean branch and absent owned Jotai fork.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Owning lead: [`#282`](https://github.com/teamleaderleo/fieldwork/issues/282)  
Accepted research carrier: [`#317`](https://github.com/teamleaderleo/fieldwork/pull/317)  
Characterization carrier: [`#284`](https://github.com/teamleaderleo/fieldwork/pull/284)  
Unit 20 prerequisite: [`#252`](https://github.com/teamleaderleo/fieldwork/pull/252), [`#235`](https://github.com/teamleaderleo/fieldwork/issues/235)  
Upstream contact authorized: `no`

## Contribution

- Target project: `pmndrs/jotai`
- Proposed upstream destination: `main`, as a stacked pull request after unit 20 unless the prerequisite has already merged
- Proposed title: `fix(utils): fence stale async JSON reads by per-key generation`
- Contribution synopsis: add per-key read generations to `createJSONStorage()` so obsolete asynchronous read completions cannot publish or delete shared parsed identity after a newer read or completed removal, while preserving caller results, errors, stored bytes, and same-string identity reuse
- Work class: `upstream-fork research and stacked patch preparation`

## Exact identities

- Public upstream base inspected: [`56a9cc51de8a5dd762b95a145820f12589cc47c9`](https://github.com/pmndrs/jotai/commit/56a9cc51de8a5dd762b95a145820f12589cc47c9)
- Public main relation on 2026-08-01: the current main head remained the exact inspected revision
- Owned target fork: repository admission needed; `teamleaderleo/jotai` does not exist
- Intended unit-20 source branch: owned by unit 20; exact branch/head absent
- Intended unit-21 source branch: `teamleaderleo/jotai:fix/utils-async-read-generation`, based on unit 20's clean source head
- Canonical source head: none
- Accepted target-executed research head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- Workflow-free research carrier head: `34670f709753668827043bbc76c4159a8b36ade2`
- Characterization head: `2fb60bd0497d5557afb54d11c3d6d1a31020b312`
- Unit 20 prerequisite carrier head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Fieldwork packet branch: `p0/435-unit-21-jotai-async-read-generation`
- Fieldwork packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Fieldwork packet head: the commit containing this README; exact SHA is recorded in the final #435 handoff
- Execution carriers: Fieldwork PRs #284 and #317
- Superseded prerequisite carriers reviewed: Fieldwork PRs #236 and #242

## Current code and tests

### Product code

- [`patches/0001-fix-utils-fence-stale-async-json-reads.patch`](./patches/0001-fix-utils-fence-stale-async-json-reads.patch) — unit-only source diff on top of unit 20
- [`accepted patch at 34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/async-read-generation-candidate.patch) — original workflow-free retained patch

### Target-native tests

- [`fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts`](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts) — expanded eleven-case native test draft for the eventual Jotai branch
- [`accepted six-case test at 34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGenerationRepair.test.ts) — exact target-executed repair test
- [`characterization test at 2fb60bd...`](https://github.com/teamleaderleo/fieldwork/blob/2fb60bd0497d5557afb54d11c3d6d1a31020b312/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGeneration.test.ts) — exact failing-behavior characterization on the selected base
- [`fixtures/async-read-generation-model.mjs`](./fixtures/async-read-generation-model.mjs) — retained executable model

### Receipts

- [`receipts/20260801-local-reconciliation.md`](./receipts/20260801-local-reconciliation.md) — exact patch-order and 11-case local model output
- [`accepted execution receipt at 34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/async-read-generation-execution-receipt.md) — exact target runs and claim boundary

### Required generated or dependency files

- not applicable

## Changed-file fence

Proposed unit-21 target diff relative to unit 20:

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `src/vanilla/utils/atomWithStorage.ts` | production generation map and publication guards | yes |
| `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` | eleven target-native regressions | yes |

No workflow, receipt, Fieldwork file, dependency, lock, snapshot, generated output, or unrelated formatting belongs in the target-source branch.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| the selected unit-20 cache permits stale async publication | `target-executed` | characterization run `30588753020` at `2fb60bd...` | focused Ubuntu/Node matrix |
| the six-case generation repair works | `target-executed` | repair run `30623229098` at `e99c7d2...` | focused tests, not complete repository gate |
| adjacent key-scoped cache behavior remains green | `target-executed` | run `30623229114` | unit-20 matrix only |
| changed-file lint, format, and repository typecheck pass | `target-executed` | Node 24 job `91132389642` | changed-file lint/format; no build |
| unit 21 must stack after unit 20 | `source-read` plus local source-segment execution | packet reconciliation receipt | exact function segment rather than full checkout |
| rejected-read and same-string semantics are coherent | `model-executed` | 11/11 Node `v22.16.0` model | target-native execution pending |
| expanded eleven-case native test passes | `target-test-prepared` | packet fixture | never run in target checkout |
| ordinary target gates pass | none | no receipt | clean source head absent |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Retained source patch](./patches/0001-fix-utils-fence-stale-async-json-reads.patch)
- [Expanded target-native test draft](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts)
- [Executable model](./fixtures/async-read-generation-model.mjs)
- [Local reconciliation receipt](./receipts/20260801-local-reconciliation.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Searches checked: current Jotai issues and pull requests for async JSON read generation, stale async reads, cache publication, and equivalent `atomWithStorage` fixes
- Equivalent current implementation found: `no in searched records`
- Relationship to prior work: complementary to [issue #1079](https://github.com/pmndrs/jotai/issues/1079), [PR #1080](https://github.com/pmndrs/jotai/pull/1080), and [commit `9e336c6...`](https://github.com/pmndrs/jotai/commit/9e336c6bd2bebf257ffca957b0af18f97444323c), which introduced same-key parsed identity reuse for mount/subscription consistency
- Search limit: differently worded, unindexed, or off-GitHub discussion may exist; repeat immediately before authorized filing

## Remaining work

Complete in this order:

1. Materialize unit 20 on one clean owned Jotai source branch based on a recent exact public main head.
2. Create unit 21 as a clean child branch containing only the two-file unit-21 fence.
3. Copy the expanded eleven-case native test into the target repository.
4. Run the focused four-file Vitest command, changed-file checks, `pnpm run build`, and `pnpm run test` at the exact unit-21 source head.
5. Review the complete unit-21 diff relative to the unit-20 source head and obtain independent acceptance.
6. Repeat duplicate, contribution-policy, and AI-disclosure checks.
7. Await exact user authority before any public discussion or pull request.

## Blockers and limits

- owned `teamleaderleo/jotai` fork absent;
- unit 20 clean source branch/head absent;
- canonical unit-21 source head absent;
- expanded rejected-read and same-string native cases remain unexecuted in Jotai;
- ordinary Jotai build and complete test gates remain unexecuted;
- direct-head independent review remains absent;
- write and subscription-event ordering stay outside this unit;
- public upstream contact remains unauthorized.

## Latest handoff

State: `HOLD`  
Exact source head: `none`; accepted research execution head `e99c7d2e9e3b16c04b1738397ad6109758ad481e`; workflow-free carrier `34670f709753668827043bbc76c4159a8b36ade2`  
Exact packet head: final branch head recorded on issue #435  
Tests: target-focused Node 22/24/26 repair matrix passed; local patch-order reconciliation passed for the stack; local Node `v22.16.0` model passed 11/11; expanded native and ordinary gates pending  
Temporary machinery remaining: no unit-21 workflow on `34670f7...`; Fieldwork PRs #284/#317 remain open carriers; no target branch exists  
Next worker action: after unit 20 publishes its clean source head and the owned fork exists, create `fix/utils-async-read-generation` as a child, add the two-file fence, and execute the commands in `TESTS.md`  
Public upstream interaction: none
