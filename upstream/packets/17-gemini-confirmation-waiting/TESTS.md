# Tests — confirmation waiting ownership

## Current status

The original defect is target-executed. The selected repair passed its focused staged gate. The clean current-head source diff is materialized at `7980e0651364593350d21114b3d0552a09506afb` and preserved in owned draft PR [`#20`](https://github.com/teamleaderleo/gemini-cli/pull/20). Its exact-head execution remains queued under run [`30675261256`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30675261256).

Exact clean source head: `7980e0651364593350d21114b3d0552a09506afb`  
Exact current source base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`

## Evidence ledger

| Stage | Exact revision | Commands or artifact | Result | Evidence class |
| --- | --- | --- | --- | --- |
| Source-equivalent single-wait probe | Fieldwork PR #45 head `9515e6a091f1c654f5ccdd6d60656b469f7b5889`; target pin `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e` | [`lifecycle_probe.mjs`](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/lifecycle_probe.mjs) | Reproduced abort transitions `[true]`; the clear transition was skipped. | probe-reproduced |
| Source-equivalent overlap probe | Same Fieldwork head and target pin | [`expanded_lifecycle_probe.mjs`](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/expanded_lifecycle_probe.mjs) | Reproduced `[true, true, false]` with one approval still pending and reported waiting `false`. | probe-reproduced |
| Target-native negative test | Candidate `974f6e288bf3e86af0c06cb445b9626bd5d2280f` | Run [`30504716033`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30504716033), job [`90751825412`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30504716033/job/90751825412) | The intended assertion ran and failed exactly at `[true]` versus `[true, false]`; carrier required that failure; core typecheck passed. | target-executed defect |
| Staged repair focused gate | Carrier `9d257f565fa42c88bed519038a789dff81668b35` | Run [`30581298716`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30581298716), job [`91001907749`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30581298716/job/91001907749) | 4 test files / 16 tests passed; core typecheck, Prettier, and diff hygiene passed. | target-executed staged repair |
| First source publication attempt | Carrier `ccd85e92c267109294e5596f9a8f16813c838bfd` | Run [`30594684917`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30594684917), job [`91044377734`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30594684917/job/91044377734) | Transform and formatting completed; file-fence command omitted four untracked files; behavior tests and publication did not run. | carrier failure |
| Explicit Linux publication reruns | Carrier `893749cc087fec170956c4f439f36ee1c1888aff` | Runs [`30674864738`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30674864738) and [`30675261256`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30675261256) | First run cancelled after a newer carrier commit; current run remains queued without a runner assignment. | carrier queue blocker |
| Clean current-head source materialization | Source `7980e0651364593350d21114b3d0552a09506afb`; base `f47d6c6f…` | [`gemini-cli#20`](https://github.com/teamleaderleo/gemini-cli/pull/20) and exact compare | Six source/test files only; source diff reviewed and mergeable inside the owned fork; exact-head tests remain unevaluated. | source-reviewed, execution pending |

## Exact negative execution

Environment from job `90751825412`:

- Ubuntu `24.04.4` on the `ubuntu-24.04` runner image
- Node `v22.23.1`
- npm `10.9.8`
- exact checked-out head `974f6e288bf3e86af0c06cb445b9626bd5d2280f`

Commands:

```sh
npm ci
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.waiting-state.test.ts
npm run typecheck --workspace @google/gemini-cli-core
```

Observed assertion:

```text
expected [ true ] to deeply equal [ true, false ]
```

This distinguishes the product defect from setup failure. Dependency installation completed, the intended test body ran, and core typecheck passed afterward.

## Exact staged repair gate

Environment from job `91001907749`:

- Ubuntu `24.04`
- Node `v22.23.1`
- npm `10.9.8`
- exact carrier head `9d257f565fa42c88bed519038a789dff81668b35`
- exact source base used by the transform `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`

Focused command:

```sh
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.waiting-state.test.ts \
  src/scheduler/confirmation.waiting-state.repair.test.ts \
  src/scheduler/confirmation-wait-tracker.test.ts \
  src/scheduler/confirmation.test.ts
npm run typecheck --workspace @google/gemini-cli-core
npx prettier --check \
  packages/core/src/scheduler/confirmation-wait-tracker.test.ts \
  packages/core/src/scheduler/confirmation-wait-tracker.ts \
  packages/core/src/scheduler/confirmation.ts \
  packages/core/src/scheduler/confirmation.waiting-state.repair.test.ts \
  packages/core/src/scheduler/confirmation.waiting-state.test.ts \
  packages/core/src/scheduler/scheduler.ts
git diff --check
```

Observed result:

```text
Test Files  4 passed (4)
Tests       16 passed (16)
FIELDWORK_WAITING_OWNERSHIP_TYPED=16/16
```

## Focused cases

### Existing confirmation controls — 8 tests

`confirmation.test.ts` preserves existing bus/IDE confirmation behavior and listener cleanup.

### Original abort regression — 1 test

`confirmation.waiting-state.test.ts` proves an aborted entered wait clears the callback back to `false`.

### Repair behavior — 4 tests

`confirmation.waiting-state.repair.test.ts` covers:

1. abort cleanup;
2. current IDE-rejection behavior while the bus remains the surviving owner;
3. primary wait-error preservation when the clear callback also throws;
4. clear-callback failure after a successful wait.

### Counted owner — 3 tests

`confirmation-wait-tracker.test.ts` covers:

1. first-enter/final-leave aggregation across overlapping waits;
2. unmatched clear rejection;
3. initial external-enter callback failure leaving the internal count at zero.

## Current-head source gate

The queued exact-head carrier checks out base `f47d6c6f…`, reapplies the reviewed transform with the current two-call-site fence, formats and commits the six files, then runs:

```sh
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.waiting-state.test.ts \
  src/scheduler/confirmation.waiting-state.repair.test.ts \
  src/scheduler/confirmation-wait-tracker.test.ts \
  src/scheduler/confirmation.test.ts
npm run typecheck --workspace @google/gemini-cli-core
git diff --exit-code
```

A successful receipt will print:

```text
FIELDWORK_WAITING_OWNERSHIP_CURRENT=16/16
FIELDWORK_SOURCE_HEAD=<exact tested commit>
FIELDWORK_SOURCE_BASE=f47d6c6f7a1308d81f9f57acf7d279f0928c5249
```

At the latest recorded check, run `30675261256`, job `91301036547`, remained queued with no steps assigned. The packet records this as an execution blocker, not a product failure.

## Unevaluated gates

- Focused tests and core typecheck on exact clean source head `7980e065…`.
- `npm run preflight` on the final clean source head.
- Full core test suite beyond the four focused files.
- Platform-specific execution beyond the recorded Linux staged gate.
- Manual subagent timeout exercise with two overlapping human approvals.

These remain submission/review tasks. The packet does not treat them as completed.
