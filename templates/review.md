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

- Prior reviewed generation: exact head plus every governing input generation named by the prior receipt
- Current generation: exact head plus every current governing input generation
- Disposition-relevant reviewed paths:
- Old/new blob identity for every reviewed path:
- Governing input generations unchanged: yes | no
- Changed reviewed paths: none | exact paths
- Material configuration, generated input, indirect dependency, policy, or mergeability change: none | exact change
- Carry-forward without fresh review allowed: yes | no
- Fresh review receipt required: yes | no
- Exact reason:

A prior disposition may carry forward without fresh review only when every disposition-relevant reviewed path is byte-identical across the named generations and every governing-input generation named by the prior receipt is unchanged. Record `changed reviewed paths: none`; file-disjoint base movement alone is not sufficient.

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

This review applies only to the exact head and reviewed input generations named above. Any head movement, issue-body generation change, issue-state label change, finding-state change, dependency change, policy change, material configuration or generated-input change, indirect dependency change, or contradictory evidence expires the disposition unless the Review-identity reconciliation section proves every disposition-relevant reviewed path byte-identical and every governing input generation unchanged. Any changed reviewed byte or governing input requires a fresh review receipt.
