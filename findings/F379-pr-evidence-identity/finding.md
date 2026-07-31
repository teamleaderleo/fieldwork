# F379 — Pull-request checkout evidence identity

Issue: #379  
State: `review-ready`  
Work class: evidence reliability / repository gate  
Current main at claim: `c247681f80d3504045e5b34dd99aeda4907a2829`  
Upstream contact authorized: `no`

## In simple words

A pull-request check can test the proposed commit itself, or GitHub can make a temporary merge with the current base and test that combined commit. Both tests are useful. They answer different questions and expire for different reasons.

Fieldwork's main integrity workflow used the default pull-request checkout while many coordination records called its result an exact-head gate. A live checkout log proved that the workflow tested GitHub's generated merge commit instead.

The selected repair keeps both gates and labels them honestly.

## Why we care

A merge-ref success can depend on base-side files, workflow code, helpers, or dependencies that are not present on the proposed head. It also expires when the base snapshot moves even if the proposed head stays unchanged.

A literal-head success proves that the proposed generation itself executes. It does not prove integration with a newer base.

Collapsing both receipts into “exact-head” can:

- attribute a merge-ref result to an unexecuted source head;
- miss a branch-head failure masked by a base-side helper or workflow change;
- retain an integration receipt after its base moved;
- make later review-currentness automation reproduce the wrong object.

## Confirmed predecessor defect

Current main workflow `.github/workflows/fieldwork-integrity.yml` used default `actions/checkout` on `pull_request`.

For Fieldwork PR #378:

| Identity | SHA |
| --- | --- |
| declared pull-request head | `c642af5e7b934055e8ba6389acddbc8f73be1c58` |
| declared base snapshot | `c247681f80d3504045e5b34dd99aeda4907a2829` |
| generated merge checkout | `63eed97c9fd3d350502b50e4ecd6ba91614287c5` |

Integrity run `30635730689`, job `91172725027`, succeeded after fetching `63eed97...` into `refs/remotes/pull/378/merge` and checking out:

```text
HEAD is now at 63eed97 Merge c642af5... into c247681...
```

That is `target-executed` merge-ref integration evidence. It is not literal-head execution.

## Historical precedent

Linux Fieldwork issue 342 and merged PR 344 established the reused contract:

- literal proposed head → `exact-head`;
- generated pull-request merge with ordered parents `[base, head]` → `synthetic-merge-ref`;
- every other internally valid identity → `other-checkout`.

Reusing that contract avoids a competing vocabulary.

## Selected contract

### Head gate

A **head gate** checks out and executes `github.event.pull_request.head.sha`.

It proves the named proposed generation ran. Its receipt stays tied to that source head and makes no integration claim about a later base.

### Merge-ref gate

A **merge-ref gate** checks out GitHub's pull-request event SHA and proves the checkout is a two-parent generated merge with ordered parents `[declared base, declared head]`.

It proves integration with that exact base snapshot and expires when either parent moves.

### Push gate

A push gate checks out and executes the pushed event SHA. It is classified separately from pull-request merge construction.

## Required receipt fields

Each receipt records:

- tested checkout SHA;
- declared pull-request head SHA;
- declared base SHA;
- event SHA;
- ordered local parent SHAs;
- event name and ref;
- head and base branch refs where applicable;
- run ID and attempt;
- classification.

Malformed, contradictory, or unexpectedly classified inputs fail closed.

## Implementation

PR #380 changes five files:

- `scripts/audit_pr_evidence_identity.py` — exact-type and Git-identity classifier;
- `scripts/test_pr_evidence_identity.py` — literal head, synthetic merge, unrelated merge, malformed identity, contradiction, push, and optimizer-parity controls;
- `.github/workflows/fieldwork-integrity.yml` — separate merge-ref, literal-head, and push jobs with durable JSON receipts;
- `REVIEWING.md` — explicit head-gate and merge-ref-gate review language;
- this finding.

The existing interaction-reference and Fieldwork-integrity commands run in both pull-request jobs. The repair does not weaken the integration check.

## Executed mechanism result

PR #380 predecessor head `dbfda40c072ab49621d20bce0f2313ce1ab56881` executed workflow `30636532630` successfully.

### Literal-head job

- job `91175428782`: success;
- checkout and declared head: `dbfda40c072ab49621d20bce0f2313ce1ab56881`;
- classification: `exact-head`;
- artifact `8795551528`;
- digest `sha256:3a2d3ed24cacd391e6566ccf52a5e6bff30bd3174204f6a60b8d1a709ba97c32`.

### Merge-ref job

- job `91175428722`: success;
- checkout: `a98113611e0368351158c21045b2a7b880ad55c6`;
- ordered parents: `[c247681f80d3504045e5b34dd99aeda4907a2829, dbfda40c072ab49621d20bce0f2313ce1ab56881]`;
- classification: `synthetic-merge-ref`;
- artifact `8795552208`;
- digest `sha256:7159346c50f3afeac07a968c3314b190da83a4dc69408854c69185554b1a4f22`.

Both jobs ran the interaction-reference scanner, Fieldwork integrity, and eight classifier controls. The push job was correctly skipped on the pull-request event.

The pull-request front page and issue #379 carry the external dual-checkout receipt for the current exact head. Review must verify those live receipts because embedding a current-head workflow run inside the commit would move the head recursively.

## Alternatives considered

### Keep only the default merge-ref gate

Declined. It preserves integration evidence but leaves the literal source generation unexecuted.

### Replace the default gate with a head-only checkout

Declined. It proves the proposed head but loses useful integration evidence against the exact base snapshot.

### Infer checkout mode from the workflow name

Declined. Names are editable claims. Classification derives from actual SHA, event identity, and Git parents.

### Call both results exact-head

Rejected. The generated merge is an exact commit, but it is not the pull-request head.

### Require both gates for every target repository

Deferred. This finding repairs Fieldwork's own integrity gate. Other repositories may choose different gate combinations, but their receipts still need honest checkout identity.

## Covered edge cases

- lower-case SHA and exact JSON type validation;
- duplicate and self-parent rejection;
- generated merge parent order;
- reversed or unrelated merges remain `other-checkout`;
- expected-classification mismatch fails closed;
- ordinary and optimized Python parity;
- pull-request branch-ref requirements;
- non-PR push event with empty head/base refs;
- artifact upload for each executed gate.

## Deferred edge cases

- fork pull requests with different checkout permissions;
- merge queues and `merge_group` events;
- reusable workflows whose workflow code and tested source use different generations;
- branch protection policy deciding mandatory gate combinations;
- action and dependency provenance beyond checkout identity;
- base-side generated files or caches that create semantic identity beyond Git parents.

## Uncertainty and expiration

External current-head receipts can expire after head movement. Merge-ref evidence also expires after base movement. Review must compare the live PR head, declared base, run, artifacts, and classifications rather than relying on this file's historical example alone.

## Current transition

Obtain one eligible complete-diff review of PR #380's five-file fence after verifying both live current-head receipts. Merge authority remains separate.

No merge, release, deployment, credential, spending, private-data, writer-transfer, or public-upstream authority follows from this finding.
