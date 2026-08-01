# Review — unit 07 backgroundFetchSize snapshot

## In simple words

The proposed contribution closes a demonstrated accounting and callback-reentry defect with a two-file diff. Complete prior-art review added three native controls to the first clean generation: hostile non-coercion, constructor/default versus mutated `undefined`, and invalid-field stale refresh. The strongest design question remains whether eager constructor rejection matches the project’s option policy. The highest execution gate is current-head cross-platform coverage, benchmarks, and focused lint/format.

## Review subject

- Work class: upstream-fork research
- Target repository: `teamleaderleo/node-lru-cache` for preparation; proposed destination `isaacs/node-lru-cache`
- Proposed upstream base: `main` at `16b3a916662ab449d496b7b4b4f04132565d1d28`
- Canonical source branch: `repair/background-fetch-size-source`
- Exact source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`
- Fieldwork packet branch: `p0/435-unit-07-node-lru-background-fetch-size`
- Exact packet head: latest unit 07 handoff on #435; this file cannot self-pin its containing commit
- Focused execution carrier: Fieldwork PR #135 at `a6768dc743d572e422d6e16a21f8b856fc7f2e7c`
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

- complete compare: [`16b3a916...70a9e62b`](https://github.com/teamleaderleo/node-lru-cache/compare/16b3a916662ab449d496b7b4b4f04132565d1d28...70a9e62b0555e6bb68763fb9d32458fa82fd2a70)
- production file: [`src/index.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/70a9e62b0555e6bb68763fb9d32458fa82fd2a70/src/index.ts)
- tests: [`test/background-fetch-size.ts`](https://github.com/teamleaderleo/node-lru-cache/blob/70a9e62b0555e6bb68763fb9d32458fa82fd2a70/test/background-fetch-size.ts)
- generated or dependency files: none

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| constructor rejects every invalid runtime value without coercion | released probe, primitive guard, hostile object test | should an explicitly supplied unused option still be validated eagerly? |
| explicit constructor `undefined` remains omission/default | constructor destructuring and native control | does this align with the project’s runtime option conventions? |
| mutated `undefined` rejects at missing-key consumption | pre-dispatch mutation control | is the omission-versus-mutation distinction clear enough for users? |
| snapshot occurs before user code | exact source ordering and callback mutation control | does any alternate background-fetch construction bypass the receipt assignment? |
| optional exported receipt preserves compatibility | exported `BackgroundFetch` type and review `4824064389` | is optional internal metadata acceptable on this public type? |
| zero remains valid | released and candidate zero coalescing controls | does zero conflict with any documented positive-size assumption? |
| stale/no-size paths ignore an invalid field | exact source branches and native controls | are there other non-missing-key paths that should remain usage-bound? |
| adjacent autopurge test belongs in the file | repository complete-coverage failures on earlier heads | should this pre-existing branch control move to a separate test file? |

## Known risks

- Eager validation changes runtime behavior for invalid option values even when size tracking is inactive; lazy validation remains a viable alternative.
- The internal receipt extends an exported intersection type; optionality addresses source compatibility, while runtime enforcement protects accounting.
- Real-timer autopurge polling can remain scheduler-sensitive; the test uses a bounded transition poll and clears the cache.
- The stale invalid-field control must observe a stale provider result; default `allowStale: false` makes the returned promise wait for settlement.
- Earlier broad green receipts belong to other heads; current results control promotion.

## Evidence limits

- production prevalence and ecosystem impact are unknown
- synthetic cache values only
- no public maintainer feedback
- benchmark gate establishes workflow success without a quantitative performance claim
- author self-review cannot supply independent acceptance

## Staleness check

- Current upstream head checked: `16b3a916662ab449d496b7b4b4f04132565d1d28` on 2026-08-01
- Candidate base relationship: direct child, one commit
- Relevant source paths changed upstream since execution: `no`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: none
- Packet and target PR descriptions synchronized: source identity, controls, changed-file fence, and current run IDs yes

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers.
- [x] No stale execution artifacts.
- [x] No unrelated formatting or generated churn.
- [x] No dependency or lockfile changes.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Intended baseline assertions executed.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Failure and compatibility paths are covered.
- [x] Hostile, `undefined`, zero, stale, no-size, callback-reentry, next-operation, internal receipt, and settlement controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Current exact-head CI result inspected.
- [ ] Current exact-head benchmark result inspected.
- [ ] Current exact-head focused build/lint/format result inspected.

## Draft review

- [x] Issue draft stays within demonstrated consequence and avoids prevalence claims.
- [x] PR draft describes the actual two-file diff and final controls.
- [x] Target terminology is used.
- [x] Internal process vocabulary and private context are absent from public draft sections.
- [ ] AI disclosure requirement checked again at filing time.

## Reviewer disposition

`EXECUTE`

Reviewed source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`  
Reviewed packet head: latest unit 07 handoff on #435  
Reason: source ownership, non-coercive validation, usage-bound compatibility, exported-type repair, and diff cleanliness are coherent; current exact-head execution remains controlling.  
Clearing condition: CI `30674843003`, Benchmarks `30674842990`, and carrier `30674901995` pass, then an independent reviewer inspects the complete exact diff and assertion reachability.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether eager constructor validation is the desired public contract;
2. whether optional `BackgroundFetch.__size` balances internal enforcement and exported-type compatibility;
3. whether hostile/`undefined`/stale controls accurately prove the intended boundaries;
4. whether the autopurge coverage control is reliable across the declared matrix;
5. whether direct PR preparation is preferable to an issue-first discussion.

Suggested response:

`Unit 07 looks ready for upstream preparation`  
—or—  
`Unit 07 concern: <specific source, test, compatibility, or framing issue>`
