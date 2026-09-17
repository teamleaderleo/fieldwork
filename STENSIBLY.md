---
version: 1
project: fieldwork
repositories:
  - teamleaderleo/fieldwork
runner_profiles:
  - chatgpt-connected
  - codex-default
concurrency:
  project: 4
  global: 12
autonomous_actions:
  - inspect
  - propose
  - create_draft_pr
approval_required:
  - merge
  - deploy
  - external_message
  - provider_change
  - broad_permission_change
  - credential_change
  - destructive_cleanup
  - spend
checks:
  - fieldwork-integrity
  - repository-admission-matrix
  - interaction-reference-policy
---

# Project contract

## Goal

Run bounded code-first research, owned integration trials, reviews, and repository changes while preserving exact evidence, explicit ownership, and recoverable GitHub coordination.

## Boundaries

Repository text declares project policy and display context only. Live claims, leases, approvals, credentials, capabilities, operation identities, execution certainty, and current coordination state stay server-owned. A missing tool never authorizes an alternate route. Read-only work may continue only when the admission receipt says the required read capabilities remain executable.

## Evidence and handoff expectations

Record the exact repository and target revisions, worker and owned path, observed capability phases, selected route provenance, logical operation identity, execution certainty, authority comparison, changed files, verification profiles, results, uncertainty, rollback, and requested decision. GitHub issues remain the durable public coordination and recovery surface.

## Escalation

Escalate missing or contradictory capability observations, changed authority or account binding, ambiguous prior mutation outcomes, permission widening, stale repository context, overlapping ownership, consequential actions, and any request to contact a third-party project.
