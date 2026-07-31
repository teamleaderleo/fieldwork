# Start Here

Use this runbook whenever a person or agent is told to investigate something through Fieldwork.

## In simple words

Find the programme and target hub, claim one bounded scout or lane, read the code, explain the system simply, reproduce or model the important behaviour, and use an owned application as a controlled testbed when realistic use adds evidence. Retain the current technical answer in one canonical finding, compare plausible designs autonomously, and use a workspace only when several findings or outputs need one front door.

## 1. Read the rules

Read, in order:

1. `AGENTS.md`
2. `CHARTER.md`
3. `CODE_FIRST.md`
4. `PLAIN_LANGUAGE.md`
5. `METHOD.md`
6. `REFERENCE_POLICY.md`
7. `PROGRAMMES.md`
8. `TARGET_HUBS.md`
9. `EXPERIMENTS.md` for a fork-free local test
10. `TESTBEDS.md` for realistic use in an owned repository
11. `INTEGRATION_CONTEXT.md` when making claims about wider use or consequence
12. `COORDINATION.md` for shared or parallel work
13. `BATCHES.md` when the assignment belongs to a batch
14. `REVIEWING.md` before asking for acceptance, execution, promotion, merge, or upstream preparation
15. `FINDINGS.md` when work has a retained conclusion, comparison, implementation candidate, or transition
16. `DECISIONS.md` when several plausible technical approaches remain
17. `INVESTIGATION_WORKSPACES.md` when several findings, alternatives, source candidates, or outputs need one front door
18. the relevant programme hub, target hub, canonical finding, workspace, map, experiment, trial, context, manifest, campaign, lane, issue, implementation PR, and execution carrier

Tool-specific instruction files point back to `AGENTS.md`; they do not replace it.

## 2. Identify the programme, target, and assigned unit

Search `programmes/registry.yml`, `targets/hubs.yml`, open Fieldwork issues, active pull requests, canonical findings, investigation workspaces, active batches, existing playgrounds, testbeds, contexts, and campaign folders before creating a record.

Apply the correct `programme:<slug>` and `target:<slug>` labels. Link the stable programme and target hubs when they exist. If an owned repository will exercise the target, apply `testbed:<slug>` only when the trial actually begins.

Choose the smallest correct unit:

- **Programme hub** — stable cross-target direction and branching surface.
- **Target hub** — stable orientation and discovery issue for recurring work.
- **Scout lane** — bounded reconnaissance that maps a target or boundary and returns branch candidates.
- **Experiment** — bounded one-worker local test requiring no upstream fork or issue.
- **Integration trial** — realistic use in an owned repository.
- **Context dossier** — sourced explanation of how a mechanism participates in a larger workflow.
- **Canonical finding** — one retained current technical answer, evidence boundary, alternatives, and transition.
- **Investigation workspace** — orientation across several findings, alternatives, receipts, or audience-specific outputs.
- **Batch** — controlled temporary dispatch across many assignments.
- **Lead** — possible investigation awaiting triage.
- **Campaign** — bounded parent question promoted from evidence.
- **Lane** — coordinated independently owned campaign unit.
- **Probe** — one-shot assignment recorded in a batch manifest.
- **Decision** — coordinator or human choice.
- **Synthesis** — combination and closeout work.

Do not create work merely because an external repository has an available issue.

## 3. Establish ownership, state, and claim scope

Never silently begin work another assignment may already own. One mutable branch, canonical finding edit, shared workspace front door, or coordinator file has one active writer lease. Parallel workers use unique evidence, artifact, alternative, or review paths.

For every durable record, begin with `## In simple words` and answer:

- What is this?
- Where does it sit?
- What is wrong, uncertain, or being tested?
- Why could anyone care?
- What is the current answer or next step?

For issue-backed work, keep two fields separate:

```text
Issue state: `state:<live GitHub label>`
Finding state: `<FINDINGS.md transition | not applicable>`
```

`Issue state:` must agree with the live `state:*` label. `Finding state:` mirrors the canonical finding and is not required to map one-to-one to the issue label.

For a scout or lane, record worker identity, programme and target hubs, exact question, expected deliverable, owned output path, dependencies, source revision or retrieval boundary, claim scope, stop condition, and upstream-contact authorization.

A scout must return code and test maps, at least one runnable probe or explicit reason none is feasible, ranked branch candidates, and a recommendation to stop, retain a finding, open a campaign, or run another scout.

For an experiment, record one bounded question, claim scope, exact command and environment, source revisions, distinguishing outcomes, context path when required, stop condition, and upstream-contact authorization in `experiment.json`.

For an integration trial, record target and target hub, owned testbed, exact target and testbed revisions, dedicated branch and owner, realistic scenario, baseline and candidate behaviour, rollback and cleanup, claim scope, and limitations.

## 4. Protect external projects before posting interaction text

Before creating or editing any Fieldwork issue, pull request, comment, review, inline review comment, or discussion containing third-party GitHub work:

- convert third-party GitHub issue, pull-request, discussion, and commit links to `redirect.github.com`;
- remove third-party shorthand cross-references;
- use the intentional marker only after explicit authorization for that interaction.

Repository reports, canonical findings, experiments, context dossiers, data records, and other tracked files may use ordinary direct links. The interaction detector is a safety net, not permission to post a direct reference first.

## 5. Read the code and form a change thesis

Follow `CODE_FIRST.md`.

Before proposing implementation:

1. map entrypoints, control flow, data flow, state ownership, side effects, failure paths, cleanup, public contracts, and tests;
2. use recent issues and pull requests only as supplementary context;
3. state competing hypotheses;
4. identify evidence that would distinguish them;
5. state the change thesis: current behaviour, consequence, proposed improvement, evidence, and boundary.

Prioritize consequential correctness, security, recovery, performance, compatibility, integration, ergonomics, and meaningful refactors. Do not hunt documentation, lint, wording, or style work by default.

## 6. Compare alternatives autonomously

Follow `DECISIONS.md` when more than one plausible technical approach exists.

Recover project goals and contracts, derive criteria before choosing, instantiate useful alternatives when practical, run controls that can make an option lose, seek adversarial review, select the best-supported provisional winner, retain losing reasons, and name a reopening trigger.

Escalate only when the remaining choice depends on public-interaction authority, merge or deployment authority, private context, material cost, product values absent from repository evidence, irreversible risk, credentials, legal commitment, or an explicit human reservation.

## 7. Reproduce, model, or try realistic use

For small local tests, prefer synthetic fixtures and `playgrounds/cases/`. Default to no network access.

Use an owned testbed when the question depends on application lifecycle, integration, deployment, or API ergonomics that a toy model cannot reveal. Keep the trial reversible and off production systems.

A model is `model-executed`, not target execution. A prepared test is `target-test-prepared`, not executed. One owned testbed does not prove ecosystem demand or an upstream contract.

## 8. Work quietly and preserve claim-scoped evidence

Fieldwork itself and explicitly selected owned testbeds may be updated as part of the assignment. External upstream interaction remains prohibited unless the user explicitly authorizes that exact interaction.

Preserve exact repository and revision, retrieval date, commands and environment, baseline and candidate behaviour, source title and section, evidence labels, competing hypotheses, negative results, uncertainty, rollback, safety, and data-handling boundaries.

Classify each disposition-relevant claim separately as `source-read`, `model-executed`, `target-test-prepared`, `target-executed`, `integration-executed`, or `full-gate`. A record may list `Evidence classes present`; it must not assign one strongest class to the whole work.

## 9. Connect the small test to the larger system

A mechanism-only experiment may stop after validating its bounded question.

When claiming wider usefulness, downstream dependence, user impact, operational risk, or ecosystem importance, identify actual callers and state owners, map side effects, retries, ordering, persistence, recovery, and observability, distinguish documented use from inference, state what the small model omits, and create or link `templates/integration-context.md`.

## 10. Put evidence in the correct place

Preferred durable outputs include:

- `findings/F<issue>-<slug>/finding.md` plus unique `evidence/`, `artifacts/`, and `reviews/` files;
- `investigations/<issue>-<slug>/` for multi-finding orientation;
- programme scout reports;
- target maps;
- `playgrounds/EXP-YYYYMMDD-short-name/`;
- integration trials and context dossiers;
- campaign lane reports and batch results;
- retained artifacts beside the record that interprets them.

Issue comments are routing notices and receipts. They do not replace canonical findings or workspace evidence.

## 11. Self-review before handoff

Follow `REVIEWING.md` and complete `templates/review.md` before asking another reviewer to accept, execute, promote, merge, or prepare work for upstream use.

At minimum:

1. trace every transition-relevant claim to an exact source path, artifact, test, workflow receipt, or retained result;
2. record evidence class per claim;
3. separate harness, setup, fixture, installation, and product failures;
4. inspect the complete current diff and current-main relation;
5. synchronize issue state, finding state, canonical finding, PR front page, receipts, and queue or Delivery Desk entry;
6. version issue-body and live-metadata inputs separately when they affect the disposition;
7. mark non-applicable fields instead of inventing evidence;
8. prove temporary workflows or carriers are absent from the final canonical head before calling them retired.

Self-review prepares the handoff. It does not replace eligible independent acceptance.

## 12. Report and close visibly

For coordinated work, post short routing updates only when issue state, finding state, canonical path, exact head, evidence, selected direction, blocker, or authority changes. Put full reasoning in the canonical finding, workspace, review, or implementation PR.

A coordinated handoff names the programme and target, issue state, finding state, canonical finding, exact source and carrier heads, commands and outcomes, claim scope, uncertainty, dependencies, exact next transition, and upstream-contact authorization.

Coordinated work is finished only when evidence is durable, the issue and finding are synchronized, labels are correct, blockers and uncertainty are visible, the coordinator can discover the result, broader claims retain their limits, and the assignment is accepted, revised, promoted, stopped, or retained as a negative result.
