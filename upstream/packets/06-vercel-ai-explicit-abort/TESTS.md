# Tests and receipts — unit 06

## Exact source states

- Characterization head: `e685a4c92a5869aec306718ab5a440b7cb4fa5b1`
- Repair head tested through carriers: `19a9dbe26b48af848f3202fa0c409ed67d034c7d`
- Initial clean source head: `92079da650430d8376a7eeef2436910b44393411`
- Target-native cancellation-regression head before merge: `7ae1794889d9dd22eeef9faf4f33d01330c0918d`
- Current canonical source head: `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`
- Current public base: `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`
- Canonical review PR: `teamleaderleo/ai#13`

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

## Target-native cancellation regression

Owned-fork PR #12 encoded the model result in `stream-language-model-call-cancellation.test.ts` at head `7ae1794889d9dd22eeef9faf4f33d01330c0918d`.

The PR was squash-merged into the canonical source branch as `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15` after exact-head self-review.

Original PR #12 CI:

- Run: `30691171818`
- State: queued
- Jobs created: full repository matrix
- Jobs started: zero
- Classification: execution availability/authorization; no product-test conclusion.

## Adjacent stream lifecycle models

Receipt: `receipts/2026-08-01-adjacent-stream-lifecycle-scout.md`.

Environment: Node `v22.16.0` with native Web Streams.

### Async-iterator source-error cleanup

The model copied the exact `createAsyncIterableStream()` / `asAsyncIterableStream()` control flow and compared it with native async iteration plus a minimal catch-and-release candidate.

Observed:

- current SDK helper propagated `Error('source failed')`;
- the returned stream remained locked;
- acquiring another reader failed with `TypeError: Invalid state: ReadableStream is locked`;
- native iteration propagated the same error and left the stream unlocked;
- the candidate caught `reader.read()` rejection, called `cleanup(false)`, rethrew the same error, and left the stream unlocked.

Evidence class: `source-read` plus `model-executed`.

Coverage limit: no target-native Node or Edge test has run. The result supports a separate follow-up, not a change to unit 06.

### Stitchable terminate rejection containment

A raw stream whose underlying `cancel()` rejected produced one modeled `unhandledRejection` when its reader cancellation promise was ignored. One or two identity transform layers contained the rejection.

The relevant `streamText` inner streams cross transform layers before stitchable registration. No product-path failure was demonstrated.

Evidence class: `source-read` plus `model-executed`.

Disposition: retained utility-contract hazard and negative result for unit 06.

### Pre-aborted first provider attempt

Source review shows that pre-aborted `streamText` settles outward state while background setup continues and calls `doStream()` with the already-aborted signal. `generateText` follows the same convention on its first provider attempt and guards only later iterations. The provider V4 contract supplies the signal for cancelling the operation.

Evidence class: `source-read`.

Coverage limit: callback and provider invocation counts have no target-native characterization; expected cross-API semantics remain unresolved.

## Current canonical execution

Exact canonical head: `3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15`.

Owned-fork review PR: `teamleaderleo/ai#13` against current-public-base branch `upstream/06-public-main-base` at `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`.

- Verify Changesets run: `30691402294`
- Ordinary CI run: `30691402306`
- State: queued
- Jobs created: changeset job plus full ordinary repository matrix
- Jobs started: zero
- Classification: execution availability/authorization; no product-test conclusion.

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

The pre-aborted case does not assert counts for `onStart`, `onStepStart`, `onLanguageModelCallStart`, or provider invocation.

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

### Shared iterator test blind spot

`async-iterable-stream.test.ts` verifies source-error propagation and collected chunks. It does not assert reader lock release or a second-reader acquisition after the error.

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
pnpm ultracite check \
  packages/ai/src/generate-text/stream-language-model-call-cancellation.test.ts \
  packages/ai/src/generate-text/stream-text.ts \
  packages/ai/src/generate-text/stream-text-explicit-abort.test.ts \
  packages/ai/src/generate-text/stream-text-explicit-abort-races.test.ts

git diff --check e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0...3035f6e5a3ef6ff9236c8d1b08f4ea3dfe852c15
```

Separate async-iterator follow-up command after a target-native regression exists:

```bash
pnpm --dir packages/ai test:node -- src/util/async-iterable-stream.test.ts
pnpm --dir packages/ai test:edge -- src/util/async-iterable-stream.test.ts
```

## Remaining execution controls

1. Complete Verify Changesets `30691402294` and ordinary CI `30691402306` on exact canonical head.
2. Classify any job failure against the intended assertions and repository setup.
3. Obtain an independent complete-diff disposition on PR #13.
4. Keep committed external tool side effects outside abort-reversal claims.
5. Route the async-iterator lock-release finding through a separate target-native characterization.

## Evidence limits

- The six focused tests exercise target code in Node and Edge at the prior repair diff.
- The cancellation model proves native Web Streams promise behavior and has a canonical target-native regression, whose jobs remain queued.
- The adjacent iterator result is a Node model and source review; target-native and Edge execution remain absent.
- The pre-aborted first-attempt result establishes source ordering, not the intended compatibility contract.
- Current exact-head repository jobs have produced no product result.
- A green package run cannot establish rollback of committed external tool effects.
- Current unit disposition is `HOLD` until exact-head CI and independent acceptance complete.
