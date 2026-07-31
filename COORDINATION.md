# Coordination

Fieldwork supports long-lived programmes, batches, multiple campaigns, multiple lanes within a campaign, and many one-shot probes when ownership remains explicit.

## Unit hierarchy

```text
programme: long-lived research direction
├── scout lane: bounded reconnaissance on one target or boundary
│   ├── finding: concrete observation
│   └── campaign: one bounded parent question promoted from evidence
│       ├── lane: coordinated independently owned unit
│       ├── probe: one-shot bounded check
│       ├── decision: coordinator or human choice
│       └── synthesis: campaign-level interpretation
└── programme synthesis: cross-target interpretation and next branches

batch: temporary dispatch envelope
├── campaign
├── probe
└── synthesis
```

A programme has one hub issue and a durable registry entry. A batch has one parent issue and one durable manifest. A campaign has one parent issue and one durable campaign directory. A coordinated lane has one issue and one lane-owned directory. A tiny probe may exist only in the batch manifest, one owned result file, and a handoff to the batch issue.

## Programme scouts

A scout lane maps the lay of the land without pretending a specific bug or change is already known. It must still answer a bounded question and produce more than a repository summary.

A scout should deliver:

- an `In simple words` explanation;
- exact revision and code map;
- entrypoints, state ownership, side effects, failure paths, contracts, and test boundaries;
- recent change and issue context where useful;
- a runnable probe, adversarial case, or realistic testbed scenario when feasible;
- ranked branch candidates with consequences and evidence needs;
- negative results and dead ends;
- a recommendation to stop, retain a finding, open a campaign, or dispatch another scout.

A scout may spawn several child campaigns when the questions are genuinely independent. The programme coordinator approves branching and prevents duplicate premises.

## Ownership convention

```text
programmes/<programme-id>/
├── STATUS.md              # coordinator only
├── scouts/
│   ├── <scout-id>/
│   │   ├── report.md      # scout owner only
│   │   └── artifacts/
│   └── ...
└── synthesis.md           # coordinator only

batches/<batch-id>-<slug>/
├── manifest.json          # coordinator only
├── STATUS.md              # coordinator only
├── results/
│   ├── A001.md            # assignment A001 only
│   └── ...
├── synthesis.md           # coordinator only
└── closeout.md            # coordinator only

campaigns/<campaign-id>-<slug>/
├── STATUS.md              # coordinator only
├── question.md
├── lanes/
│   ├── <lane-id>-<slug>/
│   │   ├── report.md      # lane owner only
│   │   └── artifacts/
│   └── ...
├── synthesis.md           # coordinator only
├── decision.md            # coordinator only
└── closeout.md            # coordinator only
```

Workers edit only their owned scout, result, experiment, or lane paths unless a handoff explicitly changes ownership. Never have several workers push shared files directly to `main`.

## Local improvement default

Problem ownership is non-exclusive. Any worker may inspect, review, reproduce, or improve work across programmes while one active writer lease remains authoritative for each mutable branch or output path.

When a worker encounters a concrete nearby defect, stale claim, weak assertion, missing regression, untransferred receipt, obsolete temporary workflow, or duplicate carrier, the default is to repair it in the same pass when:

- the repair is bounded and technically understood;
- the worker owns the artifact, the lease has transferred or expired, or the repair is made through a separate stacked branch or evidence record;
- validation is available without widening authority, using prohibited data, or erasing another worker's evidence;
- the repair materially improves the next transition.

A review comment alone is not the preferred endpoint when the reviewer can safely produce the bounded repair without violating the writer lease. When direct repair would conflict with an active writer, retain an exact repair recipe, focused regression, or non-conflicting stack instead of silently rewriting that worker's branch.

Service nearby work before creating distant coordination surfaces unless the marginal value of exploration is clearly higher. The normal order is:

1. repair concrete defects already in reach;
2. compose overlapping work and finish exact-head gates;
3. synchronize findings, receipts, descriptions, and state;
4. retire superseded carriers and temporary machinery;
5. obtain or perform independent complete-diff review;
6. explore new questions when nearby work is stable, genuinely blocked, or lower value.

This is a throughput heuristic, not a ban on exploration. A fresh investigation is appropriate when it can expose a high-consequence mechanism, unblock several lanes, or progress without consuming a saturated shared bottleneck.

## Good lane boundaries

Split work by independently answerable question or evidence type, for example:

- source and execution-path map;
- realistic usage or integration trial;
- minimal reproduction;
- prior issues, changes, and policy research;
- competing hypotheses;
- compatibility matrix;
- security analysis;
- performance experiment;
- test strategy;
- alternative implementation directions.

Do not split work by arbitrary file ranges when every worker would need to reconstruct the same context.

## Probe boundary

Use a probe when the work:

- is answerable in one bounded pass;
- has no shared edits;
- has one result path;
- has no unresolved design dependency;
- can be accepted or rejected by the batch or programme coordinator without separate discussion.

Promote a probe when scope expands, another worker depends on it, it needs a sustained conversation, or its result becomes a substantive campaign.

## Claim protocol

Before substantial coordinated work, the worker records:

- worker identity;
- state `claimed`;
- programme, target hub, and parent issue;
- exact assignment question;
- expected deliverable;
- owned path;
- dependencies;
- target source revision or retrieval boundary;
- stop condition;
- upstream-contact authorization, normally `false`.

A claim is a coordination lease, not ownership of the broader programme, campaign, or batch. If the worker disappears or the premise changes, the coordinator may release or replace it.

## Communication protocol

Use the relevant Fieldwork issue for short state changes, blockers, questions, and handoff notices. Put evidence and reasoning in repository files.

Do not rely on ephemeral chat history as the only location of a decision or result.

When new evidence changes another assignment's premise, post a concise cross-assignment note in both relevant Fieldwork records. Same-repository references may be direct; external references remain wrapped.

Routine peer-review routing, safe bounded repair, cleanup, source synchronization, and ordinary technical comparison are autonomous work. Do not turn them into user tasks merely because several agents, repositories, or alternatives are involved. Escalate only when the next transition requires human authority, private or regulated context, credentials, material spending, acceptable irreversible risk, or product values unavailable from repository evidence.

## Handoff protocol

A handoff must state:

1. what was asked;
2. what was examined and at which revisions;
3. the strongest supported finding;
4. retained artifacts and paths;
5. failed hypotheses and negative results;
6. unresolved uncertainty;
7. blockers or dependencies;
8. exact branch candidates or next decision;
9. whether upstream contact remains unauthorized.

Use `templates/handoff.md` and the `FIELDWORK HANDOFF` block from `START_HERE.md`.

## Synthesis protocol

The synthesiser reads accepted result files and lane reports, reconciles contradictions, identifies shared assumptions, and distinguishes:

- established findings;
- plausible but unconfirmed interpretations;
- disagreements between assignments;
- missing evidence;
- campaign candidates;
- decisions requiring human judgement.

Synthesis never silently upgrades a hypothesis into a fact. It identifies the result and artifact supporting every consequential conclusion.

## Completion protocol

A scout, lane, or probe reaches a completed handoff state when its report and artifacts are durable or explicitly queued for materialization. The coordinator accepts, requests revision, promotes, or records a negative result.

A campaign or batch reaches `complete` only after:

- every dispatched active assignment has an outcome;
- synthesis exists or is explicitly unnecessary;
- the decision gate is recorded;
- upstream status is accurate;
- ledgers and closeout are updated.

A programme remains open while its direction is useful. It may become dormant even when completed campaigns remain valuable.

## Conflict protocol

When two workers overlap:

1. stop edits to shared files;
2. retain both evidence sets;
3. identify the narrower ownership boundary;
4. choose one synthesiser for the disputed conclusion;
5. record the resolution in the parent programme, campaign, or batch.

Do not resolve conflicts by silently deleting another worker's evidence.

## High-volume write modes

- **Fieldwork PR:** preferred for a substantial scout, lane, or coherent result set.
- **Issue-only handoff:** allowed when repository writes are unavailable; apply `needs:materialization`.
- **Coordinator bundle:** combines several tiny probe handoffs into one durable change.

Avoid one PR per trivial observation and avoid one giant PR containing unrelated lanes.

## Future automation boundary

A future coordinator may automate dispatch, claims, state transitions, reminders, and synthesis queues. The durable contract is deliberately simple: stable identifiers, exact state tokens, JSON registries and manifests, owned paths, issue numbers, and explicit handoff blocks.
