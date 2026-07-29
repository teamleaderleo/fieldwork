# Workboard

GitHub Issues are the canonical live workboard. This document defines how to read and use that queue; it is not a manually duplicated list of every open item.

## Record types

Issue forms and labels are configured for:

- `[Batch]` — controlled high-volume dispatch
- `[Finding]` — retained observation
- `[Lead]` — untriaged possibility
- `[Campaign]` — parent investigation
- `[Lane]` — parallel coordinated unit
- `[Decision]` — human or coordinator choice
- `[Synthesis]` — combination and closeout work
- `[Meta]` — Fieldwork's own operation

Tiny probes normally live in a batch manifest and result file rather than receiving an issue.

## Labels

See `LABELS.md`. Every work item should have:

- exactly one `type:*` label;
- exactly one current `state:*` label;
- optional `needs:*`, `parallel-safe`, or policy labels.

Issue forms apply the initial type and state automatically.

## What to work on

A worker should select work in this order:

1. an explicitly assigned batch probe or lane;
2. an unclaimed `state:ready` lane inside an active campaign;
3. a requested synthesis or decision;
4. a lead the user explicitly asked to triage.

Never treat the target registry as an automatic work queue.

## Source of truth

- **Issue** — current owner, state, blockers, dependencies, and completion signal.
- **Batch manifest** — dispatched assignment identities and owned paths.
- **Campaign `STATUS.md`** — durable campaign snapshot and identifiers.
- **Lane or batch result** — evidence and conclusion owned by one worker.
- **Synthesis** — interpretation across assignments.
- **Ledgers** — final normalized outcomes, not active task management.

## Useful searches

```text
is:open label:"type:lane" label:"state:ready"
is:open label:"state:claimed"
is:open label:"state:blocked"
is:open label:"state:ready-for-synthesis"
is:open label:"needs:human-decision"
is:open label:"type:batch"
is:open label:"policy:reference-violation"
```

## Work-in-progress limits

- One worker claims one primary coordinated lane at a time unless assignments are explicitly coupled.
- Tiny independent probes may run concurrently when each has an immutable output path.
- A campaign should have no more active lanes than a coordinator can review and synthesise.
- A batch should declare a maximum useful concurrency.
- New lanes require a distinct question, deliverable, or evidence type.
- Duplicate reconnaissance should be merged or stopped quickly.
