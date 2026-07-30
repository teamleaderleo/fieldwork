# Investigation Workspaces

## In simple words

A large investigation can contain several real questions, several workers, several competing explanations, and several possible deliverables. An investigation workspace gives that work one front door while letting each finding live in its own file. Later, a coordinator can compare the findings, preserve disagreements, and declare one or more canonical outputs without erasing the research trail.

The reader should be able to open `README.md` and answer:

- What are we studying?
- Where does it sit in the larger system?
- Why could anyone care?
- What have we established?
- Which answers still compete?
- Which outputs are canonical today?
- What happens next?

## Why this exists

Fieldwork already separates campaign lanes from synthesis, batch results from synthesis, and execution carriers from canonical source branches. Complex meta-issues still scatter their orientation, source pins, alternatives, receipts, and final conclusions across issue comments, pull requests, lane reports, and chat handoffs.

That scattering creates four recurring costs:

1. **Orientation cost** — a new reader must reconstruct the entire history before understanding the current question.
2. **Parallel-edit cost** — several workers compete for one shared report or avoid durable files entirely.
3. **Premature-consensus cost** — one early summary can hide a useful disagreement or negative result.
4. **Canonicalization cost** — the repository may contain many strong notes without a declared answer suitable for review, publication, implementation, or a new issue.

A workspace lowers those costs by separating collection from synthesis and synthesis from decision.

## Position in Fieldwork

Programmes, target hubs, campaigns, lanes, batches, issues, and pull requests remain the authority and coordination units defined by the existing Fieldwork rules. A workspace organizes evidence that spans several owned areas or needs several independently authored files.

Use a workspace when at least one of these conditions applies:

- one issue has several independently answerable areas;
- several workers need separate owned output paths;
- competing explanations or designs deserve side-by-side treatment;
- the same evidence may support several final outputs;
- a meta-analysis spans several campaigns, branches, or source candidates;
- a reader needs a stable orientation page before entering detailed records.

Small scouts, lanes, experiments, and findings can keep their existing single-report layout.

## Location

For a cross-campaign, cross-lane, or meta-issue workspace, use:

```text
investigations/<issue-number>-<short-slug>/
```

For a workspace contained entirely inside one campaign, scout, batch, or lane, use the same internal layout beneath that unit's existing owned directory.

The parent issue or report must link the workspace. The workspace `README.md` must link the parent issue and every authority-bearing campaign, lane, decision, source branch, or pull request.

## Recommended layout

```text
<workspace>/
├── README.md                 # coordinator-owned front door and current map
├── findings/                 # independently owned observations and analyses
├── evidence/                 # exact receipts, source maps, matrices, and raw records
├── alternatives/             # candidate approaches and tradeoffs
├── precedent/                # prior art and earlier internal decisions
├── canonical/                # candidate or accepted outward-facing outputs
├── decisions/                # explicit accept, hold, split, supersede, or stop records
└── handoff.md                # exact current state, blockers, and continuation points
```

Create only the areas the investigation uses. A compact workspace may contain `README.md`, two finding files, one canonical output, and `handoff.md`.

## Front-door contract

`README.md` is the current orientation surface. Keep it concise enough that a reader can understand the investigation before opening source-level detail.

It should contain:

1. `## In simple words`;
2. parent issue, programme, target, and authority links;
3. exact current source or retrieval boundary;
4. the system map and the bounded question;
5. why the answer could be useful;
6. investigation areas and their owned files;
7. current established findings;
8. active disagreements and missing evidence;
9. canonical outputs and their status;
10. blockers, decisions, and next actions;
11. upstream-contact authorization.

The front door summarizes. Finding files carry the reasoning and evidence.

## Finding files

Each finding file has one owner or one explicitly transferred owner. It should record:

- the exact question;
- source revisions and retrieval dates;
- code, workflow, or system boundary examined;
- evidence and evidence class per consequential claim;
- strongest supported conclusion;
- competing explanations;
- negative results;
- uncertainty and omitted boundaries;
- dependencies on other findings;
- recommendation for synthesis or further work.

Workers may create several files when the areas have different owners, evidence types, or decision consequences. They should avoid editing another worker's finding merely to make the prose agree.

## Evidence area

Use `evidence/` for records whose main value is exactness or replayability, such as:

- source and commit maps;
- changed-file inventories;
- workflow receipts and exact test-name/count records;
- compatibility or candidate matrices;
- raw traces, reduced logs, and protocol transcripts;
- citation tables;
- branch and carrier retirement ledgers.

A finding links the evidence it interprets. Raw records never carry a stronger claim by themselves.

## Alternatives and precedent

`alternatives/` records serious approaches that were considered, including the attractive parts, failure modes, evidence required, and current disposition.

`precedent/` records relevant prior art:

- earlier Fieldwork findings and decisions;
- current and historical target-project implementations;
- specifications, official design documents, and source history;
- engineering patterns from incident response, RFC review, architecture decisions, or scientific research practice.

Precedent informs the decision. It does not replace current source and execution evidence.

## Canonical outputs

Canonical status is declared explicitly. File location alone never grants authority.

`canonical/README.md` indexes every outward-facing output and gives each one a status:

- `candidate` — ready for comparison or review;
- `accepted` — chosen for its named audience and claim boundary;
- `disputed` — viable output with an unresolved decision;
- `superseded` — retained for history and linked to its successor;
- `retired` — useful evidence transferred, no longer an active presentation.

An investigation may have several accepted canonical outputs when they serve distinct purposes, for example:

- a plain-language explainer;
- an implementation proposal;
- a separate issue for one independent invariant;
- an exact-head review packet;
- a negative-result closeout;
- a historical or operational analysis.

Every accepted output must name:

- audience and purpose;
- exact source findings and evidence inputs;
- claim scope;
- unresolved limits;
- decision owner and date;
- successor or follow-up issue when applicable.

Canonicalization links and interprets the underlying findings. The underlying records remain available.

## Conflict protocol

When findings disagree:

1. preserve both files;
2. state the exact proposition in dispute;
3. identify which source pin, assumption, evidence class, or decision value differs;
4. record the test or judgment that could resolve it;
5. assign one coordinator for the synthesis;
6. carry unresolved disagreement into `canonical/README.md` or a decision record.

A disagreement can produce two canonical candidates when the choice depends on audience, compatibility, policy, or a human value judgment.

## Lifecycle

Use this sequence:

```text
orient
→ collect independent findings
→ compare and challenge
→ draft canonical candidates
→ decide, split, or retain disagreement
→ publish, implement, open follow-up issues, or close
```

Source drift can send an output back to collection or comparison. Preserve the expired decision and name the new input that reopened it.

## Approaches considered for this convention

### One giant issue or comment thread

Useful for live coordination, weak for exact diffs, durable ownership, and reviewable synthesis. Issue comments remain the notification surface; repository files carry the research record.

### One shared report

Simple at small scale, costly under parallel work. It encourages edit collisions and forces agreement before the evidence has matured.

### One issue per observation

Clear ownership, heavy coordination overhead. Use a new issue when a finding becomes an independently actionable question, decision, or campaign.

### Independent agent files with no synthesis layer

Safe for parallel collection, poor for readers and decisions. The workspace front door and `canonical/` area supply the missing convergence step.

### Immediate single-answer consensus

Efficient only when the evidence already converges. Complex lifecycle and source-drift work benefits from retaining competing candidates until their assumptions and evidence are explicit.

### Database-first or generated registry-first workflow

Potentially useful later. A file convention gives humans and agents an inspectable contract while the workflow is still evolving. Automation can index stable identifiers and statuses after the convention proves useful.

## Historical precedent

This convention extends patterns already present in Fieldwork:

- campaign lane reports feed coordinator-owned `synthesis.md` and `decision.md`;
- batch `results/` feed coordinator-owned synthesis and closeout;
- execution carriers produce receipts for a separate canonical source branch;
- exact-head review preserves the reviewed input and expires conclusions after relevant drift.

It also follows familiar engineering practice:

- laboratory notes remain separate from the paper that presents the conclusion;
- incident timelines and raw evidence remain separate from the postmortem;
- RFCs and architecture decision records preserve alternatives and the reason for the selected direction;
- legal and investigative case files preserve exhibits separately from the final argument.

The shared principle is simple: preserve what was learned, make authorship and evidence visible, and declare the current presentation through an explicit decision.

## Adoption

New complex investigations should begin with this layout. Existing work can adopt it incrementally:

1. create a front-door `README.md`;
2. link existing reports and receipts before moving or rewriting them;
3. add separate files for missing alternatives, precedent, or conflicts;
4. create `canonical/README.md` when the investigation has an output ready for comparison;
5. record the exact decision and successor links;
6. update the parent issue with the workspace path and current handoff.

Migration should preserve existing URLs and evidence owners whenever practical.