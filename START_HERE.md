# Start Here

Use this runbook whenever a person or agent is told to investigate something through Fieldwork.

## 1. Read the rules

Read, in order:

1. `CHARTER.md`
2. `METHOD.md`
3. `REFERENCE_POLICY.md`
4. `COORDINATION.md`
5. the relevant target map and campaign material

`AGENTS.md` is binding for automated workers.

## 2. Search before creating

Search open Fieldwork issues and existing campaign folders before opening a new record.

Choose the smallest correct record:

- **Finding** — an observation worth retaining, with no approved campaign yet.
- **Lead** — a possible investigation awaiting triage.
- **Campaign** — a bounded parent question with an explicit value and stop conditions.
- **Lane** — one independently owned part of an active campaign.
- **Decision** — a question requiring a coordinator or human choice.

Do not create a new campaign because an external repository has an available issue.

## 3. Establish ownership

Never silently begin work that another lane may already own.

For an existing lane:

- assign or identify the worker;
- state the exact deliverable;
- record dependencies and source revision;
- identify the lane-owned directory;
- post a brief claim comment before substantial work.

For parallel work, follow `COORDINATION.md`.

## 4. Work quietly

Fieldwork itself may be updated as part of the assignment. External upstream interaction remains prohibited unless the user explicitly authorizes that exact interaction.

Wrap external GitHub issue, pull-request, discussion, and commit references under `REFERENCE_POLICY.md`.

Preserve:

- exact repository and revision;
- commands and environment;
- evidence supporting each factual claim;
- competing hypotheses;
- negative results and uncertainty;
- safety and data-handling boundaries.

## 5. Put evidence in files

The preferred durable output is a branch or pull request containing a lane report and its retained artifacts.

Use:

- `templates/lane-report.md` for findings;
- `templates/handoff.md` when transferring or completing work;
- `templates/synthesis.md` when combining lanes.

Each lane owns its own directory. Avoid multiple agents editing one shared report.

## 6. Report completion visibly

After the durable material is ready, post a completion comment on the lane issue using this exact summary shape:

```text
FIELDWORK HANDOFF
State: ready-for-synthesis | blocked | negative-result | complete
Campaign: <campaign id or issue>
Lane: <lane id or issue>
Durable artifacts: <paths or Fieldwork PR>
Finding: <one-paragraph result>
Uncertainty: <remaining uncertainty>
Decision needed: <none or exact decision>
```

If repository writes are unavailable, place the full handoff in the issue and mark it `needs-materialization` so a coordinator can move it into durable files.

## 7. Close through synthesis

A lane is not finished merely because research stopped. It is finished when:

- its evidence is durable or explicitly queued for materialization;
- the issue carries a handoff state;
- blockers and uncertainty are visible;
- the parent campaign can discover the result;
- the lane is merged, rejected, or intentionally retained as a negative result.

The campaign coordinator owns synthesis and final closeout.
