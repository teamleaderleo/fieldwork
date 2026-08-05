# Review — unit 21 Jotai async read generation

## In simple words

The clean unit-21 diff adds one per-key generation so obsolete asynchronous reads cannot replace or delete shared parsed identity after a newer read or completed removal. The source branch is clean, stacked on the exact unit-20 head, and contains the expanded eleven-case target-native test.

The project owner has explicitly accepted a separate AI complete-diff pass as the available independent review class for this work. This review is labeled accurately as an owner-authorized AI review, not a human review. The exact diff is accepted subject to the queued fork workflows completing successfully.

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
- Review class: owner-authorized AI complete-diff review
- Human-independent review: not claimed
- Complete unit-21 changed-file fence:
  - `src/vanilla/utils/atomWithStorage.ts`
  - `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts`
- Upstream-contact authority: none

## Exact diff review

Comparison `b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531` is ahead by two commits and behind by zero.

| Path | Additions | Deletions | Purpose |
| --- | ---: | ---: | --- |
| `src/vanilla/utils/atomWithStorage.ts` | 15 | 2 | per-key generation state, initiation capture, guarded publish/delete, completed-removal advance |
| `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` | 280 | 0 | eleven deterministic regression cases |

Commit shape:

1. `fix(utils): fence stale async JSON reads by per-key generation`
2. `test(utils): cover stale async JSON read fencing`

No workflow, Fieldwork file, receipt, dependency, lockfile, generated output, publisher, snapshot, or unrelated formatting is present.

## Review findings

### 1. State ownership is correctly placed

`createJSONStorage()` owns parsed cache identity, so its adapter-local generation map is the narrowest owner of publication authority. The change does not add state to callers or exported types.

### 2. Initiation order is implemented consistently

Every `getItem()` advances the key generation before backend access. A valid parse may publish and a malformed parse may delete only when the captured generation remains current. This treats successful and malformed completions symmetrically.

### 3. Rejection behavior remains precise

A backend rejection never reaches the parse closure, so it remains caller-visible and does not publish or delete cache identity. Because the newer read advanced authority at initiation, an older completion remains stale after that rejection. Existing cache identity is preserved.

### 4. Same-string compatibility is preserved

The cached-string lookup occurs before the generation publication guard. A stale caller resolving with bytes already represented by the current cache may receive that current cached object. This preserves historical same-string identity reuse while still preventing stale publication.

### 5. Removal timing matches the prerequisite

Generation advances inside unit 20's terminal `invalidate()` path. Pending asynchronous removal therefore preserves current identity until settlement, while any read started before completed removal loses later publication authority.

### 6. The stack boundary is real and clean

Unit 21 depends mechanically on unit 20's `cachedValues` map. Keeping the unit-21 diff stacked avoids duplicating the cross-key cache contribution and leaves a two-file review surface.

### 7. Exclusions are honest

`setItem()` and subscription callbacks do not participate in this generation. The packet and upstream draft explicitly leave read/write and read/subscription authority as separate questions.

## Risks and limits

- fork-local workflows are queued and not yet clean-head execution evidence;
- public main may move after the pinned 2026-08-01 source check;
- browser, React Native, Windows, and macOS integration remain unproved unless the queued jobs establish coverage;
- application-level frequency and retained-key cardinality remain unmeasured;
- the accepted review class is AI, not human, by explicit project-owner decision.

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
- [x] Owner-authorized AI complete-diff review is recorded at the exact head.

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

## Review disposition

`ACCEPT — subject to exact-head execution`

Reviewed source head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`  
Reviewed base head: `b2f84273b53bbed9df073354dac503e520be7101`  
Reviewer class: owner-authorized AI complete-diff review; human review not claimed  
Finding: no source, test, compatibility, or packaging defect requiring repair was found inside the stated boundary.  
Execution condition: the unit remains packet disposition `HOLD` until the queued exact-head workflows reach final conclusions and their actual coverage is recorded.  
Public interaction: unauthorized

## Final inspection focus after CI

1. Confirm the Test workflow executes the expanded eleven-case file at the exact source head.
2. Confirm build and aggregate test coverage rather than inferring it from workflow names.
3. Classify any failure as product, test, packaging, dependency, or runner failure.
4. Recheck current upstream overlap and contribution policy immediately before any authorized filing.
