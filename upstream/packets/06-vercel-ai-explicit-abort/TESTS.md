# Tests and receipts — unit 06

## Exact source states

- Characterization head: `e685a4c92a5869aec306718ab5a440b7cb4fa5b1`
- Repair head tested through carriers: `19a9dbe26b48af848f3202fa0c409ed67d034c7d`
- Current clean source head: `92079da650430d8376a7eeef2436910b44393411`
- Target-native cancellation-regression head: `7ae1794889d9dd22eeef9faf4f33d01330c0918d`
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

### Ordinary repository CI attempt on prior repair head

- Run: `30507332233`
- Exact repair head: `19a9dbe26b48af848f3202fa0c409ed67d034c7d`
- Result: `action_required`
- Product jobs created: zero
- Classification: execution authorization; no product-test conclusion.

## Model-executed cancellation receipt

Receipt: `receipts/2026-08-01-provider-cancel-promise-model.md`.

Environment: Node `v22.17.0` with native Web Streams.

Exact stack modeled:

```ts
const standardized = providerStream.pipeThrough(new TransformStream());
const returned = standardized.pipeThrough(new TransformStream());
```

This matches `streamLanguageModelCall()` followed by `createAsyncIterableStream()` at clean source head `92079da650430d8376a7eeef2436910b44393411`.

Observed controls:

1. provider `cancel()` returned a never-settling promise;
   - provider cancellation was requested with the exact reason;
   - returned stream cancellation resolved within the bound;
   - provider cleanup remained pending.
2. provider `cancel()` rejected;
   - returned stream cancellation resolved;
   - an `unhandledRejection` listener observed zero events.
3. proposed extra-wrapper negative control;
   - ordinary cancellation also resolved before provider cleanup;
   - the wrapper direction was discarded because it could not preserve the claimed distinction.

Evidence class: `model-executed`. This clears the earlier premise that the pre-registration `await languageModelStream.cancel(...)` joins provider-controlled cleanup.

## Current target-native execution

Owned-fork PR #12 adds `stream-language-model-call-cancellation.test.ts` at exact head `7ae1794889d9dd22eeef9faf4f33d01330c0918d`.

Repository CI run `30691171818` is queued. The relevant assertions are:

- returned cancellation settles after requesting pending provider cleanup;
- exact abort reason reaches provider cancellation;
- rejected provider cleanup produces no unhandled rejection.

Until this run completes, classify the new file as `target-test-prepared`; the historical six-test repair remains `target-executed` at its earlier exact diff.

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

### `stream-language-model-call-cancellation.test.ts`

- pending provider cleanup does not retain the returned cancellation promise;
- provider cleanup rejection is contained;
- exact abort reason reaches provider cancellation.

## Remaining execution controls

1. Complete repository CI run `30691171818` on exact test head `7ae1794889d9dd22eeef9faf4f33d01330c0918d`.
2. After merging the test into the canonical source branch, run ordinary repository CI on that exact canonical head.
3. Confirm current complete diff contains no temporary workflow or trigger files.
4. Keep committed external tool side effects outside abort-reversal claims.

## Focused commands

```bash
pnpm --dir packages/ai test:node -- \
  src/generate-text/stream-language-model-call-cancellation.test.ts \
  src/generate-text/stream-text-explicit-abort.test.ts \
  src/generate-text/stream-text-explicit-abort-races.test.ts

pnpm --dir packages/ai test:edge -- \
  src/generate-text/stream-language-model-call-cancellation.test.ts \
  src/generate-text/stream-text-explicit-abort.test.ts \
  src/generate-text/stream-text-explicit-abort-races.test.ts

pnpm --dir packages/ai type-check
pnpm ultracite check packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts

git diff --check e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0...HEAD
```

## Evidence limits

- The six focused tests exercise target code in Node and Edge at the prior repair diff.
- The cancellation model proves the native Web Streams promise behavior but does not replace package execution.
- The new target-native test head has no completed receipt yet.
- A green package run cannot establish rollback of committed external tool effects.
- Current disposition remains `EXECUTE` until the exact-head target test and ordinary canonical CI complete.
