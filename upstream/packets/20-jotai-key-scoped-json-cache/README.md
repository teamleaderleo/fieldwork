# Unit 20 — fix(utils): isolate JSON storage cache identity by key

## In simple words

Jotai's `createJSONStorage()` adapter remembers parsed JSON so unchanged reads can reuse the same value identity. The released implementation keeps one remembered string and value for the whole adapter. Two different storage keys containing identical JSON can therefore receive the same mutable object. Mutating the value returned for one key changes the value already returned for the other key without a write or subscription event for that second key.

Unit 20 gives every storage key its own cache entry. Unchanged same-key reads retain identity across unrelated-key activity, equal JSON under different keys parses independently, and removal or unreadable storage invalidates only the affected key.

The code now exists on a clean owned Jotai branch and has passed focused tests, changed-file lint and formatting, repository typechecking, and the complete Jotai build on Node 22, 24, and 26. A separate accepted successor, unit 21, owns generation fencing for stale asynchronous read completions. Unit 20 is a validated base contribution; final public preparation must sequence both units deliberately.

## Current disposition

`HOLD — DIRECT SOURCE BASE ACCEPTED; FINAL UPSTREAM CANDIDATE AWAITS UNIT 21 SEQUENCING AND CLEAN-HEAD NATIVE RECEIPTS`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `pmndrs/jotai`
- Owned target fork: [`teamleaderleo/jotai`](https://github.com/teamleaderleo/jotai)
- Owned-fork review surface: [`teamleaderleo/jotai#1`](https://github.com/teamleaderleo/jotai/pull/1)
- Proposed upstream destination: `pmndrs/jotai` `main`
- Proposed title: `fix(utils): scope JSON cache by storage key`
- Contribution synopsis: replace one adapter-wide parsed-JSON cache with adapter-lifetime per-key entries so equal serialized data under different keys produces independent values while unchanged same-key reads preserve identity.
- Work class: `upstream-fork research / clean source candidate base`

## Exact identities

- Public upstream base inspected: [`56a9cc51de8a5dd762b95a145820f12589cc47c9`](https://github.com/pmndrs/jotai/commit/56a9cc51de8a5dd762b95a145820f12589cc47c9)
- Owned fork `main` at admission: identical to `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Canonical source branch: `fix/key-scoped-json-cache`
- First clean product-and-test generation: [`e295dc741a706153b50e7d27fbd424fcc48519cb`](https://github.com/teamleaderleo/jotai/commit/e295dc741a706153b50e7d27fbd424fcc48519cb)
- Target-executed carrier head: [`ac5dd98da6c3083f31560b71d84ad3bf850aaafc`](https://github.com/teamleaderleo/jotai/commit/ac5dd98da6c3083f31560b71d84ad3bf850aaafc)
- Current clean source head: [`9fb2e455ed844d0fb248823009714ab5084d06fc`](https://github.com/teamleaderleo/jotai/commit/9fb2e455ed844d0fb248823009714ab5084d06fc)
- Current clean compare: [`56a9cc51...9fb2e455`](https://github.com/teamleaderleo/jotai/compare/56a9cc51de8a5dd762b95a145820f12589cc47c9...9fb2e455ed844d0fb248823009714ab5084d06fc)
- Fieldwork packet branch: `p0/435-unit-20-jotai-key-scoped-json-cache`
- Fieldwork packet PR: [`teamleaderleo/fieldwork#441`](https://github.com/teamleaderleo/fieldwork/pull/441)
- Historical Fieldwork carrier: [PR #252](https://github.com/teamleaderleo/fieldwork/pull/252), head `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Historical executed source/test generation: `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e`
- Retention-selection head: `fbfdebabd692d5635cdf03965c61f9a4e9764080`
- Superseded Fieldwork carriers: PRs #236 and #242
- Adjacent dependency: Fieldwork issue #282 and PR #317, owned by unit 21

## Current code and tests

### Product code

- [`src/vanilla/utils/atomWithStorage.ts`](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/src/vanilla/utils/atomWithStorage.ts) — key-scoped parsed-value cache and affected-key invalidation.

### Target-native tests

- [`atomWithStorageKeyIsolation.test.ts`](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts) — same-key identity, cross-key isolation, mutation isolation, asynchronous storage, reviver behavior, and removal terminal outcomes.
- [`atomWithStorageReadInvalidation.test.ts`](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts) — out-of-band removal and malformed-JSON restoration controls.
- Existing Jotai `tests/react/vanilla-utils/atomWithStorage.test.tsx` — historical mount/subscription compatibility control.

### Required generated or dependency files

`not applicable`

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `src/vanilla/utils/atomWithStorage.ts` | production | yes |
| `tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts` | regression | yes, subject to final test-placement review |
| `tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts` | regression | yes, subject to final test-placement review |

The current clean head contains exactly these three changed files. The one-off workflow and every `UNIT20_*.md` execution note were removed after receipt transfer.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Released Jotai shares parsed identity across equal JSON under different keys. | `target-executed` | Fieldwork run `30548784323`, Node 22/24/26 | Application frequency remains unmeasured. |
| Key-scoped caching removes cross-key aliases and preserves same-key identity. | `target-executed` | Owned-fork run `30690503592`, jobs `91344257705`, `91344257734`, `91344257736` | Unit 21 owns stale async publication ordering. |
| Focused candidate and existing storage tests pass. | `target-executed` | Same owned-fork run on Node 22/24/26 | Focused and adjacent storage suites, not every integration. |
| Changed source/tests pass ESLint, Prettier, and `tsc --noEmit`. | `target-executed` | Same owned-fork run | Changed-file lint/format plus repository typecheck. |
| Complete Jotai build passes on Node 22/24/26. | `target-executed` | Same owned-fork run, `Build` step successful in all three jobs | Build receipt belongs to carrier head `ac5dd98...`; clean head removes only execution files. |
| Current clean source diff contains only production source and two native tests. | `source-read` | clean head `9fb2e455...` and PR #1 changed-file list | Fresh clean-head native workflows were queued at this update. |
| Native `Test` red on carrier head was execution-file formatting only. | `target-executed harness finding` | run `30690503622`, job `91344257666`; only `UNIT20_STOP.md` differed | Product, types, lint, specs, and build were skipped after format failure. |
| Preview Release built successfully and failed at publication setup. | `target-executed harness finding` | run `30690503585`, job `91344257650`; `pkg-pr-new` app absent on fork | Publication is outside the unit's required evidence. |
| Adapter-lifetime retention best preserves historical same-key identity. | `source-read` plus comparative review | retention selection at `fbfdeb...` | Dynamic-key retained size remains unmeasured. |
| A late pre-removal async read can regain cache publication authority. | `model-executed` plus independent review | review `4823648945`; unit 21 repair records | Repair belongs to unit 21. |

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

1. Let the current clean-head native Jotai workflows settle and classify any failures against `9fb2e455...`.
2. Obtain independent complete-diff review of the exact clean three-file head.
3. Decide delivery sequencing with unit 21: stack its accepted generation repair onto this base or prepare one combined source candidate after both packets identify the same source head.
4. Run browser or React Native integration only if final review identifies a concrete compatibility question that focused and native gates cannot answer.
5. Repeat duplicate and contribution-policy checks immediately before any separately authorized public contact.

## Blockers and limits

- Final submission sequencing with unit 21 remains unresolved.
- Fresh native clean-head workflow results were queued at the time of this packet update.
- Browser and React Native storage integrations remain unexecuted.
- Dynamic-key retention frequency and retained size remain unmeasured.
- Public upstream interaction remains unauthorized.

## Latest handoff

State: `HOLD — direct source base accepted`  
Exact source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`  
Exact packet head: `see current PR #441 head and latest #435 handoff`  
Tests: `direct-source run 30690503592 passed focused tests, ESLint, Prettier, tsc, and full build on Node 22/24/26; clean-head native runs queued`  
Temporary machinery remaining: `none on clean source head; receipt retained in PR #1 history and workflow run`  
Next worker action: `classify clean-head native runs, obtain complete-diff review, then align source-head sequencing with unit 21`  
Public upstream interaction: `none`
