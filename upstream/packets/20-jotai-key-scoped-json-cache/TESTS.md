# Tests and receipts — unit 20 Jotai key-scoped JSON cache

## In simple words

The released cross-key alias and the unit 20 repair both have exact target execution receipts. The released package shares one parsed object across different keys containing equal JSON. The direct owned-fork candidate scopes that identity by key and passes the focused storage matrix, changed-file lint and formatting, repository typechecking, and the complete Jotai build on Node 22, 24, and 26.

The source branch has since been cleaned to exactly one production file and two target-native test files. Native Jotai workflows for that clean head were queued at the latest check. The main remaining technical dependency is unit 21's accepted generation fence for stale asynchronous read completions.

## Identity

- Exact upstream and fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Owned fork: `teamleaderleo/jotai`
- Canonical source branch: `fix/key-scoped-json-cache`
- First clean product-and-test generation: `e295dc741a706153b50e7d27fbd424fcc48519cb`
- Exact executed carrier head: `ac5dd98da6c3083f31560b71d84ad3bf850aaafc`
- Current clean source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`
- Owned-fork PR: `teamleaderleo/jotai#1`
- Direct-source workflow: `30690503592`
- Test date: `2026-08-01`
- Environment: GitHub-hosted Ubuntu 24.04; Node 22, 24, and 26; pnpm 11.3.0

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Released adapter aliases equal JSON across keys. | `target-executed` | Fieldwork run `30548784323` | reproduced on Node 22/24/26 | released package only |
| Mutation through key A changes key B's previously returned value. | `target-executed` | same run and retained `result.json` | reproduced | application frequency unmeasured |
| Per-key map isolates equal JSON and preserves same-key identity. | `target-executed` | owned-fork run `30690503592` | pass on Node 22/24/26 | unit 21 owns stale async publication ordering |
| Missing or malformed observation prevents obsolete identity resurrection in the covered ordering. | `target-executed` | same run, `atomWithStorageReadInvalidation.test.ts` | pass | synchronous observation ordering |
| Removal terminal outcomes invalidate only the affected key and preserve the initiating error. | `target-executed` | same run, key-isolation tests | pass | no general storage transaction protocol |
| Existing mount/subscription behavior remains green. | `target-executed` | same run, existing `atomWithStorage.test.tsx` | 25 pass per runtime | named suite only |
| Source/tests satisfy ESLint and Prettier. | `target-executed` | same run, changed-file checks | pass on Node 22/24/26 | changed files only |
| Repository typecheck succeeds. | `target-executed` | same run, `pnpm tsc --noEmit` | pass on Node 22/24/26 | one repository revision |
| Complete Jotai build succeeds. | `target-executed` | same run, `pnpm run build` | pass on Node 22/24/26 | build warnings retained; no publish result claimed |
| Current source head contains only the intended product and test fence. | `source-read` | PR #1 changed-file list at `9fb2e455...` | exactly three files | clean-head native workflows queued at latest check |
| Late pre-removal async completion can regain cache authority. | `model-executed` plus independent review | review `4823648945`; unit 21 records | reproduced | target-executed repair belongs to unit 21 |

## Baseline characterization

### Command or workflow

```text
npm install --ignore-scripts --no-audit --no-fund
node probe.mjs
```

Workflow: `30548784323`.

### Assertions

- same adapter + same key + same JSON returns one object;
- same adapter + different keys + same JSON returns one object on baseline;
- different JSON returns different objects;
- separate adapters return different objects;
- mutating key A changes key B's previously returned object.

### Result

- status: success;
- platform matrix: Node `v22.23.1`, `v24.18.0`, `v26.5.1`;
- observed behavior: cross-key mutable alias confirmed;
- receipt: `playgrounds/EXP-20260730-jotai-json-key-isolation/result.json` in merged Fieldwork PR #228.

## Direct-source candidate execution

### Exact command set

```text
pnpm install --frozen-lockfile
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
pnpm eslint \
  src/vanilla/utils/atomWithStorage.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts
pnpm prettier --check \
  src/vanilla/utils/atomWithStorage.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts
pnpm tsc --noEmit
pnpm run build
```

### Exact jobs

- Node 22: job `91344257705` — success;
- Node 24: job `91344257734` — success;
- Node 26: job `91344257736` — success.

### Assertions and results per runtime

- `atomWithStorageKeyIsolation.test.ts`: 10 passed;
- `atomWithStorageReadInvalidation.test.ts`: 2 passed;
- existing `atomWithStorage.test.tsx`: 25 passed;
- total: 37 passed in three files;
- ESLint: passed;
- Prettier: passed;
- TypeScript: passed;
- complete build: passed.

The existing async storage suite emitted React `act(...)` warnings. Its assertions passed. Build output retained existing Rollup and TypeScript warnings while completing successfully.

## Native Jotai workflow classification

### Carrier-head `Test`

- run: `30690503622`;
- job: `91344257666`;
- result: failed at `pnpm run test:format`;
- exact cause: temporary execution note `UNIT20_STOP.md` required formatting;
- later steps: types, lint, specs, and build skipped;
- classification: `harness / execution-artifact failure`;
- product claim affected: no;
- repair: every temporary `UNIT20_*.md` file was removed from the clean head.

### Carrier-head `Preview Release`

- run: `30690503585`;
- job: `91344257650`;
- build: passed;
- publish preview: failed because the `pkg-pr-new` GitHub App is absent on `teamleaderleo/jotai`;
- classification: `fork publication setup`;
- product claim affected: no;
- repair: none required for unit 20 validation; public publishing remains outside authority.

### Other carrier-head workflows

- Compressed Size: success;
- Test Multiple Builds, Test Multiple Versions, and Test Old TypeScript: native runs were triggered; superseded run generations may remain queued or active due the cleanup commit sequence.

## Current clean-head native workflows

Clean head: `9fb2e455ed844d0fb248823009714ab5084d06fc`.

| Workflow | Run | Last observed state |
| --- | --- | --- |
| Test | `30690722042` | queued |
| Test Multiple Versions | `30690722083` | queued |
| Test Multiple Builds | `30690722063` | queued |
| Test Old TypeScript | `30690722057` | queued |
| Compressed Size | `30690722050` | queued |
| Preview Release | `30690722061` | queued; expected fork-app limit remains possible |

These runs belong to the exact clean source head. Update this section when they settle; do not substitute results from a superseded cleanup generation.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| changed-file format | `pnpm prettier --check <three files>` | pass | Node 22/24/26 |
| full repository format | native `Test` on clean head | queued | carrier red was temporary-file-only |
| changed-file lint | `pnpm eslint <three files>` | pass | Node 22/24/26 |
| full repository lint | native `Test` on clean head | queued |  |
| typecheck | `pnpm tsc --noEmit` | pass | Node 22/24/26 |
| focused package tests | named Vitest command | pass, 37/37 | Node 22/24/26 |
| complete target-declared specs | native `Test` on clean head | queued |  |
| build | `pnpm run build` | pass | Node 22/24/26 direct matrix |
| old TypeScript | native workflow | queued | clean head |
| multiple builds | native workflow | queued | clean head |
| multiple React versions | native workflow | queued | clean head |
| compressed size | native workflow | queued | clean head; carrier generation passed |
| preview publication | native workflow | queued | fork lacks `pkg-pr-new` app on carrier generation |

## Reversing controls

- Baseline fails cross-key identity isolation; candidate passes.
- Same-key identity and existing mount/subscription controls pass on candidate.
- Sync and async removal error/settlement paths preserve the initiating error while applying affected-key invalidation.
- Unrelated-key identity survives affected-key transitions.
- Late async completion remains a failing control for unit 20 alone and passes under unit 21's accepted generation repair.

## Soak, leak, and cleanup controls

- retained high-volume soak: absent;
- resources observed: adapter-local map entries by source inspection;
- retained-memory measurement: absent;
- cancellation/interruption: no cancellation API; async completion ordering characterized separately;
- immediate focused rerun: direct matrix passed on all three runtimes;
- execution workflow removed from clean source head: yes;
- all `UNIT20_*.md` notes removed from clean source head: yes;
- final changed-file fence: exactly three files.

## Historical setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| Fieldwork PR #236 run `30553976771` | corrupt patch at line 38; target setup never began | packaging | no candidate result | superseded by #252 |
| Fieldwork PR #242 | no transferable matrix on final head | execution absent | no | restacked in #252 |
| carrier native Test `30690503622` | temporary Markdown format failure | execution artifact | no | carrier files removed |
| Preview Release `30690503585` | fork lacks `pkg-pr-new` app | publication setup | no | record and exclude from product judgment |

## Platform and integration gaps

- browser storage events and real `localStorage`;
- React Native AsyncStorage;
- custom thenables with unusual settlement behavior;
- large dynamic key sets and retained heap measurements;
- final composed unit 20 + unit 21 source head.

## Cleanup receipt

- Temporary workflow absent from current source head: `yes`;
- execution-only root notes absent: `yes`;
- current source diff: exactly three intended files;
- retained workflow receipt: run `30690503592` at carrier head `ac5dd98...`;
- current clean head: `9fb2e455...`;
- remaining execution-only source files: `none`;
- remaining owned-fork PR: draft PR #1 as the source-review surface.

## Current test judgment

`HOLD — ACCEPT DIRECT-SOURCE UNIT 20 BASE`

Reason: the unit 20 code and focused compatibility boundary are directly materialized and target-executed, including the complete build on Node 22, 24, and 26. The current branch is clean. Final public preparation still needs the clean-head native workflows, independent complete-diff review, and an explicit source-head decision with unit 21's generation repair.

Clearing condition: settle and classify the clean-head native workflows at `9fb2e455...`, obtain independent review of that exact three-file diff, then select one final source head that sequences unit 21 without widening unit 20's claims.
