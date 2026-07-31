# F379 — Pull-request checkout evidence identity

Issue: #379  
State: `research-active`  
Work class: evidence reliability / repository gate  
Current main at claim: `c247681f80d3504045e5b34dd99aeda4907a2829`  
Upstream contact authorized: `no`

## In simple words

A pull-request check can test the proposed commit itself, or GitHub can make a temporary merge with the current base and test that combined commit. Both tests are useful. They answer different questions and expire for different reasons.

Fieldwork's main integrity workflow used the default pull-request checkout while many coordination records called its result an exact-head gate. The live checkout log proves that the workflow tested GitHub's generated merge commit instead.

The selected repair keeps both gates and labels them honestly.

## Why we care

A merge-ref success can depend on base-side files, workflow code, helpers, or dependencies that are not present on the proposed head. It also expires when the base snapshot moves even if the proposed head stays unchanged.

A literal-head success proves that the proposed generation itself executes. It does not prove integration with a newer base.

Collapsing both receipts into “exact-head” hides which object ran and can carry a review or promotion claim farther than its evidence.

## Consequence if unchanged

Fieldwork can continue to:

- attribute a merge-ref result to an unexecuted source head;
- miss a branch-head failure masked by a base-side helper or workflow change;
- treat an integration receipt as current after its base moved;
- describe two different execution identities with one ambiguous phrase;
- make later review-currentness automation reproduce the wrong object.

## Confirmed current behavior

Current main workflow `.github/workflows/fieldwork-integrity.yml` used:

```yaml
on:
  pull_request:

steps:
  - uses: actions/checkout@v4
```

For Fieldwork PR #378:

| Identity | SHA |
| --- | --- |
| declared pull-request head | `c642af5e7b934055e8ba6389acddbc8f73be1c58` |
| declared base snapshot | `c247681f80d3504045e5b34dd99aeda4907a2829` |
| generated merge checkout | `63eed97c9fd3d350502b50e4ecd6ba91614287c5` |

Integrity run `30635730689`, job `91172725027`, succeeded. Its checkout log fetched `63eed97...` into `refs/remotes/pull/378/merge`, checked out that ref, and reported:

```text
HEAD is now at 63eed97 Merge c642af5... into c247681...
```

Evidence class: `target-executed` for the workflow checkout identity and integrity commands at that generated merge. It is not literal-head execution.

## Historical precedent

Linux Fieldwork issue 342 and merged PR 344 established the same distinction with a dual live checkout and typed receipts:

- literal proposed head → `exact-head`;
- generated pull-request merge with ordered parents `[base, head]` → `synthetic-merge-ref`;
- every other internally valid identity → `other-checkout`.

That precedent is reused here to avoid a second vocabulary.

## Selected contract

### Head gate

A **head gate** checks out and executes `github.event.pull_request.head.sha`.

It proves the named proposed generation ran. Its receipt is tied to that source head. It says nothing about integration with a later base unless a separate merge-ref gate exists.

### Merge-ref gate

A **merge-ref gate** checks out GitHub's pull-request event SHA and proves the checkout is a two-parent generated merge with ordered parents `[declared base, declared head]`.

It proves integration with that exact base snapshot. It expires when either parent changes.

### Push gate

A push gate checks out and executes the pushed event SHA. It is classified separately from pull-request merge construction.

## Required receipt fields

Each checkout receipt records:

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

The candidate branch adds:

- `scripts/audit_pr_evidence_identity.py` — exact-type and Git-identity classifier;
- `scripts/test_pr_evidence_identity.py` — literal head, synthetic merge, unrelated merge, malformed identity, contradiction, push, and optimizer-parity controls;
- `.github/workflows/fieldwork-integrity.yml` — separate merge-ref, literal-head, and push jobs with durable JSON receipts;
- `REVIEWING.md` — explicit head-gate and merge-ref-gate review language;
- this finding.

The existing interaction-reference and Fieldwork-integrity commands run in both pull-request jobs. The repair does not weaken the current integration check.

## Alternatives considered

### Keep only the default merge-ref gate

Declined. It preserves integration evidence but leaves the literal source generation unexecuted while records continue to reason about exact heads.

### Replace the default gate with a head-only checkout

Declined. It proves the proposed head but loses useful integration evidence against the exact base snapshot.

### Infer checkout mode from the workflow name

Declined. Names are editable claims. The receipt must derive classification from the actual checkout SHA, event identity, and Git parents.

### Call both results exact-head

Rejected. The generated merge commit is an exact commit, but it is not the pull-request head. The phrase obscures the identity needed for review and expiration.

### Require both gates for every target repository

Deferred. This finding repairs Fieldwork's own integrity gate and terminology. Target repositories may have different trusted gate contracts, fork restrictions, or workflow provenance. Their receipts still need honest identity.

## Covered edge cases

- exact lower-case SHA and exact JSON type validation;
- duplicate and self-parent rejection;
- generated merge parent order;
- reversed or unrelated two-parent commits classified as `other-checkout`;
- expected-classification mismatch fails the job;
- ordinary and optimized Python parity;
- pull-request branch-ref requirements;
- non-PR push event with empty head/base refs;
- artifact upload on each gate.

## Deferred edge cases

- fork pull requests whose head SHA may need different checkout permission handling;
- merge queues and `merge_group` events;
- reusable workflows whose workflow code and tested source come from different generations;
- branch protection policy deciding which combination of gates is mandatory;
- workflow dependency or action provenance beyond checkout identity;
- base-side generated files or caches that create semantic identity beyond Git parents.

## Uncertainty

The first Fieldwork dual-checkout workflow must still execute. A green static review cannot prove that both live GitHub checkouts expose the expected parent topology or that artifact upload succeeds.

## Current transition

`EXECUTE` the candidate pull request. Inspect both JSON artifacts and raw `rev-list` lines. If both classifications are internally consistent, update this finding and issue #379 to `review-ready`, then obtain one eligible complete-diff review.

No merge, release, deployment, credential, spending, private-data, writer-transfer, or public-upstream authority follows from this finding.
