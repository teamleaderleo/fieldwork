# Delivery Desk

Fieldwork issue [#160](https://github.com/teamleaderleo/fieldwork/issues/160) is the canonical live finish-line index for work that has moved beyond broad research.

## In simple words

The review queue answers **what needs judgment**. The Delivery Desk answers **what can move toward landing now, what exact gate remains, and where the canonical implementation lives**.

Do not put every finding in the Delivery Desk. Enter it only when one of these is true:

- a selected implementation is waiting on its final exact-head gate;
- an executed candidate needs a clean restack, direct source application, or bounded polish;
- one human decision is the only thing blocking implementation or landing;
- a completed result needs receipt transfer, merge, closeout, or archival.

The live issue is a routing surface. The canonical Fieldwork issue, owned-repository PR, exact workflow receipt, review disposition, and durable report remain the sources of truth.

## Delivery lanes

### D0 — Land now

Use only when the exact current head has:

- an accepted eligible independent review;
- the named full repository gate;
- a clean intentionally scoped direct source diff;
- a current base relationship with the intended target branch;
- current issue, label, description, and receipt state;
- no unresolved execution carrier or superseded branch.

Green CI alone does not establish D0.

### D1 — Final gate now

Use when one canonical implementation exists and the remaining work is bounded:

- exact-head execution;
- complete-diff review;
- final cross-platform or compatibility gate;
- removal of temporary validation machinery;
- transfer of retained receipts to the canonical source PR.

### D2 — Polish or clean application

Use when the evidence and direction are strong but the implementation surface still needs a reviewable landing candidate. Common causes include:

- patch-file transport instead of a direct source diff;
- research files or temporary workflows mixed into the implementation branch;
- a prototype that still needs a stable result contract;
- several competing implementations without one selected canonical branch;
- a stale base or changed head that invalidates the current disposition.

### D3 — Human decision unlocks implementation

Use when broad exploration should stop and one explicit decision is the useful next move, such as:

- accepting or revising an invariant;
- choosing an internal representation;
- selecting one repair direction;
- deciding whether target-native execution is required;
- authorizing or withholding one exact upstream interaction.

## Required delivery record

Every Delivery Desk entry must identify:

```text
Delivery lane: D0 | D1 | D2 | D3
Canonical Fieldwork issue: #<number>
Canonical implementation: <owned repository PR or none>
Exact head: <sha or pending>
Base relationship: <base branch and revision, current | stale | pending>
Movement claim: <the exact claim supporting this lane>
Movement evidence class: source-read | model-executed | target-test-prepared | target-executed | integration-executed | full-gate
Claim and receipt references: <exact records>
Accepted disposition: ACCEPT | REPAIR | HOLD | EXECUTE | none
Disposition receipt: <review URL or durable record>
Reviewed head: <sha or none>
Reviewed input generation: <body digest, explicit revision, metadata generation, or none>
Clearing condition: <one named finish-line condition>
Required subgates: <explicit list or none>
Current owner: <identity or unclaimed>
Execution carrier: <PR or none>
Upstream contact authorized: no | yes with exact authority
```

`Movement evidence class` is the minimum evidence class supporting the exact lane movement. It never upgrades every claim in the item. Link claim-scoped evidence and receipts when the underlying work contains mixed evidence classes. A `full-gate` record must name the gate and its material exclusions.

One clearing condition may contain several inseparable subgates, such as cross-platform execution, receipt transfer, carrier closure, and exact-head review. Name the condition once and keep every required subgate visible.

Do not use “done,” “polished,” “ready,” or “green” without the exact head, reviewed inputs, evidence for the movement claim, and remaining gate.

## Movement rules

- D3 moves to D2 only after the implementation contract is selected.
- D2 moves to D1 only when one canonical clean candidate exists.
- D1 moves to D0 only after exact-head acceptance, the named full gate, a direct source diff, and a current base relationship.
- D0 exits immediately after merge, closeout, an explicit hold, or authorized submission.
- Changed inputs, a changed head, failed required checks, contradictory evidence, a stale base, or a stale receipt move an item backward.
- Execution carriers never become D0. Transfer their results to the canonical source PR and close them.
- Patch-only transport remains D2 or D1 until the canonical direct source diff is independently reviewable.
- Do not create a duplicate entry when a canonical candidate already exists.

## Submission-commit boundary

The final contribution commit is a human-attributed release artifact, not a repeatable CI output.

- Research and execution branches may be mutable and noisy.
- Create the upstream-intended submission commit deliberately **once** after the candidate is accepted.
- After that point, CI validates the exact submission SHA; CI must not recreate equivalent signed-off commits on every research update.
- Never infer the contributor name or email from a base commit, upstream author, repository owner, nearby commit, or stale workflow configuration.
- Before an upstream compare link or PR is handed to the submitter, verify the exact source diff, GitHub-resolved author and committer, `Signed-off-by:` trailer when required, and any assistance/coauthor trailers.
- Disposable or internal commits should not carry canonical `Fixes`/`Closes` metadata that would create external issue events.
- Temporary write-capable materializers, force-push workflows, and execution carriers must be disabled or removed when the durable submission branch exists.

See `research/postmortems/2026-08-07-cloud-hypervisor-submission-materializer.md` for the incident that established this rule.

## Worker handoff

Workers update the canonical Fieldwork issue and implementation PR first. Add or update a Delivery Desk entry only when the next useful human action changes.

A completion handoff for work near the finish line should include:

```text
Delivery lane: D0 | D1 | D2 | D3 | not-entered
Canonical implementation: <owned repository PR or none>
Exact reviewed or tested head: <sha or none>
Reviewed input generation: <digest, revision, metadata generation, or none>
Remaining delivery gate: <one clearing condition or none>
Required subgates: <list or none>
Execution carrier cleanup: complete | required | none
```

The coordinator owns lane movement and removes items that have crossed the finish line.

## Relationship to other surfaces

- GitHub issues remain the canonical live workboard.
- `REVIEWING.md` defines evidence classes, exact-head dispositions, reviewed-input expiry, and canonical-branch rules.
- A review queue or review hub prioritizes independent review and decisions.
- The Delivery Desk prioritizes landing, final execution, and cleanup.
- Synthesis records combine evidence; they do not automatically make an implementation landing-ready.
- Ledgers retain normalized outcomes after completion; they are not active queues.
- Issue #138 should eventually derive review and delivery projections from exact live records.

## Current live desk

Use [Fieldwork issue #160](https://github.com/teamleaderleo/fieldwork/issues/160). Keep the issue short enough to scan and link outward to canonical records instead of copying their evidence.