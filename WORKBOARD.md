# Workboard

GitHub Issues are the canonical live workboard. This document defines how to read and use that queue; it is not a manually duplicated list of every open item.

## In simple words

Programme hubs explain broad research directions. Target hubs explain recurring systems. Scout lanes map the lay of the land and return concrete branches. Target labels collect work by system. Testbed labels show which owned repository was actually used for a realistic trial.

## Record types

Issue forms and labels are configured for:

- `[Programme]` — stable cross-target research direction and branching surface
- `[Target]` — stable target hub and orientation index
- `[Batch]` — controlled temporary high-volume dispatch
- `[Finding]` — retained observation
- `[Lead]` — untriaged possibility
- `[Campaign]` — parent investigation promoted from evidence
- `[Lane]` — scout or campaign unit with one owner
- `[Decision]` — human or coordinator choice
- `[Synthesis]` — combination and closeout work
- `[Meta]` — Fieldwork's own operation

Tiny probes normally live in a batch manifest and result file rather than receiving an issue.

## Programme hubs

Each active long-lived direction has one `type:programme` issue and a `programme:<slug>` label. The hub holds the thesis, targets, scout list, candidate testbeds, branching rule, and current direction.

The active portfolio is recorded in `programmes/registry.yml`. Programme hubs are not giant backlogs. Child work is discovered through the programme label and issue links.

A scout lane may begin before a specific bug is known. It must still produce code and test maps, runnable evidence or a feasibility limit, ranked branch candidates, negative results, and a recommendation.

## Target hubs

Each active recurring target may have one long-lived `type:target` issue. The hub holds the plain-language model, target map, change thesis, research surfaces, testbed history, and label searches.

Active hubs are recorded in `targets/hubs.yml`. Do not pin every hub. Discover them through `type:target`, target labels, the hub registry, and the README.

Every related work issue should carry the same `target:<slug>` label. A target hub is an index, not a giant checklist.

## Labels

See `LABELS.md`. Every work item should have:

- exactly one `type:*` label;
- exactly one current `state:*` label;
- a `programme:*` label when it belongs to a long-lived direction;
- one or more `target:*` labels when a recurring system is involved;
- an optional `testbed:*` label only after an owned-repository trial begins;
- optional `needs:*`, `parallel-safe`, or policy labels.

Issue forms apply the initial type and state automatically. Agents add programme, target, and testbed labels when known.

## What to work on

A worker should select work in this order:

1. an explicitly assigned scout, batch probe, or campaign lane;
2. an unclaimed `state:ready` scout in an active programme;
3. an unclaimed `state:ready` lane inside an active campaign;
4. a requested synthesis or decision;
5. a lead the user explicitly asked to triage;
6. a bounded code-first exploration explicitly assigned against a target.

Never treat programme, target, or testbed registries as automatic permission to work or contact upstream.

## Source of truth

- **Programme hub** — direction, target set, scouts, and branching rule.
- **Programme registry** — stable programme IDs and live scout index.
- **Target hub** — stable orientation, change thesis, and discovery links.
- **Issue** — current owner, state, blockers, dependencies, and completion signal.
- **Batch manifest** — temporary dispatched assignment identities and owned paths.
- **Campaign `STATUS.md`** — durable campaign snapshot and identifiers.
- **Scout, lane, or batch result** — evidence and conclusion owned by one worker.
- **Integration trial** — realistic use in an owned repository.
- **Synthesis** — interpretation across assignments.
- **Ledgers** — final normalized outcomes, not active task management.

## Useful searches

```text
is:open label:"type:programme"
is:open label:"programme:sdk-integration-lifecycle"
is:open label:"programme:agent-cli-execution" label:"type:lane" label:"state:ready"
is:open label:"programme:web-tooling-runtime-correctness" label:"type:lane" label:"state:ready"
is:open label:"programme:data-durable-workflows" label:"type:lane" label:"state:ready"
is:open label:"type:target"
is:open label:"target:vercel-ai"
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

- One worker claims one primary scout or coordinated lane at a time unless assignments are explicitly coupled.
- Tiny independent probes may run concurrently when each has an immutable output path.
- One integration trial branch has one owner.
- A programme may have many active scouts when each question is distinct and synthesis capacity exists.
- A campaign should have no more active lanes than a coordinator can review and synthesise.
- A batch should declare a maximum useful concurrency.
- New scouts or lanes require a distinct question, deliverable, or evidence type.
- Duplicate reconnaissance should be merged or stopped quickly.
