# Batch Research Protocol

A **batch** is a controlled dispatch envelope for researching many targets, questions, methods, or context dimensions at once. It makes fan-out observable and recoverable without creating hundreds of unrelated issues.

## When to use a batch

Use a batch for work such as:

- comparing the same behaviour across many repositories;
- surveying several ecosystems under one research question;
- applying several research methods to one target;
- mapping mechanism, usage, standards, operations, and adversarial context separately;
- running a bounded repository × question × method matrix;
- delegating enough work that stable assignment IDs and synthesis are required.

Do not create a batch for one ordinary campaign or one small finding.

## Do not blindly materialize a Cartesian product

A coordinator may begin with dimensions such as targets, questions, methods, and context lenses, but must prune the matrix before dispatch. Remove cells that are duplicates, impossible to verify, irrelevant, dependent on the same unresolved premise, too broad for one worker, or unlikely to produce useful evidence.

The manifest records dispatched assignments, not every mathematically possible combination.

## Unit model

```text
batch
├── campaign — substantive parent question requiring coordination
│   ├── mechanism lane
│   ├── usage or integration lane
│   ├── contract or standards lane
│   ├── operations lane
│   ├── adversarial lane
│   └── probe — optional one-shot bounded check
└── probe — one-shot assignment that may be promoted later
```

These lane names are available patterns, not a requirement to create all five.

A **probe** is a small one-worker assignment with no shared edits and no need for its own issue. It writes one result file and reports completion to the batch issue.

Promote a probe to a finding, context dossier, campaign, lane, or decision when it develops dependencies, broader claims, unresolved scope, sustained work, or a need for separate coordination.

## Directory convention

```text
batches/BYYYYMMDD-NNN-slug/
├── manifest.json
├── STATUS.md
├── results/
│   ├── A001.md
│   └── ...
├── contexts/
│   └── optional-draft-or-synthesis.md
├── synthesis.md
└── closeout.md
```

The coordinator owns `manifest.json`, `STATUS.md`, shared context synthesis, `synthesis.md`, and `closeout.md`. Each worker owns only the result path assigned in the manifest.

## Assignment contract

Every assignment includes:

- unique assignment ID;
- target and exact source revision or retrieval boundary;
- one concrete question;
- method or context lens;
- intended claim scope;
- expected deliverable;
- owned output path;
- dependencies;
- state;
- stop condition;
- upstream-contact authorization: `false`.

For agents and automated workers, upstream-contact authorization remains `false` because it records standing authority. A campaign decision or coordinator cannot authorize upstream contact. Record any bounded human greenlight and its consumed interaction separately under `AGENTS.md`.

For citation or context assignments, also include:

- preferred primary-source types;
- exact claim to support or falsify;
- evidence labels allowed;
- integration-context path or synthesis destination.

Use `templates/batch-manifest.json` and `INTEGRATION_CONTEXT.md`.

## Context fan-out

When a small code result needs wider interpretation, a coordinator may dispatch independent assignments for:

1. **Mechanism** — source path and local behaviour.
2. **Usage** — actual callers, examples, dependants, and deployed workflows.
3. **Contract** — standards, API guarantees, protocol semantics, and compatibility promises.
4. **Operations** — retries, timeouts, recovery, observability, persistence, and concurrency.
5. **Adversarial** — malformed inputs, partial failure, abuse, security, and resource pressure.
6. **Synthesis** — determine which broader claims are documented, observed, inferred, illustrative, unknown, or contradicted.

Each assignment should answer one evidence question. Do not ask every worker for a complete architecture essay.

## Dispatch protocol

Before fan-out, the coordinator:

1. states the purpose and exclusions;
2. states the intended claim scope;
3. creates one batch issue;
4. creates the durable batch directory and manifest;
5. deduplicates assignments;
6. assigns unique output paths;
7. identifies dependencies and shared assumptions;
8. chooses a maximum useful concurrency;
9. confirms that automated third-party upstream contact is prohibited;
10. dispatches immutable assignment packets.

Workers do not expand their assignment into additional repositories, claims, or questions without reporting the proposed expansion.

## Completion protocol

A worker completes an assignment with:

- the assigned result file or a full issue handoff;
- exact revisions and retrieval dates;
- strongest supported finding;
- evidence labels and primary sources;
- evidence and reproduction details;
- claim scope actually supported;
- integration-context relationship where relevant;
- uncertainty, alternative architectures, and negative results;
- dependencies discovered;
- a final state: `complete`, `blocked`, `negative-result`, or `needs-decision`.

Workers do not edit the shared manifest to mark themselves complete. The coordinator updates shared state after accepting the handoff.

## Synthesis rule

The coordinator must keep these categories separate:

- demonstrated mechanism behaviour;
- documented real use;
- observed integration behaviour;
- inference from sources or experiments;
- illustrative examples;
- unknown or contradicted claims.

A synthesis may conclude that an isolated bug is real while its supposed wider impact remains unsupported.

## Write modes under high concurrency

- Use separate Fieldwork branches or PRs for substantial lanes.
- Bundle several tiny probe results into one coordinator PR when issue-only handoffs are adequate.
- Avoid one PR per trivial observation.
- Never allow several workers to update one shared status or context file concurrently.
- Never use an external upstream repository as the coordination surface.
- Never mutate a third-party upstream repository from a worker or coordinator automation path.

## Future automation

Ostensibly or another coordinator may later generate assignments, claims, reminders, citation queues, and synthesis queues. It may not automate any mutation of a third-party upstream repository. The durable interface is intentionally simple: JSON manifests, stable IDs, issue numbers, exact state tokens, claim scopes, evidence labels, owned paths, and explicit handoff blocks.
