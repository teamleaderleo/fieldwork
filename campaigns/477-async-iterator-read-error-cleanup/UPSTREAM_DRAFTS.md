# Upstream issue and pull-request drafts

Status: internal drafts only. No public upstream interaction is authorized by this file.

## Editorial decision

Keep the public issue and pull request self-contained and short.

Do not link the internal Fieldwork briefing or evidence repository from the public issue or PR. Those materials are useful for our review record, but maintainers should not need to read an investigation log to verify this change.

The only related public link worth keeping is the directly relevant cleanup precedent in the same helper:

- https://redirect.github.com/vercel/ai/issues/11715

## Issue draft

### Title

`AsyncIterableStream` stays locked after the source stream errors

### Description

When async iteration starts, `AsyncIterableStream` acquires a stream reader. The helper releases that reader after normal completion, early return, and explicit iterator failure.

When the source stream errors, `reader.read()` rejects before cleanup runs. The caller receives the original error, but the failed iterator keeps the reader lock, so the stream remains locked after the consuming operation has ended.

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

The read should reject with the exact source reason, and the failed iterator should release its reader without cancelling the already-errored stream. Later calls on that iterator should be terminal.

The stream should remain errored. Releasing the reader is cleanup, not recovery.

### Actual behavior

The read rejects with the correct source reason, but the reader lock is retained. The stream remains locked, and later stream operations such as `getReader()` fail because the terminal iterator still owns the reader.

### Additional context

This appears to be the missing read-error branch in the helper's existing cleanup lifecycle. A related prior issue fixed repeated cleanup after normal completion:

- https://redirect.github.com/vercel/ai/issues/11715

### AI SDK version

Current `main` at the time of filing.

### Code of Conduct

- [x] I agree to follow this project's Code of Conduct

## Pull-request draft

### Title

fix(ai): release async iterator reader after read errors

### Body

## Background

Closes #ISSUE_NUMBER.

`AsyncIterableStream` releases its reader after normal completion, early return, and explicit iterator failure. A rejected `reader.read()` currently exits `next()` before cleanup runs, so the source error reaches the caller while the failed iterator keeps the stream locked.

## Summary

- run the existing `cleanup(false)` path when `reader.read()` rejects;
- release the reader without cancelling the already-errored stream;
- rethrow the exact original reason;
- make later calls on the failed iterator terminal;
- add regression coverage for both async-iterable stream helpers;
- add a patch changeset for `ai`.

The stream remains errored. This change only releases stale reader ownership.

## End-to-End Verification

A minimal Web Streams reproduction was run before and after the change.

Before the change, the source error reached the iterator but the stream remained locked, so a later `getReader()` failed.

After the change, the same error is preserved, the stream becomes unlocked, a new reader can be acquired, and that reader still observes the source's stored error.

## Checklist

- [x] All commits are signed (PRs with unsigned commits cannot be merged)
- [x] Tests have been added / updated (for bug fixes / features)
- [ ] Documentation has been added / updated (for bug fixes / features)
- [x] A _patch_ changeset for relevant packages has been added (for bug fixes / features - run `pnpm changeset` in the project root)
- [x] I have reviewed this pull request (self-review)

## Related Issues

- Closes #ISSUE_NUMBER
- Related cleanup precedent: https://redirect.github.com/vercel/ai/issues/11715

## Publication sequence

1. Refresh upstream `main` and the duplicate search.
2. Open the issue using the draft above.
3. Replace `#ISSUE_NUMBER` in the PR draft.
4. Open the pull request from signed head `7291578cc24f39dcfe68fa4c56778a46513fae34` to upstream `main` only after explicit authorization.

Signed-head CI run `30838351122` passed.