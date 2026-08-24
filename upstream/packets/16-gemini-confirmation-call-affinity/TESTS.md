# Tests and receipts — Unit 16 confirmation modification call affinity

## In simple words

The baseline defect reached the exact wrong-call assertion. The final current-main candidate passed six focused authority controls, eight adjacent confirmation controls, and one real scheduler reverse-order control. Core build, core typecheck, formatting, changed-file lint, exact fencing, clean-tree verification, and publication all passed.

Full repository preflight reaches a shellcheck failure in an unchanged workflow. A separate job checked out the exact base and reproduced the same path and `SC2031`, classifying it as a repository baseline blocker outside unit 16.

## Identity

- public/fork base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- final candidate head: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- canonical branch: `fix/scheduler-confirmation-call-affinity`
- clean review PR: `teamleaderleo/gemini-cli#24`
- final run: `30692554758`
- candidate job: `91350078426`
- baseline-control job: `91349770438`
- environment: Ubuntu 22.04, Node `v20.19.0`, npm `10.8.2`, Vitest `3.2.4`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Baseline can modify the wrong active call | `target-executed` | PR #2 run `30505534210` | predicted call A versus call B assertion reached | inline harness |
| Inline candidate selects correlated call | `target-executed` | focused repair test 1 | pass | controlled state |
| Editor candidate selects correlated call | `target-executed` | focused repair test 2 | pass | editor resolution mocked |
| Removal during inline modification cannot publish | `target-executed` | focused test 3 | pass | lookup-loss model |
| Status loss during editor modification cannot publish | `target-executed` | focused test 4 | pass | direct status transition |
| Same-ID replacement cannot publish stale output | `target-executed` | focused test 5 | pass | new waiting object/correlation |
| Missing call before modification fails closed | `target-executed` | focused test 6 | pass | direct harness |
| Existing confirmation behavior remains green | `target-executed` | eight adjacent tests | pass | selected confirmation suite |
| Two simultaneous approvals stay isolated under reverse responses | `target-executed` | scheduler reverse-order test | pass | policy/executor/modifier controlled |
| Candidate source quality gates pass | `target-executed` | final candidate job | build, typecheck, formatting, staged lint, four-file ESLint, clean tree, publication pass | changed-source fence and core workspace |
| Full preflight lint blocker predates candidate | `baseline-confirmed` | baseline-control job | exact workflow path and `SC2031` reproduced | unchanged repository base |

## Baseline characterization

### Command

```text
npm ci
npm run test --workspace @google/gemini-cli-core -- src/scheduler/confirmation.affinity.test.ts
npm run typecheck --workspace @google/gemini-cli-core
```

### Result

- run: `30505534210`
- modifier received call A while response correlation owned call B
- core typecheck passed

## Final candidate command

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/scheduler.confirmation-affinity.test.ts \
  src/scheduler/confirmation.test.ts

npm run typecheck --workspace @google/gemini-cli-core

npx eslint --max-warnings 0 --no-warn-ignored \
  packages/core/src/scheduler/confirmation.ts \
  packages/core/src/scheduler/confirmation.affinity.repair.test.ts \
  packages/core/src/scheduler/confirmation.test.ts \
  packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts
```

### Final result

- source head created: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- test files: 3 passed
- tests: 15 passed
  - adjacent confirmation: 8
  - focused authority/stale-generation: 6
  - real scheduler reverse-order: 1
- posttest core build: pass
- standalone core typecheck: pass
- Prettier: pass
- pre-commit staged ESLint: pass
- explicit ESLint across all four changed files: pass
- exact parent and four-file fence: pass
- `git diff --check`: pass
- clean tracked tree: pass
- canonical branch publication: pass

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

- modifier order is call 2 then call 1;
- each modifier receives its own original arguments;
- the first response updates only call 2 while call 1 remains waiting;
- final call 1 arguments contain `one-updated` only;
- final call 2 arguments contain `two-updated` only;
- invocation rebuilds receive each call's own updated parameters;
- executor runs twice.

### Result

Pass at `b6d8e8bb6160aec16555647d81d46a694e44b58b`.

## Full preflight classification

Candidate preflight reached repository-wide `lint:ci` after clean, install, formatting, and build. Actionlint/shellcheck reported:

```text
.github/workflows/pr-size-labeler-batch-run.yml
SC2030 / SC2031
UPDATED_COUNT and SKIPPED_COUNT modified in a pipeline subshell
```

The candidate changes no workflow file. Baseline-control job `91349770438` checked out exact base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`, ran `npm run lint:ci`, and required the same workflow path plus `SC2031`. Result:

```text
baseline_lint_status=1
baseline_blocker=.github/workflows/pr-size-labeler-batch-run.yml:SC2031
```

Judgment: full preflight is blocked by the repository baseline; candidate-owned gates are green.

## Classified repair attempts

| Run | First result | Classification | Product claim affected? |
| --- | --- | --- | --- |
| `30690542009` | unused declarations in transient test | harness lint | no |
| `30691715651` | new test needed Prettier normalization | source formatting | no behavior executed |
| `30691895493` | 15 tests passed; posttest found incomplete response fixture | fixture typing | behavioral result retained |
| `30692033075` | fixture patch anchor mismatch | carrier setup | no |
| `30692147133` | 15 tests/build/typecheck pass; preflight hits workflow `SC2031` | repository baseline suspected | candidate gates green |
| `30692554758` | base reproduces blocker; final candidate fully validates and publishes | complete | yes, positive receipt |

## Ordinary gates

| Gate | Result |
| --- | --- |
| exact parent/four-file fence | pass |
| Prettier | pass |
| staged pre-commit ESLint | pass |
| focused and adjacent tests | 15/15 pass |
| posttest core build | pass |
| core typecheck | pass |
| explicit changed-file ESLint | pass |
| clean tracked tree | pass |
| source publication | pass |
| full repository preflight | blocked by baseline workflow `SC2031`, independently reproduced |
| macOS/Windows | not run |

## Cleanup receipt

- canonical source contains no workflow: yes
- publisher/carrier PR #6 closed: yes
- fallback carrier PR #22 closed: yes
- source composition PR #23 merged/closed: yes
- clean review PR #24 open: yes
- generated residue checked: yes
- canonical source branch updated to final head: yes

## Current test judgment

`ACCEPT`

Reason: every candidate-owned behavioral, compilation, formatting, lint, fencing, cleanliness, and publication gate passed. The only repository-wide preflight failure is confirmed on the unchanged base.

Clearing condition for public submission: eligible independent review, current duplicate search, and explicit issue-filing authority.
