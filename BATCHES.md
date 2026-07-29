# Batch Research Protocol

A **batch** is a controlled dispatch envelope for researching many targets, questions, or methods at once. It makes fan-out observable and recoverable without creating hundreds of unrelated issues.

## When to use a batch

Use a batch for work such as:

- comparing the same behaviour across many repositories;
- surveying several ecosystems under one research question;
- applying several research methods to one target;
- running a bounded repository × question × method matrix;
- delegating enough work that stable assignment IDs and synthesis are required.

Do not create a batch for one ordinary campaign or one small finding.

## Do not blindly materialize a Cartesian product

A coordinator may begin with dimensions such as targets, questions, and methods, but must prune the matrix before dispatch. Remove cells that are duplicates, impossible to verify, irrelevant, dependent on the same unresolved premise, too broad for one worker, or unlikely to produce useful evidence.

The manifest records dispatched assignments, not every mathematically possible combination.

## Unit model

```text
batch
├── campaign — substantive parent question requiring coordination
│   ├── lane — independently owned coordinated unit
│   └── probe — optional one-shot bounded check
└── probe — one-shot assignment that may be promoted later
```

A **probe** is a small one-worker assignment with no shared edits and no need for its own issue. It writes one result file and reports completion to the batch issue.

Promote a probe to a finding, campaign, lane, or decision when it develops dependencies, unresolved scope, sustained work, or a need for separate coordination.

## Directory convention

```text
batches/BYYYYMMDD-NNN-slug/
├── manifest.json
├── STATUS.md
├── results/
│   ├── A001.md
│   └── ...
├── synthesis.md
└── closeout.md
```

The coordinator owns `manifest.json`, `STATUS.md`, `synthesis.md`, and `closeout.md`. Each worker owns only the result path assigned in the manifest.

## Assignment contract

Every assignment includes:

- unique assignment ID;
- target and exact source revision or retrieval boundary;
- one concrete question;
- method;
- expected deliverable;
- owned output path;
- dependencies;
- state;
- stop condition;
- upstream-contact authorization, defaulting to `false`.

Use `templates/batch-manifest.json`.

## Dispatch protocol

Before fan-out, the coordinator:

1. states the purpose and exclusions;
2. creates one batch issue;
3. creates the durable batch directory and manifest;
4. deduplicates assignments;
5. assigns unique output paths;
6. identifies dependencies;
7. chooses a maximum useful concurrency;
8. confirms that upstream contact remains unauthorized;
9. dispatches immutable assignment packets.

Workers do not expand their assignment into additional repositories or questions without reporting the proposed expansion.

## Completion protocol

A worker completes an assignment with:

- the assigned result file or a full issue handoff;
- exact revisions and retrieval dates;
- strongest supported finding;
- evidence and reproduction details;
- uncertainty and negative results;
- dependencies discovered;
- a final state: `complete`, `blocked`, `negative-result`, or `needs-decision`.

Workers do not edit the shared manifest to mark themselves complete. The coordinator updates shared state after accepting the handoff.

## Write modes under high concurrency

- Use separate Fieldwork branches or PRs for substantial lanes.
- Bundle several tiny probe results into one coordinator PR when issue-only handoffs are adequate.
- Avoid one PR per trivial observation.
- Never allow several workers to update one shared status file concurrently.
- Never use an external upstream repository as the coordination surface.

## Future automation

Ostensibly or another coordinator may later generate assignments, claims, reminders, and synthesis queues. The durable interface is intentionally simple: JSON manifests, stable IDs, issue numbers, exact state tokens, owned paths, and explicit handoff blocks.
