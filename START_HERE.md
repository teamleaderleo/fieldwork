# Start Here

Use this runbook whenever a person or agent is told to investigate something through Fieldwork.

## 1. Read the rules

Read, in order:

1. `AGENTS.md`
2. `CHARTER.md`
3. `METHOD.md`
4. `REFERENCE_POLICY.md`
5. `EXPERIMENTS.md` for a fork-free local test
6. `COORDINATION.md` for shared or parallel work
7. `BATCHES.md` when the assignment belongs to a batch
8. the relevant target map, experiment, manifest, campaign, lane, and issue

Tool-specific instruction files point back to `AGENTS.md`; they do not replace it.

## 2. Identify the assigned unit

Search open Fieldwork issues, active batches, existing playgrounds, and campaign folders before creating a record.

Choose the smallest correct unit:

- **Experiment** — bounded one-worker local test requiring no upstream fork or issue.
- **Batch** — controlled dispatch across many assignments.
- **Finding** — retained observation with no approved campaign.
- **Lead** — possible investigation awaiting triage.
- **Campaign** — bounded parent question.
- **Lane** — coordinated independently owned unit.
- **Probe** — one-shot assignment recorded in a batch manifest.
- **Decision** — coordinator or human choice.
- **Synthesis** — combination and closeout work.

Do not create work merely because an external repository has an available issue.

## 3. Establish ownership

Never silently begin work another assignment may already own.

For an experiment, record in `experiment.json`:

- worker identity;
- one bounded question;
- exact command and environment;
- source revisions or retrieval boundary;
- distinguishing outcomes;
- stop condition;
- upstream-contact authorization, normally `false`.

For a lane or probe, record:

- worker identity;
- exact question;
- expected deliverable;
- owned output path;
- dependencies;
- target source revision or retrieval boundary;
- stop condition;
- upstream-contact authorization, normally `false`.

One worker may edit only the owned experiment or assignment path. Coordinators own manifests, status, synthesis, decision, and closeout files.

## 4. Protect external projects before writing

Before creating or editing any Fieldwork issue, PR, comment, review, report, experiment note, or data record:

- convert external GitHub issue, PR, discussion, and commit links to `redirect.github.com`;
- remove external shorthand cross-references;
- use the intentional marker only after explicit authorization for that interaction.

The CI detector runs after GitHub receives interaction text. It is a safety net, not permission to post a direct reference first.

## 5. Work quietly

Fieldwork itself may be updated as part of the assignment. External upstream interaction remains prohibited unless the user explicitly authorizes that exact interaction.

Preserve:

- exact repository and revision;
- retrieval date;
- commands and environment;
- evidence supporting each factual claim;
- competing hypotheses;
- negative results and uncertainty;
- safety and data-handling boundaries.

For small local tests, prefer synthetic fixtures and `playgrounds/cases/`. Default to no network access.

## 6. Put evidence in the correct place

Preferred durable outputs:

- `playgrounds/EXP-YYYYMMDD-short-name/`
- `campaigns/<campaign>/lanes/<lane>/report.md`
- `batches/<batch>/results/<assignment>.md`
- retained artifacts beside the report

Use:

- `templates/experiment.json`
- `templates/experiment.md`
- `templates/lane-report.md`
- `templates/batch-result.md`
- `templates/handoff.md`
- `templates/synthesis.md`

Avoid several agents editing one shared report or experiment directory.

## 7. Report completion visibly

A standalone experiment does not require an issue comment. Finish its `README.md` or report, update `experiment.json`, and promote it when other work depends on the result.

For coordinated work, post a completion comment on the relevant lane, campaign, or batch issue:

```text
FIELDWORK HANDOFF
State: ready-for-synthesis | blocked | negative-result | complete
Batch: <batch id or none>
Campaign: <campaign id or none>
Assignment: <lane or probe id>
Durable artifacts: <paths or Fieldwork PR>
Finding: <one-paragraph result>
Uncertainty: <remaining uncertainty>
Dependencies discovered: <none or exact records>
Decision needed: <none or exact decision>
Upstream contact authorized: no | yes, with explicit authority
```

If repository writes are unavailable, place the full handoff in the issue and apply `needs:materialization`.

## 8. Close through acceptance and synthesis

An experiment is finished when its question, command, result, uncertainty, and disposition are durable.

Coordinated work is finished only when:

- evidence is durable or explicitly queued for materialization;
- the issue or batch carries a handoff;
- blockers, uncertainty, and dependencies are visible;
- the coordinator can discover the result;
- the assignment is accepted, revised, promoted, or retained as a negative result.

The coordinator owns shared state transitions and synthesis.
