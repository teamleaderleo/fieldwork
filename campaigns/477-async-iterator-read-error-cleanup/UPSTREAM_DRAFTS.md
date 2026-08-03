# Upstream submission record

Status as of 2026-08-04: **PUBLISHED**

The drafts in this file were used to open:

- Issue: https://redirect.github.com/vercel/ai/issues/18370
- Pull request: https://redirect.github.com/vercel/ai/pull/18371

## Final issue

Title:

`AsyncIterableStream` stays locked after the source stream errors

The published issue includes:

- two pinned upstream source links;
- a before/after control-flow diagram;
- a small reproduction;
- the focused regression-test source;
- a saved terminal screenshot showing six failures on the unfixed baseline;
- `ai: 7.0.48` as the reproduced version;
- a direct reference to the proposed pull request.

## Final pull request

Title:

`fix(ai): release async iterator reader after read errors`

Public head:

- `fd6335acd351b4c00824d8b2e68d1fab40053c86`

Public branch:

- `teamleaderleo:fix/async-iterable-stream-read-error-cleanup`

Public base:

- `vercel/ai:main`

The pull request contains one signed commit and exactly three files:

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

It closes issue `#18370` and links the relevant cleanup precedent:

- https://redirect.github.com/vercel/ai/issues/11715

## Published explanation

Current behavior:

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

Submitted behavior:

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

## Current state

The Fieldwork publication task is complete. The public issue and pull request remain open for upstream review.

Do not modify, rebase, force-push, merge, comment, review, or react upstream unless requested by maintainers or explicitly authorized for a concrete follow-up.
