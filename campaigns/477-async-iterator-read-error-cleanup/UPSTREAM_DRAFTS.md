# Upstream issue and pull-request drafts

Status: internal drafts only. No public upstream interaction is authorized by this file.

## Recommendation

Open a concise bug issue first, then open the pull request linked to it.

Vercel AI's contribution guide says a high-quality issue is often the most useful contribution and asks contributors to consider opening or improving an issue before investing in a full bug-fix implementation. An issue also gives maintainers a stable reproduction and a place to classify the behavior independently from the proposed implementation.

This does not need to be presented as a major production incident. The accurate claim is narrower: the behavior is reproducible on current `main`, the helper's cleanup lifecycle omits one terminal path, and the patch closes that path.

The latest overlap search found no exact issue or pull request for a rejected `reader.read()` retaining the async iterator's reader lock.

Adjacent, non-duplicate context:

- https://redirect.github.com/vercel/ai/issues/11715 reports a different cleanup asymmetry in the same helper: repeated cleanup after normal completion.
- https://redirect.github.com/vercel/ai/issues/16379 reports a different reader-ownership leak in the harness/codex path that results in `ReadableStream is locked` and obscures an underlying error. It supports the general impact of stale reader ownership but is not the same defect.

## Issue draft

### Title

`AsyncIterableStream` stays locked after the source stream errors

### Description

`AsyncIterableStream` acquires a reader when async iteration begins and releases it after normal completion, early return, and explicit iterator failure.

When the source stream errors, `reader.read()` rejects. That rejection currently exits `next()` before cleanup runs. The caller receives the original source error, but the failed iterator keeps the reader lock, so the stream remains locked after the consuming operation has already ended.

### Reproduction

```ts
import { createAsyncIterableStream } from 'ai';

let controller!: ReadableStreamDefaultController<string>;

const stream = createAsyncIterableStream(
  new ReadableStream<string>({
    start(controllerParam) {
      controller = controllerParam;
    },
  }),
);

const iterator = stream[Symbol.asyncIterator]();
const pendingRead = iterator.next();
const sourceError = new Error('source failed');

controller.error(sourceError);

await pendingRead.catch(error => {
  console.log(error === sourceError); // true
});

console.log(stream.locked); // true
stream.getReader(); // throws because the failed iterator still owns the lock
```

The same behavior occurs through both `createAsyncIterableStream()` and `asAsyncIterableStream()`.

### Expected behavior

The read should reject with the exact source reason, the failed iterator should release its reader without cancelling the already-errored stream, and later calls on that iterator should be terminal.

The stream should remain errored. Releasing the reader is cleanup, not recovery.

### Actual behavior

The read rejects with the correct source reason, but the reader lock is retained. The stream remains locked and later stream operations such as `getReader()` fail because the terminal iterator still owns the reader.

### Additional context

This appears to be the missing terminal-error branch in the helper's existing cleanup lifecycle. A related prior issue fixed repeated cleanup after normal completion, but the rejected-read path still never enters cleanup:

- https://redirect.github.com/vercel/ai/issues/11715

### AI SDK version

Current `main` at the time of filing. Reproduction was confirmed against the current helper implementation.

### Code of Conduct

- [x] I agree to follow this project's Code of Conduct

## Pull-request draft

### Title

fix(ai): release async iterator reader after read errors

### Body

## Background

Closes #ISSUE_NUMBER.

`AsyncIterableStream` acquires a stream reader during async iteration. The helper already releases that ownership after normal completion, early return, and explicit iterator failure.

A rejection from `reader.read()` currently exits `next()` before cleanup runs. The source error reaches the caller, but the failed iterator retains the reader lock and leaves the stream locked.

## Summary

- catch rejected reads inside `next()`;
- call the existing idempotent `cleanup(false)` path;
- release the reader without cancelling an already-errored source;
- rethrow the exact original reason;
- make subsequent calls on the failed iterator terminal;
- add regression coverage for both async-iterable stream helpers;
- add a patch changeset for `ai`.

The stream remains errored after cleanup. This change releases stale ownership; it does not recover the stream or suppress its failure.

## End-to-End Verification

A dependency-free Web Streams reproduction was run before and after the change.

Before the change, the source error reached the iterator but the stream remained locked, so a later `getReader()` failed.

After the change, the same error is preserved, the stream becomes unlocked, a new reader can be acquired, and that reader still observes the source's stored error.

## Checklist

- [x] All commits are signed (PRs with unsigned commits cannot be merged)
- [x] Tests have been added / updated (for bug fixes / features)
- [ ] Documentation has been added / updated (for bug fixes / features)
- [x] A _patch_ changeset for relevant packages has been added (for bug fixes / features - run `pnpm changeset` in the project root)
- [x] I have reviewed this pull request (self-review)

## Future Work

None currently identified.

## Related Issues

- Closes #ISSUE_NUMBER
- Related cleanup precedent: https://redirect.github.com/vercel/ai/issues/11715

## Publication sequence

1. Wait for signed-head CI to complete on `7291578cc24f39dcfe68fa4c56778a46513fae34`.
2. Refresh upstream `main` and the duplicate search.
3. Open the issue using the concise draft above.
4. Replace `#ISSUE_NUMBER` in the PR draft.
5. Open the pull request from the signed branch to upstream `main` only after explicit authorization.
