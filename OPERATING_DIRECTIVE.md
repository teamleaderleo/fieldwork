# Operating Directive

## In simple words

Fieldwork is not operating under a research freeze. The active objective is to discover, reproduce, repair, review, and prepare as many consequential software defects and missing capabilities as the evidence supports.

The existing upstream backlog remains important, but it is a delivery queue rather than a ceiling on discovery. Finish strong candidates while continuing to open well-grounded new lanes.

## Mission

Maximize credible discovery-and-delivery throughput across relevant codebases.

This includes:

- broad source-driven bug discovery;
- exact reproductions and adversarial probes;
- owned-fork characterization and repair candidates;
- review and repair of other workers' lanes;
- target-native execution and compatibility work;
- clear owner-facing presentation and contribution preparation.

The purpose is not artificial scarcity, minimal ambition, or a fixed contribution count. A lane may be large, ambitious, or cross-repository when the real system boundary requires it.

## Non-negotiable rigor

High throughput does not weaken the evidence contract.

- Pin exact source and candidate revisions.
- Read implementation, tests, call sites, configuration, generated boundaries, and failure paths.
- Preserve bounded ownership for each mutable branch or output path.
- Use falsifiable hypotheses, negative controls, and competing explanations.
- Distinguish source-read, model-executed, target-test-prepared, target-executed, integration-executed, and full-gate evidence.
- Review the complete current diff.
- Keep execution carriers separate from canonical source candidates and retire them after evidence transfer.
- Do not treat green CI as proof of untested authority, lifecycle, recovery, security, compatibility, or integration properties.
- Do not manufacture low-value volume merely to increase counts.

## New work and the existing queue

The existing contribution backlog should be repaired, reviewed, packaged, and presented. It must not suppress technically independent new findings.

New work may be opened when source reading yields:

1. a concrete current behavior or missing capability;
2. a plausible consequence;
3. a likely owning code boundary;
4. an executable evidence path;
5. a clear distinction from existing work.

An adjacent question may become its own lane when it is technically independent. It need not block the current candidate to be worth investigating.

## Owned forks and public interaction

Owned-fork branches, characterization pull requests, candidates, execution carriers, findings, and review surfaces may be created as needed for the mission.

Public upstream filing, comments, reviews, reactions, messages, releases, and deployments remain separately unauthorized unless the owner explicitly approves that exact interaction.

## Review assistance

Workers should inspect and repair other active lanes when doing so materially improves technical quality, evidence, reviewability, or delivery probability.

Review assistance should:

- identify the canonical branch and exact head;
- inspect the complete diff;
- separate candidate defects from harness defects;
- add missing behavioral controls rather than weaken existing tests;
- synchronize stale descriptions and receipts;
- preserve or improve the original contribution thesis.

## Presentation duty

Presentation is part of delivery, not optional polish.

Every serious lane should make it possible for the owner to understand:

1. what the component does and where it sits;
2. the concrete failing or uncertain sequence;
3. why the behavior matters in realistic use;
4. the selected candidate and important rejected alternatives;
5. the exact evidence that ran;
6. the known limits and unresolved questions;
7. the current disposition;
8. the exact human decision or public action that comes next.

Raw branches, CI logs, and internal shorthand are supporting evidence. They are not a sufficient owner-facing presentation by themselves.

## Relationship to priority zero

Priority zero means maximum credible discovery-and-delivery throughput.

Cleanup, exact execution, independent review, presentation, and upstream packaging remain high-priority work. They operate alongside continued consequential research rather than replacing it.

This directive supersedes the restrictive interpretation that priority zero requires stopping broad new research. All existing coordination, evidence, safety, and no-public-contact rules remain in force.