# AsyncIterableStream read-error cleanup — final briefing

Status as of 2026-08-04: **FIELDWORK COMPLETE / UPSTREAM REVIEW PENDING**

## Outcome

The reviewed fix was submitted publicly to Vercel AI SDK:

- Issue: https://redirect.github.com/vercel/ai/issues/18370
- Pull request: https://redirect.github.com/vercel/ai/pull/18371

The issue and pull request are cross-linked. The pull request is open, mergeable, and contains one signed commit with exactly three changed files.

## Bug

The original code awaited the reader before any error cleanup:

```ts
const { done, value } = await reader.read();

if (done) {
  await cleanup(true);
  return { done: true, value: undefined };
}
```

When `reader.read()` rejected, control left `next()` before cleanup ran:

```text
source stream errors
        ↓
reader.read() rejects
        ↓
next() exits before cleanup
        ↓
caller receives the original error
        ↓
reader lock remains held
        ↓
stream stays locked
```

## Submitted fix

```text
source stream errors
        ↓
reader.read() rejects
        ↓
cleanup(false)
        ↓
reader lock is released without cancellation
        ↓
caller receives the original error
        ↓
later calls on that iterator return done: true
```

The stream remains errored, and a newly acquired reader still receives its stored source error.

## Final candidate

- Owned source PR: `teamleaderleo/ai#14`
- Branch: `fix/async-iterable-stream-read-error-cleanup`
- Signed public head: `fd6335acd351b4c00824d8b2e68d1fab40053c86`
- Public upstream base at PR creation: `9337ecd0f91aed0eaccdbd4b818c7b048d76bb31`
- Commit count: one
- Changed files: three
- Diff: 141 additions, 6 deletions

Files:

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

## Verification

The focused tests cover both `createAsyncIterableStream()` and `asAsyncIterableStream()` across six cases:

- source error after emitted data;
- an `undefined` error reason;
- concurrent pending reads;
- exact error preservation;
- lock release without cancellation;
- terminal later iterator calls;
- reader reacquisition with the stored stream error still present.

The prior signed exact-head CI passed. The final head was rebuilt as one signed commit and replayed onto current upstream `main` before publication. A local baseline run showed all six regression cases failing on the unfixed implementation, and the saved output was attached to the public issue.

Public upstream workflows currently require upstream approval/action. That is a fork-permission gate, not a reported product-test failure.

## Publication sequence

1. Refreshed upstream `main` and overlap search.
2. Rebuilt and verified the single signed commit.
3. Reconfirmed the exact three-file fence.
4. Opened the public issue.
5. Opened the public pull request from the fork branch to `vercel/ai:main`.
6. Cross-linked both public records.

No merge or further upstream interaction was performed.

## Final record

See `FINAL_OUTCOME.md` for the concise campaign closeout.
