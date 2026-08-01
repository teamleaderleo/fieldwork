# Unit 17 — Gemini CLI confirmation waiting ownership

## In simple words

Gemini CLI tells a timeout owner when the scheduler starts and stops waiting for tool confirmation. The current implementation can leave that owner paused forever when the wait rejects, and a direct shared boolean can report idle while another overlapping confirmation remains active.

The selected repair gives each wait balanced enter/leave cleanup and gives the scheduler a counted owner that emits only on the first active wait and the final completed wait.

## Current disposition

`ISSUE FIRST`

The source candidate is coherent and focused. Gemini CLI's contribution policy asks contributors to link every pull request to an existing issue and recommends opening the issue first and waiting for maintainer direction. Public upstream contact remains unauthorized.

## Exact identity

- Unit: `17`
- Target: `google-gemini/gemini-cli`
- Proposed contribution: `fix(scheduler): balance confirmation waiting ownership`
- Current public source head/base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Immutable owned source base branch: `fieldwork/upstream-f47-waiting-ownership-base`
- Clean target-source branch: `fix/scheduler-confirmation-waiting-ownership`
- Exact clean source head: `SOURCE_HEAD_PENDING_30674864738`
- Source publication/test run: [`30674864738`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30674864738)
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

No workflow, packet, generated, dependency, lock, or unrelated file belongs in the clean target-source diff.

## Evidence summary

- Source review at `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e` found `true` before the confirmation wait and `false` after it, outside guaranteed cleanup.
- Target-native negative run [`30504716033`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30504716033), job [`90751825412`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30504716033/job/90751825412), checked out `974f6e288bf3e86af0c06cb445b9626bd5d2280f` and reached the predicted `[true]` versus `[true, false]` assertion failure. Core typecheck passed.
- Fieldwork's retained deterministic probe produced `true, true, false` with one approval still pending, proving that per-call cleanup alone leaves a shared boolean ambiguous.
- Staged repair run [`30581298716`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30581298716), job [`91001907749`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30581298716/job/91001907749), passed 4 focused files / 16 tests, core typecheck, Prettier, and diff hygiene at carrier head `9d257f565fa42c88bed519038a789dff81668b35`.
- The current public head has two scheduler call sites for `resolveConfirmation`; the current-head transform accounts for both.
- The clean current-head publication/test receipt belongs to run `30674864738` and is finalized in [`TESTS.md`](./TESTS.md).

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
- Source publication carrier: [`gemini-cli#8`](https://github.com/teamleaderleo/gemini-cli/pull/8)
- Callback-origin prior art: [`google-gemini/gemini-cli#18415`](https://github.com/google-gemini/gemini-cli/pull/18415)

## Remaining blockers

1. A maintainer-facing issue needs approval before a source pull request under the target's contribution policy.
2. Public upstream interaction requires explicit human authorization.
3. `npm run preflight` remains an ordinary submission gate beyond the focused tests and core typecheck recorded here.
4. The current source publication run must finish and provide the exact source head receipt before the packet can be treated as a completed current-head source candidate.
