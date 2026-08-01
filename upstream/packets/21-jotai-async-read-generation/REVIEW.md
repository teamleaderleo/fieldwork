# Review — unit 21 Jotai async read generation

## In simple words

The selected change adds one per-key generation counter so stale asynchronous reads cannot replace shared parsed identity after a newer read or completed removal. Focused target execution supports the core repair, and this packet adds rejection controls plus a precise stack dependency result.

The main review challenge is packaging: unit 21 is a clean diff only after unit 20's per-key cache. A final reviewer should verify the stacked base, execute the expanded native cases, and challenge the initiation-ordered rejection rule before promotion.

## Review subject

- Work class: upstream-fork research and stacked patch preparation
- Target repository: `pmndrs/jotai`
- Proposed upstream base: unit 20 clean source head based on public main `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Canonical source branch: intended `teamleaderleo/jotai:fix/utils-async-read-generation`; repository absent
- Exact source head: none
- Accepted research execution head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- Workflow-free carrier head: `34670f709753668827043bbc76c4159a8b36ade2`
- Fieldwork packet branch: `p0/435-unit-21-jotai-async-read-generation`
- Exact packet head: recorded in the final #435 handoff because the packet cannot embed its own commit SHA
- Complete proposed target changed-file fence:
  - `src/vanilla/utils/atomWithStorage.ts`
  - `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [`source patch`](./patches/0001-fix-utils-fence-stale-async-json-reads.patch)
6. [`expanded native test draft`](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts)
7. [`local reconciliation receipt`](./receipts/20260801-local-reconciliation.md)
8. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
9. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- accepted repair patch: [`34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/async-read-generation-candidate.patch)
- accepted six-case tests: [`34670f7...`](https://github.com/teamleaderleo/fieldwork/blob/34670f709753668827043bbc76c4159a8b36ade2/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/atomWithStorageAsyncReadGenerationRepair.test.ts)
- unit 20 prerequisite patch: [`d9dd61c4...`](https://github.com/teamleaderleo/fieldwork/blob/d9dd61c4a0d1f9073c300519990e6ba9ec2855d9/programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/candidate.patch)
- current public source: [`56a9cc51...`](https://github.com/pmndrs/jotai/blob/56a9cc51de8a5dd762b95a145820f12589cc47c9/src/vanilla/utils/atomWithStorage.ts)
- direct target compare: unavailable until owned fork and source branches exist
- generated or dependency files: none

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| initiation order should control shared read publication | characterization and repair workflows | Does this match the intended cache contract for async backends? |
| a rejected newer read suppresses older publication while preserving prior cache identity | passing 11-case model and prepared native tests | Should rejection own authority at initiation even though it publishes no value? |
| same-string stale callers may reuse newer cached identity | source path plus model case 11 | Is this precise compatibility behavior acceptable and clearly described? |
| completed removal advances read authority | unit 20 settlement path plus repair patch | Does advancing inside terminal invalidation preserve pending-removal semantics? |
| unit 21 must stack on unit 20 | direct and stacked `git apply --check` receipt | Should upstream receive stacked PRs, or should the coordinator later combine the two units? |
| generation entries share adapter-lifetime retention | source read and unit 20 decision | Is dynamic-key growth acceptable for the narrow fix? |

## Known risks

- unit 20 may change before direct materialization, requiring patch reconciliation;
- rejected-read cases have model evidence and a native draft, with target execution pending;
- public main may move after the 2026-08-01 duplicate and source check;
- no owned fork means branch cleanliness and commit history remain unreviewed;
- focused Linux/Node evidence omits browser, React Native, Windows, and macOS paths;
- read/write and read/subscription ordering remain separate.

## Evidence limits

- strongest source behavior evidence: focused target execution on exact pinned source;
- strongest new edge evidence: local model execution;
- no complete target-declared gate at a clean source head;
- no application integration or frequency evidence;
- no maintainer feedback or upstream acceptance.

## Staleness check

- Current upstream head checked: `56a9cc51de8a5dd762b95a145820f12589cc47c9` on 2026-08-01
- Candidate base relationship: unit-21 patch applies only after unit-20 patch
- Relevant source paths changed upstream since the original execution: no change observed; public main remained the exact executed target revision
- Duplicate/overlap search date: 2026-08-01
- Open replacement work found: none in the searched current issues and pull requests
- Packet and target PR descriptions synchronized: packet yes; target PR unavailable

## Source cleanliness

- [ ] Clean target source branch exists.
- [x] Retained unit-only patch contains one production file.
- [x] Proposed target fence contains no Fieldwork files, workflows, publishers, receipts, dependency, lock, or generated changes.
- [x] No unrelated formatting change is present in the retained patch.
- [x] Temporary unit-21 workflow is absent from workflow-free carrier head `34670f7...`.
- [ ] Commit-pinned target-source links exist for the final branch.

## Test review

- [x] Intended six-case repair assertions ran.
- [x] Baseline/candidate relationship is explicit.
- [x] Setup and product failures are separated.
- [x] Valid, missing, malformed, removal, rejection, and unrelated-key paths are represented across executed and prepared evidence.
- [x] Existing storage-suite compatibility ran in the focused target workflow.
- [x] Platform and integration limits are explicit.
- [ ] Expanded eleven-case native test ran at the final source head.
- [ ] `pnpm run build` ran at the final source head.
- [ ] `pnpm run test` ran at the final source head.

## Draft review

- [x] Discussion draft avoids prevalence and severity claims.
- [x] Pull-request draft describes the retained unit-only diff and stack dependency.
- [x] Target terminology and conventional commit title are used.
- [x] Public draft body omits internal workflow vocabulary and private context.
- [ ] Current contribution and AI-disclosure policy checked immediately before filing.
- [ ] Public interaction authorized.

## Reviewer disposition

`HOLD`

Reviewed source head: none; accepted research head `e99c7d2e9e3b16c04b1738397ad6109758ad481e`  
Reviewed packet head: final branch head recorded in #435 handoff  
Reason: the technical direction is accepted for direct materialization, while the required unit-20 base branch, owned fork, expanded target-native execution, ordinary gates, and exact-head independent review remain absent.  
Clearing condition: materialize unit 20 on an owned clean source branch, create unit 21 as its clean child with the expanded native test, execute focused and ordinary gates, and obtain independent complete-diff review.  
Reviewer eligibility: self-review only

## Human deep-dive guide

The final human reviewer should focus on:

1. whether rejected read initiation should supersede older publication authority;
2. whether the same-string stale-caller behavior is described accurately;
3. whether unit 21 should remain stacked on unit 20 or be combined by coordinator decision;
4. whether adapter-lifetime generation retention needs measurement before upstream preparation;
5. whether direct PR or a bug discussion better fits the project's current contribution route.

Suggested response:

`Unit 21 looks ready for direct-source execution after unit 20`  
—or—  
`Unit 21 concern: <specific source, test, compatibility, or packaging issue>`
