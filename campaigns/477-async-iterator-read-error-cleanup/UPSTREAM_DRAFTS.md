# Upstream issue and pull-request drafts

Status: internal drafts only. No public upstream interaction is authorized by this file.

## Editorial decision

Keep the public issue and pull request self-contained and short.

The current Vercel AI issue form has four relevant fields:

1. Description
2. Reproduction
3. AI SDK Version
4. Code of Conduct

The issue draft below is arranged to paste directly into those fields. Expected behavior, actual behavior, and rationale stay inside the Description field rather than being added as unofficial form sections.

Do not link the internal Fieldwork briefing or evidence report from the public issue or PR. The public issue can cite the relevant upstream source lines, and the PR can carry the focused regression test.

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

A related prior issue fixed a different cleanup asymmetry in the same helper after normal completion:

- https://redirect.github.com/vercel/ai/issues/11715

After the pull request is opened, add this near the top of the Description field:

```md
Regression test and proposed fix: #PR_NUMBER
```

### Reproduction field

This is a repository-level reproduction because `createAsyncIterableStream()` is an internal helper rather than a package-root export.

From a checkout of `vercel/ai`, save the following as `repro.ts` in the repository root and run `pnpm exec tsx repro.ts`:

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
console.log(observedError === sourceError); // true
console.log(stream.locked); // true

stream.getReader(); // TypeError: Invalid state: ReadableStream is locked
```

The focused regression test in the proposed pull request covers both `createAsyncIterableStream()` and `asAsyncIterableStream()`. After the PR is opened, add its issue reference here as well:

```md
Regression test: #PR_NUMBER
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

A minimal Web Streams reproduction was run before and after the change.

Before the change, the source error reached the iterator but the stream remained locked, so a later `getReader()` failed.

After the change, the same error is preserved, the stream becomes unlocked, a new reader can be acquired, and that reader still observes the source's stored error.

The signed exact-head CI run `30838351122` passed.

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
2. Open the issue using the field-aligned draft above.
3. Open the pull request from signed head `7291578cc24f39dcfe68fa4c56778a46513fae34` to upstream `main` after explicit authorization.
4. Replace `#ISSUE_NUMBER` in the PR body.
5. Add `Regression test and proposed fix: #PR_NUMBER` near the top of the issue Description field and `Regression test: #PR_NUMBER` in its Reproduction field.
