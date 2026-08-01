# Unit 21 — fix(utils): fence stale async JSON reads by per-key generation

## In simple words

Jotai's JSON storage adapter reuses parsed values so unchanged serialized data can preserve object identity. Unit 20 changes the cache from one adapter-wide entry to one entry per key. On that base, asynchronous reads can still settle out of order and let an older read replace or delete the shared cache identity selected by a newer read or a completed removal.

Unit 21 adds one read generation per key. Every read captures authority when it starts. Valid and malformed completions may change shared cache state only while that generation remains current. Completed removal advances the same authority before invalidation. Every caller still receives its own result or rejection.

The owned fork now exists. Unit 20 and unit 21 have been materialized as a clean stacked source series. Unit 21's exact diff contains only the production generation fence and an eleven-case target-native regression file. An owner-authorized AI complete-diff review accepts the exact source boundary subject to execution. The fork's ordinary pull-request workflows are currently queued, so exact-head execution is the remaining active gate.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Owning lead: [`#282`](https://github.com/teamleaderleo/fieldwork/issues/282)  
Accepted research carrier: [`#317`](https://github.com/teamleaderleo/fieldwork/pull/317)  
Characterization carrier: [`#284`](https://github.com/teamleaderleo/fieldwork/pull/284)  
Unit 20 prerequisite: [`#252`](https://github.com/teamleaderleo/fieldwork/pull/252), [`#235`](https://github.com/teamleaderleo/fieldwork/issues/235)  
Packet PR: [`#450`](https://github.com/teamleaderleo/fieldwork/pull/450)  
Upstream contact authorized: `no`

## Contribution

- Target project: `pmndrs/jotai`
- Proposed upstream destination: `main`, as a stacked pull request after unit 20 unless the prerequisite has already merged
- Proposed title: `fix(utils): fence stale async JSON reads by per-key generation`
- Contribution synopsis: add per-key read generations to `createJSONStorage()` so obsolete asynchronous read completions cannot publish or delete shared parsed identity after a newer read or completed removal, while preserving caller results, backend errors, stored bytes, and same-string identity reuse
- Work class: `upstream-fork source candidate / stacked proposal`

## Exact identities

- Public upstream and fork base: [`56a9cc51de8a5dd762b95a145820f12589cc47c9`](https://github.com/pmndrs/jotai/commit/56a9cc51de8a5dd762b95a145820f12589cc47c9)
- Owned target fork: [`teamleaderleo/jotai`](https://github.com/teamleaderleo/jotai)
- Unit 20 clean branch: [`fix/utils-key-scoped-json-cache`](https://github.com/teamleaderleo/jotai/tree/fix/utils-key-scoped-json-cache)
- Unit 20 clean head: [`b2f84273b53bbed9df073354dac503e520be7101`](https://github.com/teamleaderleo/jotai/commit/b2f84273b53bbed9df073354dac503e520be7101)
- Unit 20 fork-local draft PR: [`teamleaderleo/jotai#2`](https://github.com/teamleaderleo/jotai/pull/2)
- Canonical unit 21 branch: [`fix/utils-async-read-generation`](https://github.com/teamleaderleo/jotai/tree/fix/utils-async-read-generation)
- Canonical unit 21 head: [`dfe607d7637fbcf61ae41c39f4f470f61fa7c531`](https://github.com/teamleaderleo/jotai/commit/dfe607d7637fbcf61ae41c39f4f470f61fa7c531)
- Unit 21 fork-local draft PR: [`teamleaderleo/jotai#3`](https://github.com/teamleaderleo/jotai/pull/3)
- Unit 21 merge base: `b2f84273b53bbed9df073354dac503e520be7101`
- Accepted target-executed research head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- Workflow-free research carrier head: `34670f709753668827043bbc76c4159a8b36ade2`
- Characterization head: `2fb60bd0497d5557afb54d11c3d6d1a31020b312`
- Unit 20 prerequisite carrier head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Fieldwork packet branch: `p0/435-unit-21-jotai-async-read-generation`
- Fieldwork packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Review class: owner-authorized AI complete-diff review; human review not claimed

## Canonical target diff

Comparison `b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531` is ahead by two commits, behind by zero, and contains exactly:

| Path | Role | Diff |
| --- | --- | --- |
| `src/vanilla/utils/atomWithStorage.ts` | production generation map and publication guards | 15 additions, 2 deletions |
| `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` | eleven target-native regressions | 280 additions |

No workflow, dependency, lockfile, generated output, Fieldwork file, publisher, receipt, or unrelated formatting is present in the target-source diff.

The two unit-21 commits are:

1. `fix(utils): fence stale async JSON reads by per-key generation`
2. `test(utils): cover stale async JSON read fencing`

## Current code, tests, and receipts

### Product code

- [Clean target source at `dfe607d...`](https://github.com/teamleaderleo/jotai/blob/dfe607d7637fbcf61ae41c39f4f470f61fa7c531/src/vanilla/utils/atomWithStorage.ts)
- [`patches/0001-fix-utils-fence-stale-async-json-reads.patch`](./patches/0001-fix-utils-fence-stale-async-json-reads.patch) — retained unit-only patch on top of unit 20
- [Original workflow-free accepted patch](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/async-read-generation-candidate.patch)

### Target-native tests

- [Clean eleven-case target test at `dfe607d...`](https://github.com/teamleaderleo/jotai/blob/dfe607d7637fbcf61ae41c39f4f470f61fa7c531/tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts)
- [`fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts`](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts) — byte-equivalent retained packet fixture
- [Accepted six-case test](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGenerationRepair.test.ts)
- [Characterization test](https://github.com/teamleaderleo/fieldwork/blob/2fb60bd0497d5557afb54d11c3d6d1a31020b312/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGeneration.test.ts)
- [`fixtures/async-read-generation-model.mjs`](./fixtures/async-read-generation-model.mjs)

### Receipts

- [`receipts/20260801-direct-source-materialization.md`](./receipts/20260801-direct-source-materialization.md) — clean source stack, exact heads, changed-file fence, and fork-local workflow IDs
- [`receipts/20260801-local-reconciliation.md`](./receipts/20260801-local-reconciliation.md) — patch-order and 11-case local model output
- [Accepted execution receipt](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/async-read-generation-execution-receipt.md)
- [`REVIEW.md`](./REVIEW.md) — owner-authorized AI complete-diff acceptance subject to execution

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| selected unit-20 cache permits stale async publication | `target-executed` | characterization run `30588753020` at `2fb60bd...` | focused Ubuntu/Node matrix |
| six-case generation repair works | `target-executed` | repair run `30623229098` at `e99c7d2...` | focused tests, not complete repository gate |
| adjacent key-scoped cache behavior remains green | `target-executed` | run `30623229114` | unit-20 matrix only |
| changed-file lint, format, and repository typecheck pass | `target-executed` | Node 24 job `91132389642` | historical focused repair head |
| unit 21 stacks exactly after unit 20 | `source-read` and `direct-source-materialized` | compare `b2f8427...dfe607d`; materialization receipt | no current-main movement since inspected base |
| expanded eleven-case test is present on the clean target head | `target-test-materialized` | `dfe607d...` target file | current fork workflows queued |
| exact source diff is accepted inside the stated boundary | `owner-authorized AI complete-diff review` | `REVIEW.md` at exact source/base heads | human review not claimed; execution pending |
| complete target workflows pass at clean source head | pending | runs `30690923560`, `30690923561`, `30690923575`, `30690923562`, `30690923564`, `30690923558` | queued when last checked |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and final inspection guide](./REVIEW.md)
- [Retained source patch](./patches/0001-fix-utils-fence-stale-async-json-reads.patch)
- [Expanded target-native test fixture](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts)
- [Executable model](./fixtures/async-read-generation-model.mjs)
- [Direct source materialization receipt](./receipts/20260801-direct-source-materialization.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Searches checked: current Jotai issues and pull requests for async JSON read generation, stale async reads, cache publication, and equivalent `atomWithStorage` fixes
- Equivalent current implementation found: `no in searched records`
- Direct prior work: [issue #1079](https://github.com/pmndrs/jotai/issues/1079), [PR #1080](https://github.com/pmndrs/jotai/pull/1080), and [commit `9e336c6...`](https://github.com/pmndrs/jotai/commit/9e336c6bd2bebf257ffca957b0af18f97444323c) introduced same-key parsed identity reuse for mount/subscription consistency
- Relationship: complementary correction to that one-key cache repair
- Search limit: differently worded, unindexed, or off-GitHub discussion may exist; repeat immediately before authorized filing

## Remaining work

Complete in this order:

1. Wait for the fork-local workflows on exact head `dfe607d7637fbcf61ae41c39f4f470f61fa7c531` to finish and inspect the primary Test job.
2. Record exact focused test count, build, lint, format, typecheck, and aggregate suite coverage actually provided by those workflows.
3. Repair any exact-head failure without widening the two-file unit boundary.
4. Repeat duplicate, contribution-policy, and AI-disclosure checks immediately before filing.
5. Await exact user authority before any public discussion or pull request.

## Blockers and limits

- fork-local workflows are queued and have no final conclusion yet;
- write and subscription-event ordering remain outside this unit;
- Windows, macOS, browser integration, and React Native storage adapters remain unexecuted unless current workflows cover them;
- public upstream contact remains unauthorized.

## Latest handoff

State: `HOLD — execution only`  
Exact source head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`, stacked on unit-20 head `b2f84273b53bbed9df073354dac503e520be7101`  
Exact target PR: `teamleaderleo/jotai#3`, draft and fork-local  
Review: exact diff accepted by owner-authorized AI complete-diff review; human review not claimed  
Exact packet head: recorded in the latest #435 handoff  
Tests: historical target-focused Node 22/24/26 repair matrix passed; expanded eleven-case target test is now materialized; ordinary fork workflows are queued at the canonical source head  
Temporary machinery remaining: none in the target diff; Fieldwork research carriers remain open as evidence records  
Next worker action: inspect and record the six exact fork workflow conclusions  
Public upstream interaction: none
