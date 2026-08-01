# Tests and receipts — unit 20 Jotai key-scoped JSON cache

## In simple words

The released defect and the unit 20 candidate both have exact execution receipts. The release reproduces cross-key object aliasing on Node 22, 24, and 26. The candidate applies cleanly to exact Jotai source `56a9cc51...` and passes 37 focused and existing storage tests plus changed-file lint, formatting, and repository TypeScript checks on all three Node versions.

The largest gaps are a clean owned Jotai source branch, the target-declared build and aggregate test gates, browser/React Native coverage, and sequencing with unit 21's accepted asynchronous generation repair.

## Identity

- Exact upstream base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Exact candidate carrier head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Exact executed source/test generation: `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e`
- Current-head execution carrier: Fieldwork PR #252
- Test dates: 2026-07-30 and 2026-08-01 review/model pass
- Environment: GitHub-hosted Ubuntu 24.04; Node 22, 24, 26; pnpm 11.3.0

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Released adapter aliases equal JSON across keys. | `target-executed` | run `30548784323` | reproduced on Node 22/24/26 | released package only |
| Mutation through key A changes key B's prior value. | `target-executed` | same run and retained `result.json` | reproduced | mechanism/frequency only |
| Per-key map isolates equal JSON and preserves same-key identity. | `target-executed` | `atomWithStorageKeyIsolation.test.ts`, run `30579753383` | pass | patch carrier over pinned source |
| Missing/malformed observation prevents obsolete identity resurrection. | `target-executed` | `atomWithStorageReadInvalidation.test.ts` | pass | synchronous observation order |
| Existing mount/subscription behavior remains green. | `target-executed` | existing `atomWithStorage.test.tsx` | 25 pass | named suite only |
| Source/tests satisfy static checks. | `target-executed` | ESLint, Prettier, `tsc --noEmit` | pass | lint/format scoped to changed files; typecheck repository-wide |
| Late pre-removal async completion can regain cache authority. | `model-executed` | review `4823648945` and `/tmp/jotai_unit20_model.mjs` on 2026-08-01 | reproduced | dependency-free algorithm model; unit 21 has target-executed repair |

## Baseline characterization

### Command or workflow

```text
npm install --ignore-scripts --no-audit --no-fund
node probe.mjs
```

Workflow: `30548784323`.

### Assertions

- same adapter + same key + same JSON returns one object
- same adapter + different keys + same JSON returns one object on baseline
- different JSON returns different objects
- separate adapters return different objects
- mutating key A changes key B's previously returned object

### Result

- status: success
- platform matrix: Node `v22.23.1`, `v24.18.0`, `v26.5.1`
- observed behavior: cross-key mutable alias confirmed
- receipt: `playgrounds/EXP-20260730-jotai-json-key-isolation/result.json` in merged Fieldwork PR #228

## Candidate-focused tests

### Key isolation, invalidation, and existing suite

- Exact source/test generation: `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e`
- Current report/carrier head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Workflows: `30579399493` and current-head rerun `30579753383`
- Jobs: Node 22 `90996761925`, Node 24 `90996761816`, Node 26 `90996761918`

```text
pnpm install --frozen-lockfile
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
pnpm eslint <changed source and tests>
pnpm prettier --check <changed source and tests>
pnpm tsc --noEmit
```

Node 24 log receipt:

- `atomWithStorageKeyIsolation.test.ts`: 10 passed
- `atomWithStorageReadInvalidation.test.ts`: 2 passed
- existing `atomWithStorage.test.tsx`: 25 passed
- total: 37 passed in 3 files
- ESLint: passed
- Prettier: passed
- TypeScript: passed
- existing async suite emitted React `act(...)` warnings; assertions passed

Node 22 and Node 26 completed the same workflow steps successfully.

### Fresh 2026-08-01 model

```text
node /tmp/jotai_unit20_model.mjs
```

Result:

```json
{
  "released_cross_key_same_identity": true,
  "released_mutation_crosses_key": true,
  "candidate_original_reused_after_removal": false,
  "candidate_late_read_reused_after_recreation": true
}
```

Classification: `model-executed`. This confirms the independent review's stale async-completion sequence and informs delivery sequencing; it does not replace target-native unit 21 execution.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | changed-file `pnpm prettier --check ...` | pass | full `pnpm run test:format` absent |
| lint | changed-file `pnpm eslint ...` | pass | full `pnpm run test:lint` absent |
| typecheck | `pnpm tsc --noEmit` | pass | equivalent to `test:types` script |
| focused package tests | named Vitest command | pass, 37/37 per runtime | Node 22/24/26 |
| complete target-declared suite | `pnpm run test` | not run | required on clean direct source head |
| build | `pnpm run build` | not run | required on clean direct source head |
| format repair | `pnpm run fix:format` | not run | contribution guide requests before submission |
| platform matrix | Node 22/24/26 Ubuntu | pass | browser and React Native absent |

## Reversing controls

- Baseline fails cross-key identity isolation; candidate passes.
- Same-key identity and existing mount/subscription controls pass on candidate.
- Sync/async removal error and settlement paths preserve the original error while applying candidate invalidation rules.
- Unrelated-key identity survives affected-key transitions.
- Late async completion remains a failing control for unit 20 alone and passes under unit 21's accepted generation repair.

## Soak, leak, and cleanup controls

- iterations: no retained high-volume soak
- resources observed: adapter-local map entries by source inspection
- retained-memory measurement: absent
- cancellation/interruption: no cancellation API; async completion ordering characterized separately
- immediate rerun: current-head exact-source workflow passed

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| PR #236 run `30553976771` | corrupt patch at line 38; target setup never began | packaging | no candidate result | superseded by #252 |
| PR #242 | no transferable GitHub matrix on final head | execution absent | no | restacked in #252 |
| 2026-08-01 local target clone attempt | runtime had no external DNS access | environment | no; existing exact GitHub receipts used | record and stop local target execution |

## Checks prepared but not executed

- clean direct Jotai source diff — blocked on owned fork admission
- `pnpm run build` — wait for exact direct source head
- `pnpm run test` — wait for exact direct source head
- browser and React Native integration checks — choose after direct-source premise survives
- complete source stack including unit 21 — owned by cross-unit sequencing decision

## Platform and integration gaps

- browser storage events and real `localStorage`
- React Native AsyncStorage
- custom thenables with unusual settlement behavior
- large dynamic key sets and retained heap measurements
- direct-source CI and generated package outputs

## Cleanup receipt

- Temporary workflows removed from canonical source head: `not applicable; canonical source head absent`
- Publisher or execution-only files removed: `not applicable; future target branch must exclude all Fieldwork files`
- Generated residue checked: `not applicable`
- Immediate rerun performed: `yes, current Fieldwork carrier head`
- Remaining temporary branches or PRs: PR #252 is the active evidence carrier; #236/#242 are closed; packet branch is documentation-only

## Current test judgment

`HOLD`

Reason: the bounded unit 20 mechanism is target-executed, but a clean direct source head and ordinary Jotai gates are absent, and final delivery must account for unit 21's accepted async generation fence.

Clearing condition: create one writable direct Jotai source branch from `56a9cc51...`, materialize unit 20, stack or combine the accepted unit 21 repair, then pass `pnpm run build`, `pnpm run test`, focused regressions, and independent complete-diff review.
