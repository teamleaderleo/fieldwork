# Codex rollout compaction storage

Context ID: `CTX-codex-rollout-compaction-storage`

Owner: `codex:gpt-5.6-sol`

Date: 2026-08-25

Target label: `target:codex`

Target hub: Fieldwork issue 8

Related experiment: `EXP-20260825-codex-rollout-compaction-growth`

Claim scope: `operational` for one directly measured local Desktop installation

## In simple words

Codex stores an append-only rollout for each session and writes a full replacement history into a new compacted checkpoint when it changes context windows. On one heavily used Mac, those checkpoints occupied 28.32 GB, or 83.1% of the measured 34.06 GB session store. An earlier live incident on the same product boundary observed app-server reading multi-gigabyte rollouts while its physical footprint peaked at 16 GB.

The measurements support an operational resource-exhaustion risk for this installation and identify checkpoint persistence as its dominant on-disk producer. They do not establish prevalence across users or select a recovery-safe deletion algorithm.

## Context question

Does the isolated checkpoint measurement connect to a real operational consequence beyond file-format mechanics?

## System role and workflow

```text
conversation history
→ compacted rollout checkpoint with replacement_history
→ append-only session file
→ Desktop/app-server restore and hydration
→ disk consumption and process memory pressure
```

Codex owns checkpoint serialization and reconstruction. The local session store owns durable bytes. Desktop/app-server reads that state for restore and inspection. The machine operator experiences the resulting disk and memory pressure.

## Contract boundaries

- **Documented:** current public source appends compacted records with an optional full `replacement_history` and reconstructs from the newest surviving checkpoint.
- **Observed:** the content-safe analyzer classified record type and byte size without retaining transcript text, paths, thread identifiers, or prompts.
- **Observed:** all 6,246 compacted records in the fenced snapshot contained `replacement_history` and occupied 28,319,667,945 bytes.
- **Observed:** Fieldwork issue 776 separately retained a 16 GB app-server peak while the process had multi-gigabyte rollout files open and sampled filesystem-read/JSON-allocation work.
- **Unknown:** which older checkpoints are required for rollback, forks, window chains, world state, late results, or diagnostics.

## Operational evidence

| Claim | Label | Source | Version/date | Limitation |
|---|---|---|---|---|
| Compacted replacement-history records dominate the measured store. | Observed | `playgrounds/EXP-20260825-codex-rollout-compaction-growth/results/latest.json` | snapshot fenced 2026-08-25 | One heavy local installation. |
| App-server reached a 16 GB physical-footprint peak while reading and parsing multi-GB rollouts. | Observed | [Fieldwork issue 776](https://github.com/teamleaderleo/fieldwork/issues/776) | Desktop 26.803.41515 | Earlier build and incident; exact initiating request unknown. |
| Current public source persists and reconstructs full replacement-history checkpoints. | Documented | [OpenAI Codex commit `c3953649`](https://github.com/openai/codex/commit/c3953649156e15b67e572cb9e38bc825a811c24e) | retrieved 2026-08-25 | Public-source pin is not proven identical to the bundled binary. |
| Oversized rollout hydration already has a public owner. | Documented | [Codex issue 29510](https://redirect.github.com/openai/codex/issues/29510) | retrieved 2026-08-25 | Public report; frequency remains unknown. |

## Failure propagation and visibility

On disk, repeated full checkpoints amplify session files until one thread can occupy gigabytes. During hydration, large rollouts can drive filesystem reads, JSON parsing, allocation, swap, and sustained CPU. Visible signals include session-directory growth, large compacted-record share, app-server footprint, swap, open rollout files, and sampled parse/allocation stacks.

## Competing architectures

Content-addressed checkpoints, recovery-compatible rewriting of superseded windows, per-thread byte budgets with quarantine, and bounded hydration could reduce different parts of the cost. Deleting old compacted lines without proving reconstruction semantics is not an accepted repair.

## Decisions enabled

Retain the experiment as operational evidence for this installation, keep the existing public issues as the external owners, and investigate a persistence budget or recovery-compatible compaction boundary before proposing deletion. Do not claim ecosystem prevalence.

## Promotion status

- [x] Plain-language block updated
- [x] Target hub and label recorded
- [x] Operational claim supported for one measured installation
- [x] Limitations and unknown recovery semantics recorded
- [ ] Ecosystem claim supported
- [ ] Safe repair selected
