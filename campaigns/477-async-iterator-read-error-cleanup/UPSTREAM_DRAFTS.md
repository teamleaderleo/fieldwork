# Upstream issue and pull-request drafts

Status: internal drafts only. No public upstream interaction is authorized by this file.

## Editorial decision

Keep the public issue and pull request self-contained and short.

The current issue form has four relevant fields:

1. Description
2. Reproduction
3. AI SDK Version
4. Code of Conduct

Expected behavior, actual behavior, and rationale stay inside the Description field.

The public issue should use the evidence already collected:

- pinned upstream source links;
- the small reproduction code;
- the focused regression-test source on the signed candidate head;
- the saved terminal screenshot showing all six cases failing on the unfixed baseline.

Do not link the internal Fieldwork briefing or evidence report publicly.

The only related public issue worth keeping is the cleanup precedent in the same helper:

- https://redirect.github.com/vercel/ai/issues/11715

## Issue draft

### Title

`AsyncIterableStream` stays locked after the source stream errors

### Description field

When async iteration starts, [`AsyncIterableStream` acquires a stream reader](https://github.com/vercel/ai/blob/861d42334474f5e411a4b58b741f6ab3c7fb86f3/packages/ai/src/util/async-iterable-stream.ts#L43-L49). The helper documents cleanup on completion, early exit, or error, and its shared cleanup routine marks the iterator as finished and releases the reader lock: [`cleanup()` implementation](https://github.com/vercel/ai/blob/861d42334474f5e411a4b58b741f6ab3c7fb86f3/packages/ai/src/util/async-iterable-stream.ts#L51-L69).

However, when the source stream errors, [`reader.read()` rejects before any cleanup call is reached](https://github.com/vercel/ai/blob/861d42334474f5e411a4b58b741f6ab3c7fb86f3/packages/ai/src/util/async-iterable-stream.ts#L76-L89). The caller receives the original source error, but the failed iterator keeps the reader lock, so the stream remains locked after the consuming operation has ended.

I think a rejected read should enter the same existing cleanup path before its rejection is rethrown. Calling `cleanup(false)` would mark the iterator as finished and release the reader without invoking `reader.cancel()`. The existing [`finished` check](https://github.com/vercel/ai/blob/861d42334474f5e411a4b58b741f6ab3c7fb86f3/packages/ai/src/util/async-iterable-stream.ts#L76-L81) already defines later `next()` calls as terminal, while the current [`return()` and `throw()` paths](https://github.com/vercel/ai/blob/861d42334474f5e411a4b58b741f6ab3c7fb86f3/packages/ai/src/util/async-iterable-stream.ts#L91-L110) establish that terminal iterator paths release their reader ownership.

This would preserve the exact source rejection while making the iterator's ownership state consistent with the helper's other terminal paths.

Regression coverage for this behavior is available on the signed candidate head:

- [read-error cleanup regression test](https://github.com/teamleaderleo/ai/blob/fd6335acd351b4c00824d8b2e68d1fab40053c86/packages/ai/src/util/async-iterable-stream-read-error.test.ts#L1-L125)

A related prior issue fixed a different cleanup asymmetry in the same helper after normal completion:

- https://redirect.github.com/vercel/ai/issues/11715

After the pull request is opened, add this near the top of the Description field:

```md
Regression test and proposed fix: #PR_NUMBER
```

### Reproduction field

A small reproduction against `main` at `861d42334474f5e411a4b58b741f6ab3c7fb86f3`:

```ts
import { createAsyncIterableStream } from './packages/ai/src/util/async-iterable-stream';

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

const observedError = await pendingRead.catch(error => error);
console.log('original error preserved:', observedError === sourceError);
console.log('stream locked:', stream.locked);

stream.getReader();
```

Observed on the unfixed baseline:

```text
original error preserved: true
stream locked: true
TypeError: Invalid state: ReadableStream is locked
```

The focused test covers three source-error scenarios for both `createAsyncIterableStream()` and `asAsyncIterableStream()`:

- [async-iterable-stream-read-error.test.ts](https://github.com/teamleaderleo/ai/blob/fd6335acd351b4c00824d8b2e68d1fab40053c86/packages/ai/src/util/async-iterable-stream-read-error.test.ts#L1-L125)

A local Vitest run against the unfixed baseline produced six failures. In each helper, the source rejection was received but `stream.locked` remained `true` where the test expected the reader to have been released.

Attach the saved terminal screenshot here when filing:

```md
![Six regression cases failing against the unfixed baseline](PASTE_GITHUB_IMAGE_ATTACHMENT_HERE)
```

After the pull request is opened, add:

```md
Proposed fix: #PR_NUMBER
```

### AI SDK Version field

```text
ai: 7.0.48
```

Reproduced against `main` at `861d42334474f5e411a4b58b741f6ab3c7fb86f3`.

### Code of Conduct field

- [x] I agree to follow this project's Code of Conduct

## Pull-request draft

### Title

fix(ai): release async iterator reader after read errors

### Body

## Background

Closes #ISSUE_NUMBER.

`AsyncIterableStream` releases its reader after normal completion, early return, and explicit iterator failure. However, a rejected `reader.read()` currently exits `next()` before cleanup runs, so the source error reaches the caller while the failed iterator keeps the stream locked.

## Summary

- run the existing `cleanup(false)` path when `reader.read()` rejects;
- release the reader without cancelling the already-errored stream;
- rethrow the exact original reason;
- make later calls on the failed iterator terminal;
- add regression coverage for both async-iterable stream helpers;
- add a patch changeset for `ai`.

The stream remains errored after the reader is released, and a newly acquired reader still observes the stored source error.

## End-to-End Verification

The focused regression test was run against the unfixed upstream baseline at `861d42334474f5e411a4b58b741f6ab3c7fb86f3`.

All six cases failed across both helper implementations. The saved terminal output shows that the exact source rejection reached the iterator while `stream.locked` remained `true`.

With this change, the same focused cases pass: the original rejection is preserved, the reader lock is released without cancellation, later calls on the failed iterator are terminal, and a newly acquired reader still observes the stream's stored error.

The rebased signed candidate head is `fd6335acd351b4c00824d8b2e68d1fab40053c86`. Fresh exact-head CI run `30852947280` is queued.

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

1. Refresh upstream `main`, package version, and the duplicate search.
2. Open the issue using the field-aligned draft above and attach the saved failing-test screenshot.
3. Open the pull request from signed head `fd6335acd351b4c00824d8b2e68d1fab40053c86` to upstream `main` after explicit authorization.
4. Replace `#ISSUE_NUMBER` in the PR body.
5. Add `Regression test and proposed fix: #PR_NUMBER` near the top of the issue Description field and `Proposed fix: #PR_NUMBER` in its Reproduction field.
