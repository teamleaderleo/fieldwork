# AsyncIterableStream read-error cleanup — briefing

Status as of 2026-08-03: **HOLD — exact-head CI and independent final review pending**

## Executive summary

Vercel AI SDK exposes several streaming results as objects that are simultaneously a Web `ReadableStream` and an `AsyncIterable`. The shared adapter acquires a stream reader when iteration starts and normally releases that reader when iteration finishes, exits early, or is explicitly thrown out of.

There is one missing path: when `reader.read()` itself rejects because the source stream errors, the rejection escapes before cleanup runs. The consumer sees the correct source error, but the adapter retains the reader lock. The object therefore remains locked after failure even though the iterator has no useful work left to do.

The proposed fix is intentionally small:

```ts
try {
  const { done, value } = await reader.read();
  // existing success path
} catch (error) {
  await cleanup(false);
  throw error;
}
```

It uses the existing idempotent cleanup routine, releases the reader without cancelling an already-errored stream, and rethrows the exact original reason.

The code-level case is strong. The remaining reasons to hold are procedural and evidentiary: current-head hosted CI has not started, the corrected focused execution carrier is queued, and no independent final review has arrived.

## What this object is

`AsyncIterableStream<T>` is not merely an internal iterator. It is a public combination of:

- `ReadableStream<T>` — callers can use `getReader()`, `cancel()`, piping, and lock state;
- `AsyncIterable<T>` — callers can consume it with `for await`.

The helper sits below multiple public streaming surfaces, including text generation, object generation, agents, UI-message streams, transcription, translation, workflows, and test harnesses. That makes reader ownership part of observable behavior: a leaked lock prevents later stream operations and changes how the object behaves after an error.

## The defect

The iterator currently follows this lifecycle:

1. Acquire a reader with `stream.getReader()`.
2. On normal completion, call cleanup.
3. On `return()`, call cleanup.
4. On iterator `throw()`, call cleanup.
5. On a rejected `reader.read()`, do nothing before rethrowing.

The fifth case is asymmetric. Error propagation is correct, but ownership cleanup is skipped.

The unfixed reproduction shows both construction paths behaving the same way:

- the exact source error reaches the consumer;
- `stream.locked` remains `true`;
- `stream.getReader()` fails with an invalid-state error;
- later `next()` calls continue to encounter the source error instead of observing a terminal iterator.

## Why we are doing this

The objective is not to suppress errors or make a failed stream reusable. The objective is to end the iterator's ownership cleanly after the failure.

After a source stream has errored:

- the source error should remain the observable failure;
- the iterator should no longer own a reader;
- later iterator calls should be terminal;
- other stream APIs should not be blocked by a stale reader lock;
- cleanup should not introduce a second cancellation operation against an already-terminal source.

This is a resource-lifecycle correction. It aligns the rejected-read path with the helper's stated promise of cleanup on completion, early exit, or error.

## Why `cleanup(false)` is the selected solution

The existing cleanup function already provides the right shared machinery:

- an idempotent `finished` guard;
- optional cancellation;
- reader release in a `finally` block;
- defensive handling if lock release is already impossible.

Calling `cleanup(false)` is preferable to adding a separate release path because it preserves the single lifecycle state machine. It is also preferable to `cleanup(true)` because the source is already errored.

That choice follows upstream review precedent. The original iterator-cleanup review explicitly cautioned against calling cancellation after terminal states because behavior can vary across runtimes. A later merged fix made cleanup idempotent rather than adding another special-case state path.

## What changed

Canonical owned candidate: `teamleaderleo/ai#14`

Public-base mirror:

`3bc0d4f40df7a77af4b181bc97dc1c54843545ab`

Current canonical source head:

`be190b928918eb75bf550cc8e92305f57b126392`

Final three-file fence:

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

The production diff is limited to catching the rejected read, invoking `cleanup(false)`, and rethrowing the same reason.

A complete-diff review found that two workers had independently added changesets after an earlier changeset-gate failure. The duplicate was removed. The final branch contains one patch changeset.

## Test coverage

The focused tests exercise both exported construction paths:

- `createAsyncIterableStream()`;
- `asAsyncIterableStream()`.

They verify:

- exact identity of a non-`Error` object reason;
- preservation of an `undefined` error reason;
- reader-lock release;
- zero source cancellation calls after source failure;
- terminal later `next()` and `return()` calls;
- reader reacquisition after cleanup, with the stream still reporting its original error;
- two concurrent pending reads rejecting with the same original error.

The Node and Edge Vitest configurations collect the focused test file. A dependency-free Node 22 baseline model reproduces the defect, and a candidate model demonstrates the intended lifecycle.

## What other upstream work says

I reviewed three relevant upstream changes without posting or reacting publicly.

### Loop-breaking cleanup — upstream PR 8220

This introduced `return()`, `throw()`, and the shared cleanup structure. Its review discussion established an important boundary: do not casually call cancellation after a stream has reached a terminal state, because runtime behavior may differ.

### Idempotent cleanup — upstream issue 11715 and PR 11716

A real consumer reported that calling `return()` after normal completion ran cleanup twice and threw because the reader was detached. Upstream treated it as a high-confidence bug. The merged repair added the `finished` guard, a direct regression test, and a patch changeset.

Our finding is the remaining symmetric gap: cleanup is now safe once entered, but a rejected source read never enters it.

### Direct stream ownership — upstream PR 17182

This merged transcription fix treats stream ownership as an explicit contract. It avoids replay buffering for unbounded live streams, enforces a single owner, preserves backpressure and cancellation, and includes Node 26 unhandled-rejection protections. It passed the full AI package Node and Edge suite and received maintainer approval.

That work reinforces the design principle behind this candidate: stream ownership must be explicit, terminal, and released correctly. Our fix operates one layer lower and does not alter any public API.

Upstream references:

- https://redirect.github.com/vercel/ai/pull/8220
- https://redirect.github.com/vercel/ai/issues/11715
- https://redirect.github.com/vercel/ai/pull/11716
- https://redirect.github.com/vercel/ai/pull/17182

## Current verification state

Established evidence:

- Public `main` still contains the rejected-read cleanup gap.
- Refreshed exact-duplicate issue and PR searches returned no active match.
- The unfixed Node 22 model reproduces the lock leak for both helper variants.
- The candidate Node 22 model releases ownership while preserving exact reasons.
- A narrower previous candidate passed full repository CI across Node 22, 24, and 26, plus type checks, builds, lint/format, consistency checks, codemods, and examples.
- The current final compare is clean and contains one changeset, one focused test file, and one production file.

Pending evidence:

- Exact-head ordinary CI run `30754625714` is queued.
- Corrected focused execution run `30759467232` is queued.
- The earlier focused carrier pointed at superseded head `147e4066...`; it has been corrected to checkout `be190b928...`, and the old receipt must not be used.
- No independent final review has arrived on the canonical candidate.
- Commit-signature verification remains open.
- Bun and Deno behavior has not been directly executed.

## Current judgment

The repair is technically coherent and appropriately scoped. I do not currently see a better production design than reusing `cleanup(false)` around the rejected read.

The strongest arguments in favor are:

- it closes a real ownership leak demonstrated by an unfixed control;
- it preserves the exact source failure;
- it does not add cancellation or public behavior beyond releasing a stale lock;
- it follows the helper's existing lifecycle model and upstream review precedent;
- it is covered across both helper paths and concurrency/error-shape cases.

The strongest arguments for caution are:

- exact final-head CI has not executed;
- no independent reviewer has challenged the concurrency and runtime assumptions;
- the operational frequency and user-visible severity are not measured;
- runtime-specific Web Streams behavior outside the tested Node environment remains a boundary.

Therefore the disposition is **HOLD**, not because the fix is currently suspected to be wrong, but because the final evidence and independent review gates are incomplete.

## Questions for our review

1. Is releasing the reader lock after a source error part of the public behavioral contract, or merely internal hygiene?
2. Should later iterator calls be terminal after the first rejected read, or should they continue surfacing the stored source error?
3. Is `cleanup(false)` sufficient across Node, Edge, Bun, and Deno, or do we need runtime-specific controls?
4. Are the concurrent `next()` tests validating supported usage or only defensive behavior?
5. Is a focused utility regression enough, or should one public surface such as `streamText` or `streamTranscribe` get an integration regression?
6. Does the likely impact justify upstream contribution once authorization and evidence gates are cleared?

## Links

- Canonical candidate: https://github.com/teamleaderleo/ai/pull/14
- Corrected execution carrier: https://github.com/teamleaderleo/ai/pull/17
- Evidence and receipts: https://github.com/teamleaderleo/fieldwork/pull/532
- Campaign coordination: https://github.com/teamleaderleo/fieldwork/issues/477

Public upstream interaction remains disabled. No upstream issue, pull request, comment, review, reaction, or email was created.