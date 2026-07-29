# Fieldwork

Public research, experiments, reproductions, and upstream engineering campaigns.

Fieldwork exists to investigate external systems seriously before asking their maintainers to spend time on us. Forks hold candidate code. This repository holds the durable reasoning: questions, source maps, reproductions, experiments, decisions, negative results, and upstream packets.

## What this is for

- investigate problems encountered while building our own projects;
- map important external systems without immediately contacting upstream;
- turn uncertain observations into reproducible findings;
- prepare contributions that reduce, rather than export, verification work;
- study rigorous human-accountable AI-assisted engineering;
- retain useful research even when no patch is submitted or accepted.

## Operating principle

> Every upstream submission should reduce the maintainer's uncertainty more than it increases their review burden.

## Repository map

- [`CHARTER.md`](CHARTER.md) — purpose, boundaries, and standards.
- [`METHOD.md`](METHOD.md) — the campaign lifecycle.
- [`OPERATIONS.md`](OPERATIONS.md) — day-to-day intake, triage, and stopping rules.
- [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) — quiet external references and intentional contact.
- [`targets/`](targets/) — maps of ecosystems worth understanding.
- [`research/`](research/) — cross-project research programmes.
- [`campaigns/`](campaigns/) — bounded investigations with explicit outcomes.
- [`templates/`](templates/) — reusable investigation and upstream documents.
- [`ledger/`](ledger/) — machine-readable findings and contribution history.

## Reference states

1. **Observed** — quiet research; external references are backlink-suppressing.
2. **Candidate** — evidence exists, but upstream contact has not been earned.
3. **Submitted** — deliberate upstream interaction exists and direct references may be used.

## Current target set

The initial maps cover Vercel AI SDK, Cloudflare Workers SDK, OpenTelemetry JavaScript, Gemini CLI, and Biome. These are research targets, not quotas or obligations. Work starts when a problem intersects something we actually care about.

## First research programme

[`campaigns/0001-proof-carrying-contributions/`](campaigns/0001-proof-carrying-contributions/) asks whether heavily AI-assisted engineering can produce contributions that lower maintainer verification cost while preserving human accountability.
