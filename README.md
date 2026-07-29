# Fieldwork

Public research, experiments, reproductions, and upstream engineering campaigns.

Fieldwork exists to investigate external systems seriously before asking their maintainers to spend time on us. Forks hold candidate code. This repository holds the durable reasoning: questions, source maps, reproductions, experiments, decisions, negative results, handoffs, and upstream packets.

## Enter here

- [`START_HERE.md`](START_HERE.md) — exact runbook for a person or agent sent to Fieldwork.
- [`WORKBOARD.md`](WORKBOARD.md) — how to find work, distinguish records, and see what is ready.
- [`COORDINATION.md`](COORDINATION.md) — parallel lanes, ownership, handoffs, synthesis, and completion signals.
- [Open Fieldwork issues](https://github.com/teamleaderleo/fieldwork/issues) — canonical live queue.

## Operating principle

> Every upstream submission should reduce the maintainer's uncertainty more than it increases their review burden.

## Two surfaces

**GitHub issues are live coordination.** They hold claims, assignments, state changes, blockers, decisions, and completion signals.

**Repository files are durable evidence.** They hold source maps, exact revisions, reproductions, experiments, reports, synthesis, and closeout records.

Do not use one surface as a poor substitute for the other. A long-lived finding should not exist only in an issue comment, and a status file should not become a manually maintained imitation of the issue queue.

## Repository map

- [`CHARTER.md`](CHARTER.md) — purpose, boundaries, and standards.
- [`METHOD.md`](METHOD.md) — campaign lifecycle and evidence method.
- [`OPERATIONS.md`](OPERATIONS.md) — intake, triage, states, and stopping rules.
- [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) — quiet external references and intentional contact.
- [`targets/`](targets/) — target registry and deeper ecosystem maps.
- [`research/`](research/) — cross-project research programmes.
- [`campaigns/`](campaigns/) — bounded investigations and parallel lane reports.
- [`templates/`](templates/) — investigation, lane, handoff, synthesis, and upstream documents.
- [`ledger/`](ledger/) — machine-readable findings and contribution history.

## Reference states

1. **Observed** — quiet research; external references are backlink-suppressing.
2. **Candidate** — evidence exists, but upstream contact has not been earned.
3. **Submitted** — deliberate upstream interaction exists and direct references may be used.

## Target set

The target registry contains mapped, watch, and unassessed candidates. A target's presence is not a quota, endorsement, or commitment. Work starts when a question intersects something we actually value.

## First research programme

[`campaigns/0001-proof-carrying-contributions/`](campaigns/0001-proof-carrying-contributions/) asks whether heavily AI-assisted engineering can produce contributions that lower maintainer verification cost while preserving human accountability.
