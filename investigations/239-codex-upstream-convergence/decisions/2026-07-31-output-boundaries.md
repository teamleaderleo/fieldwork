# Decision: one lifecycle model and several bounded Codex outputs

Decision date: 2026-07-31  
Decision owner: Fieldwork #239 coordinator  
State: `accepted for investigation packaging`  
Implementation and source proposal authority: `none`  
Upstream contact authorized: `false`

## In simple words

Codex tool continuity crosses request construction, runtime authority, execution, persistence, history, and terminal output. These areas share one story and require separate technical decisions.

Fieldwork will maintain one plain-language lifecycle model for orientation and several bounded canonical outputs for source review. Independent findings remain available, including disagreements and negative results.

## Decision

Use this packaging:

1. one workspace front door;
2. independently owned finding and evidence files;
3. explicit alternatives and prior art;
4. one accepted internal lifecycle explainer;
5. separate candidate proposal packets by source owner and invariant;
6. separate stopped records for absorbed or obsolete candidates;
7. new Fieldwork issues when a canonical output becomes independently actionable;
8. carrier retirement only after source and receipts transfer.

## Why

The active Codex questions belong to different owners:

- request and model-visible capability construction;
- standalone Code Mode execution authority;
- MCP runtime reconciliation and publication;
- operation timeout, cancellation, and settlement;
- session live history and ThreadStore append;
- rollout projection and reconstruction;
- unified-exec output production and completion.

Each owner needs its own exact source fence, tests, compatibility analysis, rollback, and reviewer. One combined implementation would let evidence from one layer appear to support another.

## Alternatives considered

### One issue thread

Retained for live coordination. Durable reasoning and canonical outputs live in repository files.

### One mega-report

Declined because parallel authorship, partial source expiry, and disagreement become difficult to preserve.

### One mega-patch

Declined because authority, operation settlement, persistence, replay, and terminal output have different owners and safety conditions.

### Immediate single canonical answer

Declined while source execution and policy decisions remain open. Candidate and disputed outputs stay visible.

### One issue per intermediate observation

Declined for early evidence collection. Promotion to an issue occurs when the finding becomes independently actionable.

## Precedent

This decision extends existing Fieldwork practice:

- worker-owned lane reports feed coordinator-owned synthesis and decisions;
- batch result files feed a shared synthesis;
- execution carriers produce receipts for separate canonical source branches;
- exact-head review expires conclusions after relevant input drift;
- negative and superseded work remains durable.

It also follows common research and engineering practice: laboratory records remain distinct from papers, incident evidence remains distinct from postmortems, and architecture decisions preserve alternatives alongside the selected direction.

## Consequences

### Benefits

- new readers get one understandable entry point;
- workers can write in parallel without shared-file collisions;
- disagreements remain reviewable;
- each proposal has a narrow evidence boundary;
- absorbed work closes with a reusable record;
- several audiences can receive purpose-specific outputs.

### Costs

- coordinators must maintain links and canonical statuses;
- source drift can reopen part of the workspace;
- duplicated background requires editorial control;
- automation should wait until stable identifiers and lifecycle rules prove useful.

## Clearing conditions for technical outputs

This packaging decision is active now. Individual source outputs still require:

- current upstream classification;
- canonical source-only branch and exact head;
- exact test-name and count preflight;
- target-native execution receipts;
- complete current diff review;
- prior-art and compatibility analysis;
- explicit risks, non-goals, and successor mapping;
- separate authority for public upstream contact.

## Inputs

- [`../findings/problem-map.md`](../findings/problem-map.md);
- [`../findings/upstream-drift-and-overlap.md`](../findings/upstream-drift-and-overlap.md);
- [`../alternatives/approach-selection.md`](../alternatives/approach-selection.md);
- [`../precedent/fieldwork-and-upstream-prior-art.md`](../precedent/fieldwork-and-upstream-prior-art.md);
- [`../canonical/convergence-model.md`](../canonical/convergence-model.md).