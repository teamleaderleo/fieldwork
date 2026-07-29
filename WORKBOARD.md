# Workboard

GitHub Issues are the canonical live workboard. This document defines how to read and use that queue; it is not a manually duplicated list of every open item.

## In simple words

Target hubs explain each recurring system. Target labels collect everything about that system. Ordinary issues represent actual work. Testbed labels show which owned repository was used for a realistic trial.

## Record types

Issue forms and labels are configured for:

- `[Target]` — stable target hub and orientation index
- `[Batch]` — controlled high-volume dispatch
- `[Finding]` — retained observation
- `[Lead]` — untriaged possibility
- `[Campaign]` — parent investigation
- `[Lane]` — parallel coordinated unit
- `[Decision]` — human or coordinator choice
- `[Synthesis]` — combination and closeout work
- `[Meta]` — Fieldwork's own operation

Tiny probes normally live in a batch manifest and result file rather than receiving an issue.

## Target hubs

Each active recurring target may have one long-lived `type:target` issue. The hub holds the plain-language model, target map, change thesis, research surfaces, testbed history, and label searches.

The initial hubs are recorded in `targets/hubs.yml`. Do not pin every hub. Discover them through `type:target`, target labels, the hub registry, and the README.

Every related work issue should carry the same `target:<slug>` label. A target hub is an index, not a giant checklist.

## Labels

See `LABELS.md`. Every work item should have:

- exactly one `type:*` label;
- exactly one current `state:*` label;
- one or more `target:*` labels when a recurring system is involved;
- an optional `testbed:*` label when an owned repository supports an integration trial;
- optional `needs:*`, `parallel-safe`, or policy labels.

Issue forms apply the initial type and state automatically. Agents must add the correct target and testbed labels when known.

## What to work on

A worker should select work in this order:

1. an explicitly assigned batch probe or lane;
2. an unclaimed `state:ready` lane inside an active campaign;
3. a requested synthesis or decision;
4. a lead the user explicitly asked to triage;
5. a bounded code-first exploration explicitly assigned against a target.

Never treat the target or testbed registries as automatic work queues.

## Source of truth

- **Target hub** — stable orientation, change thesis, and discovery links.
- **Issue** — current owner, state, blockers, dependencies, and completion signal.
- **Batch manifest** — dispatched assignment identities and owned paths.
- **Campaign `STATUS.md`** — durable campaign snapshot and identifiers.
- **Lane or batch result** — evidence and conclusion owned by one worker.
- **Integration trial** — realistic use in an owned repository.
- **Synthesis** — interpretation across assignments.
- **Ledgers** — final normalized outcomes, not active task management.

## Useful searches

```text
is:open label:"type:target"
is:open label:"target:vercel-ai"
is:open label:"target:workers-sdk"
is:open label:"target:opentelemetry-js"
is:open label:"testbed:stensibly"
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
- One integration trial branch has one owner.
- A campaign should have no more active lanes than a coordinator can review and synthesise.
- A batch should declare a maximum useful concurrency.
- New lanes require a distinct question, deliverable, or evidence type.
- Duplicate reconnaissance should be merged or stopped quickly.