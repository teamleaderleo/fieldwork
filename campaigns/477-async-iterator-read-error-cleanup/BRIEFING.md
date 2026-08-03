# AsyncIterableStream read-error cleanup — reviewer briefing

Status as of 2026-08-03: **ACCEPT / TECHNICALLY READY**

Public-upstream submission is not authorized. Commit-signature verification remains open.

## Executive summary

Vercel AI SDK exposes several streaming results as objects that are both a Web `ReadableStream` and an `AsyncIterable`. Async iteration acquires a stream reader. The adapter already releases that reader after normal completion, early return, and explicit iterator failure.

One terminal path is missing: when `reader.read()` rejects because the source stream errors, the rejection escapes before cleanup. The consumer receives the correct error, but the failed iterator retains the reader lock.

That leaves the object in an inconsistent state: the consuming operation has ended in failure and cannot continue usefully, yet it still owns the stream reader.

The candidate closes that missing branch:

```ts
try {
  const { done, value } = await reader.read();
  // existing success path
} catch (error) {
  await cleanup(false);
  throw error;
}
```

The stream remains errored. The patch does not recover it, suppress its failure, or introduce cancellation. It releases stale ownership, preserves the exact source reason, and makes the failed iterator terminal.

## What the object is

`AsyncIterableStream<T>` combines two public interfaces:

- `ReadableStream<T>`: callers can acquire readers, inspect `locked`, cancel, or pipe the stream;
- `AsyncIterable<T>`: callers can consume values using `for await`.

The iterator side implements consumption by acquiring a `ReadableStreamDefaultReader`. That reader has exclusive ownership while attached, so cleanup is observable: a leaked lock prevents later stream operations.

## Current defect

The existing lifecycle is:

1. acquire a reader;
2. clean up after normal completion;
3. clean up after `return()`;
4. clean up after iterator `throw()`;
5. skip cleanup when `reader.read()` rejects.

The fifth path is the defect. Error propagation is already correct; ownership cleanup is not.

In the unfixed behavior:

- the exact source error reaches the consumer;
- `stream.locked` remains `true`;
- `stream.getReader()` fails because the old iterator still owns the lock;
- later calls continue through a terminally broken iterator state.

## Behavioral change

Before:

```text
read rejects
→ exact source error reaches caller
→ reader remains attached
→ stream remains locked
```

After:

```text
read rejects
→ cleanup(false)
→ reader lock is released
→ exact source error reaches caller
→ old iterator is terminal
```

A newly acquired reader still observes the stream's stored source error. Releasing the lock does not make the stream healthy again.

The deliberate semantic choice is that the operation that encounters the failure receives it once; later calls on that same iterator observe terminal completion rather than repeatedly operating through the failed reader.

## Why `cleanup(false)`

The helper already has one idempotent cleanup routine with:

- a `finished` guard;
- optional cancellation;
- reader release in a `finally` block;
- defensive handling around lock release.

Using `cleanup(false)` keeps one lifecycle state machine. The `false` avoids cancelling an already-errored source, which would be redundant and can vary across Web Streams runtimes.

A separate release-only branch would duplicate lifecycle logic. `cleanup(true)` would add an unnecessary terminal-state cancellation.

## Exact candidate

Canonical owned draft:

- https://github.com/teamleaderleo/ai/pull/14

Pinned public-base mirror:

- `3bc0d4f40df7a77af4b181bc97dc1c54843545ab`

Exact candidate head:

- `be190b928918eb75bf550cc8e92305f57b126392`

Final three-file fence:

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

The compare is seven commits ahead and zero behind the pinned base, with no unrelated files.

## Test coverage

Both exported helper paths are covered:

- `createAsyncIterableStream()`;
- `asAsyncIterableStream()`.

The six focused cases verify:

- exact identity of a non-`Error` object reason;
- preservation of an `undefined` reason;
- release of the reader lock;
- no source cancellation after source failure;
- terminal later `next()` and `return()` calls;
- reader reacquisition with the original stream error still present;
- idempotent behavior for concurrent pending reads.

## Verification

The exact candidate head passed the ordinary repository CI matrix, including:

- AI test shards on Node 22, 24, and 26;
- TypeScript;
- package builds;
- lint and formatting;
- code consistency;
- codemods;
- example builds.

A focused carrier checked out the exact candidate and passed:

- dependency-closure build;
- Node execution, including all six focused cases;
- Edge execution, including all six focused cases;
- package type-checking;
- formatting and linting.

That carrier's displayed failure came only from its final `git diff --check` command. The workflow used `fetch-depth: 1`, so the pinned base commit was unavailable and Git could not resolve the symmetric-difference expression. This was a carrier configuration error, not a product failure.

## Review conclusion

The designated human reviewer accepted the behavioral model:

- this is a missing terminal-error cleanup case, not a redesign;
- the exact error should still be reported;
- the failed iterator should relinquish reader ownership;
- the already-errored source should not be cancelled again;
- subsequent calls on that iterator should be terminal.

Complete-diff review found no blocking source defect. The exact head and three-file fence remain unchanged after review and CI.

## Upstream alignment

The owned PR body now follows Vercel AI's current pull-request template sections: Background, Summary, End-to-End Verification, Checklist, and Related Issues.

Relevant upstream precedent supports the selected lifecycle:

- https://redirect.github.com/vercel/ai/pull/8220
- https://redirect.github.com/vercel/ai/issues/11715
- https://redirect.github.com/vercel/ai/pull/11716
- https://redirect.github.com/vercel/ai/pull/17182

No exact active public issue or pull request for this rejected-read lock leak was found during the latest overlap check.

## Remaining publication gates

The source is technically ready. It is not publication-ready until:

1. every candidate commit is verified as signed or the candidate is rebuilt with signed commits;
2. the final upstream target is refreshed and checked for overlap or drift;
3. the exact source fence is reconfirmed after any rebuild;
4. explicit authorization is given for public-upstream submission.

## Links

- Candidate draft: https://github.com/teamleaderleo/ai/pull/14
- Evidence PR: https://github.com/teamleaderleo/fieldwork/pull/532
- Campaign issue: https://github.com/teamleaderleo/fieldwork/issues/477

No public upstream issue, pull request, comment, review, reaction, or email has been created.