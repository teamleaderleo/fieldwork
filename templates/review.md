# Exact-head review

## In simple words

State what is being reviewed, what transition is requested, the best-supported current conclusion, and the main reason it should be accepted, repaired, held, executed, or rejected.

## Scope

- Repository:
- Pull request or issue:
- Reviewed issue-body generation: issue number plus body digest, explicit body revision marker, or not applicable
- Legacy issue `State:` input present: yes | no | not applicable
- Reviewed live issue-state generation: exact `state:*` label plus accepted metadata snapshot marker, or not applicable
- Reviewed canonical finding generation: path, branch, and exact head, or not applicable
- Reviewed finding state: exact `FINDINGS.md` transition, absent because legacy issue is not migrated, or not applicable
- Reviewed other decision input generation: path, digest, revision marker, or not applicable
- Work class: owned product delivery | upstream-fork research | execution carrier | evidence/documentation | blocked/security-sensitive
- Canonical branch:
- Exact head SHA:
- Base or current-main SHA:
- Changed-file fence:
- Author eligible to accept or merge: yes | no | not applicable
- Upstream contact authorized: yes | no | not applicable

`updated_at` may be recorded as an explicitly accepted coarse snapshot marker. It is not a body-specific generation and can change after unrelated activity.

Issue state and finding state are independent review inputs. The issue-body `Issue state:` field must agree with the live `state:*` label. The issue-body `Finding state:` field must agree with the canonical finding when one exists.

A legacy issue-body `State:` value is issue coordination state only. It never supplies a finding state. A new review-ready, design-decision-ready, delivery-gate-ready, or land-ready transition requires migration to the two-field form before acceptance.

## Review-identity reconciliation

Complete this section whenever a prior disposition or execution receipt is proposed for carry-forward after any head, base, dependency, issue, finding, policy, generated input, or reviewed-input movement.

- Prior reviewed generation: exact head plus prior reviewed-input manifest identity
- Current generation: exact head plus current reviewed-input manifest identity
- Disposition-relevant reviewed paths:
- Old/new blob identity for every reviewed path:
- Prior governing-input manifest identity:
- Prior governing-input manifest complete for this disposition: `True | False | Unknown`
- Prior completeness evidence:
- Current governing-input manifest identity:
- Current governing-input manifest complete for this disposition: `True | False | Unknown`
- Current completeness evidence:
- Prior governing-input name set:
- Current governing-input name set:
- Governing-input names added:
- Governing-input names removed:
- Exact old/current generation for every input-name-set member:
- Unknown transitive or indirect dependency coverage: none | exact unknown coverage
- Changed reviewed paths: none | exact paths
- Material configuration, generated input, indirect dependency, policy, or mergeability change: none | exact change
- Carry-forward without fresh review allowed: yes | no
- Fresh review receipt required: yes | no
- Exact reason:

A prior disposition may carry forward without fresh review only when every disposition-relevant reviewed path is byte-identical, both the prior and current governing-input manifests are complete (`True`) for the disposition, the exact governing-input name sets are equal, and every member has the same exact generation. File-disjoint base movement and equality over only the previously named subset are insufficient.

`False` or `Unknown` completeness, any added or removed input name, a newly discovered previously unnamed disposition-relevant input, or inability to establish transitive or indirect dependency coverage requires fresh review. Never let an incomplete prior receipt define its own universe of governing inputs.

Reversing example: the prior receipt names source and governing protocol but silently omits generated configuration. The generated configuration moves while all named generations remain equal. Carry-forward is denied and fresh review is required.

Any changed reviewed byte or changed governing input is a new review input. A reviewer may conclude the new input is semantically equivalent, but that conclusion is a fresh review receipt. It does not retroactively make the prior disposition current.

## Claim-scoped evidence

Record one row for every claim that affects the disposition. Do not assign one strongest evidence class to the whole pull request or finding when different claims have different support.

| Claim or invariant | Evidence class | Exact receipt, source, or artifact | Coverage limits |
| --- | --- | --- | --- |
|  | source-read |  |  |

Allowed evidence classes: `source-read` | `model-executed` | `target-test-prepared` | `target-executed` | `integration-executed` | `full-gate`.

- Evidence classes present:
- Commands or workflow runs:
- Platforms and runtimes:
- Focused tests:
- Named full repository gate or command set: not applicable when no full-gate claim is made
- Material paths not exercised by that gate: not applicable when no full-gate claim is made
- Checks skipped, not triggered, or still running:
- Retained artifacts or receipts:

## Self-review before handoff

- Every disposition-relevant claim traced to exact support: yes | no
- Intended assertion actually ran: yes | no | not applicable
- Harness, setup, fixture, installation, and product failures separated: yes | no | not applicable
- Candidate or theory rewritten after contradictory execution: yes | no | not applicable
- Issue state, finding state, canonical finding, pull-request description, receipt, and queue or desk entry synchronized: yes | no | not applicable

## Complete-diff review

- Invariant or contract under review:
- Positive evidence:
- Negative controls:
- Compatibility controls:
- Error, cleanup, retry, authority, and recovery paths examined:
- Diff-quality concerns:
- Evidence or claims that remain unsupported:

## Coordination state

- Dependencies:
- Supersedes:
- Superseded by:
- Execution carriers to close:
- Legacy issue body migrated before requested promotion: yes | no | not applicable
- Issue `Issue state:` agrees with live label: yes | no | not applicable
- Issue `Finding state:` agrees with canonical finding: yes | no | not applicable
- Pull-request description is current for this head: yes | no | not applicable
- Current-main relation is known: yes | no | not applicable

## Disposition

Disposition: ACCEPT | REPAIR | HOLD | EXECUTE | REJECT

Accepted transition or clearing condition:

## Uncertainty

State the remaining technical, operational, compatibility, impact, or policy uncertainty without upgrading it into a fact.

## Expiry

This review applies only to the exact head and reviewed input generations named above. Any head movement, issue-body generation change, issue-state label change, finding-state change, dependency change, policy change, material configuration or generated-input change, indirect dependency change, contradictory evidence, governing-input name-set change, or governing-input manifest completeness that is `False` or `Unknown` expires the disposition.

Carry-forward without fresh review requires byte-identical disposition-relevant reviewed paths, prior and current governing-input manifest completeness `True`, equal exact governing-input name sets, and equal exact generations for every member. Any changed reviewed byte, changed governing input, newly discovered previously unnamed input, or unknown indirect coverage requires a fresh review receipt.
