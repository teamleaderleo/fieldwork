# Tests and receipts — unit 21 Jotai async read generation

## In simple words

The stale-publication behavior and the selected generation repair already ran against exact Jotai source on Node 22, 24, and 26. The owned fork now contains the clean stacked source and the expanded eleven-case target-native test at exact head `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`.

Opening fork-local draft PR #3 triggered Jotai's existing pull-request workflows. They are queued. Until their final conclusions and job contents are recorded, this packet keeps the exact distinction between historical focused target execution and current clean-head execution.

## Identity

- Exact public/fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Unit 20 clean prerequisite head: `b2f84273b53bbed9df073354dac503e520be7101`
- Unit 21 clean source head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`
- Unit 21 fork-local draft PR: `teamleaderleo/jotai#3`
- Accepted repair execution head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- Workflow-free repair carrier: `34670f709753668827043bbc76c4159a8b36ade2`
- Characterization head: `2fb60bd0497d5557afb54d11c3d6d1a31020b312`
- Environments already executed: GitHub Actions Ubuntu 24.04 with Node 22/24/26; local Linux with Node `v22.16.0`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| completion-order publication exists on the unit-20 base | `target-executed` | PR #284 run `30588753020` | pass on Node 22/24/26 | focused source stack, Linux only |
| per-key generation fences the six accepted stale-publication transitions | `target-executed` | PR #317 run `30623229098` | pass on Node 22/24/26 | focused matrix, not complete repository CI |
| unit-20 adjacent cache behavior remains green | `target-executed` | run `30623229114` | success | selected cache matrix only |
| changed source and tests satisfy lint, formatting, and TypeScript | `target-executed` | Node 24 job `91132389642` | pass | historical focused head |
| unit 21 depends mechanically on unit 20 | `source-read`, `source-segment-executed`, and `direct-source-materialized` | patch-order receipt and clean branch comparison | direct apply fails; stacked source is exact | current base still pinned to `56a9cc...` |
| expanded eleven-case controls are coherent | `model-executed` | Node model | 11/11 pass | model execution |
| expanded eleven-case target test is on the clean source head | `target-test-materialized` | target file at `dfe607d...` | present, exact packet bytes | fork workflows queued |
| ordinary target workflows pass on the clean source head | pending | six fork-local workflow runs | queued | no final conclusions yet |

## Historical target execution

### Baseline characterization

Workflow at `2fb60bd0497d5557afb54d11c3d6d1a31020b312` ran:

```text
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageAsyncReadGeneration.test.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
pnpm eslint <four changed files>
pnpm prettier --check <four changed files>
pnpm tsc --noEmit
```

Result:

- workflow `30588753020`: success on Node 22, 24, and 26;
- inspected Node 24 job: four files, 42 tests, ESLint, Prettier, and TypeScript passed;
- observed behavior: the selected unit-20 cache publishes shared identity by async completion order.

### Accepted repair

At exact repair head `e99c7d2e9e3b16c04b1738397ad6109758ad481e`:

- workflow `30623229098`: success on Node 22, 24, and 26;
- adjacent unit-20 workflow `30623229114`: success;
- inspected Node 24 job `91132389642`: four files, 43 tests, ESLint, Prettier, and TypeScript passed;
- covered transitions: newer valid, completed removal, newer missing, newer malformed, stale malformed, unrelated key;
- explicit limit: read/read and read/completed-removal only; write and subscription authority are separate questions.

## Local reconciliation

### Patch order

On the exact `createJSONStorage()` source segment from `56a9cc...`:

```text
git apply --check unit21.patch
git apply --check unit20.patch
git apply unit20.patch
git apply --check unit21.patch
git apply unit21.patch
git diff --check
```

Result:

- unit 21 direct application failed because `cachedValues` was absent;
- unit 20 applied;
- unit 21 then applied;
- final diff check passed.

Receipt: [`receipts/20260801-local-reconciliation.md`](./receipts/20260801-local-reconciliation.md)

### Expanded model

- command: `node executed-model.mjs`
- environment: Node `v22.16.0`
- result: 11/11 passed
- additional semantics: rejection remains caller-visible; rejection does not transfer publication authority backward; later success can establish identity; unrelated keys remain stable; same serialized bytes preserve the newer cached identity.

## Clean direct source execution

### Source and test

- source: `teamleaderleo/jotai:fix/utils-async-read-generation`
- exact head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`
- exact merge base: `b2f84273b53bbed9df073354dac503e520be7101`
- target test: `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts`
- target test assertions: eleven
- diff: two files, 295 additions, 2 deletions
- commit count: two

### Existing pull-request workflows triggered

| Workflow | Run | Current status |
| --- | --- | --- |
| Test Multiple Versions | `30690923560` | queued |
| Test Old TypeScript | `30690923561` | queued |
| Test | `30690923575` | queued |
| Compressed Size | `30690923562` | queued |
| Test Multiple Builds | `30690923564` | queued |
| Preview Release | `30690923558` | queued |

The exact final status and job contents must be recorded rather than inferred from workflow names.

Materialization receipt: [`receipts/20260801-direct-source-materialization.md`](./receipts/20260801-direct-source-materialization.md)

## Ordinary repository gates

| Gate | Existing evidence | Clean-head result |
| --- | --- | --- |
| focused target regression | historical six-case matrix passed | eleven-case file materialized; queued workflow |
| formatting | historical changed-file Prettier passed | queued workflow; `pnpm run fix:format` conclusion not yet known |
| lint | historical changed-file ESLint passed | queued workflow; exact clean-head command not yet known |
| typecheck | historical repository `tsc --noEmit` passed | queued workflow; exact clean-head command not yet known |
| build | not previously run | queued workflows may cover builds; inspect jobs |
| aggregate test | not previously run | queued Test workflow; inspect jobs |
| multiple versions/builds | focused Node 22/24/26 previously passed | dedicated clean-head workflows queued |

## Reversing controls

- characterization fails the intended invariant and repair passes it;
- existing `atomWithStorage.test.tsx` stayed green in historical focused execution;
- missing and malformed outcomes exercise deletion authority;
- backend rejection stays visible;
- unrelated-key controls reject cross-key generation interference;
- same-string control preserves historical identity reuse;
- clean target diff excludes temporary workflow or evidence machinery.

## Setup and harness history

| Attempt | Result | Classification | Effect on claim |
| --- | --- | --- | --- |
| unit-21 patch directly on public main | prerequisite context absent | packaging/dependency | established stack requirement |
| historical unit-20 PR #236 run `30553976771` | malformed patch before install | packaging | no product result transferred |
| local clone in this session | container DNS blocked GitHub | runner/network setup | direct GitHub object writes used instead |
| fork-local PR workflows | queued | execution pending | current exact-head gate remains open |

## Platform and integration gaps

- Windows and macOS unless current workflow jobs prove coverage;
- browser and real `StorageEvent` ordering;
- React Native storage adapters;
- custom thenables and unusual backends;
- application-level frequency and dynamic-key retention;
- read versus write and subscription-event ordering.

## Cleanup receipt

- target source contains temporary workflows: no;
- target source contains Fieldwork files or receipts: no;
- target source contains dependency or lock changes: no;
- unit 21 diff is exactly two files: yes;
- branch is two conventional commits: yes;
- public upstream interaction: none.

## Current test judgment

`HOLD`

Reason: the clean branch and expanded target-native test now exist, but the exact-head fork workflows are queued and independent complete-diff review is absent.

Clearing condition: record final conclusions and actual job coverage for all six exact-head workflow runs, repair any failures inside the two-file boundary, then obtain independent review.
