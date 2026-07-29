# Fieldwork

Public code-first research, experiments, reproductions, owned-repository trials, integration contexts, and upstream engineering campaigns.

## In simple words

Fieldwork is where we understand software deeply enough to test real behaviour and decide whether anything should change. Programmes organize broad directions, target hubs explain recurring systems, and scout lanes map the lay of the land before concrete findings branch into campaigns.

Fieldwork investigates external systems seriously before asking their maintainers to spend time on us. Forks hold candidate upstream code. Owned repositories may hold controlled integration trials. This repository holds durable reasoning: programme and target maps, reproductions, experiments, trial records, context dossiers, decisions, negative results, handoffs, and upstream packets.

## Enter here

- [`START_HERE.md`](START_HERE.md) — exact runbook for a person or agent sent to Fieldwork.
- [`PROGRAMMES.md`](PROGRAMMES.md) — long-lived directions, scout lanes, branching, and concurrency.
- [`CODE_FIRST.md`](CODE_FIRST.md) — what kinds of changes are worth investigating and how to understand code before proposing them.
- [`PLAIN_LANGUAGE.md`](PLAIN_LANGUAGE.md) — the short understanding check required near the top of durable work.
- [`TARGET_HUBS.md`](TARGET_HUBS.md) — stable target issues, `target:*` labels, and discovery rules.
- [`TESTBEDS.md`](TESTBEDS.md) — using owned repositories for controlled realistic integration trials.
- [`EXPERIMENTS.md`](EXPERIMENTS.md) — fork-free one-off tests, canonical cases, and promotion rules.
- [`INTEGRATION_CONTEXT.md`](INTEGRATION_CONTEXT.md) — connecting isolated results to actual workflows, sources, and consequences.
- [`BATCHES.md`](BATCHES.md) — controlled temporary fan-out for many repositories, questions, and methods.
- [`WORKBOARD.md`](WORKBOARD.md) — issue types, labels, states, and useful queue views.
- [`COORDINATION.md`](COORDINATION.md) — programme scouts, campaign lanes, ownership, handoffs, synthesis, and completion signals.
- [Open Fieldwork issues](https://github.com/teamleaderleo/fieldwork/issues) — canonical live queue.

## Operating principle

> Every upstream submission should reduce the maintainer's uncertainty more than it increases their review burden.

A proposed change should also explain what becomes safer, faster, more correct, more compatible, easier to integrate, or easier to maintain.

## Active research programmes

- [SDK integration and lifecycle](https://github.com/teamleaderleo/fieldwork/issues/13) — streaming, retries, cancellation, state, types, transports, and observability.
- [Agent and CLI execution](https://github.com/teamleaderleo/fieldwork/issues/14) — tools, approval, processes, sessions, terminals, interruption, and recovery.
- [Web tooling and runtime correctness](https://github.com/teamleaderleo/fieldwork/issues/15) — source preservation, invalidation, teardown, isolation, compatibility, and performance.
- [Data and durable workflows](https://github.com/teamleaderleo/fieldwork/issues/16) — transactions, retries, identity, storage, interruption, recovery, and reconciliation.

The machine-readable portfolio is [`programmes/registry.yml`](programmes/registry.yml). The initial scout wave is already open as `type:lane`, `state:ready`, and `parallel-safe` work.

## Target hubs

The active mapped targets have stable orientation issues and dedicated labels:

- [Vercel AI SDK](https://github.com/teamleaderleo/fieldwork/issues/2) — `target:vercel-ai`
- [Cloudflare Workers SDK](https://github.com/teamleaderleo/fieldwork/issues/3) — `target:workers-sdk`
- [OpenTelemetry JS](https://github.com/teamleaderleo/fieldwork/issues/4) — `target:opentelemetry-js`
- [Gemini CLI](https://github.com/teamleaderleo/fieldwork/issues/5) — `target:gemini-cli`
- [Biome](https://github.com/teamleaderleo/fieldwork/issues/6) — `target:biome`
- [MCP TypeScript SDK](https://github.com/teamleaderleo/fieldwork/issues/7) — `target:mcp-typescript-sdk`
- [Codex](https://github.com/teamleaderleo/fieldwork/issues/8) — `target:codex`
- [Vite](https://github.com/teamleaderleo/fieldwork/issues/9) — `target:vite`
- [Playwright](https://github.com/teamleaderleo/fieldwork/issues/10) — `target:playwright`
- [DuckDB](https://github.com/teamleaderleo/fieldwork/issues/11) — `target:duckdb`
- [Supabase](https://github.com/teamleaderleo/fieldwork/issues/12) — `target:supabase`

Hubs are indexes, not giant task lists. Related issues are discovered through their target label. The machine-readable registry is [`targets/hubs.yml`](targets/hubs.yml).

## Working surfaces

**Programme hubs organize broad responsibility.** They hold the thesis, target set, scout list, candidate testbeds, branching rule, and current direction.

**Scout lanes map the lay of the land.** They must return code and test maps, runnable evidence or a feasibility limit, ranked branch candidates, negative results, and a recommendation.

**Target hubs orient recurring work.** They hold the plain-language model, change thesis, code surfaces, discovery searches, and current direction.

**Playgrounds are bounded local experimentation.** They hold small runnable tests that need no upstream fork or Fieldwork issue.

**Owned testbeds provide realistic use.** They let SDKs, runtimes, and tools run inside actual projects under controlled branches, exact revisions, and rollback rules. Add `testbed:*` only after a real trial starts.

**Contexts connect evidence to larger use.** They distinguish actual integrations, standards, and observed consequences from inference and illustrative examples.

**GitHub issues are live coordination.** They hold assignments, claims, state changes, blockers, decisions, and completion signals.

**Repository research files are durable evidence.** They hold exact revisions, reproductions, reports, synthesis, and closeout records.

Do not use one surface as a poor substitute for another. A scout is not complete after a code tour, a disposable test should not require campaign bureaucracy, a durable finding should not exist only in an issue comment, a testbed should not be presented as proof of ecosystem demand, and a toy reproduction should not be presented as proof of production impact.

## What Fieldwork prioritizes

In broad order:

1. security, correctness, data integrity, and trust boundaries;
2. lifecycle, concurrency, cancellation, retry, recovery, and partial failure;
3. performance and resource behaviour;
4. compatibility, protocols, deployment, and integration;
5. API and workflow ergonomics demonstrated through actual use;
6. refactors with a concrete correctness, safety, or maintenance payoff.

Documentation, lint, wording, and style work are not default research targets.

## Scale model

Fieldwork supports these work units:

1. **Programme hub** — stable direction across related targets.
2. **Target hub** — stable orientation and discovery for a recurring system.
3. **Scout lane** — bounded reconnaissance that returns concrete branches.
4. **Experiment** — a bounded fork-free local test owned by one worker.
5. **Integration trial** — realistic use in an owned repository.
6. **Context dossier** — sourced integration, operational, or ecosystem interpretation of a mechanism.
7. **Batch** — a temporary dispatch envelope for many related assignments.
8. **Campaign** — one bounded parent question promoted from evidence.
9. **Lane** — a coordinated independently owned campaign unit.
10. **Probe** — a one-shot assignment that can report into a batch without receiving its own issue.

A scout or experiment may be promoted into a finding, trial, context dossier, campaign, regression fixture, or another bounded scout when other work begins to depend on it.

Any public repository may be observed quietly when a user or coordinator assigns a concrete question. Programme, target, and testbed registries are not automatic permission to work or contact upstream.

## Worked example

The retry/idempotency example shows the intended evidence stack:

- [`playgrounds/examples/retry-idempotency/`](playgrounds/examples/retry-idempotency/) — a tiny deterministic simulator;
- [`playgrounds/cases/retry-idempotency.json`](playgrounds/cases/retry-idempotency.json) — reusable cases;
- [`contexts/patterns/retry-idempotency.md`](contexts/patterns/retry-idempotency.md) — standards, real integration patterns, failure propagation, observability, and explicit limitations.

The small model validates one property. The context dossier explains where that property can be useful without pretending the model reproduces a specific production system.

## Repository map

- [`CHARTER.md`](CHARTER.md) — purpose, boundaries, and standards.
- [`METHOD.md`](METHOD.md) — campaign lifecycle and evidence method.
- [`OPERATIONS.md`](OPERATIONS.md) — intake, triage, states, and stopping rules.
- [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) — quiet external references and intentional contact.
- [`LABELS.md`](LABELS.md) — type, state, programme, target, testbed, coordination, and policy labels.
- [`programmes/`](programmes/) — active portfolio and future scout reports.
- [`targets/`](targets/) — target registry, hubs, and deeper ecosystem maps.
- [`testbeds/`](testbeds/) — public owned-repository testbed candidates.
- [`playgrounds/`](playgrounds/) — fork-free runnable experiments and canonical cases.
- [`contexts/`](contexts/) — integration patterns and system contexts.
- [`batches/`](batches/) — high-volume dispatch manifests and result sets.
- [`research/`](research/) — cross-project research topics and background work.
- [`campaigns/`](campaigns/) — bounded investigations and parallel campaign lanes.
- [`templates/`](templates/) — experiment, trial, context, batch, programme, campaign, lane, handoff, synthesis, and upstream documents.
- [`ledger/`](ledger/) — normalized findings and contribution history.

## Reference states

1. **Observed** — quiet research; external references are backlink-suppressing.
2. **Candidate** — evidence exists, but upstream contact has not been earned.
3. **Submitted** — deliberate upstream interaction exists and direct references may be used.

The existing proof-carrying-contributions campaign remains under [`campaigns/0001-proof-carrying-contributions/`](campaigns/0001-proof-carrying-contributions/).
