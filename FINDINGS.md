# Canonical Findings

## In simple words

An issue tells people **where work is happening**. A canonical finding file tells them **what we currently know and what technical transition remains**.

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
- Later pull requests must reconcile against the exact current `finding.md`. Rebase or restack when current movement overlaps the proposed edit, changes governing protocol or mergeability, or a current-base promotion package is required. When movement is file-disjoint and the canonical bytes and reviewed claim fence are unchanged, record the newer exact generation and prove semantic identity within the reviewed fence instead of rebasing mechanically. An expired receipt remains expired until the affected review identity is renewed.
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

## Issue state and finding state are different

Do not overload one `State:` field with two vocabularies.

- **Issue state** is the live GitHub coordination state from `LABELS.md`, such as `state:claimed`, `state:investigating`, `state:blocked`, or `state:complete`. The issue-body `Issue state:` field must agree with the one live `state:*` label.
- **Finding state** is the technical transition state below, such as `comparative-evaluation-active`, `review-ready`, or `land-ready`. It lives in the canonical finding and is mirrored in the owning issue as `Finding state:` when a canonical finding exists.

There is deliberately no one-to-one mapping. An issue may be `state:claimed` while its finding is `comparative-evaluation-active`; an issue may remain `state:investigating` while its finding is `delivery-gate-ready`. Review receipts must version and validate the two inputs separately.

For issue-backed findings, use:

```text
Issue state: `state:<label>`
Finding state: `<finding transition state>`
```

Use `Finding state: not applicable` for work with no retained canonical finding.

## Finding states and desk routing

Never use `complete`, `ready`, or `done` alone for a canonical finding. Use one of these explicit states:

| Finding state | Meaning | Human action | Live index |
| --- | --- | --- | --- |
| `research-active` | Evidence or implementation work remains within one current direction. | None unless a blocker is named. | Owning issue or campaign |
| `comparative-evaluation-active` | Two or more technically plausible directions remain and autonomous prototypes, controls, or compatibility work can still distinguish them. | None; continue comparison until one direction wins, all stop, or a genuine human decision boundary appears. | Owning issue, campaign, or investigation workspace |
| `review-ready` | The canonical finding, complete diff, exact-head evidence, limits, and proposed disposition are ready for examination. | Review and choose `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT`. | Review Queue #213 |
| `design-decision-ready` | Evidence is sufficient and one unresolved authority, value, material cost, private-context, or irreversible-risk choice blocks continuation. | Choose among the named options and consequences. | Review Queue #213 and Delivery Desk #160 lane D3 |
| `delivery-gate-ready` | One canonical implementation exists and only bounded execution, cleanup, restacking, or final review remains. | Clear the named gate. | Delivery Desk #160 lane D1 or D2 |
| `land-ready` | The exact current head has eligible acceptance, the named full gate, a clean direct diff, and a current base relationship. | Merge or explicitly hold. | Delivery Desk #160 lane D0 |
| `stopped` | The investigation ended with a retained negative result, overlap, disproved premise, or explicit scope stop. | None unless reopened by new evidence. | Owning issue and durable ledger |
| `closed` | The accepted result has been merged, archived, or otherwise completed with no active transition. | None. | Durable ledger or closeout |

### `comparative-evaluation-active`

Workers should keep testing technically plausible alternatives. This state does not route to a decision desk merely because several options exist. Move to `design-decision-ready` only when additional autonomous technical work cannot resolve a genuine authority, value, private-context, material cost, or irreversible-risk choice.

### Review and delivery states

`review-ready` means the user can open one finding file and its linked implementation or evidence PR and examine the current case without reading the full issue history.

`design-decision-ready` means research should pause. The finding must present a small number of explicit options, the likely consequence of each option, and the recommendation. The user supplies judgment instead of asking workers to keep exploring indefinitely.

The Delivery Desk tracks movement toward landing. It does not replace the canonical finding. A desk entry links to the finding, exact implementation head, accepted review receipt, and one clearing condition.

## Issue comment rule

For investigations with a canonical finding, issue comments should contain only material routing information:

```text
Issue state: state:<label>
Finding state: <finding transition state>
Canonical finding: <path and Fieldwork PR>
Canonical implementation: <repository PR or none>
Exact head: <sha or none>
New evidence: <receipt, workflow, or note>
Decision or blocker: <one sentence>
Upstream contact authorized: no | yes with exact authority
```

Put the full reasoning in the finding PR. Post another issue comment only when the issue state, finding state, head, evidence class, decision request, blocker, authority, or canonical path changes.

When repository writes are unavailable, an issue-only handoff remains allowed and must carry `needs:materialization`. The next coordinator should create the canonical finding before further synthesis.

## Evidence and citation rule

The finding must cite every consequence-bearing claim to one of:

- exact source paths and revisions;
- retained workflow runs and job IDs;
- durable Fieldwork evidence files;
- primary specifications, documentation, issues, pull requests, or commits;
- explicit inference from named evidence.

Evidence is classified per claim. A finding may list `Evidence classes present`, but it must not assign one “strongest” class to the whole record or use a stronger claim row to upgrade weaker rows.

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
- owning issue — live coordination state, assignment, authority, and short routing comments;
- implementation PR — exact source diff, checks, and candidate front page;
- Review Queue #213 — items awaiting judgment;
- Delivery Desk #160 — accepted or selected work awaiting a landing transition;
- evidence notes and artifacts — supporting material;
- closeout or ledger — completed normalized outcome.

When any conclusion changes, update the finding first or in the same pull request as the evidence. Then synchronize the issue, implementation PR, and applicable desk entry with links to the canonical finding.

## Adoption for autonomous initiatives

For high-volume initiatives:

- the initiative issue remains the dispatch and global status surface;
- each retained investigation gets one canonical finding directory;
- material progress comments link to the relevant finding PR and summarize only the state change;
- a workstream final handoff links its touched findings and classifies each with one of the explicit finding states above;
- the initiative issue should never become the sole repository of investigation reasoning.
