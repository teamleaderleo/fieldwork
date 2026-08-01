# Review — Unit 02: uv BusyBox `realpath` compatibility

## In simple words

The proposed source change removes unsupported shell utility delimiters from every current relocatable-launcher owner. Prior GNU/BusyBox execution and affected-crate compilation passed. The final reviewer should challenge bare option-like `$0`, macOS/BSD behavior, source-branch cleanliness, and whether project-run should recognize both old and new generated forms.

## Review subject

- Work class: upstream bug-fix preparation
- Target repository: `astral-sh/uv`
- Proposed upstream base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Canonical source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Exact source head: packet `README.md`
- Fieldwork packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Exact packet head: packet `README.md` and #435 handoff
- Complete changed-file fence: wheel.rs, virtualenv.rs, project/run.rs
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact product diff from packet README
6. exact test links in `TESTS.md`
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: packet `README.md`
- production files: packet `README.md`
- tests: wheel `test_shebang` is updated in the same source file; current integration expectations remain linked in `DEEP_DIVE.md`
- generated or dependency files: none

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Removing both delimiters is the narrow repair | 24-case GNU/BusyBox matrix | Does any supported invocation supply a bare option-like `$0`? |
| All three owners must change together | exact current source links and 3-file candidate fence | Should project-run accept both historical and corrected forms? |
| Symlink behavior is retained | external-symlink matrix and upstream PR #8079 lineage | Is the controlled fixture sufficient, or should a target-native integration test be added? |
| No runtime BusyBox detection is needed | GNU candidate matrix remains clean | Does upstream prefer explicit platform branching despite the simpler result? |
| Source diff should remain three files | generated and recognizer strings are co-located | Is centralization worth the broader change now? |

## Known risks

- bare `-tool` `$0` remains outside executed evidence;
- macOS/BSD utility behavior remains unexecuted;
- older generated shebangs may remain in environments after update;
- fork default main is stale, so carrier PR-wide diff and CI cannot represent the clean source diff;
- Astral AI policy requires independent human ownership and forbids autonomous public contribution.

## Evidence limits

- no production prevalence estimate;
- no native macOS/FreeBSD execution;
- no newline-containing paths;
- no complete source-only upstream CI run against a synchronized fork base at initial review write.

## Staleness check

- Current upstream head checked: `79bbface771210df216b738e9bdc7df95e5a9e6b` on 2026-08-01
- Candidate base relationship: direct child required
- Relevant source paths changed upstream since prior execution: virtualenv path changed, but delimiter text and exact 5/7 counts remained compatible at current base
- Duplicate/overlap search date: 2026-08-01
- Open replacement work found: public issue #16209; no equivalent public PR found
- Packet and target PR descriptions synchronized: draft packet only; no public PR created

## Source cleanliness

- [ ] Exact source head recorded.
- [ ] No Fieldwork-only files in target source diff.
- [ ] No temporary workflows or publishers.
- [ ] No stale execution artifacts.
- [ ] No unrelated formatting or generated churn.
- [ ] Exact 3-file compare reviewed.
- [ ] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Prior intended matrix assertions ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Cleanup paths are controlled by trap.
- [x] GNU compatibility control is present.
- [ ] Current-head focused workflow is green.
- [ ] macOS/BSD platform gap accepted or closed.
- [ ] Ordinary source-only target gates are named and run at the clean head.

## Draft review

- [x] Existing issue selected instead of duplicate filing.
- [x] PR draft describes the intended three-file diff.
- [x] Target terminology is used.
- [x] Internal process vocabulary is excluded from proposed public summary.
- [x] AI policy checked and recorded.
- [ ] Human rewrites and owns all public communication.

## Reviewer disposition

`HOLD`

Reviewed source head: pending final clean commit  
Reviewed packet head: pending final packet commit  
Reason: current-head execution, clean source materialization, and independent human review remain open.  
Clearing condition: record a successful current workflow, publish one exact source-only commit, verify its complete compare, and obtain human review.  
Reviewer eligibility: self-review only

## Human deep-dive guide

The final human reviewer should focus on:

1. whether delimiter removal covers the supported `$0` contract;
2. whether project-run should recognize both generated forms;
3. macOS/BSD compatibility;
4. exact three-file cleanliness and test sufficiency;
5. rewriting any public description in their own words under Astral's AI policy.

Suggested response:

`Unit 02 looks ready for human upstream preparation`  
—or—  
`Unit 02 concern: <specific source, test, compatibility, or framing issue>`
