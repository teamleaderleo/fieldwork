# Tests and receipts — unit 21 Jotai async read generation

## In simple words

The stale-publication behavior and the selected generation repair both ran against exact Jotai source with Node 22, 24, and 26. The accepted repair matrix covers six read/read and read/removal cases, adjacent unit-20 cache controls, the existing storage suite, changed-file lint and formatting, and TypeScript checking.

This session added a passing 11-case Node model and an expanded target-native test draft for rejected reads and same-string identity. A clean direct source branch, the expanded native run, `pnpm run build`, and the repository's complete `pnpm run test` gate remain outstanding.

## Identity

- Exact upstream base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Exact accepted repair execution head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- Exact workflow-free repair carrier head: `34670f709753668827043bbc76c4159a8b36ade2`
- Characterization head: `2fb60bd0497d5557afb54d11c3d6d1a31020b312`
- Unit 20 prerequisite head: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Test dates: 2026-07-31 target execution; 2026-08-01 local reconciliation
- Environments: GitHub Actions Ubuntu 24.04 with Node 22/24/26; local Linux container with Node `v22.16.0`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| completion-order publication exists on the unit-20 base | `target-executed` | PR #284 run `30588753020` | pass on Node 22/24/26 | focused source stack, Linux only |
| per-key generation fences the six accepted stale-publication transitions | `target-executed` | PR #317 run `30623229098` | pass on Node 22/24/26 | focused matrix, not complete repository CI |
| unit-20 adjacent cache behavior remains green | `target-executed` | run `30623229114` | success | selected cache matrix only |
| changed source and tests satisfy lint, formatting, and TypeScript | `target-executed` | inspected Node 24 job `91132389642` | pass | changed-file ESLint/Prettier; repository-wide `tsc --noEmit` |
| unit 21 depends mechanically on unit 20 | `source-read` plus source-segment execution | local patch-order check | direct apply fails; stacked apply passes | exact function segment, not full checkout |
| rejected-read semantics and same-string precision are coherent | `model-executed` | 11-case Node model | 11/11 pass | model mirrors source algorithm; target runtime pending |
| expanded native controls compile and pass | `target-test-prepared` | packet fixture | prepared | never run in Jotai checkout yet |
| full Jotai contribution gates pass on clean source branch | none | `pnpm run fix:format`, `pnpm run build`, `pnpm run test` | not run | clean source branch absent |

## Baseline characterization

### Command or workflow

Workflow at characterization head `2fb60bd0497d5557afb54d11c3d6d1a31020b312`:

```text
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageAsyncReadGeneration.test.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
pnpm eslint <four changed files>
pnpm prettier --check <four changed files>
pnpm tsc --noEmit
```

### Assertions

- older same-key completion replaces newer cached identity;
- pre-removal read repopulates after removal settlement;
- older valid completion restores after newer missing storage;
- older valid completion restores after newer malformed JSON;
- unrelated key remains stable.

### Result

- status: success
- workflow: `30588753020`
- adjacent unit-20 workflow: `30588753001`, success
- Fieldwork integrity: `30588752988`, success
- platform matrix: Node 22, 24, and 26
- inspected Node 24 job: four files, 42 tests, ESLint, Prettier, and TypeScript passed
- observed behavior: the selected unit-20 cache publishes by completion order

## Candidate-focused tests

### Accepted six-case repair matrix

- Exact source head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- Workflow: `30623229098`
- Tests and assertions:
  - newer same-key completion remains authoritative;
  - pre-removal completion cannot repopulate after settlement;
  - older valid completion cannot restore after newer missing storage;
  - older valid completion cannot restore after newer malformed storage;
  - stale malformed completion cannot delete newer valid identity;
  - unrelated key remains stable.
- Result: success on Node 22, 24, and 26
- Adjacent cache workflow: `30623229114`, success
- Fieldwork integrity: `30623229093`, success
- Inspected Node 24 job `91132389642`: four files, 43 tests, ESLint, Prettier, and TypeScript passed
- Coverage limit: read/read and read/completed-removal only; no write/subscription ordering

### Local patch-order reconciliation

- Exact source: `56a9cc51de8a5dd762b95a145820f12589cc47c9` function segment
- Unit 20 patch: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Unit 21 patch: `34670f709753668827043bbc76c4159a8b36ade2`
- Command:

```text
git apply --check unit21.patch
git apply --check unit20.patch
git apply unit20.patch
git apply --check unit21.patch
git apply unit21.patch
git diff --check
```

- Result: unit 21 direct apply failed; unit 20 followed by unit 21 passed
- Failure classification: expected dependency/packaging result, not a product failure
- Receipt: [`20260801-local-reconciliation.md`](./receipts/20260801-local-reconciliation.md)

### Expanded 11-case model

- Command: `node executed-model.mjs`
- Environment: Node `v22.16.0`
- Result: 11/11 passed
- Added assertions:
  - cached identity survives a newer rejected read while an older read remains stale;
  - without prior cache, a newer rejection prevents an older read from establishing shared identity;
  - a later successful read establishes identity after rejection;
  - rejection remains caller-visible and unrelated-key identity remains stable;
  - a stale caller resolving with current serialized bytes reuses the newer cached identity.
- Retained model: [`fixtures/async-read-generation-model.mjs`](./fixtures/async-read-generation-model.mjs)
- Coverage limit: model execution, not target package execution

### Expanded target-native draft

- Intended target path: `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts`
- Retained draft: [`fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts`](./fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts)
- Assertions: eleven cases matching the executed model and accepted six-case matrix
- Result: prepared, never executed in a direct Jotai checkout

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | focused `pnpm prettier --check` at `e99c7d2...` | pass | changed files only; contribution guide's `pnpm run fix:format` pending on clean branch |
| lint | focused `pnpm eslint` at `e99c7d2...` | pass | changed files only; complete `pnpm run test:lint` pending |
| typecheck | `pnpm tsc --noEmit` at `e99c7d2...` | pass | repository-wide typecheck in focused workflow |
| focused package tests | four-file Vitest command at `e99c7d2...` | pass | Node 22/24/26, 43 tests in inspected Node 24 job |
| complete target-declared suite | `pnpm run test` | not run | required on clean direct source head |
| build | `pnpm run build` | not run | required by Jotai contribution guide |
| platform matrix | focused Ubuntu Node 22/24/26 | pass | no Windows, macOS, browser integration, or React Native matrix |

## Reversing controls

- characterization fails the intended invariant and repair passes it;
- existing `atomWithStorage.test.tsx` remains green;
- malformed and missing outcomes exercise cache deletion authority;
- rejection controls preserve the backend error;
- unrelated-key controls reject cross-key generation interference;
- same-string control preserves historical identity reuse.

## Soak, leak, and cleanup controls

- iterations: one deterministic run per case; no soak loop
- resources observed: adapter-local maps and promises only
- timers/tasks/processes/files/listeners before and after: not measured
- cancellation or interruption behavior: not applicable at this boundary
- immediate rerun result: no immediate target rerun in this session

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| unit-21 patch directly on public main | missing `cachedValues` prerequisite | packaging/dependency | no; establishes stack dependency | base source branch on unit 20 |
| historical unit-20 PR #236 run `30553976771` | malformed patch at line 38 before install | packaging | no unit-20 target result transferred | superseded by PR #252 |
| this session full target execution | owned fork and complete checkout absent | repository access/setup | expanded cases remain prepared | create owned fork and clean branches |

## Checks prepared but not executed

- expanded native 11-case test — waits on clean unit-20 and unit-21 source branches;
- `pnpm install --frozen-lockfile` — direct checkout pending;
- `pnpm run fix:format` — direct checkout pending;
- `pnpm run build` — direct checkout pending;
- `pnpm run test` — direct checkout pending;
- complete-diff target review — direct source head pending.

## Platform and integration gaps

- Windows and macOS;
- browsers and real `StorageEvent` ordering;
- React Native storage adapters;
- custom thenables and unusual storage backends;
- application-level frequency and dynamic-key retention;
- read versus write and subscription-event ordering.

## Cleanup receipt

- Temporary repair workflow removed from workflow-free carrier head `34670f709753668827043bbc76c4159a8b36ade2`: yes
- Publisher or execution-only files removed from that carrier: yes for the unit-21 workflow; PR #317 remains an open Fieldwork carrier
- Generated residue checked: patch and test files only
- Immediate target rerun after workflow removal: no; receipts belong to `e99c7d2...`
- Remaining temporary branches or PRs: Fieldwork PRs #284 and #317; no target-source branch exists

## Current test judgment

`HOLD`

Reason: the accepted repair has strong focused target evidence, but unit 21 lacks a clean target-source head, depends on unit 20's future clean source branch, and has five newly retained native cases that remain unexecuted in Jotai.

Clearing condition: create the owned Jotai fork, materialize unit 20 on a clean branch, stack unit 21 with the expanded native test, then run focused tests plus `pnpm run build` and `pnpm run test` at the exact unit-21 head.
