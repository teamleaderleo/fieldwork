# Review — unit 20 Jotai key-scoped JSON cache

## In simple words

The unit 20 mechanism is well supported: Jotai's released adapter shares parsed object identity across different keys containing equal JSON, and a per-key map removes that alias while preserving same-key identity in the executed matrix. The packet remains on hold because the clean owned source branch and ordinary repository gates are absent, and final delivery must include or explicitly sequence unit 21's asynchronous generation fence.

The final reviewer should challenge the delivery boundary: whether unit 20 can be submitted independently with an explicit ordering limit, or whether one composed source head should carry both key isolation and generation authority.

## Review subject

- Work class: upstream-fork research / patch-series preparation
- Target repository: `pmndrs/jotai`
- Proposed upstream base: `main` at `56a9cc51de8a5dd762b95a145820f12589cc47c9`, current as checked 2026-08-01
- Canonical source branch: intended `teamleaderleo/jotai:fix/utils-key-scoped-json-cache`
- Exact source head: none
- Fieldwork packet branch: `p0/435-unit-20-jotai-key-scoped-json-cache`
- Exact packet head: latest #435 handoff
- Complete eventual changed-file fence: `src/vanilla/utils/atomWithStorage.ts` plus target-native regression tests
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [unit 20 product patch](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/candidate.patch)
6. [key-isolation tests](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageKeyIsolation.test.ts)
7. [read-invalidation tests](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageReadInvalidation.test.ts)
8. Fieldwork issue #282 / PR #317 for the adjacent accepted generation repair
9. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
10. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- current evidence carrier: Fieldwork PR #252 at `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- production file baseline: [`atomWithStorage.ts`](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/src/vanilla/utils/atomWithStorage.ts)
- target compare: unavailable until owned source branch exists
- generated or dependency files: none expected

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Cache ownership must include storage key. | released run `30548784323` and source at `56a9cc51...` | Does any intended contract justify cross-key mutable identity? |
| Adapter-lifetime per-key retention is the narrow compatibility choice. | selection review `fbfdeb...` | Does Jotai have representative dynamic-key use that warrants a bound or lifecycle API now? |
| Missing, malformed, and removal outcomes should invalidate affected-key identity. | unit 20 focused tests | Are the selected terminal-outcome rules consistent with storage backend contracts? |
| Async completion publication requires generation authority. | review `4823648945`, issue #282, PR #317 | Should this ship in one PR with unit 20 or as an explicit stacked change? |
| Two focused test files are appropriate. | executed 37-test matrix | Would maintainers prefer cases integrated into existing test files without losing assertion coverage? |

## Known risks

- Per-key entries can accumulate for dynamic keys; reopen with representative measurements.
- Unit 20 alone leaves stale async completion publication possible; unit 21 has the accepted repair.
- Focused green execution may miss complete build or suite failures.
- Removal rejection can follow a durable delete, making cache authority conservative by design.
- Existing React test warnings appeared in the baseline suite; assertions passed and the warnings were unrelated to this candidate.

## Evidence limits

- no clean direct source branch
- no `pnpm run build` receipt
- no aggregate `pnpm run test` receipt
- no browser or React Native integration receipt
- no production prevalence or retained-memory measurement
- self-review only for this packet

## Staleness check

- Current upstream head checked: `56a9cc51de8a5dd762b95a145820f12589cc47c9` on 2026-08-01
- Candidate base relationship: patch applies and current-head workflow passed against that exact source
- Relevant source paths changed upstream since execution: no, based on the checked `main` head
- Duplicate/overlap search date: 2026-08-01
- Open replacement work found: none
- Related public work: #1079/PR #1080 and #1815; neither implements cross-key isolation
- Packet and target PR descriptions synchronized: target PR absent; draft synchronized with packet

## Source cleanliness

- [ ] Direct target source head exists.
- [ ] No Fieldwork-only files in target source diff.
- [ ] No temporary workflows or publishers.
- [ ] No stale execution artifacts.
- [ ] No unrelated formatting or generated churn.
- [x] Required generated or lock changes currently expected: none.
- [ ] Commit-pinned target links resolve to the reviewed direct head.

## Test review

- [x] Intended cross-key assertion actually ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Named failure and cleanup paths are covered.
- [x] Same-key compatibility controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Ordinary target gates ran on a direct source head.
- [ ] Unit 21 mechanism reran on the composed source head.

## Draft review

- [x] Discussion draft stays within mechanism evidence.
- [x] Pull-request draft describes the intended composed diff and marks its missing head.
- [x] Target terminology and conventional commit style are used.
- [x] Internal process vocabulary is absent from the public draft body.
- [ ] AI disclosure requirement checked at filing time.
- [ ] Exact public-contact authorization recorded.

## Reviewer disposition

`HOLD`

Reviewed source head: `none; carrier d9dd61c4a0d1f9073c300519990e6ba9ec2855d9 over upstream 56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Reviewed packet head: `latest #435 handoff`  
Reason: key isolation is target-executed, while source admission, ordinary gates, and unit 21 sequencing remain unresolved.  
Clearing condition: materialize one clean owned Jotai source head carrying the agreed unit 20/21 sequence, pass declared target gates, and obtain independent complete-diff review.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether the per-key map belongs in one combined PR with generation fencing;
2. whether invalidation on every terminal removal outcome matches expected backend semantics;
3. whether adapter-lifetime retention is acceptable for real Jotai adapter usage;
4. whether the test layout fits repository conventions;
5. whether a Discussion-first route is preferable before source submission.

Suggested response:

`Unit 20 looks ready for source admission and composed execution`  
—or—  
`Unit 20 concern: <specific source, test, compatibility, or sequencing issue>`
