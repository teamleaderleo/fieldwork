# Mechanism lane — release async iterator readers after source errors

## In simple words

AI SDK turns many `ReadableStream` results into objects that can also be consumed with `for await`. The iterator owns a stream reader and promises to release it when iteration ends. Today it releases the reader after normal completion and explicit iterator cleanup, but a source-stream error escapes directly from `reader.read()` and leaves the reader attached. The consumer receives the correct error while the stream stays locked.

The selected repair catches only that rejected read, marks the iterator finished, releases the reader without cancelling an already-errored stream, and rethrows the exact original reason. A clean owned-fork candidate now carries this repair, broader Node/Edge-ready tests for both helper variants, and the required patch changeset. Exact-head CI is running.

## Assignment

- Fieldwork campaign: [`teamleaderleo/fieldwork#477`](https://github.com/teamleaderleo/fieldwork/issues/477)
- Programme: [`#13`](https://github.com/teamleaderleo/fieldwork/issues/13)
- Target hub: [`#2`](https://github.com/teamleaderleo/fieldwork/issues/2)
- Worker: OpenAI
- Claim scope: mechanism and public stream interface
- Upstream contact authorized: `false`
- Public upstream interaction performed: none

## Exact revisions

- Current public source inspected: [`vercel/ai@3bc0d4f40df7a77af4b181bc97dc1c54843545ab`](https://github.com/vercel/ai/commit/3bc0d4f40df7a77af4b181bc97dc1c54843545ab)
- Owned base branch: `teamleaderleo/ai:upstream/async-iterable-read-error-base`
- Owned base head: `3bc0d4f40df7a77af4b181bc97dc1c54843545ab`
- Owned candidate branch: `teamleaderleo/ai:fix/async-iterable-stream-read-error-cleanup`
- Current candidate head: [`2fdb5921a16c08e341861e5674feba5bb7cbaa9c`](https://github.com/teamleaderleo/ai/commit/2fdb5921a16c08e341861e5674feba5bb7cbaa9c)
- Owned review PR: [`teamleaderleo/ai#14`](https://github.com/teamleaderleo/ai/pull/14)
- Previous candidate head: `1d7941fc689c8378dc0352ae49517e422af75622`
- Retained model environment: Linux, Node `v22.16.0`
- Retrieval and execution date: `2026-08-02`

## Target instructions and conventions applied

Current target guidance requires:

- Node 22, 24, and 26 compatibility;
- colocated Vitest tests for behavioral changes;
- a patch changeset for production changes in published packages;
- a narrow, backward-compatible repair;
- full type, build, lint/format, consistency, and test validation;
- signed commits before an eventual public pull request;
- high-quality reproductions and failing tests as useful contribution artifacts.

The target's project philosophy favors focused changes and stable public APIs. No ADR governs this helper. The current candidate changes no signature, export, or provider contract.

## Source map

### Owning helper

[`packages/ai/src/util/async-iterable-stream.ts`](https://github.com/vercel/ai/blob/3bc0d4f40df7a77af4b181bc97dc1c54843545ab/packages/ai/src/util/async-iterable-stream.ts)

- `createAsyncIterableStream()` adds one identity `TransformStream`, then delegates to `asAsyncIterableStream()`.
- `asAsyncIterableStream()` attaches `[Symbol.asyncIterator]` to a fresh stream.
- Each iterator owns one `ReadableStreamDefaultReader`.
- `cleanup(cancelStream)` is idempotent, optionally calls `reader.cancel()`, and always attempts `reader.releaseLock()`.
- `next()` checks `finished`, awaits `reader.read()`, and calls cleanup after `{ done: true }`.
- `return()` and `throw()` call cleanup for explicit early termination.
- Before the candidate, rejection from `reader.read()` bypasses cleanup.

### Existing tests

[`packages/ai/src/util/async-iterable-stream.test.ts`](https://github.com/vercel/ai/blob/3bc0d4f40df7a77af4b181bc97dc1c54843545ab/packages/ai/src/util/async-iterable-stream.test.ts)

The existing source-error test proves propagation and collected values. It does not inspect the lock, reacquire a reader, distinguish exact unknown reasons, check cancellation, or exercise concurrent pending reads.

### Usage surface

Repository search found the helper on streaming results and adapters including text, object, agent, UI-message, workflow, transcription, and translation paths. This establishes a shared interface surface. It does not establish how often callers reuse a stream after catching an upstream error.

## Current behavior

Given a stream that emits one chunk and then errors:

1. the async iterator yields the chunk;
2. its next `reader.read()` rejects with the source reason;
3. `next()` propagates that reason;
4. `finished` remains false;
5. `reader.releaseLock()` never runs;
6. the wrapper remains locked;
7. `getReader()` fails with an invalid-state `TypeError`.

The defect is resource ownership after error propagation, rather than error suppression or transformation.

## Governing invariant

Once a source read rejects, that iterator is terminal. It must:

- preserve the exact source reason;
- release its reader lock;
- avoid cancelling a stream that is already errored;
- make later `next()` and `return()` calls idempotently terminal;
- behave consistently through both exported construction paths;
- settle concurrent pending reads without replacing the original source reason.

## Prior art and duplicate result

### Exact overlap

Searches on `2026-08-02` found no active public issue or pull request specifically covering reader-lock retention after `reader.read()` rejects.

Search terms included:

- `"ReadableStream is locked" async iterator`
- `"AsyncIterableStream" "read error"`
- `createAsyncIterableStream error`
- `reader is not attached async iterable`

This is a bounded search result, not proof of uniqueness.

### Directly relevant precedent

- [`vercel/ai#8220`](https://github.com/vercel/ai/pull/8220), merged as `7a2bf8d99074b37d083153bbe835873c78a888ae`, introduced iterator `return()`, `throw()`, and shared cleanup.
- Its review explicitly concluded that cancellation should not be called after normal stream completion because behavior may differ across Node, Bun, and Deno. That supports releasing without cancellation after a source error.
- [`vercel/ai#11715`](https://github.com/vercel/ai/issues/11715) reported that repeated cleanup after normal completion threw. The maintainer classified it as a high-confidence bug.
- [`vercel/ai#11716`](https://github.com/vercel/ai/pull/11716), merged as `d4486d257e823b6edfe82a3d55a4c0f59a86a7ed`, made cleanup idempotent, added a direct regression, and included a patch changeset.

The current finding is the remaining symmetric gap: cleanup is idempotent once entered, while source-read rejection never enters it.

## Reproduction and model execution

Retained runner:

- [`artifacts/read-error-model.mjs`](./artifacts/read-error-model.mjs)
- [`artifacts/read-error-model-result.json`](./artifacts/read-error-model-result.json)

Command:

```sh
node campaigns/477-async-iterator-read-error-cleanup/lanes/mechanism/artifacts/read-error-model.mjs
```

The model mirrors the selected helper control flow and exercises both:

- `createAsyncIterableStream()` with its identity-transform layer;
- `asAsyncIterableStream()` directly.

Observed on Node `v22.16.0`:

- exact object reason preserved: yes;
- stream unlocked after error: yes with candidate;
- source cancellation calls: zero;
- later `next()`: terminal done;
- later `return()`: terminal done;
- reacquired reader receives the same exact error reason;
- two concurrent pending reads both reject with the same original error;
- no added dependency or network access.

Evidence class: `model-executed`.

## Selected implementation

```ts
try {
  const { done, value } = await reader.read();

  if (done) {
    await cleanup(true);
    return { done: true, value: undefined };
  }

  return { done: false, value };
} catch (error) {
  await cleanup(false);
  throw error;
}
```

Why it owns the failure:

- the rejected `reader.read()` is the transition that bypasses cleanup;
- `cleanup(false)` sets the existing terminal latch and releases the reader;
- skipping cancellation matches an already-errored source and related upstream review guidance;
- rethrow preserves the source contract and accepts arbitrary Web Streams error reasons;
- no public API or abstraction changes.

## Target-native candidate

Current three-file fence:

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

The new test file runs four cases:

- wrapped helper preserves an exact non-`Error` reason, unlocks, skips cancellation, supports terminal repeated calls, and allows reader reacquisition;
- direct helper provides the same guarantees;
- wrapped helper settles concurrent pending reads with the original error and unlocks;
- direct helper provides the same concurrent guarantees.

The production diff is five added lines around the existing read path.

## Execution receipts

### Previous head

Head `1d7941fc689c8378dc0352ae49517e422af75622`:

- ordinary CI run `30693740097`: passed;
- AI test shards passed on Node 22, 24, and 26;
- TypeScript, package builds, lint/format, code consistency, codemods, and example builds passed;
- Verify Changesets run `30693740104`, job `91352903452`: failed because package files changed without a `.changeset/*.md` file.

The changeset failure was packaging evidence, not a product-test failure.

### Current head

Head `2fdb5921a16c08e341861e5674feba5bb7cbaa9c`:

- ordinary CI run `30753797999`: queued at report time;
- patch changeset now exists;
- exact-head Verify Changesets receipt had not appeared at report time.

Evidence class: prior head `full-gate` for the repository-declared ordinary CI gate, with current-head execution still pending. The prior gate did not include the broader current test file or current public base.

## Alternatives

### Release the lock in a `finally` around `reader.read()`

Rejected. A `finally` would also release after successful nonterminal reads unless guarded by additional state, obscuring the transition and increasing risk.

### Call `cleanup(true)` after read rejection

Rejected. The stream is already errored. Calling cancellation is unnecessary and conflicts with prior upstream caution around cancellation after terminal states across runtime implementations.

### Call only `reader.releaseLock()`

Rejected. This would unlock the stream while leaving `finished === false`, allowing later iterator calls to attempt reads through a detached reader.

### Convert the error into `{ done: true }`

Rejected. It would suppress a provider or transform failure that the current API already propagates.

### Refactor cleanup into a larger state machine

Deferred. The existing `finished` latch is sufficient for this transition and already has upstream precedent. A broader refactor adds review cost without evidence of another state ambiguity.

### Fold into explicit-abort unit 06

Rejected. This helper defect has a wider owner and API surface, independent source/test files, and separate prior art. Unit 06 remains focused on `streamText` terminal arbitration.

## Compatibility and limits

- Public signatures and exports remain unchanged.
- Successful iteration, early `return()`, explicit iterator `throw()`, and consumer cancellation paths retain their existing code.
- The model and prior CI cover Node. Current CI is expected to exercise Node 22, 24, and 26 plus Edge-configured AI tests.
- No Bun or Deno execution receipt exists.
- Reacquiring a reader after an error does not recover the stream; it exposes the same stored error. The improvement is released ownership and predictable terminal behavior.
- Application frequency and operational impact remain unmeasured.
- Commit-signature verification remains required before any public submission.

## Current disposition

`EXECUTE`

The implementation, changeset, and target-native tests are prepared on the current public base. Exact-head CI and Verify Changesets must complete, followed by independent complete-diff review.

## Continuation handoff

1. Inspect current-head CI run `30753797999` and classify any failure by intended assertion versus harness/setup.
2. Locate or trigger Verify Changesets for exact head `2fdb5921a16c08e341861e5674feba5bb7cbaa9c`.
3. Confirm Node and Edge collection includes `async-iterable-stream-read-error.test.ts`.
4. Review all three changed files against base `3bc0d4f40df7a77af4b181bc97dc1c54843545ab`.
5. Verify commit signatures or rebuild the exact patch as signed commits before public use.
6. Obtain independent disposition on `teamleaderleo/ai#14`.
7. Keep public upstream contact disabled until the user authorizes that exact action.
