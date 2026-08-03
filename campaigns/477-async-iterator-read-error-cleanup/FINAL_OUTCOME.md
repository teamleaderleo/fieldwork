# Campaign 477 final outcome

Status as of 2026-08-04: **FIELDWORK COMPLETE / UPSTREAM REVIEW PENDING**

## Public submission

- Upstream issue: https://redirect.github.com/vercel/ai/issues/18370
- Upstream pull request: https://redirect.github.com/vercel/ai/pull/18371

The issue and pull request were opened on 2026-08-04. The issue links to the pull request, and the pull request closes the issue.

## What was submitted

The patch handles the one missing cleanup path in `AsyncIterableStream`:

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

The stream remains errored. A newly acquired reader still receives the stored source error.

## Final source fence

Signed public head:

- `fd6335acd351b4c00824d8b2e68d1fab40053c86`

Branch:

- `teamleaderleo:fix/async-iterable-stream-read-error-cleanup`

Changed files:

1. `.changeset/quiet-stream-errors-release.md`
2. `packages/ai/src/util/async-iterable-stream-read-error.test.ts`
3. `packages/ai/src/util/async-iterable-stream.ts`

The public pull request contains one commit, three files, 141 additions, and 6 deletions.

## Verification and evidence

- The signed commit was verified locally with the configured ED25519 signing key.
- The previous exact signed-head CI completed successfully.
- The rebased head was checked as one signed commit with the same three-file fence.
- The focused regression test was run against the unfixed upstream baseline and produced six expected failures across both helper implementations.
- The public issue includes the reproduction, pinned test source, and saved terminal screenshot.
- Public upstream workflows are currently waiting on upstream approval/action rather than reporting a product-test failure.

## Publication notes

1. The candidate was rebuilt as a single signed commit.
2. It was replayed onto the then-current upstream `main`.
3. The issue was opened first.
4. The pull request was opened immediately afterward from the fork branch to `vercel/ai:main`.
5. The issue and pull request were cross-linked.
6. No upstream merge, review, comment, reaction, or follow-up action was performed after submission.

## Current boundary

The Fieldwork campaign is complete because the researched and reviewed contribution has been publicly submitted.

The upstream issue and pull request remain open for Vercel maintainers. They should not be merged, rebased, force-pushed, or otherwise changed unless upstream requests it or a real conflict appears.
