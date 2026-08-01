# Unit 17 — Gemini CLI confirmation waiting ownership

## In simple words

Gemini CLI tells a timeout owner when the scheduler starts and stops waiting for tool confirmation. The current implementation can leave that owner paused forever when the wait rejects, and a direct shared boolean can report idle while another overlapping confirmation remains active.

The selected repair gives each wait balanced enter/leave cleanup and gives the scheduler a counted owner that emits only on the first active wait and the final completed wait.

## Current disposition

`ISSUE FIRST`

The clean source candidate is coherent and focused. Gemini CLI's contribution policy asks contributors to link every pull request to an existing issue and recommends opening the issue first and waiting for maintainer direction. Public upstream contact remains unauthorized.

## Exact identity

- Unit: `17`
- Target: `google-gemini/gemini-cli`
- Proposed contribution: `fix(core): balance confirmation waiting ownership`
- Current public source head/base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Immutable owned source base branch: `fieldwork/upstream-f47-waiting-ownership-base`
- Clean target-source branch: `fix/scheduler-confirmation-waiting-ownership`
- Exact clean source head: `7980e0651364593350d21114b3d0552a09506afb`
- Clean owned review PR: [`gemini-cli#20`](https://github.com/teamleaderleo/gemini-cli/pull/20)
- Current-head execution carrier: [`gemini-cli#8`](https://github.com/teamleaderleo/gemini-cli/pull/8), head `f3a92cb60173f7ae88447de99843068c12261509`
- Current-head execution run: [`30675261256`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30675261256), queued at the latest recorded check
- Packet branch: `p0/435-unit-17-gemini-confirmation-waiting`
- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Exact packet head: recorded in the final handoff on [`fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Public upstream contact: `false`

## Changed-file fence

Production:

- `packages/core/src/scheduler/confirmation-wait-tracker.ts`
- `packages/core/src/scheduler/confirmation.ts`
- `packages/core/src/scheduler/scheduler.ts`

Tests:

- `packages/core/src/scheduler/confirmation-wait-tracker.test.ts`
- `packages/core/src/scheduler/confirmation.waiting-state.repair.test.ts`
- `packages/core/src/scheduler/confirmation.waiting-state.test.ts`

The exact compare from base to clean head reports six commits, six changed files, 455 additions, and 7 deletions. The diff contains no workflow, packet, generated, dependency, lock, or unrelated file.

- [`f47d6c6f…7980e065`](https://github.com/teamleaderleo/gemini-cli/compare/f47d6c6f7a1308d81f9f57acf7d279f0928c5249...7980e0651364593350d21114b3d0552a09506afb)

## Evidence summary

- Source review at `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e` found `true` before the confirmation wait and `false` after it, outside guaranteed cleanup.
- Target-native negative run [`30504716033`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30504716033), job [`90751825412`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30504716033/job/90751825412), checked out `974f6e288bf3e86af0c06cb445b9626bd5d2280f` and reached the predicted `[true]` versus `[true, false]` assertion failure. Core typecheck passed.
- Fieldwork's retained deterministic probe produced `true, true, false` with one approval still pending, proving that per-call cleanup alone leaves a shared boolean ambiguous.
- Staged repair run [`30581298716`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30581298716), job [`91001907749`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30581298716/job/91001907749), passed 4 focused files / 16 tests, core typecheck, Prettier, and diff hygiene at carrier head `9d257f565fa42c88bed519038a789dff81668b35`.
- The current public head has two scheduler call sites for `resolveConfirmation`; the clean source head routes both through one scheduler-owned tracker.
- The clean diff was materialized directly from exact base `f47d6c6f…` and preserved as owned draft PR #20. Current-head execution remains queued under run `30675261256`; [`TESTS.md`](./TESTS.md) separates that pending receipt from the passed staged gate.

## Reading order

1. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
2. [`APPROACHES.md`](./APPROACHES.md)
3. [`TESTS.md`](./TESTS.md)
4. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
5. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
6. [`REVIEW.md`](./REVIEW.md)

## Durable source records

- Original source-confirmed scout: [`fieldwork#22`](https://github.com/teamleaderleo/fieldwork/issues/22)
- Merged scout packet: [`fieldwork#45`](https://github.com/teamleaderleo/fieldwork/pull/45)
- Test-only negative candidate: [`gemini-cli#3`](https://github.com/teamleaderleo/gemini-cli/pull/3)
- Completed negative execution carrier: [`gemini-cli#5`](https://github.com/teamleaderleo/gemini-cli/pull/5)
- Staged repair and typed receipt: [`gemini-cli#7`](https://github.com/teamleaderleo/gemini-cli/pull/7)
- Source publication/execution carrier: [`gemini-cli#8`](https://github.com/teamleaderleo/gemini-cli/pull/8)
- Clean current-head source review: [`gemini-cli#20`](https://github.com/teamleaderleo/gemini-cli/pull/20)
- Callback-origin prior art: [`google-gemini/gemini-cli#18415`](https://github.com/google-gemini/gemini-cli/pull/18415)

## Remaining blockers

1. Current-head focused tests and core typecheck remain queued in run `30675261256`; the clean source head has source review plus staged-equivalent execution evidence, while its own exact execution receipt remains open.
2. `npm run preflight` remains an ordinary submission gate on the final clean head.
3. A maintainer-facing issue needs approval before a public source pull request under the target's contribution policy.
4. Public upstream interaction requires explicit human authorization.
