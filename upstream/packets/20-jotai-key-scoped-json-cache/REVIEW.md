# Review — unit 20 Jotai key-scoped JSON cache

## In simple words

Unit 20 is now directly materialized in the owned Jotai fork. The clean branch contains exactly one production file and two target-native test files. A dedicated exact-head matrix passed 37 focused and adjacent tests, changed-file ESLint and Prettier, repository TypeScript checking, and the complete Jotai build on Node 22, 24, and 26.

The key-scoped cache base is ready for independent source review. Final public preparation remains held because unit 21 owns the accepted generation fence for stale asynchronous read completions. The reviewer should decide the clean delivery sequence, not revisit the already-executed cross-key alias mechanism without reversing evidence.

## Review subject

- Work class: `upstream-fork research / clean source candidate base`
- Target repository: `teamleaderleo/jotai`, intended destination `pmndrs/jotai`
- Proposed upstream base: `main` at `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Canonical source branch: `fix/key-scoped-json-cache`
- First clean product-and-test generation: `e295dc741a706153b50e7d27fbd424fcc48519cb`
- Exact executed carrier head: `ac5dd98da6c3083f31560b71d84ad3bf850aaafc`
- Current clean source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`
- Owned-fork PR: `teamleaderleo/jotai#1`
- Fieldwork packet branch: `p0/435-unit-20-jotai-key-scoped-json-cache`
- Fieldwork packet PR: `teamleaderleo/fieldwork#441`
- Complete changed-file fence: one production file and two native test files
- Upstream-contact authority: `none`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [complete clean source compare](https://github.com/teamleaderleo/jotai/compare/56a9cc51de8a5dd762b95a145820f12589cc47c9...9fb2e455ed844d0fb248823009714ab5084d06fc)
6. [production file](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/src/vanilla/utils/atomWithStorage.ts)
7. [key-isolation tests](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts)
8. [read-invalidation tests](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts)
9. Fieldwork issue #282 and PR #317 for unit 21's accepted generation repair
10. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
11. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- clean compare: [`56a9cc51...9fb2e455`](https://github.com/teamleaderleo/jotai/compare/56a9cc51de8a5dd762b95a145820f12589cc47c9...9fb2e455ed844d0fb248823009714ab5084d06fc)
- production source: [`atomWithStorage.ts`](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/src/vanilla/utils/atomWithStorage.ts)
- tests: [`atomWithStorageKeyIsolation.test.ts`](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts), [`atomWithStorageReadInvalidation.test.ts`](https://github.com/teamleaderleo/jotai/blob/9fb2e455ed844d0fb248823009714ab5084d06fc/tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts)
- generated or dependency files: `none`

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Cache ownership must include storage key. | released run `30548784323` and direct run `30690503592` | Does any intended Jotai contract justify one mutable parsed identity crossing key boundaries? |
| Adapter-lifetime per-key retention is the narrow compatibility choice. | retention review `fbfdeb...` and interleaved same-key controls | Is there representative dynamic-key evidence strong enough to require a lifecycle change in this bug fix? |
| Missing, malformed, and removal outcomes should invalidate affected-key identity. | direct native tests and source diff | Are the terminal-outcome rules consistent with backend ambiguity and Jotai's current storage contract? |
| Unit 21 should fence stale async publication. | independent review `4823648945`, issue #282, PR #317 | Should the final upstream source head combine both units or use a reviewed stack? |
| Two focused test files are appropriate. | direct 37-test matrix | Would consolidation improve review without losing the failure-order controls? |

## Known risks

- Per-key entries can accumulate for dynamic keys; practical retained size remains unmeasured.
- Unit 20 alone leaves stale async completion publication possible; unit 21 has the accepted repair.
- Removal rejection can follow a durable delete, so terminal invalidation is conservative.
- Browser and React Native storage integrations remain outside the executed matrix.
- Existing React `act(...)` warnings appeared in the adjacent suite; assertions passed and the warnings predate the candidate.

## Evidence limits

- clean-head native Jotai workflows were queued at the latest packet update;
- browser and React Native integration were not executed;
- production prevalence and retained-memory cost remain unmeasured;
- unit 21 has not yet been materialized on the same final source head;
- packet review remains self-review until an independent reviewer records a disposition.

## Staleness check

- Current upstream and fork base checked: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Candidate base relationship: clean branch is a direct descendant, three files changed
- Relevant source paths changed upstream since the selected base: `no` at fork admission
- Duplicate/overlap search date: `2026-08-01`
- Open equivalent implementation found: `none`
- Related public work: issue #1079 / PR #1080 and issue #1815; neither implements cross-key cache isolation
- Packet and owned-fork PR descriptions synchronized: `pending final PR-body update after clean-head workflow classification`

## Source cleanliness

- [x] Direct target source head exists.
- [x] No Fieldwork-only files in target source diff.
- [x] Temporary execution workflow removed.
- [x] Temporary `UNIT20_*.md` files removed.
- [x] No unrelated formatting or generated churn.
- [x] Required generated or lock changes: none.
- [x] Commit-pinned links resolve to the current clean head.
- [x] Changed-file fence is exactly three files.

## Test review

- [x] Intended cross-key assertion ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Named failure and cleanup paths are covered.
- [x] Same-key compatibility controls are present.
- [x] Changed-file lint and format checks passed.
- [x] Repository typecheck passed.
- [x] Complete build passed on Node 22/24/26.
- [x] Temporary carrier files are absent on the current source head.
- [ ] Clean-head native workflow generation settled and classified.
- [ ] Unit 21 mechanism reran on the agreed final source head.

## Draft review

- [x] Discussion draft stays within mechanism evidence.
- [x] Pull-request draft names the exact unit 20 base and its unit 21 limit.
- [x] Target terminology and conventional commit style are used.
- [x] Internal process vocabulary is excluded from the proposed public body.
- [ ] AI-disclosure requirement checked immediately before filing.
- [ ] Exact public-contact authorization recorded.

## Reviewer disposition

`HOLD — ACCEPT UNIT 20 DIRECT-SOURCE BASE`

Reviewed source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`  
Executed carrier head: `ac5dd98da6c3083f31560b71d84ad3bf850aaafc`  
Reviewed packet head: `current PR #441 head`  
Reason: the direct unit 20 implementation is clean and target-executed. Final source promotion still requires clean-head native workflow classification, independent complete-diff review, and an explicit composition or stacking decision with unit 21.  
Clearing condition: accept the exact three-file diff independently, settle clean-head workflows, and select one final source head carrying the agreed unit 20/unit 21 sequence.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The independent reviewer should focus on:

1. whether terminal invalidation on removal rejection is the right conservative cache rule;
2. whether adapter-lifetime retention is acceptable for actual Jotai storage adapter use;
3. whether the current two-file regression layout is easier to review than consolidation;
4. whether unit 21 should land in one combined source diff or a clearly ordered stack;
5. whether any clean-head native failure points to product behavior instead of fork setup.

Suggested response:

`Unit 20 direct-source base accepted at 9fb2e455; proceed to unit 21 sequencing`  
—or—  
`Unit 20 concern: <specific source, test, compatibility, or evidence issue>`
