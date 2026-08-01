# Unit 16 current-main repair attempts — 2026-08-01

## Scope

Repair the confirmation modification call-affinity candidate on exact public base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`, add a real scheduler-level two-call out-of-order control, run full target validation, and publish a workflow-free clean source branch. Public upstream interaction remains unauthorized.

## Exact inputs

- reviewed predecessor source: `teamleaderleo/gemini-cli@b359ece8a2bd059aef870a084ab9494eff16fa8f`
- current public/fork base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- canonical source destination: `fix/scheduler-confirmation-call-affinity`

## Attempt 1 — PR #6

- carrier branch: `fieldwork/confirmation-call-affinity-repair`
- carrier head: `12e096c7672c86fd45d45f87c6a3324347559d11`
- run/job: `30690542009` / `91344358931`
- completed: checkout, Node `20.19.0`, locked install, predecessor source restore, integration-test generation, Prettier
- failure: pre-commit ESLint rejected two unused declarations in the generated integration test: `AnyToolInvocation` and local `toolRegistry`
- classification: test-harness lint failure before product execution
- product tests executed: none
- typecheck/preflight/publication executed: none
- durable review record: PR #6 review `4834204326`

## Corrected integration control

- branch: `fieldwork/confirmation-call-affinity-integration-test`
- exact head: `6804d0b87c196b265c42276f2939573edaf6d89c`
- file: `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts`
- boundary:
  - real `Scheduler`
  - real `SchedulerStateManager` through the scheduler
  - real `MessageBus`
  - two simultaneously `AwaitingApproval` calls
  - response for `call-2` delivered before `call-1`
  - each modifier input, rebuilt invocation, completed result, and updated arguments required to remain with the correlated call
  - executor and modifier are controlled fakes; no model or external service

## Attempt 2 — PR #22

- carrier branch: `fieldwork/confirmation-call-affinity-repair-v2`
- carrier head: `e41dd92ab680f5eb05370bf7d5263a70f6897e34`
- run/job: `30690739632` / `91344882192`
- exact inputs: current base `f47d6c6...`, predecessor source `b359ece8...`, corrected integration test `6804d0b8...`
- intended clean source fence:
  - `packages/core/src/scheduler/confirmation.ts`
  - `packages/core/src/scheduler/confirmation.affinity.repair.test.ts`
  - `packages/core/src/scheduler/confirmation.test.ts`
  - `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts`
- gates: staged Prettier/ESLint, focused and adjacent Vitest files, core typecheck, full `npm run preflight`, exact-parent and four-file checks, clean tracked tree, clean source publication
- current status at this receipt revision: hosted-runner queue; no source step started
- durable review record: PR #22 review `4834204972`

## Continuation

Classify attempt 2 by its first failing gate or, when green, record the exact published source head, focused test count, preflight result, runtime versions, and complete four-file compare. Then synchronize packet files, packet PR #443, target carrier records, and parent issue #435.
