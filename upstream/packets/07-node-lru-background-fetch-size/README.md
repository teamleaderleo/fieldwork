# Unit 07 — snapshot backgroundFetchSize before invoking user code

## In simple words

`lru-cache` reserves provisional size while a missing value is fetched. Released `11.5.2` accepts invalid runtime values into that accounting. `NaN`, infinity, negative and fractional numbers, and runtime strings can corrupt calculated size, split same-key fetches, evict unrelated entries, or damage index bookkeeping.

The selected repair validates the option, snapshots it before synchronous user `fetchMethod` code runs, stores that receipt on the internal background-fetch promise, and charges the dispatched operation from the receipt. Later field mutation applies to later operations. Zero remains valid; stale refresh and caches without size tracking keep their existing behavior.

The canonical target branch is one commit over the public `11.5.2` head, with only product source and the native test file changed. The final test generation adds hostile non-coercion, explicit constructor/default versus mutated `undefined`, and invalid-field stale refresh controls preserved in the superseded carrier reviews.

## Current disposition

`HOLD — exact-head target execution pending`

Last verified: `2026-08-01`  
Worker: `OpenAI assistant — unit 07`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `isaacs/node-lru-cache`
- Proposed upstream destination: `isaacs/node-lru-cache:main`
- Proposed title: `fix: snapshot backgroundFetchSize before invoking user code`
- Contribution synopsis: validate `backgroundFetchSize` as a primitive nonnegative integer and bind each missing-key fetch to one validated provisional-size receipt captured before user code runs.
- Work class: `upstream-fork research`

## Exact identities

- Public upstream base inspected: [`16b3a916662ab449d496b7b4b4f04132565d1d28`](https://github.com/isaacs/node-lru-cache/commit/16b3a916662ab449d496b7b4b4f04132565d1d28)
- Owned target fork: `teamleaderleo/node-lru-cache`
- Canonical source branch: `repair/background-fetch-size-source`
- Canonical source head: [`70a9e62b0555e6bb68763fb9d32458fa82fd2a70`](https://github.com/teamleaderleo/node-lru-cache/commit/70a9e62b0555e6bb68763fb9d32458fa82fd2a70)
- Canonical target PR: [`teamleaderleo/node-lru-cache#2`](https://github.com/teamleaderleo/node-lru-cache/pull/2)
- Fieldwork packet branch: `p0/435-unit-07-node-lru-background-fetch-size`
- Fieldwork packet head: see the latest unit 07 handoff on [`#435`](https://github.com/teamleaderleo/fieldwork/issues/435); a file cannot pin the commit that contains itself.
- Exact focused execution carrier: Fieldwork PR [`#135`](https://github.com/teamleaderleo/fieldwork/pull/135) at `a6768dc743d572e422d6e16a21f8b856fc7f2e7c`
- Superseded source heads: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`, `fef8328c9431b656c0ee48547250e37d6caeabef`, and earlier PR #2 review heads
- Superseded carriers: owned target PR [`#1`](https://github.com/teamleaderleo/node-lru-cache/pull/1), patch artifact on Fieldwork PR #135

## Current code and tests

### Product code

- [`src/index.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/70a9e62b0555e6bb68763fb9d32458fa82fd2a70/src/index.ts) — constructor validation, pre-dispatch snapshot, optional exported receipt field, and receipt-based provisional accounting.

### Target-native tests

- [`test/background-fetch-size.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/70a9e62b0555e6bb68763fb9d32458fa82fd2a70/test/background-fetch-size.ts) — labeled invalid values, hostile non-coercion, constructor/default and mutated `undefined`, public mutation, synchronous re-entry, next-operation semantics, zero coalescing, invalid stale/no-size controls, settlement, corrupted internal receipt, and autopurge branch coverage.

### Required generated or dependency files

- `not applicable`; the clean target diff contains no dependency, lockfile, workflow, snapshot, or generated-output changes.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `src/index.ts` | production | yes |
| `test/background-fetch-size.ts` | regression and compatibility controls | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Released `11.5.2` accepts invalid values into live accounting | `target-executed` | Fieldwork workflow `30491292307`, Node 22/24/26; retained probe on PR #135 | synthetic values and released package |
| User `fetchMethod` runs before provisional insertion consumes size | `source-read` | base and candidate `src/index.ts` at exact commits | source ordering |
| Snapshot design closes the mutable-field consumption window | `source-read` | target head `70a9e62b...` | exact-head execution controls promotion |
| Product patch and an earlier focused test pair passed Node 22/24/26 | `target-executed` | Fieldwork PR #135; 70 assertions per runtime, build, OXLint, Prettier | earlier test revision and external carrier |
| Broader native suite passed on several earlier direct heads | `target-executed` | target PR #2 comments for runs `30580263075`, `30580879839`, and benchmarks `30580263012` | earlier heads; coverage and compatibility repairs followed |
| Current clean candidate passes native matrix | `target-test-prepared` | CI `30674843003`; Benchmarks `30674842990` | queued at this packet revision |
| Current final test content passes focused build/lint/format matrix | `target-test-prepared` | Fieldwork carrier `30674901995`, Node 22/24/26 | queued at this packet revision |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues/PRs checked: GitHub issue and PR searches for `backgroundFetchSize` and `background fetch size`
- Equivalent implementation found: `no`
- Relationship to prior work: the candidate repairs the public option introduced by upstream commit [`4708153206daf822a3ad440ce47248b9cfbdb973`](https://github.com/isaacs/node-lru-cache/commit/4708153206daf822a3ad440ce47248b9cfbdb973); no later replacement exists on current public `main`.

## Remaining work

Complete in this order:

1. Inspect CI `30674843003`, Benchmarks `30674842990`, and focused carrier `30674901995` at exact source head `70a9e62b...`.
2. Repair only assertion-relevant source or test defects; classify setup, dependency, coverage, and runner failures separately.
3. Perform fresh complete-diff review, update the packet and PR front page, and obtain independent acceptance before any upstream preparation.

## Blockers and limits

- Exact-head native CI, benchmarks, and focused lint/format receipts are pending.
- Current evidence uses synthetic cache values; production frequency and ecosystem impact remain unmeasured.
- Public upstream filing and PR creation require separate explicit authority.
- The author can complete self-review and repair; consequential final acceptance requires an independent reviewer.

## Latest handoff

State: `HOLD — exact-head target execution pending`  
Exact source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`  
Exact packet head: latest unit 07 handoff on #435  
Tests: released probe passed Node 22/24/26; earlier direct heads passed focused/full behavior and benchmarks; current native and focused gates queued  
Temporary machinery remaining: Fieldwork execution workflow on PR #135; retire after receipt transfer  
Next worker action: inspect runs `30674843003`, `30674842990`, and `30674901995`, then synchronize disposition  
Public upstream interaction: `none`
