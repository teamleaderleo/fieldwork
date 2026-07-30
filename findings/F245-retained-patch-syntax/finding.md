# F245-retained-patch-syntax: require every retained Git binary marker to be complete

Finding state: `research-active`

Workstream: `A`  
Canonical Fieldwork issue: `#245`  
Canonical finding path: `findings/F245-retained-patch-syntax/finding.md`  
Canonical implementation: parent PR #249 with bounded repair PR #281  
Reviewed parent head: `e093eb8af37fb9ee08020596c13d9d50d0f8789b`  
Current repair head: `8b78f88115bacbe93c07c9e5628dac6ae26cb803`  
Exact Fieldwork main reviewed: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`  
Strongest current evidence class: `target-test-prepared` for the mixed-form repair; predecessor parser behavior is `target-executed`  
Reviewed input generation: complete-diff review `4823746557`, issue #245 current body, PR #249, and PR #281  
Current review disposition: `REPAIR / EXECUTE`  
Desk routing: outside Review Queue promotion and Delivery Desk until repair execution and fresh review  
Upstream contact authorized: `no`

## In simple words

Fieldwork keeps patch files as evidence. Its validator learned to reject a complete first binary-data block followed by a truncated later block. A later complete-diff review found a neighboring hole: a bare `GIT binary patch` marker can still hide behind a valid mode change, text hunk, empty-file record, rename/copy record, or binary summary in the same file section.

The reviewed parent head therefore remains defective. PR #281 makes every Git binary marker an independent obligation: the marker must contain a `literal` or `delta` header, every started block must contain encoded data, and every later block must also finish.

Current action: execute the original and new controls at PR #281 head `8b78f881...`, integrate or restack the repair onto the canonical branch, synchronize the resulting exact head, and perform fresh independent complete-diff review.

## Why we care

A retained patch is evidence that a proposed change can be reproduced. Accepting an incomplete patch allows repository integrity to report valid evidence while native Git later rejects the file. That creates expired review claims, misleading delivery status, and wasted target execution.

The mixed-form hole is especially easy to miss because another valid form can make the file section look complete even though the binary marker remains truncated.

## What happens if we leave it alone

Observed parent behavior accepts this malformed patch:

```text
diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
GIT binary patch
```

The same masking class applies when a complete text hunk or binary-summary line appears with the bare marker. Frequency among future retained patches is unknown. The failure occurs whenever such a file is promoted as valid evidence.

## Current finding

Git binary syntax creates two distinct obligations:

1. **marker completeness** — every `GIT binary patch` marker must be followed by at least one `literal` or `delta` payload header;
2. **block completeness** — every started payload block must contain encoded data and finish before another block or section boundary.

The reviewed parent head enforces block completeness only after a payload header appears. PR #281 adds marker completeness before alternate file-section forms can pass.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The older validator accepted a complete first binary block followed by a truncated later block. | `target-executed` | Parent PR #249 controls and native Git negative check. | One malformed binary-block class. |
| Parent head `e093eb8a...` rejects unfinished started blocks. | `target-executed` | Original 29-test suite and Fieldwork integrity `30579669056`. | Does not cover a marker with no payload header when another section form is valid. |
| Parent head accepts a bare marker hidden behind another valid section form. | `source-read` plus deterministic counterexample | Review `4823746557` and issue #245 minimal patch. | Current repair execution is pending. |
| PR #281 checks marker completeness before alternate section acceptance. | `source-read` | `scripts/validate_patch_syntax.py` at `8b78f881...`. | Requires exact-head execution and independent review. |
| Three mixed-form negative controls exercise mode, text-hunk, and binary-summary masking. | `target-test-prepared` | `scripts/test_validate_patch_syntax_binary_marker.py`. | Workflow `30587468319` is queued at this finding generation. |

## System and ownership map

- Entry point: `.github/workflows/fieldwork-integrity.yml`.
- Parser owner: `scripts/validate_patch_syntax.py`.
- Evidence input: every tracked `*.patch` file plus focused generated controls.
- File-section state: text hunks, metadata-only forms, binary summaries, and Git binary payload state.
- Side effect: integrity success permits the patch to be treated as syntactically valid evidence.
- Recovery: repair the malformed file or parser before promotion.
- Target boundary: each target workflow still runs native `git apply --check` against its pinned source.

## Historical precedent

### Native Git patch validation

- Source: Git `apply` documentation and the native executable used by the retained controls.
- Principle supported: the receiving patch implementation remains authoritative for actual parse and applicability behavior.
- Important difference: Fieldwork performs an earlier repository-wide evidence check without checking out every target source.

### Expired exact-head signoff

- Source: PR #249 predecessor review at `62e35d52cc64757951e4f99e57f086b46d0899d2`.
- Principle supported: acceptance belongs to one immutable head.
- Important difference: later counterexamples expired that signoff and every later review-ready claim on the defective generation.

## Approaches considered

### Retained: explicit marker and block state

Track whether a Git binary marker appeared, whether a payload header began, and whether the current block received encoded data. Validate each obligation at the next header or section boundary. This gives local diagnostics and preserves Fieldwork's bounded parser.

### Declined: infer completeness from any valid section form

A mode change, text hunk, binary summary, or metadata record says nothing about whether an adjacent Git binary marker is complete.

### Complementary: native Git parse-only validation

PR #262 adds Git's parser as another bounded layer. It catches malformed base85 and compressed payload details that the custom parser does not model. That stack complements marker completeness; it does not remove the need for clear custom diagnostics or target-source applicability checks.

## Edge cases covered or prepared

| Edge case | Current result |
| --- | --- |
| Complete first block, truncated second block | Rejected by parent repair and native Git. |
| One or two complete binary blocks | Accepted by positive controls. |
| Payload header without encoded data | Rejected. |
| Bare marker as sole section content | Rejected. |
| Bare marker plus complete mode change | New PR #281 negative control. |
| Bare marker plus complete text hunk | New PR #281 negative control. |
| Bare marker plus binary summary | New PR #281 negative control. |
| Empty-file SHA-1/SHA-256 forms | Existing positive controls retained. |
| Full-similarity rename/copy and mode-only metadata | Existing positive controls retained when no incomplete marker is present. |
| Malformed, truncated, or overlong text hunks | Existing matrix rejects them. |

## Deferred boundaries

| Boundary | Next owner |
| --- | --- |
| Exact parity with future Git patch extensions | Reopen when valid Git output is rejected or invalid output passes. |
| Base85/compression payload validity | Native parse stack PR #262 and future integrated review. |
| Applicability to pinned target source | Target-native `git apply --check`. |
| Semantic correctness of represented source change | Target finding and implementation review. |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| PR #249 `e093eb8a...` | original focused suite | 29 passed | `target-executed` |
| same | native malformed later-block control | rejected as corrupt | `target-executed` |
| same | Fieldwork integrity `30579669056` | success | `full-gate` for the parent generation |
| PR #281 `8b78f881...` | original suite + three mixed-form controls + tracked-patch validation | queued in run `30587468319` | `target-test-prepared` |

## Complete-diff and compatibility review

- Parent file fence: integrity workflow, parser source, and original focused tests.
- Repair stack file fence: parser source, `scripts/test_validate_patch_syntax_binary_marker.py`, and integrity workflow.
- Parent branch remains the canonical implementation surface; PR #281 is the bounded repair stack.
- PR #262 is a separate complementary native-parse stack and should be reconciled deliberately after marker repair execution.
- Known defect: marker completeness at the reviewed parent head.
- Fresh independent review must examine the integrated complete diff, exact head, current base relation, and both custom/native evidence boundaries.

## Current disposition and routing

- Finding state: `research-active`
- Review disposition: `REPAIR / EXECUTE`
- Review Queue entry: repair-active notice only; no R1/R2/R3 promotion marker
- Delivery lane: none
- Exact next transition: complete run `30587468319`, integrate or restack PR #281, update the canonical head, and obtain independent complete-diff review
- Clearing condition: original and mixed-form controls plus tracked-patch validation succeed at one exact integrated head
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-30 | predecessor `62e35d5...` | Earlier locked state accepted a narrower parser. |
| 2026-07-30 | parent `e093eb8...` | Added per-block validation and malformed second-block control. |
| 2026-07-31 | review `4823746557` | Found bare-marker masking behind other complete section forms; parent demoted to REPAIR. |
| 2026-07-31 | PR #281 `8b78f881...` | Prepared marker-completeness repair and three mixed-form controls. |

## References

- issue #245
- parent PR #249
- repair PR #281
- native parse stack PR #262
- review `4823746557`
- Fieldwork integrity `30579669056`
- queued repair run `30587468319`
- `.github/workflows/fieldwork-integrity.yml`
- `scripts/validate_patch_syntax.py`
- `scripts/test_validate_patch_syntax.py`
- `scripts/test_validate_patch_syntax_binary_marker.py`
