# Canonical Findings

## In simple words

An issue tells people **where work is happening**. A canonical finding file tells them **what we currently know and what decision remains**.

Issue comments should become short pointers and receipts. The evolving explanation, evidence, alternatives, precedent, edge cases, and decision framing belong in one tracked finding directory. Git history and pull-request review then show exactly how the conclusion changed.

## Why this exists

Long issue threads make three failures easy:

1. the newest comment silently contradicts an older one;
2. a human cannot tell whether “complete” means ready to review, ready to decide, ready to land, or simply closed;
3. parallel workers add separate narratives without reconciling them into one current answer.

A canonical finding gives each investigation one durable answer surface. Multiple workers may propose updates through separate pull requests. Merge conflicts become an explicit reconciliation step instead of hidden disagreement across comments.

## Canonical layout

Use one directory for each investigation that has a retained conclusion, decision request, implementation candidate, or review state:

```text
findings/F<fieldwork-issue>-<slug>/
├── finding.md                    # canonical current answer
├── evidence/                     # parallel-safe supporting notes
│   ├── YYYYMMDD-<worker>-<slug>.md
│   └── ...
├── artifacts/                    # retained logs, fixtures, tables, or small outputs
└── reviews/                      # optional durable exact-head review receipts
    └── YYYYMMDD-<reviewer>.md
```

Use the owning Fieldwork issue number in the identifier whenever one exists. A campaign may instead use its stable campaign identifier when several issues share one parent finding.

The canonical `finding.md` owns the current interpretation. Supporting notes retain evidence and discarded reasoning without forcing the reader to reconstruct the conclusion from every artifact.

## Parallel work and merge conflicts

Parallel work is allowed under one investigation.

- Each worker owns a unique file under `evidence/`, `artifacts/`, or `reviews/`.
- A worker may also propose an edit to `finding.md` in the same pull request.
- Several pull requests may propose competing edits to `finding.md`.
- Only one canonical edit merges at a time.
- Later pull requests must rebase and reconcile the current `finding.md`; conflict resolution must preserve supported evidence and explicitly record rejected conclusions.
- Never resolve a finding conflict by deleting another worker's evidence without explanation.

This is the deliberate exception to the normal one-worker-per-output-path rule: workers still own unique evidence paths, while the canonical finding is a reviewed integration surface.

## Required finding content

Every canonical finding must answer these questions in plain language:

1. **Explain it like I am five.** What is the system and what happened?
2. **Why do we care?** Name the concrete correctness, reliability, security, compatibility, performance, or operator consequence.
3. **What happens if we leave it alone?** Describe the observed or bounded failure mode and avoid invented frequency or impact.
4. **What exactly did we establish?** Separate source-read, executed, inferred, and unknown claims.
5. **What historical precedent exists?** Cite the most relevant prior fix, issue, design, standard, or documented contract and explain both the similarity and the difference.
6. **Which approaches did we consider and decline?** State why each was rejected, deferred, or left for a different investigation.
7. **Which edge cases did we cover?** Name the controls and execution boundaries.
8. **Which edge cases remain outside this finding?** Preserve them as explicit deferred questions.
9. **What is the exact decision or next transition?** Name the implementation, head, evidence, clearing condition, and responsible desk.

Use `templates/finding.md`.

## State and desk routing

Never use `complete`, `ready`, or `done` alone. Use one of these explicit states:

| Finding state | Meaning | Human action | Live index |
| --- | --- | --- | --- |
| `research-active` | Evidence or implementation work remains. | None unless a blocker is named. | Owning issue or campaign |
| `review-ready` | The canonical finding, complete diff, exact-head evidence, limits, and proposed disposition are ready for examination. | Review and choose `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT`. | Review Queue #213 |
| `design-decision-ready` | Evidence is sufficient and one unresolved design or policy choice blocks continuation. | Choose among the named options and consequences. | Review Queue #213 and Delivery Desk #160 lane D3 |
| `delivery-gate-ready` | One canonical implementation exists and only bounded execution, cleanup, restacking, or final review remains. | Clear the named gate. | Delivery Desk #160 lane D1 or D2 |
| `land-ready` | The exact current head has eligible acceptance, the named full gate, a clean direct diff, and a current base relationship. | Merge or explicitly hold. | Delivery Desk #160 lane D0 |
| `stopped` | The investigation ended with a retained negative result, overlap, disproved premise, or explicit scope stop. | None unless reopened by new evidence. | Owning issue and durable ledger |
| `closed` | The accepted result has been merged, archived, or otherwise completed with no active transition. | None. | Durable ledger or closeout |

### What “review-ready” means for the user

`review-ready` means the user can open one finding file and its linked implementation or evidence PR and examine the current case without reading the full issue history.

### What “design-decision-ready” means for the user

`design-decision-ready` means research should pause. The finding must present a small number of explicit options, the likely consequence of each option, and the recommendation. The user supplies judgment instead of asking workers to keep exploring indefinitely.

### What the Delivery Desk means

The Delivery Desk tracks movement toward landing. It does not replace the canonical finding. A desk entry links to the finding, exact implementation head, accepted review receipt, and one clearing condition.

## Issue comment rule

For investigations with a canonical finding, issue comments should contain only material routing information:

```text
State: <explicit finding state>
Canonical finding: <path and Fieldwork PR>
Canonical implementation: <repository PR or none>
Exact head: <sha or none>
New evidence: <receipt, workflow, or note>
Decision or blocker: <one sentence>
Upstream contact authorized: no | exact authority
```

Put the full reasoning in the finding PR. Post another issue comment only when the state, head, evidence class, decision request, blocker, or canonical path changes.

When repository writes are unavailable, an issue-only handoff remains allowed and must carry `needs:materialization`. The next coordinator should create the canonical finding before further synthesis.

## Evidence and citation rule

The finding must cite every consequence-bearing claim to one of:

- exact source paths and revisions;
- retained workflow runs and job IDs;
- durable Fieldwork evidence files;
- primary specifications, documentation, issues, pull requests, or commits;
- explicit inference from named evidence.

Historical precedent must include:

- title or concise description;
- stable URL;
- revision, version, or date when available;
- the principle it supports;
- the important way the current finding differs.

A missing precedent search should say what was searched and that no close match was found.

## Canonicality and synchronization

The following surfaces have distinct jobs:

- `finding.md` — canonical current explanation, evidence boundary, alternatives, edge cases, and transition;
- owning issue — live state, assignment, authority, and short routing comments;
- implementation PR — exact source diff, checks, and candidate front page;
- Review Queue #213 — items awaiting judgment;
- Delivery Desk #160 — accepted or selected work awaiting a landing transition;
- evidence notes and artifacts — supporting material;
- closeout or ledger — completed normalized outcome.

When any conclusion changes, update the finding first or in the same pull request as the evidence. Then synchronize the issue, implementation PR, and applicable desk entry with links to the canonical finding.

## Adoption for autonomous initiatives

For high-volume initiatives such as #254:

- the initiative issue remains the dispatch and global status surface;
- each retained investigation gets one canonical finding directory;
- material progress comments link to the relevant finding PR and summarize only the state change;
- a workstream final handoff links its touched findings and classifies each as review-ready, design-decision-ready, delivery-gate-ready, stopped, or closed;
- the initiative issue should never become the sole repository of investigation reasoning.
