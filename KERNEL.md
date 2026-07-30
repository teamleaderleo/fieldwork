# Fieldwork Coordination Kernel

Status: draft implementation for #301  
Parent architecture: #300

## In simple words

Read this file for every assignment. Then read only the task profiles named by the dispatch packet and the canonical records for the work.

The kernel contains universal invariants. Profiles contain phase-specific procedure. Target instructions may strengthen these rules but may not weaken authority, privacy, evidence, or safety boundaries.

## Precedence

When instructions disagree, use this order:

1. explicit current user authority and safety boundaries;
2. this kernel;
3. the assignment dispatch packet;
4. named task profiles;
5. target-specific instructions;
6. canonical finding, owning issue, implementation PR, and exact receipts;
7. optional background manuals and historical records.

Do not resolve a contradiction silently. Record the exact conflict in the owning coordination issue and continue only through the narrower safe interpretation.

## Start protocol

1. Read this kernel.
2. Read the dispatch packet.
3. Read only the named profiles.
4. Read the canonical records and current exact heads named by the packet.
5. Search for active branches, carriers, findings, reviews, and writer leases before creating work.
6. Begin the next bounded safe action without waiting for the user when repository evidence resolves the choice.

Do not post an instruction-intake or first-read report unless the read discovers a material contradiction, stale premise, authority defect, or blocker.

## Universal coordination invariants

- A problem space is open to parallel reading, review, reproduction, and unique evidence contributions.
- One mutable branch, shared file, status record, or canonical finding edit has one active writer lease.
- Never force-push or silently rewrite another active worker's branch or artifact.
- Preserve exact repository, branch, source head, base head, retrieval boundary, commands, environments, and receipts.
- Keep canonical source identity separate from execution-carrier identity.
- An execution carrier is temporary evidence machinery, never the merge or upstream candidate.
- Use one preferred source candidate and one active execution carrier per invariant unless the current carrier has a classified defect or materially different execution purpose.
- Queue delay alone is not a reason to create an equivalent carrier.
- Put durable reasoning and evidence in repository files or owning records; chat is never the only record.
- Preserve negative results, rejected alternatives, uncertainty, and reopening triggers.
- No public upstream interaction, merge, release, deployment, production action, private-data use, credential use, or material spending occurs without exact authority.

## Evidence honesty

Every consequence-bearing claim must identify its evidence level and receipt.

Use the narrowest accurate level:

- `source-read`;
- `model-executed`;
- `target-test-prepared`;
- `target-executed`;
- `integration-executed`;
- `full-gate`.

Never describe:

- a prepared test as executed;
- a setup, installation, fixture, harness, timeout, or queue failure as product behavior;
- a focused test as a full gate;
- one platform as cross-platform;
- green CI as proof of an untested authority, security, recovery, or lifecycle property;
- a stale head or reviewed input as current.

## Canonical state

For retained investigations, the canonical finding owns the current technical interpretation. Structured coordination state owns phase, work class, evidence, review disposition, source and carrier identity, freshness, writer lease, authority, blocker, and next transition.

Issues and PR comments carry routing events. They should not duplicate the full evolving report.

Post a global initiative update only when one of these changes materially:

- phase;
- canonical source head;
- active carrier or carrier purpose;
- evidence level or exact receipt;
- selected direction;
- blocker or next transition;
- authority;
- canonical path;
- retirement or supersession.

## Autonomous decisions

Multiple plausible technical approaches are active comparative work, not an automatic human blocker.

Continue through source and precedent research, explicit criteria, concrete alternatives when practical, discriminating execution, and adversarial cross-review. Select the best-supported direction and retain losing reasons and reopening triggers.

Escalate only when the remaining choice depends on authority, private context, material cost, product values absent from repository evidence, irreversible risk, credentials, legal commitment, or an explicitly reserved human decision.

## Completion and handoff

Before ending available work, leave enough durable state for another worker to continue without the chat transcript:

- bounded question and strongest current answer;
- canonical finding or materialization requirement;
- repository, branch, exact source and carrier heads;
- files changed or `none`;
- exact tests, runs, jobs, and outcomes;
- evidence limits and failed hypotheses;
- current phase and review disposition;
- writer-lease state;
- blocker and smallest next action;
- authority state only when changed or exceptional.

A technically useful result may end as selected, review-ready, delivery-gate-ready, land-ready, stopped, or closed. Do not use `ready`, `complete`, or `done` alone.

## Task profiles

Dispatch packets name the profiles that apply:

- `profiles/research.md`;
- `profiles/execute.md`;
- `profiles/review.md`;
- `profiles/coordinate.md`;
- `profiles/integrate.md`;
- `profiles/upstream.md`.

Read deeper manuals only when a profile points to them or the assignment reaches that phase.
