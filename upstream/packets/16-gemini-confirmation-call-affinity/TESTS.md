# Tests and receipts — Unit 16 confirmation modification call affinity

## In simple words

The baseline defect reached the exact wrong-call assertion in a target-native Vitest run. The current clean candidate passed six focused authority controls, eight adjacent confirmation controls, pre-commit formatting/lint, core build, core typecheck, an exact three-file fence, and a clean-tree check. The largest gaps are a real two-call out-of-order scheduler test, current-main execution, and full repository preflight.

## Identity

- Exact upstream base: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- Exact candidate head: `b359ece8a2bd059aef870a084ab9494eff16fa8f`
- Exact execution carrier head: `07307db4bfbbc66acaa8f58faeb279a1f765b301`
- Test date: `2026-07-31`
- Environment and platform: GitHub-hosted Ubuntu 24.04, Node `v22.23.1`, npm `10.9.8`, Vitest `3.2.4`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Baseline can modify the wrong active call | `target-executed` | PR #2 run `30505534210`, `confirmation.affinity.test.ts` | predicted `call-a` versus `call-b` assertion reached | inline path only |
| Inline candidate selects correlated call | `target-executed` | focused repair test 1 in run `30595253180` | pass | mocked state manager |
| Editor candidate selects correlated call | `target-executed` | focused repair test 2 | pass | editor resolution mocked |
| Removal during inline modification cannot publish | `target-executed` | focused repair test 3 | pass | removal modeled by lookup loss |
| Status loss during editor modification cannot publish | `target-executed` | focused repair test 4 | pass | status transition modeled directly |
| Same-ID replacement generation cannot publish stale output | `target-executed` | focused repair test 5 | pass | replacement modeled by new waiting object/correlation ID |
| Missing correlated call before modification fails closed | `target-executed` | focused repair test 6 | pass | direct harness |
| Existing confirmation behavior remains green | `target-executed` | eight tests in `confirmation.test.ts` | pass | adjacent file, not all scheduler tests |
| Current public source still carries baseline mechanism | `source-read` | public `confirmation.ts` at `f47d6c6...` | confirmed | read-only inspection |

## Baseline characterization

### Command or workflow

```text
npm ci
npm run test --workspace @google/gemini-cli-core -- src/scheduler/confirmation.affinity.test.ts
npm run typecheck --workspace @google/gemini-cli-core
```

### Assertions

- response and update target belong to `call-b`;
- `call-a` remains first active;
- modifier must receive `call-b` and its original arguments;
- no hidden lookup of `call-a` should justify selection.

### Result

- status: expected product failure classified successfully
- test count: one distinguishing focused case
- workflow and job: [run `30505534210`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30505534210), evidence PR #2
- artifact or receipt: PR #2 body and comments
- observed behavior: modifier received `call-a`; core typecheck passed

## Candidate-focused tests

### Current clean publication

- Exact source head: `b359ece8a2bd059aef870a084ab9494eff16fa8f`
- Command:

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/confirmation.test.ts
```

- Tests and assertions: six focused authority controls plus eight adjacent confirmation controls
- Result: `2` files passed, `14` tests passed, duration `4.25s`
- Workflow: [run `30595253180`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30595253180), job `91046140436`
- Failure classification: none
- Coverage limit: stateful unit harness; no real dual-loop scheduler ordering test

### Earlier clean publication

- Exact source head: `c707e267ae2053195646f00f495c159484fc6c15`
- Workflow: [run `30591785562`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30591785562), job `91035469691`
- Result: `13/13` tests passed, core build/typecheck and publication gates passed
- Coverage limit: five focused tests; same-ID generation replacement had not yet been added

### Initial repaired source execution

- Run: `30585861453`
- Result: five focused controls passed; three adjacent tests failed because the mock kept returning `Validating` after `updateStatus(AwaitingApproval)`
- Classification: fixture failure representing an impossible state, not product regression
- Repair: make the adjacent fixture stateful, then rerun with focused and adjacent files together

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | `npx prettier --write/check` on three files | pass | current publisher run |
| lint | repository pre-commit `eslint --fix --max-warnings 0 --no-warn-ignored` on staged files | pass | invoked during clean commit creation |
| typecheck or compile | `npm run typecheck --workspace @google/gemini-cli-core` | pass | current publisher run |
| focused package tests | exact two-file Vitest command | pass, 14/14 | current publisher run |
| complete target-declared suite | `npm run preflight` | not run | required before promotion |
| build or generated output | core test posttest `npm run build`; install prepare/bundle | pass | no generated diff retained |
| platform matrix | Linux only | partial | no macOS/Windows run |
| clean diff | exact parent, three-file fence, `git diff --check`, `git diff --exit-code` | pass | source branch excludes workflow |

## Reversing controls

- Baseline focused case fails at wrong-call assertion and candidate focused selection controls pass.
- Eight adjacent confirmation tests pass with a stateful status-transition fixture.
- Removal, status loss, and generation replacement all prevent `updateArgs`.
- Other waiting call remains available while target call selection stays on `call-b`.

## Soak, leak, and cleanup controls

- iterations: one run per focused case; no soak loop
- resources observed: message-bus listener count used as deterministic synchronization
- timers/tasks/processes/files/listeners before and after: no dedicated leak accounting beyond `waitForConfirmation` iterator cleanup and clean job exit
- cancellation or interruption behavior: state loss during modifier await represented; parent abort path belongs to existing adjacent behavior
- immediate rerun result: current publisher followed earlier green publication and reproduced green results with one added control

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| early evidence run before `30505534210` | test-only TypeScript/harness issue | fixture | no | repaired ID-aware fixture and reran |
| run `30585861453` adjacent file | mock stayed `Validating` after waiting transition | fixture | no | stateful `updateStatus` mock |
| local packet-session clone | DNS/network boundary prevented clone | runner | no; no new execution claimed | rely on retained Actions receipts; next worker reruns after rebase |

## Checks prepared but not executed

- Real scheduler two-call out-of-order approval control — design requirement repeated in PR #2, PR #6 review, issue #22, and portfolio PR #269.
- `npm run preflight` — target-declared final gate.
- Current-main rebased focused/adjacent run — source paths have no direct public overlap, yet adjacent scheduler files changed.
- Independent review tool or equivalent exact-head review — author self-review only so far.

## Platform and integration gaps

- macOS and Windows
- actual external editor process lifetime
- real scheduler event ordering with simultaneous approvals
- IDE and TUI confirmation paths together
- full repository suites and E2E

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes`, clean tracked tree in publisher job
- Immediate rerun performed: `yes`, later publication superseded earlier green head
- Remaining temporary branches or PRs: draft carrier PR #6 and branch `fieldwork/confirmation-call-affinity-repair`; evidence PR #2 is closed; original source branch remains as provenance

## Current test judgment

`REPAIR`

Reason: The exact candidate is strong at unit level and cleanly published, while current-main execution, the real parallel scheduler control, and full preflight remain open.

Clearing condition: one rebased clean head passes the dual-call out-of-order control, current focused/adjacent tests, core gates, and `npm run preflight`.
