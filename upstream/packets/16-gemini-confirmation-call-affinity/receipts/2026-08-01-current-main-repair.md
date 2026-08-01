# Unit 16 current-main repair attempts — 2026-08-01

## Scope

Repair the confirmation modification call-affinity candidate on exact public base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`, add a real scheduler-level two-call reverse-order control, run full target validation, and preserve a workflow-free clean source branch. Public upstream interaction remains unauthorized.

## Exact inputs

- predecessor source: `b359ece8a2bd059aef870a084ab9494eff16fa8f`
- current public/fork base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- corrected integration-test provenance: `6804d0b87c196b265c42276f2939573edaf6d89c`
- current clean source: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- canonical source branch: `fix/scheduler-confirmation-call-affinity`
- clean source PR: `teamleaderleo/gemini-cli#24`

## Attempt 1 — transient integration-test generation

- carrier: PR #6
- carrier head: `12e096c7672c86fd45d45f87c6a3324347559d11`
- run/job: `30690542009` / `91344358931`
- completed: checkout, Node `20.19.0`, locked install, predecessor source restore, integration-test generation, Prettier
- failure: pre-commit ESLint rejected unused `AnyToolInvocation` and local `toolRegistry`
- classification: test-harness lint failure before product execution
- product tests/typecheck/preflight/publication: none
- durable review: PR #6 review `4834204326`

## Corrected integration control

- initial committed head: `6804d0b87c196b265c42276f2939573edaf6d89c`
- final source file: `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts` at `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- boundary:
  - real `Scheduler`;
  - real scheduler state manager through Scheduler;
  - real `MessageBus`;
  - two simultaneously `AwaitingApproval` calls;
  - call 2 response delivered before call 1;
  - each modifier input, rebuild, completed result, and argument update required to remain with its correlated call;
  - controlled policy, executor, and modifier; no model or external service.

## Attempt 2 — fallback publisher

- carrier: PR #22
- branch/head: `fieldwork/confirmation-call-affinity-repair-v2` / `e41dd92ab680f5eb05370bf7d5263a70f6897e34`
- run/job: `30690739632` / `91344882192`
- status: remained in hosted-runner queue
- disposition: PR closed superseded after direct source materialization
- product execution: none
- durable review: PR #22 review `4834204972`

## Source materialization

### Staging

The corrected integration branch started from current base and accumulated the exact source/test diff:

- integration test commit: `6804d0b87c196b265c42276f2939573edaf6d89c`
- product source commit: `34d6a647783fe5d3d15273d5bbe801934bd6fec4`
- adjacent fixture commit: `5121459bd1f9c0f8962db15eac68f9566f090c31`
- focused test commit/final staging head: `789d250f72f4b3dc6ee7ac3bc08789ec45f28e01`

### Squash

Internal source composition PR #23 targeted `repair/16-confirmation-call-affinity-current-main` and squash-merged the four-file diff.

- source composition PR: `teamleaderleo/gemini-cli#23`
- base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- staging head: `789d250f72f4b3dc6ee7ac3bc08789ec45f28e01`
- squash result: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- relationship: one commit ahead, zero behind
- exact files:
  - `packages/core/src/scheduler/confirmation.ts`
  - `packages/core/src/scheduler/confirmation.affinity.repair.test.ts`
  - `packages/core/src/scheduler/confirmation.test.ts`
  - `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts`
- additions/deletions: 778 / 20
- workflow, dependency, snapshot, generated, or Fieldwork files: none

The canonical branch was force-updated to this exact source. Clean review PR #24 exposes the one-commit diff.

## Attempt 3 — immutable source on Ubuntu 24.04

- carrier: PR #6
- carrier head: `5daf74fccef0fda01ca75f5ef17254102cb2d64e`
- run/job: `30691280000` / `91346341184`
- behavior: checkout source `0c3a86b` directly, verify parent/fence, install, format check, focused tests, core typecheck, full preflight, clean tree, canonical push
- status: remained queued without acquiring a runner
- disposition: superseded by the same immutable-source gate on Ubuntu 22.04

## Attempt 4 — active immutable source gate

- carrier: PR #6
- carrier head: `51fb36c0c2c7bceb4c954acf918c82c9b966ed4f`
- run/job: `30691565496` / `91347102291`
- runner request: Ubuntu 22.04
- runtime request: Node `20.19.0`
- exact source: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- gates:
  1. exact source head and parent;
  2. exact four-file fence and diff check;
  3. locked install;
  4. Prettier check on four files;
  5. focused/real-scheduler/adjacent Vitest command;
  6. core typecheck;
  7. full `npm run preflight`;
  8. clean tracked tree;
  9. canonical source branch push and runtime receipt.
- current status at this receipt revision: hosted-runner queue

## Execution commands

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/scheduler.confirmation-affinity.test.ts \
  src/scheduler/confirmation.test.ts

npm run typecheck --workspace @google/gemini-cli-core
npm run preflight
```

## Continuation

Classify attempt 4 by its first failing gate or retain its complete green receipt. When complete, update exact test counts, preflight output, runtime versions, source/packet heads, packet PR #443, carrier #6, clean source PR #24, and parent issue #435. No public upstream action is permitted without explicit authority.
