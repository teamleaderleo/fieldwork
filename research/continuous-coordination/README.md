# Continuous coordination

This research seed studies whether distributed project coordination can be evaluated like an incremental build while preserving human judgement, evidence classes, repository independence, and explicit authority.

## Current artifacts

- [`landscape-2026-07-30.md`](landscape-2026-07-30.md) — research synthesis, design decisions, rejected shortcuts, architecture, CI topology, and implementation sequence.
- [`operational-lessons-2026-07-30.md`](operational-lessons-2026-07-30.md) — release engineering, cache reliability, shadow evaluation, canarying, postmortems, and operational conditions.
- [`source-map.yml`](source-map.yml) — machine-readable source, concept, and adopt/adapt/reject map.

## Live coordination

- Fieldwork issue [#138](https://github.com/teamleaderleo/fieldwork/issues/138) owns the strict research and CI dogfood contract.
- Stensibly issue [`teamleaderleo/stensibly#566`](https://github.com/teamleaderleo/stensibly/issues/566) owns the reusable product and evaluator architecture.
- Fieldwork PR [#105](https://github.com/teamleaderleo/fieldwork/pull/105) provides the first human and machine review-queue seed.

## Current recommendation

Proceed with a read-only coordination compiler before any automatic assignment, dispatch, issue mutation, merge, deployment, or upstream contact.

The first proof should generate the human review queue and normalized graph from one source, preserve evidence classes, calculate affected descendants, explain invalidation, and match a clean rebuild.

Treat cache reuse and evaluator rollout as correctness-sensitive operations: support clean rebuilds, shadow comparison, explicit cache conditions, and regression fixtures for every consequential invalidation mistake.

Upstream contact authorized: `false`.
