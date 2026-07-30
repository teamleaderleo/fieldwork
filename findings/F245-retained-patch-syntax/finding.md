# F245-retained-patch-syntax: reject incomplete retained patches before they become evidence

Finding state: `review-ready`

Workstream: `A`  
Canonical Fieldwork issue: `#245`  
Canonical finding path: `findings/F245-retained-patch-syntax/finding.md`  
Canonical implementation: `teamleaderleo/fieldwork#249`  
Exact implementation head: `e093eb8af37fb9ee08020596c13d9d50d0f8789b`  
Exact base or source revision: `teamleaderleo/fieldwork@896a617c4b4dd8dd9fb9493d05f801c7baf9ade3` reviewed main; PR base history is older and diverged  
Strongest evidence class: `full-gate`  
Reviewed input generation: `PR #249 exact head e093eb8af37fb9ee08020596c13d9d50d0f8789b`  
Current review disposition: `none — independent complete-diff review pending`  
Desk routing: `Review Queue #213`  
Upstream contact authorized: `no`

## In simple words

Fieldwork keeps patch files as evidence and later applies them to pinned source trees. Its validator previously checked enough syntax to catch many broken patches, yet one binary-patch case slipped through: the first binary data block could be complete while a later block was cut off. The validator remembered that some data had appeared and accepted the whole file. Git itself rejected the same patch as corrupt.

PR #249 now checks each binary `literal` or `delta` block separately. Starting a new block forces the previous block to be complete, and ending the file forces the final block to be complete.

The current answer is: the known parser hole is repaired and the exact head is green. A separate reviewer still needs to inspect the complete three-file diff before promotion.

## Why we care

A retained patch is used as evidence that a proposed change can be reproduced. Accepting a truncated patch allows a repository check to say the evidence is valid while the target tool refuses to apply it. That creates false confidence, stale review claims, and wasted execution time later in the delivery path.

## What happens if we leave it alone

The observed failure is narrow and concrete: a patch with one valid Git binary block followed by a truncated second block passes Fieldwork's old validator and fails native `git apply --check` as corrupt. Frequency across future retained patches is unknown. The consequence appears whenever such a malformed file is treated as valid evidence.

## Current finding

The retained-patch validator must track completeness per binary payload block, along with its existing per-file and per-hunk checks. The repaired exact head does this and passes the focused suite plus Fieldwork integrity.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The predecessor validator accepted a complete first binary block followed by a truncated later block. | `target-executed` | Native negative control recorded in PR #249; reproducer added to `scripts/test_validate_patch_syntax.py`. | Proves this parser case, not every possible Git patch extension. |
| Native Git rejects that malformed patch. | `target-executed` | `git apply --check` rejected the retained reproducer as corrupt. | Native rejection does not prove the Fieldwork parser matches every Git version. |
| Head `e093eb8a...` validates every binary block independently. | `source-read` | `scripts/validate_patch_syntax.py` complete diff at PR #249. | Requires review of the exact head; later movement expires the claim. |
| The repaired exact head passes repository validation. | `full-gate` | Fieldwork integrity run `30579669056`; local focused suite 29/29. | This validates retained-patch syntax, not application against every target source. |

## System and ownership map

- Entry point: `.github/workflows/fieldwork-integrity.yml` invokes repository validation.
- State owner: `scripts/validate_patch_syntax.py` owns parser state for each file section, hunk, and Git binary payload block.
- Data flow: tracked `*.patch` files are read, parsed, and either accepted or rejected before the repository gate succeeds.
- Side effect: gate success permits the retained patch to be treated as syntactically valid evidence.
- Recovery: malformed patches fail the gate and must be repaired before later target execution.
- Public contract: repository-local evidence validation only.
- Test boundary: `scripts/test_validate_patch_syntax.py` plus every tracked retained patch.

## Historical precedent

### Native Git patch validation

- Source: `https://git-scm.com/docs/git-apply`
- Revision or date: documentation retrieved for the 2026-07-31 review; native executable used in the exact control.
- Principle supported: the receiving patch tool is authoritative about whether an encoded patch is complete enough to apply.
- Important difference: Fieldwork performs an earlier repository-level syntax gate across retained evidence; target workflows still need native `git apply --check` against each pinned source revision.

### Earlier Fieldwork signoff at the predecessor head

- Source: `https://github.com/teamleaderleo/fieldwork/pull/249`
- Revision or date: predecessor signoff was bound to `62e35d52cc64757951e4f99e57f086b46d0899d2`.
- Principle supported: review approval belongs to an exact commit, not a moving branch name.
- Important difference: later complete-diff review found the second-block defect, so the predecessor R3/D0 signoff expired automatically.

## Approaches considered

### Retained approach: block-local parser state

Track whether each binary block has payload data. Validate the previous block when a new `literal` or `delta` header appears and validate the final block at section end. This matches the actual encoded-unit boundary and keeps diagnostics local.

### Declined: one `binary_data_seen` flag per file

This was the defective design. Once the first block contained data, later incomplete blocks inherited a false success state.

### Deferred: delegate all syntax validation to native Git

Native Git remains mandatory in target-specific workflows, yet repository integrity also needs a deterministic check that scans every retained patch without checking out every target repository. Full native equivalence belongs outside this finding.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Complete first binary block, truncated second block | Focused test plus native Git control | Rejected by repaired parser and native Git. |
| One complete binary block | Focused positive control | Accepted. |
| Two complete binary blocks | Focused positive control | Accepted. |
| Bare or header-only `GIT binary patch` | Focused negative controls | Rejected. |
| Non-empty metadata-only create/delete | Focused negative controls | Rejected. |
| Empty-file SHA-1/SHA-256 create/delete | Focused positive controls | Accepted. |
| Mode-only and 100% rename/copy metadata | Focused positive controls | Accepted. |
| Malformed, truncated, and overlong text hunks | Existing focused matrix | Rejected. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Exact parity with all future Git patch syntax | Fieldwork intentionally implements a bounded validator. | Reopen when a valid Git-produced patch is rejected or an invalid one passes. |
| Patch applicability to the pinned target source | Syntax alone cannot establish context applicability. | Each target workflow must run native `git apply --check`. |
| Semantic correctness of the represented source change | Parser validation carries no product-semantics claim. | Owning target finding and implementation review. |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/fieldwork@e093eb8af37fb9ee08020596c13d9d50d0f8789b` | focused validator suite | coordinator environment | 29 tests passed | `target-executed` |
| same | native `git apply --check` malformed second-block control | native Git | rejected as corrupt | `target-executed` |
| same | Fieldwork integrity `30579669056` | GitHub Actions | success | `full-gate` |

## Complete-diff and compatibility review

- Complete changed-file fence: `.github/workflows/fieldwork-integrity.yml`, `scripts/validate_patch_syntax.py`, `scripts/test_validate_patch_syntax.py`.
- Current-base relationship: GitHub reports mergeable; PR #249 is diverged from current main and must be reviewed as a complete diff.
- Temporary carrier status: none; this is the direct Fieldwork implementation branch.
- Compatibility surfaces examined: text hunks, multi-file sections, mode metadata, empty files, rename/copy metadata, binary summaries, and Git binary payload blocks.
- Known source defect or routine repair remaining: none identified at the exact head.
- Reviewer eligibility: independent complete-diff review remains required because the repair author performed the latest technical pass.

## Current disposition and desk routing

- Finding state: `review-ready`
- Review disposition: `none — independent review pending`
- Review Queue entry: `#213`
- Delivery lane: `not-entered`
- Exact next transition: independent complete-diff review of PR #249 at `e093eb8a...`
- Clearing condition: reviewer returns ACCEPT with the exact head and current full-gate receipt.
- Required subgates: complete diff, base relationship, focused tests, Fieldwork integrity, evidence boundary.
- User decision requested: none; technical review comes first.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | PR #249 predecessor `62e35d5...` | Earlier R3/D0 signoff accepted a narrower parser implementation. |
| 2026-07-30 | `59020c40b34dfd2529bdef470868f438c6a76c81` | Added per-binary-block validation. |
| 2026-07-30 | `e093eb8af37fb9ee08020596c13d9d50d0f8789b` | Added the malformed second-block regression and two-complete-block control; state became review-ready. |

## References

- `https://github.com/teamleaderleo/fieldwork/issues/245`
- `https://github.com/teamleaderleo/fieldwork/pull/249`
- `https://github.com/teamleaderleo/fieldwork/actions/runs/30579669056`
- `https://git-scm.com/docs/git-apply`
- `.github/workflows/fieldwork-integrity.yml`
- `scripts/validate_patch_syntax.py`
- `scripts/test_validate_patch_syntax.py`
