# Coordination

Fieldwork supports multiple campaigns, multiple lanes within a campaign, and multiple workers inside one lane only when ownership remains explicit.

## Unit hierarchy

```text
programme or target
└── campaign: one bounded parent question
    ├── lane: independently owned research unit
    ├── lane: independently owned research unit
    ├── decision: coordinator or human choice
    └── synthesis: campaign-level interpretation
```

A campaign has one parent issue and one durable campaign directory. Each lane has one issue and one lane-owned directory.

## Directory convention

```text
campaigns/<campaign-id>-<slug>/
├── STATUS.md
├── question.md
├── lanes/
│   ├── <lane-id>-<slug>/
│   │   ├── report.md
│   │   └── artifacts/
│   └── ...
├── synthesis.md
├── decision.md
└── closeout.md
```

Only the coordinator edits `STATUS.md`, `synthesis.md`, `decision.md`, and `closeout.md`. Lane workers edit only their lane directories unless a handoff explicitly changes ownership.

## Good lane boundaries

Split work by independently answerable question or evidence type, for example:

- source and execution-path map;
- minimal reproduction;
- prior issues, changes, and policy research;
- competing hypotheses;
- compatibility matrix;
- security analysis;
- performance experiment;
- test strategy;
- alternative implementation directions.

Do not split work merely by arbitrary file ranges when the workers would need to reconstruct the same context.

## Claim protocol

Before substantial work, the worker records:

- worker identity;
- state `claimed`;
- exact lane question;
- expected deliverable;
- owned paths;
- dependencies;
- target source revision;
- stop condition.

A claim is a coordination lease, not ownership of the broader campaign. If the worker disappears or the premise changes, the coordinator may release or replace it.

## Communication protocol

Use the lane issue for short state changes, blockers, questions, and handoff notices. Put evidence and reasoning in repository files.

Do not rely on ephemeral chat history as the only location of a decision or result.

When new evidence changes another lane's premise, post a concise cross-lane note in both relevant Fieldwork issues. Use same-repository references directly; keep external references wrapped.

## Handoff protocol

A handoff must state:

1. what was asked;
2. what was examined and at which revisions;
3. the strongest supported finding;
4. retained artifacts and their paths;
5. failed hypotheses and negative results;
6. unresolved uncertainty;
7. blockers or dependencies;
8. the exact next decision or action;
9. whether upstream contact remains unauthorized.

Use `templates/handoff.md` and the `FIELDWORK HANDOFF` completion comment from `START_HERE.md`.

## Synthesis protocol

The synthesiser reads merged lane reports, reconciles contradictions, identifies shared assumptions, and distinguishes:

- established findings;
- plausible but unconfirmed interpretations;
- disagreements between lanes;
- missing evidence;
- decisions that require human judgement.

Synthesis never silently upgrades a hypothesis into a fact. It cites the lane and artifact supporting every consequential conclusion.

## Completion protocol

A lane reaches `ready-for-synthesis` when its report and artifacts are durable. The coordinator then accepts, requests revision, or records a negative result.

A campaign reaches `complete` only after:

- all active lanes have an outcome;
- synthesis exists or is explicitly unnecessary;
- the decision gate is recorded;
- upstream status is accurate;
- ledgers and closeout are updated.

## Conflict protocol

When two workers overlap:

1. stop edits to shared files;
2. retain both evidence sets;
3. identify the narrower ownership boundary;
4. choose one synthesiser for the disputed conclusion;
5. record the resolution in the parent campaign.

Do not resolve conflicts by silently deleting another worker's evidence.

## Future automation boundary

A future coordinator may automate claims, state transitions, reminders, and synthesis queues. The durable contract is deliberately simple: issue identifiers, exact state tokens, owned paths, machine-readable ledgers, and explicit handoff blocks.
