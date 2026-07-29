# Exact-head review

## In simple words

State what is being reviewed, what transition is requested, the strongest supported result, and the main reason it should be accepted, repaired, held, executed, or rejected.

## Scope

- Repository:
- Pull request or issue:
- Reviewed issue or decision input generation: issue number plus `updated_at`, body digest, or explicit revision marker
- Work class: owned product delivery | upstream-fork research | execution carrier | evidence/documentation | blocked/security-sensitive
- Canonical branch:
- Exact head SHA:
- Base or current-main SHA:
- Changed-file fence:
- Author eligible to accept or merge: yes | no
- Upstream contact authorized: yes | no

## Evidence

- Evidence class: source-read | model-executed | target-test-prepared | target-executed | integration-executed | full-gate
- Commands or workflow runs:
- Platforms and runtimes:
- Focused tests:
- Named full repository gate or command set:
- Material paths not exercised by that gate:
- Checks skipped, not triggered, or still running:
- Retained artifacts or receipts:

## Complete-diff review

- Invariant or contract under review:
- Strongest positive evidence:
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
- Issue `State:` text agrees with labels: yes | no
- Pull-request description is current for this head: yes | no
- Current-main relation is known: yes | no

## Disposition

Disposition: ACCEPT | REPAIR | HOLD | EXECUTE | REJECT

Accepted transition or clearing condition:

## Uncertainty

State the remaining technical, operational, compatibility, impact, or policy uncertainty without upgrading it into a fact.

## Expiry

This review applies only to the exact head and reviewed input generations named above. Any head movement, issue or decision-input generation change, dependency change, policy change, or contradictory evidence expires the disposition unless semantic identity is proved within the reviewed fence.
