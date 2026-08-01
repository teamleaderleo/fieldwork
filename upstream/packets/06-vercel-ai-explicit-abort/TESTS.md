# Tests and receipts — unit 06

## Exact source states

- Characterization head: `e685a4c92a5869aec306718ab5a440b7cb4fa5b1`
- Repair head tested through carriers: `19a9dbe26b48af848f3202fa0c409ed67d034c7d` matching the staged two-file repair diff
- Current clean source head: `92079da650430d8376a7eeef2436910b44393411`
- Current public base: `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`

## Executed target-native receipts

### Read-only staged repair

- Run: `30506931561`
- Job: `90758627827`
- Carrier head: `1edd359e3af359d29f020c3ab54574cf45413ee5`
- Environment: Ubuntu 24.04, Node `v22.23.1`, pnpm `10.33.4`
- Result: passed
- Gates:
  - AI dependency closure build;
  - Node Vitest: 2 files, 6 tests;
  - Edge Vitest: 2 files, 6 tests;
  - AI package TypeScript build;
  - Ultracite formatting/lint;
  - `git diff --check`.

### Publisher validation

- Run: `30507215391`
- Job: `90759478304`
- Result: passed the same gates, then published the tested source/test tree as repair head `19a9dbe26b48af848f3202fa0c409ed67d034c7d`.

### Ordinary repository CI attempt

- Run: `30507332233`
- Exact repair head: `19a9dbe26b48af848f3202fa0c409ed67d034c7d`
- Result: `action_required`
- Product jobs created: zero
- Classification: execution authorization; no product-test conclusion.

## Current clean-head execution

No workflow run is associated with `92079da650430d8376a7eeef2436910b44393411`.

The historical target receipts support the same retained repair mechanics but do not prove current-main compatibility or the pending hostile-cancel repair.

## Existing test coverage

### `stream-text-explicit-abort.test.ts`

- pending provider read;
- five result roots and representative derived getters;
- provider-reader cancellation;
- pre-aborted signal;
- active cooperative local tool;
- one abort part;
- one abort callback;
- no normal end/error callback;
- no later tool result.

### `stream-text-explicit-abort-races.test.ts`

- pending `onAbort` cannot delay outward closure or provider cancellation;
- normal provider error after abort cannot replace abort;
- multiple active consumers each receive one abort part while callback and provider cancellation occur once.

### `stream-text.test.ts`

- upstream-style regression that `text` and `steps` reject when a signal fires while the provider stream remains open.

## Required new controls

1. Abort wins after provider stream creation and before registration while provider `cancel()` returns a never-settling promise.
   - public root results reject within the bound;
   - outward stream completes with one abort part;
   - cancel is called once with the abort reason;
   - setup does not remain authoritative over public settlement.
2. Same registration gap with provider `cancel()` rejecting.
   - no unhandled rejection;
   - no competing `onError` or public error outcome;
   - root and outward state remain aborted.
3. Repeated execution under fake timers or retained handle observation.
   - abort listener removed;
   - step/first-chunk timers cleared;
   - no reader or rejection leak visible to the test harness.
4. Negative control for ordinary consumer cancellation.
   - operation signal remains unfired;
   - `onAbort` remains zero;
   - shared operation state is not rejected as aborted.

## Commands for the next exact head

```bash
pnpm --dir packages/ai test:node -- \
  src/generate-text/stream-text-explicit-abort.test.ts \
  src/generate-text/stream-text-explicit-abort-races.test.ts

pnpm --dir packages/ai test:edge -- \
  src/generate-text/stream-text-explicit-abort.test.ts \
  src/generate-text/stream-text-explicit-abort-races.test.ts

pnpm --dir packages/ai type-check
pnpm ultracite check packages/ai/src/generate-text/stream-text.ts \
  packages/ai/src/generate-text/stream-text-explicit-abort.test.ts \
  packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts

git diff --check e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0...HEAD
```

Follow with the repository-declared ordinary CI gate on the exact source head.

## Evidence limits

- The six focused tests exercise target code in Node and Edge at the prior repair diff.
- The receipt does not cover current public main, all AI package tests, provider integrations, browser runtimes, or hostile cancel promises.
- A green focused run cannot establish rollback of committed external tool effects.
- Current disposition stays `REPAIR` until the hostile cancellation defect is corrected and executed.