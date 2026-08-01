# Review — unit 10 workerd receiver-aware types

## Review subject

- Work class: upstream source contribution preparation
- Target repository: `cloudflare/workerd`
- Proposed upstream base: `7cdc8c0e089287c8f3643f3a6f668ecdc221722a`
- Canonical clean source branch: `teamleaderleo/workerd:unit-10/receiver-aware-types`
- Exact source head: `f167a283fc9f792c427eeded306c38602e60261d`
- Owned clean PR: https://github.com/teamleaderleo/workerd/pull/5
- Fieldwork packet branch: `p0/435-unit-10-workerd-receiver-types`
- Complete changed-file fence: ten `types/` source/test files, one commit
- Upstream-contact authority: no

## Exact diff

https://github.com/teamleaderleo/workerd/compare/7cdc8c0e089287c8f3643f3a6f668ecdc221722a...f167a283fc9f792c427eeded306c38602e60261d

The branch excludes `.github/workflows/rook-issue-474-focused.yml`, all Fieldwork-only files, patches, and execution carriers.

## Claims requiring judgment

| Claim | Evidence | Reviewer challenge |
| --- | --- | --- |
| Ordinary JSG methods require an owning receiver | public issue #6904 source trace and native matrix | find a registered ordinary method that is intentionally receiver-independent |
| Marker provenance is required | print/reparse pipeline plus override/global transforms | propose a smaller durable identity mechanism |
| Context-global receiver union matches workerd | native matrix and TypeScript 5.8.3 fixture | inspect `globalThis`, `self`, nullish, and recursive generated output |
| Full replacements must use replacement generics | three-case standalone control | find another type-parameter ownership case |
| Checker-first heritage resolution is safe | same-name namespace regression | inspect generated declarations lacking checker symbols |
| Static members stay receiver-free and unextracted | generator/global tests | identify a static API represented as an ambient global by design |

## Source review history

- `d08e2e968b6db600c220e2babe0a07befa728ba2`: repair stale static ambient expectations.
- `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`: repair simple-name lexical heritage resolution.
- `54926f86c95185a7b83b2bf1ea901c35876a9a58`: repair generic full-replacement receiver specialization.
- `0ecc0a6632747031a6650c49a401760e511c9f36`: technical review `4827890474` accepted the repaired source and required exact-head execution.
- `f167a283fc9f792c427eeded306c38602e60261d`: exact ten source/test blobs rebased onto current public main; coordinator verified one-commit ten-file compare.

## Staleness and duplicate check

- Current public head checked: `7cdc8c0e089287c8f3643f3a6f668ecdc221722a`, 2026-08-01 review.
- Original base relationship: public head is three commits ahead of `6aa890be…`; only release-date files changed.
- Relevant source paths changed upstream: no.
- Open duplicate search: only issue #6904 found; no competing open implementation found.
- Contribution guidance checked at pinned current base: non-trivial changes should have prior discussion, tested code, small reviewable commits, and clean history.

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers.
- [x] No stale execution artifacts.
- [x] No unrelated formatting or generated churn identified.
- [x] One clean commit against current public main.
- [x] Commit-pinned code and test links recorded.

## Test review

- [x] Runtime/application matrix executed and merged in the owned testbed.
- [x] TypeScript receiver and erasure model executed.
- [x] Carrier lint passed.
- [ ] Clean-head focused target assertions completed.
- [ ] Clean-head ordinary target gates completed.
- [ ] Representative generated-output compatibility measured.
- [ ] Independent complete-diff acceptance at clean head.

## Known risks

- explicit receivers may expose existing callback assignment patterns as source errors;
- receiver widening can still be erased by plain callback types;
- broad ordinary-method annotation may encounter an intentionally detachable method registered through ordinary JSG machinery;
- global owner unions may affect generated-output complexity;
- a one-commit presentation is coherent but larger than ideal for review.

## Reviewer disposition

**EXECUTE**

Reviewed source head: `f167a283fc9f792c427eeded306c38602e60261d`  
Reason: source history and repaired diff are credible; clean-head target execution and independent acceptance remain outstanding.  
Clearing condition: complete focused and ordinary target gates, review representative generated output, then obtain independent complete-diff `ACCEPT` or a concrete repair.  
Reviewer eligibility: coordinator/self-review only for the clean rebase; prior technical review is supporting evidence, not final independent acceptance.

## Human deep-dive focus

1. Whether ordinary JSG registration always implies a receiver-sensitive declaration.
2. Whether the context-global union is the right source-compatibility boundary.
3. Whether generated-output review reveals broad source breaks or recursive type growth.
4. Whether to retain one commit or split into generator, overrides, and globals/test commits before public review.
