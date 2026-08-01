# Review — unit 07 backgroundFetchSize snapshot

## In simple words

The proposed contribution closes a demonstrated accounting and callback-reentry defect with a two-file diff. The strongest review question is whether constructor-wide rejection of invalid runtime values matches the project’s option policy. The highest execution gate is current-head cross-platform coverage and benchmarks.

## Review subject

- Work class: upstream-fork research
- Target repository: `teamleaderleo/node-lru-cache` for preparation; proposed destination `isaacs/node-lru-cache`
- Proposed upstream base: `main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`
- Canonical source branch: `repair/background-fetch-size-source`
- Exact source head: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`
- Fieldwork packet branch: `p0/435-unit-07-node-lru-background-fetch-size`
- Exact packet head: latest unit 07 handoff on #435; this file cannot self-pin its containing commit
- Complete changed-file fence: `src/index.ts`, `test/background-fetch-size.ts`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact product diff
6. exact test diff
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: [`16b3a916...0f4a357a`](https://github.com/teamleaderleo/node-lru-cache/compare/16b3a916662ab449d496b7b4b4f04132565d1d28...0f4a357a9bc0b09ad413e99fa566317bf4ce283c)
- production file: [`src/index.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/src/index.ts)
- tests: [`test/background-fetch-size.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/0f4a357a9bc0b09ad413e99fa566317bf4ce283c/test/background-fetch-size.ts)
- generated or dependency files: none

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| constructor rejects every invalid runtime value | released probe plus constructor matrix | should an explicitly supplied unused option still be validated eagerly? |
| snapshot occurs before user code | exact source ordering and callback mutation control | does any alternate background-fetch construction bypass the receipt assignment? |
| optional exported receipt preserves compatibility | exported `BackgroundFetch` type and review `4824064389` | is optional internal metadata acceptable on this public type? |
| zero remains valid | released and candidate zero coalescing controls | does zero conflict with any documented positive-size assumption? |
| stale/no-size paths remain unchanged | exact source branches and native controls | are there other size-tracked refresh paths that should receive a receipt? |
| adjacent autopurge test belongs in the file | repository complete-coverage failures on earlier heads | should this pre-existing branch control move to a separate test file? |

## Known risks

- Eager validation changes runtime behavior for invalid option values even when size tracking is inactive; the packet records lazy validation as a viable alternative.
- The internal receipt extends an exported intersection type; optionality addresses source compatibility, while runtime enforcement protects accounting.
- Real-timer autopurge polling can remain scheduler-sensitive; the test uses a bounded transition poll and clears the cache.
- Earlier broad green receipts belong to other heads; current results control promotion.

## Evidence limits

- production prevalence and ecosystem impact are unknown
- synthetic cache values only
- no public maintainer feedback
- benchmark gate establishes absence of workflow failure, without a quantitative performance claim
- author self-review cannot supply independent acceptance

## Staleness check

- Current upstream head checked: `16b3a916662ab449d496b7b4b4f04132565d1d28` on 2026-08-01
- Candidate base relationship: direct child, one commit
- Relevant source paths changed upstream since execution: `no`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: none
- Packet and target PR descriptions synchronized: source identity and changed-file fence yes; final workflow outcomes pending

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers.
- [x] No stale execution artifacts.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are absent.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Intended baseline assertions executed.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Failure and compatibility paths are covered.
- [x] Zero, stale, no-size, and next-operation controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Current exact-head CI result inspected.
- [ ] Current exact-head benchmark result inspected.

## Draft review

- [x] Issue draft stays within demonstrated consequence and avoids prevalence claims.
- [x] PR draft describes the actual two-file diff.
- [x] Target terminology is used.
- [x] Internal process vocabulary and private context are absent from public draft sections.
- [ ] AI disclosure requirement checked again at filing time.

## Reviewer disposition

`EXECUTE`

Reviewed source head: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`  
Reviewed packet head: latest unit 07 handoff on #435  
Reason: source ownership, compatibility repair, and diff cleanliness are coherent; current exact-head repository execution remains controlling.  
Clearing condition: CI `30674355332` and Benchmarks `30674355680` pass, then an independent reviewer inspects the complete exact diff and test reachability.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether eager constructor validation is the desired public contract;
2. whether optional `BackgroundFetch.__size` balances internal enforcement and exported-type compatibility;
3. whether the autopurge coverage control is reliable across the declared matrix;
4. whether direct PR preparation is preferable to an issue-first discussion.

Suggested response:

`Unit 07 looks ready for upstream preparation`  
—or—  
`Unit 07 concern: <specific source, test, compatibility, or framing issue>`
