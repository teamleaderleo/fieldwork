# Unit 20 — fix(utils): isolate JSON storage cache identity by key

## In simple words

Jotai's `createJSONStorage()` adapter remembers parsed JSON so repeated reads of unchanged storage can reuse the same value identity. The released implementation keeps one remembered string and value for the whole adapter. Two different storage keys containing identical JSON can therefore receive the same mutable object. Mutating the object returned for one key changes the object already returned for the other key without a write or subscription event for that second key.

The retained candidate gives each key its own cache entry, preserves unchanged same-key identity across unrelated-key reads, and invalidates the affected key after removal, missing storage, or malformed JSON. Exact-source focused tests pass on Node 22, 24, and 26.

The current candidate also has a known asynchronous publication ordering limit: a read started before removal can resolve after removal settlement and become the cache entry used after identical JSON is recreated. The accepted generation-counter repair belongs to upstream unit 21. Unit 20 remains the clean base contribution and must be sequenced with unit 21 before a final upstream source candidate is presented as complete.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `pmndrs/jotai`
- Proposed upstream destination: `pmndrs/jotai` `main`
- Proposed title: `fix(utils): isolate JSON storage cache identity by key`
- Contribution synopsis: replace one adapter-wide parsed-JSON cache with adapter-lifetime per-key entries so equal serialized data under different keys produces independent values while unchanged same-key reads preserve identity.
- Work class: `upstream-fork research / patch-series preparation`

## Exact identities

- Public upstream base inspected: [`56a9cc51de8a5dd762b95a145820f12589cc47c9`](https://github.com/pmndrs/jotai/commit/56a9cc51de8a5dd762b95a145820f12589cc47c9)
- Public upstream `main` checked on 2026-08-01: same revision `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Preferred owned target fork: `teamleaderleo/jotai`
- Owned target fork status: repository admission required; no writable owned Jotai repository was available
- Intended canonical source branch: `fix/utils-key-scoped-json-cache`
- Canonical source head: `none`
- Fieldwork packet branch: `p0/435-unit-20-jotai-key-scoped-json-cache`
- Fieldwork packet head: recorded in the latest #435 handoff because a commit cannot contain its own SHA
- Canonical Fieldwork carrier: [PR #252](https://github.com/teamleaderleo/fieldwork/pull/252), branch `lane/235-jotai-json-storage-key-isolation-restack`, head `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Executed source/test generation: `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e`
- Retention-selection head: `fbfdebabd692d5635cdf03965c61f9a4e9764080`
- Superseded carriers: Fieldwork PRs #236 and #242
- Adjacent dependency: Fieldwork issue #282 and PR #317, owned by unit 21

## Current code and tests

### Product code

- [`candidate.patch`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/candidate.patch) — replaces the adapter-wide `lastStr`/`lastValue` pair with a key-scoped map and adds affected-key invalidation.
- [`atomWithStorage.ts` baseline](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/src/vanilla/utils/atomWithStorage.ts) — exact source under test.

### Target-native tests

- [`atomWithStorageKeyIsolation.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageKeyIsolation.test.ts) — same-key identity, cross-key isolation, mutation isolation, async storage, reviver, and removal outcomes.
- [`atomWithStorageReadInvalidation.test.ts`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageReadInvalidation.test.ts) — out-of-band removal and malformed-JSON restoration controls.
- Existing Jotai `tests/react/vanilla-utils/atomWithStorage.test.tsx` — historical mount/subscription compatibility control.

### Required generated or dependency files

`not applicable`

## Changed-file fence for the eventual target branch

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `src/vanilla/utils/atomWithStorage.ts` | production | yes |
| `tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts` | regression | yes, subject to target test-placement review |
| `tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts` | regression | yes, subject to target test-placement review |

Fieldwork workflows, reports, receipts, and patch-carrier files stay outside the target branch.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Released Jotai shares parsed identity across equal JSON under different keys. | `target-executed` | Fieldwork run `30548784323`, Node 22/24/26 | Frequency in applications is unmeasured. |
| Key-scoped caching removes cross-key aliases and preserves same-key identity. | `target-executed` | Runs `30579399493` and `30579753383`, Node 22/24/26 | Patch applied to pinned source; no direct owned source branch. |
| Focused candidate and existing storage tests pass. | `target-executed` | Current-head run `30579753383`; Node 24 job `90996761816` reports 37 tests | Complete target-declared suite and build were not run. |
| Changed source/tests pass ESLint, Prettier, and `tsc --noEmit`. | `target-executed` | Same matrix | Changed-file lint/format plus repository typecheck only. |
| Adapter-lifetime retention best preserves historical same-key identity. | `source-read` plus comparative review | selection review at `fbfdeb...` | Dynamic-key retained size is unmeasured. |
| A late pre-removal async read can regain cache publication authority. | `model-executed` plus independent review | review `4823648945`; 2026-08-01 local model | Repair belongs to unit 21. |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue/discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Queries: `createJSONStorage cache key identity`, `atomWithStorage identical JSON different keys`, `lastStr storage`, and equivalent pull-request searches
- Equivalent open implementation found: `no`
- Direct prior work: Jotai issue #1079 and merged PR #1080 / commit `9e336c6bd2bebf257ffca957b0af18f97444323c` established same-key identity reuse during mount/subscription setup
- Related but distinct work: Jotai issue #1815 covers reset subscription propagation, not parsed-object cache identity
- Relationship: complementary correction to the 2022 one-key cache repair

## Remaining work

Complete in this order:

1. Admit or identify a writable owned Jotai fork and create `fix/utils-key-scoped-json-cache` from exact upstream base `56a9cc51...`.
2. Materialize unit 20 source and tests with no Fieldwork execution files.
3. Decide delivery sequencing with unit 21: stack its accepted generation repair on this branch or present a combined upstream change after both packets agree on one source head.
4. Run `pnpm run fix:format`, `pnpm run build`, `pnpm run test`, plus the focused regression on the exact source head.
5. Obtain independent complete-diff review and repeat duplicate/policy checks before any authorized contact.

## Blockers and limits

- Writable owned `teamleaderleo/jotai` repository absent.
- Direct target-source head absent.
- Jotai complete build and aggregate test gate absent for a clean source branch.
- Unit 20's carrier has a known stale async-completion publication limit; unit 21 owns the accepted repair.
- Browser and React Native storage integrations remain unexecuted.
- Public upstream interaction remains unauthorized.

## Latest handoff

State: `HOLD`  
Exact source head: `none; retained patch carrier d9dd61c4a0d1f9073c300519990e6ba9ec2855d9 over upstream 56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Exact packet head: `see latest #435 handoff`  
Tests: `released baseline reproduced; focused candidate 37/37 on Node 22/24/26; ESLint/Prettier/tsc passed; ordinary build and aggregate test absent`  
Temporary machinery remaining: `Fieldwork PR #252 workflow and patch carrier; excluded from future target branch`  
Next worker action: `admit the owned fork, materialize unit 20, then coordinate a source-head stack with unit 21 before ordinary gates`  
Public upstream interaction: `none`
