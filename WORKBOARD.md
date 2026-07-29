# Workboard

GitHub Issues are the canonical live workboard. This document defines how to read and use that queue; it is not a manually duplicated list of every open item.

## Record types

Use title prefixes even before repository labels are configured:

- `[Finding]` — retained observation
- `[Lead]` — untriaged possibility
- `[Campaign]` — parent investigation
- `[Lane]` — parallel unit of work under a campaign
- `[Decision]` — human or coordinator choice
- `[Synthesis]` — combination and closeout work
- `[Meta]` — Fieldwork's own operation

## States

Use these exact state tokens in issue bodies, handoffs, and status documents:

- `observed`
- `triage`
- `ready`
- `claimed`
- `investigating`
- `blocked`
- `ready-for-synthesis`
- `synthesising`
- `candidate`
- `seeking-direction`
- `submitted`
- `merged`
- `declined`
- `withdrawn`
- `negative-result`
- `dormant`
- `complete`

Labels may mirror these later. The text tokens remain the portable contract for agents and future automation.

## What to work on

A worker should select work in this order:

1. an explicitly assigned lane;
2. an unclaimed `ready` lane inside an active campaign;
3. a requested synthesis or decision;
4. a lead that the user explicitly asked to triage.

Never treat the target registry as an automatic work queue.

## Source of truth

- **Issue** — current owner, state, blockers, dependencies, and completion signal.
- **Campaign `STATUS.md`** — bounded snapshot and durable identifiers, updated by the coordinator.
- **Lane report** — evidence and result owned by one lane.
- **Synthesis** — campaign-level interpretation across lanes.
- **Ledgers** — final normalized outcomes, not active task management.

## Recommended repository views

Once labels are configured, useful saved views are:

- Ready lanes
- Claimed lanes
- Blocked work
- Ready for synthesis
- Decisions needed
- Active upstream submissions
- Negative results

Until then, use title prefixes and state tokens in GitHub issue search.

## Work-in-progress limits

- One worker claims one primary lane at a time unless the lanes are explicitly coupled.
- A campaign should have no more simultaneously active lanes than a coordinator can review and synthesise.
- New lanes require a distinct question, deliverable, or evidence type.
- Duplicate reconnaissance should be merged or stopped quickly.
