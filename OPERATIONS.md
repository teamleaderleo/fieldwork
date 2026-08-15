# Operations

## Live and durable records

GitHub issues are the live queue. Batch, campaign, lane, and result files are the durable evidence record. Follow `WORKBOARD.md`, `BATCHES.md`, and `COORDINATION.md` for parallel work and handoffs.

## Work hierarchy

- A **finding** preserves an observation.
- A **lead** awaits triage.
- A **batch** dispatches many bounded assignments.
- A **campaign** owns one substantive bounded parent question.
- A **lane** owns one coordinated research unit inside a campaign.
- A **probe** is a one-shot assignment inside a batch and normally has no issue.
- A **decision** requests human or coordinator judgement.
- A **synthesis** reconciles accepted results.

## Intake

A lead can enter Fieldwork when it comes from:

- a problem blocking or degrading one of our projects;
- repeated friction across several projects;
- a security, correctness, or interoperability concern;
- a technical question worth answering independently of a patch;
- an upstream request that overlaps our interests;
- a broader research programme already active here;
- a user-directed survey across public repositories.

A famous repository with an available issue is not, by itself, a lead.

## Triage

Score a lead informally across five dimensions:

1. **Intrinsic value** — would the result still matter without recognition?
2. **Reuse** — can the result improve our own work or several external users?
3. **Evidence access** — can the claim be reproduced and tested responsibly?
4. **Upstream viability** — is the project active, governed, and open to the kind of change proposed?
5. **Boundedness** — can useful progress be made without an open-ended research commitment?

Prefer strong intrinsic value and evidence access. Visibility is a secondary multiplier.

## Activation

A campaign becomes active only when it has one falsifiable question, intrinsic value, scope, non-goals, a coordinator, stop conditions, a parent issue, and a durable directory.

A batch becomes active only when it has one purpose, a coordinator, a pruned assignment set, unique owned paths, a declared concurrency limit, stop conditions, a parent issue, and a durable manifest.

Parallel lanes are created only after a parent campaign identifies distinct deliverables. Tiny one-shot checks remain probes until coordination is actually needed.

## Time boundaries

Before human maintainer direction exists, cap speculative implementation. Spend enough time to produce a credible reproduction and proposal, then pause when acceptance depends on upstream design choices.

Third-party upstream repositories are read-only to Fieldwork agents by default. An automated interaction requires a live human `upstream greenlight` for the current repository and specific interaction under `AGENTS.md`. Keep existing human-performed or greenlit maintainer interactions few enough to answer promptly and responsibly.

## States

Use the exact state tokens and labels in `LABELS.md`. Workers report transitions; coordinators replace the current state label after accepting them.

Probe-only manifests may temporarily use `needs-decision` before promotion to a decision issue.

## Stop conditions

Stop or pause when:

- the hypothesis is disproved;
- the project explicitly rejects the direction;
- the work requires access or data we do not have;
- expected benefit no longer justifies the verification cost;
- scope expands beyond the assigned question;
- another contributor has already solved the problem;
- the work becomes detached from anything we value;
- safe testing is unavailable;
- a batch cell duplicates another assignment;
- the coordinator cannot realistically review the active fan-out.

## Fork conventions

- Name branches after the batch, campaign, lane, and bounded outcome where practical.
- Record upstream base revision in the durable result.
- Avoid long-lived forks that silently diverge.
- Keep independent experiments in Fieldwork; keep candidate upstream modifications in an owned fork.
- Delete or archive superseded branches only after recording the relevant revision.

Third-party upstream repositories themselves remain read-only to agents and automated workers by default. A bounded greenlit interaction is the sole automated-write exception under `AGENTS.md`.

## Review cadence

Review active batches and campaigns for:

- new evidence;
- feedback from existing human-performed or greenlit upstream interactions, when any exist;
- stale assumptions caused by target changes;
- excessive scope or duplicate work;
- assignments ready for synthesis;
- decisions awaiting human judgement;
- abandoned claims;
- leads that should be closed rather than carried indefinitely.

## Metrics

Metrics describe the work; they do not become quotas. Useful measures include:

- time from observation to reproduction;
- time spent before an upstream submission, when one occurs;
- review iterations;
- maintainer questions answered by the initial packet;
- accepted, declined, withdrawn, and negative outcomes of human-performed or greenlit submissions;
- reused fixtures, tests, or methods;
- defects caught before submission;
- dispatched assignments versus accepted results;
- duplication caught before dispatch;
- coordinator review load and synthesis backlog.