# Tests and receipts — Unit 16 confirmation modification call affinity

## In simple words

The baseline defect reached the exact wrong-call assertion in a target-native run. The predecessor candidate passed six focused authority controls and eight adjacent controls with build, typecheck, formatting, lint, clean fencing, and source publication. The repaired current-main candidate is now one immutable four-file commit and includes the missing real scheduler-level two-call reverse-order test.

The first current-main carrier stopped before product execution at two unused test declarations. That harness issue is corrected and preserved in GitHub. Run `30691280000` owns exact-head focused tests, core typecheck, full preflight, clean-tree verification, and canonical publication.

## Identity

- current public/fork base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- current candidate head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- canonical source branch: `fix/scheduler-confirmation-call-affinity`
- clean review PR: `teamleaderleo/gemini-cli#24`
- active carrier head: `5daf74fccef0fda01ca75f5ef17254102cb2d64e`
- active run/job: `30691280000` / `91346341184`
- current execution environment requested: Ubuntu 24.04, Node `20.19.0`, locked npm dependencies
- predecessor environment: Ubuntu 24.04, Node `v22.23.1`, npm `10.9.8`, Vitest `3.2.4`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Baseline can modify the wrong active call | `target-executed` | PR #2 run `30505534210` | predicted call A versus call B assertion reached | inline harness |
| Inline candidate selects correlated call | `target-executed` | focused repair test 1, run `30595253180` | pass | predecessor base, mocked state |
| Editor candidate selects correlated call | `target-executed` | focused repair test 2 | pass | editor resolution mocked |
| Removal during inline modification cannot publish | `target-executed` | focused test 3 | pass | lookup loss model |
| Status loss during editor modification cannot publish | `target-executed` | focused test 4 | pass | direct status transition |
| Same-ID replacement cannot publish stale output | `target-executed` | focused test 5 | pass | new waiting object/correlation |
| Missing call before modification fails closed | `target-executed` | focused test 6 | pass | direct harness |
| Existing confirmation behavior remains green | `target-executed` | eight adjacent tests | pass | predecessor base |
| Current-main candidate is a clean one-commit four-file diff | `source-read` | compare `f47d6c6...0c3a86b`, PR #24 | confirmed | execution separate |
| Two simultaneous approvals stay isolated under reverse responses | `target-test-prepared` | `scheduler.confirmation-affinity.test.ts` at `0c3a86b` | committed; active run pending | executor/modifier controlled |
| Full current-main repository gate | `execution pending` | run `30691280000` | queued at this revision | hosted runner |

## Baseline characterization

### Command

```text
npm ci
npm run test --workspace @google/gemini-cli-core -- src/scheduler/confirmation.affinity.test.ts
npm run typecheck --workspace @google/gemini-cli-core
```

### Required assertions

- response and update target belong to call B;
- call A remains first active;
- modifier must receive call B and its original arguments;
- no call A lookup can justify selection.

### Result

- run: `30505534210`
- status: expected product failure classified successfully
- observed behavior: modifier received call A; core typecheck passed

## Predecessor candidate execution

### Exact source

`b359ece8a2bd059aef870a084ab9494eff16fa8f`

### Command

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/confirmation.test.ts
```

### Result

- run/job: `30595253180` / `91046140436`
- test files: 2 passed
- tests: 14 passed
- focused: six
- adjacent: eight
- posttest core build: pass
- core typecheck: pass
- Prettier and staged ESLint: pass
- exact three-file fence and clean tree: pass
- source publication: pass

## Current-main candidate composition

### Source history

1. Corrected integration test committed at `6804d0b87c196b265c42276f2939573edaf6d89c`.
2. Source and tests accumulated on `fieldwork/confirmation-call-affinity-integration-test` through head `789d250f72f4b3dc6ee7ac3bc08789ec45f28e01`.
3. Internal PR #23 squash-merged the four-file diff onto current base.
4. Squash result and canonical source: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`.
5. Clean source PR #24 exposes the workflow-free review diff.

### Exact fence

```text
packages/core/src/scheduler/confirmation.affinity.repair.test.ts
packages/core/src/scheduler/confirmation.test.ts
packages/core/src/scheduler/confirmation.ts
packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts
```

### Relationship

- one commit ahead of current base
- zero behind
- no workflow, Fieldwork file, dependency change, snapshot, or generated output

## Scheduler reverse-order control

### Setup

- real `Scheduler`
- real scheduler state manager
- real message bus
- two calls become `AwaitingApproval` simultaneously
- call 2 response arrives first with `two-updated`
- call 1 response arrives second with `one-updated`
- controlled policy, modifier, and executor fakes

### Assertions

- modifier call order is call 2 then call 1;
- modifier inputs carry their own original arguments;
- after the first response, call 2 has updated arguments and call 1 remains waiting;
- final call 1 arguments contain `one-updated` only;
- final call 2 arguments contain `two-updated` only;
- invocation rebuilds receive each call's own updated parameters;
- executor runs twice.

### Current status

Committed at source head; target execution owned by run `30691280000`.

## Current-main repair attempts

### Attempt 1

- PR: #6
- carrier head: `12e096c7672c86fd45d45f87c6a3324347559d11`
- run/job: `30690542009` / `91344358931`
- reached: install, source restore, transient test generation, Prettier
- failure: pre-commit ESLint — unused `AnyToolInvocation` and local `toolRegistry`
- classification: harness lint failure before product execution
- product tests/typecheck/preflight/publication: not run

### Attempt 2

- PR: #22
- carrier head: `e41dd92ab680f5eb05370bf7d5263a70f6897e34`
- run: `30690739632`
- status: queued, then superseded and PR closed after source materialization
- product claim: none

### Attempt 3 — active

- PR: #6
- carrier head: `5daf74fccef0fda01ca75f5ef17254102cb2d64e`
- run/job: `30691280000` / `91346341184`
- behavior: checks out immutable source `0c3a86b` directly
- gates:
  1. exact head, parent, and four-file fence;
  2. locked install;
  3. Prettier check;
  4. three focused/adjacent test files;
  5. core typecheck;
  6. full `npm run preflight`;
  7. clean tracked tree;
  8. canonical source push and runtime receipt.

## Ordinary repository gates

| Gate | Exact command or workflow | Current result |
| --- | --- | --- |
| exact parent/fence | carrier identity step | pending current run; source compare confirmed |
| format | Prettier check on four files | predecessor three files pass; current pending |
| staged lint | pre-commit on source composition history | current integration test corrected after exact lint failure |
| focused tests | three Vitest files | predecessor 14/14 pass; scheduler control pending |
| core typecheck | `npm run typecheck --workspace @google/gemini-cli-core` | predecessor pass; current pending |
| full suite | `npm run preflight` | pending |
| clean tree | `git diff --exit-code` | pending current run |
| platform matrix | Linux | requested current run; macOS/Windows not run |

## Reversing controls

- Baseline wrong-call assertion fails; candidate selection controls pass on predecessor.
- Adjacent confirmation controls pass with a stateful transition fixture.
- Removal, status loss, and generation replacement block `updateArgs`.
- Reverse-order scheduler test requires both calls to retain their own identity and arguments.

## Soak, leak, and cleanup

- soak loop: none
- listener synchronization: message-bus listener/snapshot observation
- process/file resources: no external process in focused scheduler control
- stale update cleanup: represented by removal/status/generation tests
- temporary workflows in canonical source: none
- generated residue: none in source diff

## Platform and integration gaps

- macOS and Windows
- real external editor process lifetime
- TUI/IDE presentation together
- production prevalence

## Cleanup receipt

- canonical source workflow-free: yes
- exact current source branch: yes, `0c3a86b`
- source composition PR: merged and closed
- fallback carrier PR #22: closed superseded
- active temporary machinery: PR #6 workflow; staging branch retained as provenance
- clean review PR: #24

## Current test judgment

`REPAIR`

Reason: the code and missing scheduler control are repaired and materialized on current main; the active immutable-source run still must classify focused execution, typecheck, full preflight, and clean-tree publication.

Clearing condition: run `30691280000` completes its candidate-owned gates, or its first red gate is repaired on a new exact source head and rerun.
