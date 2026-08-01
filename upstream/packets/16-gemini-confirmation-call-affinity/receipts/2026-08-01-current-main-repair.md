# Unit 16 current-main repair receipt — 2026-08-01

## Scope

Repair confirmation modification call affinity on exact public base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`, add a real scheduler-level two-call reverse-order control, execute candidate-owned validation, classify full-preflight limits, and publish a workflow-free clean source branch. Public upstream interaction remained unauthorized.

## Final identity

- base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- final source: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- canonical branch: `fix/scheduler-confirmation-call-affinity`
- clean review PR: `teamleaderleo/gemini-cli#24`
- completed carrier: closed `teamleaderleo/gemini-cli#6`
- final run: `30692554758`
- candidate job: `91350078426`
- baseline-control job: `91349770438`
- environment: Ubuntu 22.04, Node `v20.19.0`, npm `10.8.2`, Git `2.54.0`, Vitest `3.2.4`

## Exact final fence

```text
packages/core/src/scheduler/confirmation.affinity.repair.test.ts
packages/core/src/scheduler/confirmation.test.ts
packages/core/src/scheduler/confirmation.ts
packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts
```

Relationship: one commit ahead, zero behind the base. Diff: 775 additions, 20 deletions. No workflow, dependency, generated, snapshot, or Fieldwork file.

## Final candidate result

Run `30692554758`, candidate job `91350078426`:

- exact initial source identity: pass
- exact parent: pass
- initial four-file fence: pass
- locked install and repository prepare/bundle: pass
- executor response fixture correction: applied
- Prettier write/check: pass
- `git diff --check`: pass
- clean one-commit source creation: pass
- staged pre-commit Prettier/ESLint: pass
- final source created: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- focused/adjacent command: pass
  - `confirmation.test.ts`: 8 passed
  - `confirmation.affinity.repair.test.ts`: 6 passed
  - `scheduler.confirmation-affinity.test.ts`: 1 passed
  - total: 3 files, 15 tests
- posttest core build: pass
- standalone core typecheck: pass
- explicit ESLint across all four changed files: pass
- clean tracked tree: pass
- canonical branch publication: pass

Publication output:

```text
source_head=b6d8e8bb6160aec16555647d81d46a694e44b58b
source_base=f47d6c6f7a1308d81f9f57acf7d279f0928c5249
node=v20.19.0
npm=10.8.2
full_preflight=blocked_by_confirmed_base_SC2031
```

## Baseline preflight control

A candidate preflight run completed clean/install/format/build, then repository-wide lint stopped on:

```text
.github/workflows/pr-size-labeler-batch-run.yml
SC2030 / SC2031
UPDATED_COUNT and SKIPPED_COUNT modified in a pipeline subshell
```

The unit changes no workflow file. Final run `30692554758` added a separate control job that checked out exact unchanged base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`, installed locked dependencies, and ran `npm run lint:ci`. It required a nonzero status plus the same workflow path and `SC2031`.

Control output:

```text
baseline_head=f47d6c6f7a1308d81f9f57acf7d279f0928c5249
baseline_lint_status=1
baseline_blocker=.github/workflows/pr-size-labeler-batch-run.yml:SC2031
```

Classification: repository baseline blocker outside unit 16. Candidate-owned tests, build, typecheck, formatting, lint, fencing, clean-tree, and publication gates are green.

## Scheduler reverse-order control

- real `Scheduler`
- real scheduler state manager
- real `MessageBus`
- two calls simultaneously observed in `AwaitingApproval`
- call 2 response delivered before call 1
- modifier call order required to match response order
- each modifier required to receive its own original arguments
- first response required to update only call 2 while call 1 remained waiting
- final rebuilt invocations and completed arguments required to remain call-scoped
- controlled policy, executor, and modifier; no model or external service

Result: pass at `b6d8e8bb6160aec16555647d81d46a694e44b58b`.

## Predecessor evidence

- baseline evidence PR #2, run `30505534210`: exact call A versus call B mismatch reached; core typecheck passed
- predecessor source `b359ece8a2bd059aef870a084ab9494eff16fa8f`, run `30595253180`: 14/14, posttest build, core typecheck, formatting, staged lint, exact three-file fence, clean tree, and publication passed

## Classified current-main attempts

### Run `30690542009`, job `91344358931`

- failure: unused `AnyToolInvocation` and local `toolRegistry` in transiently generated scheduler test
- classification: harness lint before product execution
- retained value: corrected integration-test requirements

### Run `30691715651`, job `91347503312`

- passed: source identity, parent, four-file fence, install
- failure: scheduler test needed Prettier normalization
- classification: source formatting before behavior execution

### Run `30691895493`, job `91347974377`

- passed: formatting and all 15 behavioral tests
- failure: posttest TypeScript found the fake executor response lacked `resultDisplay`, `error`, and `errorType`
- classification: test-fixture typing after behavioral assertions passed

### Run `30692033075`, job `91348335683`

- failure: execution-only fixture patch anchor mismatch
- classification: carrier setup; source unchanged

### Run `30692147133`, job `91348637042`

- passed: 15 tests, posttest build, standalone core typecheck
- full preflight reached unrelated workflow `SC2031`
- classification: candidate gates green; baseline control still required

### Run `30692554758`

- baseline job reproduced exact blocker
- candidate job completed every unit-owned gate and published final source
- classification: repair complete

## Cleanup

- canonical source workflow-free: yes
- carrier PR #6: closed
- fallback carrier PR #22: closed superseded
- source composition PR #23: merged/closed
- clean source PR #24: open draft
- canonical branch points to final source: yes
- packet receipt committed: yes

## Continuation

1. Obtain eligible independent complete-diff review at `b6d8e8bb6160aec16555647d81d46a694e44b58b`.
2. Repeat public duplicate search immediately before authorized filing.
3. Use issue-first route under the target contribution policy.
4. Keep public upstream untouched until explicit authority is recorded.
