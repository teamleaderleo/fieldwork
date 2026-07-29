# Fieldwork

Public research, experiments, reproductions, and upstream engineering campaigns.

Fieldwork investigates external systems seriously before asking their maintainers to spend time on us. Forks hold candidate upstream code. This repository holds durable reasoning and fork-free experimental work: questions, source maps, reproductions, experiments, decisions, negative results, handoffs, and upstream packets.

## Enter here

- [`START_HERE.md`](START_HERE.md) — exact runbook for a person or agent sent to Fieldwork.
- [`EXPERIMENTS.md`](EXPERIMENTS.md) — fork-free one-off tests, canonical cases, and promotion rules.
- [`playgrounds/`](playgrounds/) — runnable local experiments and reusable case packs.
- [`BATCHES.md`](BATCHES.md) — controlled fan-out for many repositories, questions, and methods.
- [`WORKBOARD.md`](WORKBOARD.md) — issue types, labels, states, and useful queue views.
- [`COORDINATION.md`](COORDINATION.md) — parallel lanes, ownership, handoffs, synthesis, and completion signals.
- [Open Fieldwork issues](https://github.com/teamleaderleo/fieldwork/issues) — canonical live queue.

## Operating principle

> Every upstream submission should reduce the maintainer's uncertainty more than it increases their review burden.

## Working surfaces

**Playgrounds are bounded local experimentation.** They hold small runnable tests that need no upstream fork or Fieldwork issue.

**GitHub issues are live coordination.** They hold assignments, claims, state changes, blockers, decisions, and completion signals.

**Repository research files are durable evidence.** They hold exact revisions, reproductions, reports, synthesis, and closeout records.

Do not use one surface as a poor substitute for another. A disposable test should not require campaign bureaucracy, a durable finding should not exist only in an issue comment, and a status file should not imitate the live issue queue.

## Scale model

Fieldwork supports these work units:

1. **Experiment** — a bounded fork-free local test owned by one worker.
2. **Batch** — a dispatch envelope for many related assignments.
3. **Campaign** — one bounded parent question.
4. **Lane** — a coordinated independently owned research unit.
5. **Probe** — a one-shot assignment that can report into a batch without receiving its own issue.

An experiment may be promoted into a finding, batch probe, campaign lane, or regression fixture when other work begins to depend on it.

A target map is useful context, never a permission boundary. Any public repository may be observed quietly when a user or coordinator assigns a concrete question.

## Repository map

- [`CHARTER.md`](CHARTER.md) — purpose, boundaries, and standards.
- [`METHOD.md`](METHOD.md) — campaign lifecycle and evidence method.
- [`OPERATIONS.md`](OPERATIONS.md) — intake, triage, states, and stopping rules.
- [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) — quiet external references and intentional contact.
- [`LABELS.md`](LABELS.md) — configured issue taxonomy and state transitions.
- [`playgrounds/`](playgrounds/) — fork-free runnable experiments and canonical cases.
- [`batches/`](batches/) — high-volume dispatch manifests and result sets.
- [`targets/`](targets/) — target registry and deeper ecosystem maps.
- [`research/`](research/) — cross-project research programmes.
- [`campaigns/`](campaigns/) — bounded investigations and parallel lane reports.
- [`templates/`](templates/) — experiment, batch, campaign, lane, handoff, synthesis, and upstream documents.
- [`ledger/`](ledger/) — normalized findings and contribution history.

## Reference states

1. **Observed** — quiet research; external references are backlink-suppressing.
2. **Candidate** — evidence exists, but upstream contact has not been earned.
3. **Submitted** — deliberate upstream interaction exists and direct references may be used.

## First research programme

[`campaigns/0001-proof-carrying-contributions/`](campaigns/0001-proof-carrying-contributions/) asks whether heavily AI-assisted engineering can produce contributions that lower maintainer verification cost while preserving human accountability.
