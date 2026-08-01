# Review — unit 21 Jotai async read generation

## In simple words

The selected change adds one per-key generation counter so stale asynchronous reads cannot replace or delete shared parsed identity after a newer read or completed removal. The clean stacked source branch now exists, includes the expanded eleven-case target-native test, and has an exact two-file diff.

The technical and packaging questions are now reviewable directly. The remaining execution question is whether the fork's queued workflows pass at the exact source head. The remaining promotion question is independent complete-diff review.

## Review subject

- Work class: upstream-fork source candidate / stacked proposal
- Target repository: `pmndrs/jotai`
- Public/fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Unit 20 clean base branch: `teamleaderleo/jotai:fix/utils-key-scoped-json-cache`
- Unit 20 exact head: `b2f84273b53bbed9df073354dac503e520be7101`
- Canonical unit 21 branch: `teamleaderleo/jotai:fix/utils-async-read-generation`
- Exact unit 21 source head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`
- Fork-local draft PR: `teamleaderleo/jotai#3`
- Fieldwork packet branch: `p0/435-unit-21-jotai-async-read-generation`
- Complete unit-21 changed-file fence:
  - `src/vanilla/utils/atomWithStorage.ts`
  - `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [clean target compare](https://github.com/teamleaderleo/jotai/compare/b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531)
6. [clean production source](https://github.com/teamleaderleo/jotai/blob/dfe607d7637fbcf61ae41c39f4f470f61fa7c531/src/vanilla/utils/atomWithStorage.ts)
7. [clean target-native test](https://github.com/teamleaderleo/jotai/blob/dfe607d7637fbcf61ae41c39f4f470f61fa7c531/tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts)
8. [`direct source materialization receipt`](./receipts/20260801-direct-source-materialization.md)
9. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
10. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff review

Comparison `b2f8427...dfe607d` is ahead by two commits and behind by zero.

| Path | Additions | Deletions | Purpose |
| --- | ---: | ---: | --- |
| `src/vanilla/utils/atomWithStorage.ts` | 15 | 2 | per-key generation state, initiation capture, guarded publish/delete, completed-removal advance |
| `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` | 280 | 0 | eleven deterministic regression cases |

Commit shape:

1. `fix(utils): fence stale async JSON reads by per-key generation`
2. `test(utils): cover stale async JSON read fencing`

No workflow, Fieldwork file, receipt, dependency, lockfile, generated output, publisher, snapshot, or unrelated formatting is present.

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| initiation order controls shared read publication | characterization, accepted repair, clean source | Does this match the intended cache contract for async backends? |
| a rejected newer read suppresses older publication while preserving existing cache | model and native cases | Should a rejected initiation retain authority even though it publishes no value? |
| same-string stale callers reuse newer cached identity | source path and case 11 | Is this compatibility precision correct and sufficiently documented? |
| completed removal advances read authority only on settlement | unit-20 removal path and clean source | Does settlement-time advance preserve pending-removal identity semantics? |
| unit 21 remains stacked on unit 20 | exact branch ancestry and two-file compare | Should eventual delivery remain stacked or be combined after coordinator review? |
| generation entries have adapter-lifetime retention | source review | Is dynamic-key growth acceptable for this narrow repair? |

## Known risks and limits

- fork-local workflows are queued and not yet evidence of clean-head success;
- public main may move after the pinned 2026-08-01 source check;
- independent review is not yet recorded;
- browser, React Native, Windows, and macOS integration remain unproved unless the queued jobs establish coverage;
- read/write and read/subscription authority remain separate;
- application-level frequency and retained-key cardinality remain unmeasured.

## Staleness and overlap

- current inspected upstream head: `56a9cc51de8a5dd762b95a145820f12589cc47c9` on 2026-08-01;
- clean unit-21 merge base: unit-20 head `b2f84273b53bbed9df073354dac503e520be7101`;
- duplicate/overlap search date: 2026-08-01;
- equivalent current implementation found: none in searched records;
- target and packet PR descriptions: synchronized with the clean branch identities;
- duplicate and contribution-policy checks must be repeated immediately before any authorized filing.

## Source cleanliness

- [x] Clean target source branch exists.
- [x] Exact unit-20 base head is named.
- [x] Exact unit-21 source head is named.
- [x] Unit 21 is behind its base by zero.
- [x] Unit 21 contains exactly two target files.
- [x] Unit 21 contains two conventional commits.
- [x] Commit-pinned code and test links exist.
- [x] No temporary workflow or evidence machinery is in the target diff.
- [x] No dependency, lock, generated, or unrelated formatting change is present.

## Test review

- [x] Baseline characterization ran.
- [x] Accepted six-case repair ran on Node 22/24/26.
- [x] Existing storage compatibility ran in historical focused execution.
- [x] Missing, malformed, removal, rejection, unrelated-key, and same-string paths are represented.
- [x] Expanded eleven-case native test exists at the exact clean head.
- [x] Fork-local ordinary workflows were triggered at the exact clean head.
- [ ] Fork-local Test workflow completed and its test count/commands were inspected.
- [ ] Build coverage at the exact clean head was confirmed.
- [ ] Aggregate test coverage at the exact clean head was confirmed.
- [ ] All other fork-local workflows reached final conclusions.

## Draft review

- [x] Discussion draft avoids prevalence and severity claims.
- [x] Pull-request draft describes the unit-only diff and stack dependency.
- [x] Target terminology and conventional commit title are used.
- [x] Public draft body omits internal execution vocabulary.
- [ ] Contribution and AI-disclosure policy rechecked immediately before filing.
- [ ] Public interaction authorized.

## Self-review disposition

`HOLD`

Reviewed source head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`  
Reviewed base head: `b2f84273b53bbed9df073354dac503e520be7101`  
Reason: source materialization and cleanliness are complete; exact-head workflows remain queued and independent review remains absent.  
Clearing condition: record final workflow conclusions and actual job coverage, repair any failure inside the two-file boundary, then obtain independent complete-diff review.  
Reviewer eligibility: self-review only

## Human deep-dive guide

The independent reviewer should focus on:

1. rejection retaining publication authority at initiation;
2. same-string stale-caller identity reuse;
3. removal advancing generation only after settlement;
4. adapter-lifetime generation retention;
5. whether stacked or combined eventual delivery is clearer;
6. exact workflow evidence at `dfe607d...`.

Suggested response:

`Unit 21 ACCEPT at dfe607d7637fbcf61ae41c39f4f470f61fa7c531 over b2f84273b53bbed9df073354dac503e520be7101`  
—or—  
`Unit 21 REPAIR: <specific source, test, compatibility, or packaging issue>`
