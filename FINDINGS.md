# Canonical Findings

## In simple words

An issue tells people **where work is happening**. A canonical finding file tells them **what we currently know, which direction currently wins, and what transition remains**.

Issue comments should become short pointers and receipts. The evolving explanation, evidence, alternatives, precedent, edge cases, executed comparisons, and transition framing belong in one tracked finding directory. Git history and pull-request review then show exactly how the conclusion changed.

Read `DECISIONS.md` whenever more than one technical direction remains plausible.

## Why this exists

Long issue threads make three failures easy:

1. the newest comment silently contradicts an older one;
2. a human cannot tell whether “complete” means ready to review, ready to execute, ready to land, or simply closed;
3. parallel workers add separate narratives without reconciling them into one current answer.

A canonical finding gives each investigation one durable answer surface. Multiple workers may propose updates through separate pull requests. Merge conflicts become an explicit reconciliation step instead of hidden disagreement across comments.

## Canonical layout

Use one directory for each investigation that has a retained conclusion, decision comparison, implementation candidate, or review state:

```text
findings/F<fieldwork-issue>-<slug>/
├── finding.md                    # canonical current answer
├── evidence/                     # parallel-safe supporting notes
│   ├── YYYYMMDD-<worker>-<slug>.md
│   └── ...
├── alternatives/                 # optional competing implementations or comparisons
│   ├── A-<slug>.md
│   └── B-<slug>.md
├── artifacts/                    # retained logs, fixtures, tables, or small outputs
└── reviews/                      # optional durable exact-head review receipts
    └── YYYYMMDD-<reviewer>.md
```

Use the owning Fieldwork issue number in the identifier whenever one exists. A campaign may instead use its stable campaign identifier when several issues share one parent finding.

The canonical `finding.md` owns the current interpretation and selected direction. Supporting notes retain evidence, competing approaches, and discarded reasoning without forcing the reader to reconstruct the conclusion from every artifact.

## Parallel work and merge conflicts

Parallel work is allowed under one investigation.

- Each worker owns a unique file under `evidence/`, `alternatives/`, `artifacts/`, or `reviews/`.
- Each competing implementation uses a separate owned branch, commit series, experiment, or clearly named artifact.
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
5. **What historical precedent exists?** Cite the most relevant prior fix, design, standard, or documented contract and explain both the similarity and the difference.
6. **Which approaches did we instantiate or analyze?** Give each option the same decision criteria and record why it won, lost, or remains active.
7. **Which edge cases did we cover?** Name the controls and execution boundaries.
8. **Which edge cases remain outside this finding?** Preserve them as explicit deferred questions.
9. **What is the exact next transition?** Name the selected implementation, head, evidence, clearing condition, and responsible desk.
10. **Does any genuinely non-delegable human decision remain?** Apply `DECISIONS.md`; multiple technical options alone do not qualify.

Use `templates/finding.md`.

## Autonomous decision closure

Do not send a finding to a human merely because several technical approaches are plausible.

The default continuation is:

1. recover project goals, contracts, and invariants;
2. research current source, history, first-party analogues, specifications, and other primary precedent;
3. define decision criteria before selecting an implementation;
4. instantiate competing approaches when practical;
5. run tests, benchmarks, and negative controls that can make an option lose;
6. seek adversarial cross-review against concrete branches or artifacts;
7. select the best-supported direction and advance it to the next gate;
8. retain the losing alternatives and reopening triggers.

Escalate only when the remaining choice depends on authority, private context, material cost, product values absent from repository evidence, irreversible risk, or another boundary workers cannot discover or safely exercise. `DECISIONS.md` is canonical for this rule.

## State and desk routing

Never use `complete`, `ready`, or `done` alone. Use one of these explicit states:

| Finding state | Meaning | Next action | Live index |
| --- | --- | --- | --- |
| `research-active` | Routine source, evidence, or implementation work remains. | Continue autonomously. | Owning issue or campaign |
| `comparative-evaluation-active` | Several plausible approaches remain and research, prototypes, execution, or cross-review can still distinguish them. | Follow `DECISIONS.md`; do not wait for the user. | Owning issue and canonical finding PR |
| `review-ready` | One preferred direction or bounded conclusion, complete diff, exact-head evidence, limits, alternatives, and proposed disposition are ready for independent examination. | Review and choose `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT`. | Review Queue #213 |
| `design-decision-ready` | Comparative evaluation is complete and the remaining decision is genuinely non-delegable. | Ask the smallest exact authority, value, cost, or risk question. | Review Queue #213 and Delivery Desk #160 D3 |
| `delivery-gate-ready` | One canonical implementation exists and only bounded execution, cleanup, restacking, or final review remains. | Clear the named gate. | Delivery Desk #160 D1 or D2 |
| `land-ready` | The exact current head has eligible acceptance, the named full gate, a clean direct diff, and a current base relationship. | Merge or explicitly hold under human authority. | Delivery Desk #160 D0 |
| `stopped` | The investigation ended with a retained negative result, overlap, disproved premise, or explicit scope stop. | None unless reopened by new evidence. | Owning issue and durable ledger |
| `closed` | The accepted result has been merged, archived, or otherwise completed with no active transition. | None. | Durable ledger or closeout |

### What `review-ready` means

A reviewer can open one finding file and its linked implementation or evidence PR and examine the current case without reconstructing the full issue history. Review is technical criticism and exact-head disposition, not an automatic request for the user to choose the design.

### What `design-decision-ready` means

Use this state sparingly. The finding must explain why additional source research, prototypes, execution, or cross-review cannot settle the choice and why a person must supply authority, values, private context, acceptable risk, or material commitment. A recommendation remains required.

### What the Delivery Desk means

The Delivery Desk tracks movement toward landing. It does not replace the canonical finding. A desk entry links to the finding, exact implementation head, accepted review receipt, and one clearing condition.

## Issue comment rule

For investigations with a canonical finding, issue comments should contain only material routing information:

```text
State: <explicit finding state>
Canonical finding: <path and Fieldwork PR>
Canonical implementation or alternatives: <repository PRs or none>
Exact heads: <sha list or none>
New evidence: <receipt, workflow, comparison, or review>
Selected direction or blocker: <one sentence>
Non-delegable decision: <none or smallest exact question>
Upstream contact authorized: no | exact authority
```

Put the full reasoning in the finding PR. Post another issue comment only when the state, head, evidence class, selected direction, non-delegable question, blocker, or canonical path changes.

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

A design comparison must preserve the criteria, exact alternatives, discriminating controls, results, criticism, winner, losing reasons, and reopening trigger.

## Canonicality and synchronization

The following surfaces have distinct jobs:

- `finding.md` — canonical current explanation, evidence boundary, selected direction, alternatives, edge cases, and transition;
- owning issue — live state, assignment, authority, and short routing comments;
- implementation PRs — exact source diffs, checks, and candidate front pages;
- Review Queue #213 — items awaiting independent technical judgment or a genuine non-delegable decision;
- Delivery Desk #160 — selected work awaiting a landing transition;
- evidence notes and artifacts — supporting material;
- closeout or ledger — completed normalized outcome.

When any conclusion changes, update the finding first or in the same pull request as the evidence. Then synchronize the issue, implementation PRs, and applicable desk entry with links to the canonical finding.

## Adoption for autonomous initiatives

For high-volume initiatives such as #254:

- the initiative issue remains the dispatch and global status surface;
- each retained investigation gets one canonical finding directory;
- material progress comments link to the relevant finding PR and summarize only the state change;
- unresolved technical choices remain autonomous comparative work unless `DECISIONS.md` identifies a non-delegable boundary;
- a workstream final handoff links its touched findings and classifies each with an explicit state;
- the initiative issue should never become the sole repository of investigation reasoning.