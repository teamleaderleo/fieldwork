# Investigation Workspaces

## In simple words

A large investigation can contain several real questions, several workers, competing explanations, current and historical source candidates, and several possible deliverables.

An investigation workspace gives that work one front door. Canonical findings still own the current technical answers. Evidence notes, alternatives, precedent, decisions, carriers, and presentation outputs remain separate so readers can see how the answer was reached and what still competes.

A reader should be able to open a workspace `README.md` and answer:

- What are we studying?
- Where does it sit in the larger system?
- Why could anyone care?
- Which canonical findings currently own the conclusions?
- Which alternatives still compete?
- Which outputs are canonical for a named audience?
- What exact execution, review, or decision happens next?

## Why this exists

Complex meta-issues can scatter orientation, source pins, alternatives, receipts, decisions, and conclusions across issue comments, pull requests, reports, and handoffs.

That scattering creates four recurring costs:

1. **Orientation cost** — a new reader reconstructs the history before understanding the current question.
2. **Parallel-edit cost** — workers compete for one shared report or avoid durable files.
3. **Premature-consensus cost** — an early summary hides a useful disagreement or negative result.
4. **Canonicalization cost** — the repository has strong notes without a declared current technical answer or audience-specific output.

A workspace lowers those costs by separating collection, technical synthesis, presentation, and decision.

## Position in Fieldwork

Programmes, target hubs, campaigns, lanes, batches, issues, pull requests, canonical findings, reviews, and delivery desks keep their existing authority.

A workspace is an orientation and synthesis layer. It does not replace:

- the owning issue for live assignment and authorization;
- `findings/F<issue>-<slug>/finding.md` for the current technical conclusion and transition state;
- an implementation PR for exact source diff and tests;
- Review Queue #213 for examination;
- Delivery Desk #160 for accepted work moving toward landing;
- evidence files for exact receipts;
- output status for audience-specific presentation artifacts.

Use a workspace when at least one condition applies:

- one issue has several independently answerable areas;
- several workers need separate owned output paths;
- competing technical explanations or designs deserve side-by-side treatment;
- the same evidence supports several canonical findings or presentation outputs;
- a meta-analysis spans campaigns, repositories, branches, or source candidates;
- a reader needs a stable orientation page before entering detailed records.

Small scouts, lanes, experiments, and findings can keep their existing single-finding layout.

## Location

For a cross-campaign, cross-lane, or meta-issue workspace, use:

```text
investigations/<issue-number>-<short-slug>/
```

For a workspace contained entirely inside one campaign, scout, batch, or lane, use the same internal layout beneath that unit's existing owned directory.

The parent issue and every canonical finding must link the workspace when it materially supplies their synthesis. The workspace front door links every authority-bearing issue, campaign, lane, finding, implementation, decision, source branch, and pull request.

## Recommended layout

```text
<workspace>/
├── README.md                 # coordinator-owned front door and current map
├── findings/                 # subordinate evidence notes and comparisons
├── evidence/                 # exact receipts, source maps, matrices, raw records
├── alternatives/             # candidate approaches and tradeoffs
├── precedent/                # prior art and earlier internal decisions
├── canonical/                # audience-specific presentation outputs
├── decisions/                # packaging, accept, hold, split, supersede, stop records
└── handoff.md                # exact current state, blockers, and continuation points
```

Create only the areas the investigation uses. A compact workspace may contain one front door, two evidence notes, one canonical output, and one handoff.

Canonical technical findings remain under repository-root `findings/`, not inside the workspace.

## Three different status systems

Do not collapse these concepts.

### Workspace phase

Workspace phase describes coordinator activity:

```text
orient → collect → compare → synthesize → decide → handoff
```

It carries no review or delivery authority.

### Canonical finding transition state

The canonical finding follows `FINDINGS.md`:

- `research-active` — one technical direction still has work;
- `comparative-evaluation-active` — several technically plausible directions remain and autonomous controls can still distinguish them;
- `review-ready` — one complete current case is ready for examination;
- `design-decision-ready` — evidence is sufficient and a genuine non-delegable human choice remains;
- `delivery-gate-ready` — one implementation exists and bounded landing gates remain;
- `land-ready` — exact-head acceptance and the named full gate are complete;
- `stopped` — retained negative, overlap, disproved premise, or explicit stop;
- `closed` — no active transition remains.

Several options do not automatically mean `design-decision-ready`. Use `comparative-evaluation-active` while executable technical work can still select or reject them.

### Canonical output status

Presentation artifacts use:

- `candidate`;
- `accepted`;
- `disputed`;
- `held`;
- `superseded`;
- `retired`.

An accepted orientation document can coexist with a research-active finding. Accepted output status grants no merge, delivery, or upstream authority.

## Front-door contract

`README.md` is the current orientation surface. Keep it concise enough that a reader understands the investigation before opening source-level detail.

It should contain:

1. `## In simple words`;
2. workspace phase and current canonical transition state;
3. parent issue, programme, target, and authority links;
4. exact current source or retrieval boundary;
5. canonical finding index;
6. the system map and bounded question;
7. why the answer matters;
8. investigation areas and owned files;
9. current established findings;
10. active disagreements and missing evidence;
11. canonical outputs and presentation status;
12. blockers, decisions, and exact next actions;
13. upstream-contact authorization.

The front door summarizes. Canonical findings carry current technical reasoning. Workspace notes carry evidence and comparisons.

## Canonical finding relationship

Every retained investigation has one canonical finding directory following `FINDINGS.md`.

Workspace files under `findings/` are subordinate notes. Each note states whether it:

- supplies evidence to one canonical finding;
- compares several canonical findings;
- records a bounded question that still needs materialization;
- preserves a superseded or negative result.

A workspace may coordinate several canonical findings. It may not silently combine them into one conclusion or change their states without updating the canonical files.

## Parallel ownership

- Workers own unique workspace evidence, alternative, precedent, artifact, or review paths.
- The workspace front door and handoff are coordinator-owned synthesis surfaces.
- Canonical findings remain shared reviewed integration surfaces under `FINDINGS.md`.
- Workers should avoid editing another worker's note merely to make prose agree.
- Conflicting conclusions remain explicit until evidence or a decision resolves them.

## Evidence area

Use `evidence/` for records whose main value is exactness or replayability:

- source and commit maps;
- changed-file inventories;
- workflow receipts and exact test-name/count records;
- compatibility or candidate matrices;
- raw traces, reduced logs, protocol transcripts;
- citation tables;
- branch and carrier retirement ledgers.

A canonical finding or evidence note interprets the record. Raw data never carries a stronger claim by itself.

## Alternatives and precedent

`alternatives/` records serious approaches, including attraction, failure mode, discriminating control, current disposition, and reopening trigger.

`precedent/` records relevant prior art:

- earlier Fieldwork findings and decisions;
- current and historical target implementations;
- specifications and official design documents;
- source history;
- relevant engineering patterns.

Precedent informs the decision. It does not replace current source and execution evidence.

## Canonical outputs

`canonical/README.md` indexes audience-specific outputs and gives each one an explicit presentation status.

Several accepted outputs are allowed when they serve distinct purposes, for example:

- a plain-language explainer;
- an implementation proposal;
- a separate issue for one independent invariant;
- an exact-head review packet;
- a negative-result closeout;
- a historical or operational analysis.

Every accepted output names:

- audience and purpose;
- exact findings and evidence inputs;
- claim scope;
- unresolved limits;
- decision owner and date;
- successor or follow-up issue when applicable.

Canonicalization links and interprets underlying findings. The underlying records remain available.

## Conflict protocol

When findings or notes disagree:

1. preserve both records;
2. state the exact proposition in dispute;
3. identify which source pin, assumption, evidence class, invariant, or decision value differs;
4. record the test or judgment that could resolve it;
5. assign one coordinator for synthesis;
6. carry unresolved disagreement into the canonical finding or output index;
7. use `comparative-evaluation-active` when further autonomous technical work remains;
8. use `design-decision-ready` only when the remaining choice cannot be settled technically.

## Lifecycle

```text
orient
→ collect independent evidence and findings
→ compare and challenge
→ update canonical findings
→ draft audience-specific outputs
→ review, decide, split, stop, or retain disagreement
→ deliver, publish internally, implement, open follow-ups, or close
```

Source drift can send an output or finding back to collection or comparison. Preserve the expired conclusion and name the new input that reopened it.

## Exact handoff

`handoff.md` records:

- workspace phase and canonical finding states;
- current source and owned heads;
- exact workflows and outcomes;
- active disagreements;
- blockers and next actions;
- expiry conditions;
- public interaction boundary.

Avoid self-referential exact-head claims in committed files. Put the live PR head in PR and issue metadata, or state the content input head before the handoff commit.

## Adoption

New complex investigations should begin with this layout. Existing work can adopt it incrementally:

1. materialize or identify canonical findings;
2. create a front-door `README.md`;
3. link existing reports and receipts before moving or rewriting them;
4. add separate files for missing alternatives, precedent, evidence, or conflict;
5. create `canonical/README.md` when an audience-specific output is ready for comparison;
6. record exact decisions, successors, and stop conditions;
7. update the parent issue with the workspace, canonical paths, state, and handoff.

Migration should preserve existing URLs and evidence owners whenever practical.

## Upstream boundary

Every workspace and template uses:

```text
Upstream contact authorized: no | yes with exact authority
```

Read-only public source review is allowed when the owning instructions permit it. Public issues, pull requests, comments, reactions, messages, or other contact require separate explicit authorization.
