# Upstream pull-request draft — fix(utils): fence stale async JSON reads by per-key generation

Draft status: `not ready — exact-head workflows and independent review pending`  
Proposed head: `teamleaderleo/jotai:fix/utils-async-read-generation` at `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`  
Proposed base: `teamleaderleo/jotai:fix/utils-key-scoped-json-cache` at `b2f84273b53bbed9df073354dac503e520be7101`, itself based on `pmndrs/jotai:main` at `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Public interaction authorized: `no`

---

## Summary

- Track read publication authority independently for each JSON storage key.
- Prevent older asynchronous reads from replacing cache identity selected by a newer read or completed removal.
- Preserve caller-visible backend results, errors, stored JSON bytes, and existing same-string identity reuse.

## Problem

`createJSONStorage()` memoizes parsed JSON values. With an asynchronous backend, each read owns a parse closure that can update the shared parsed-value cache when its promise settles.

An older read can settle after a newer read and replace the cached identity chosen by the newer operation. A read started before removal can also settle after removal and repopulate the cache. Later reads then observe identity selected by stale completion order.

## Change

Add an adapter-local generation map keyed by storage key.

- Every `getItem()` captures a newly advanced generation.
- A successful parse publishes cache identity only while that generation remains current.
- A malformed result deletes cache identity only while that generation remains current.
- Completed removal invalidation advances the same generation before deleting the affected cache entry.

The generation controls shared publication only. Each caller continues to receive its own backend operation result under the existing rule that equal serialized bytes may reuse current cached identity.

## Tests

The target branch adds eleven deterministic regressions covering:

- reverse same-key completion;
- reads crossing completed removal;
- newer missing and malformed results;
- stale malformed completion;
- rejected reads with and without prior cache identity;
- recovery after rejection;
- unrelated-key isolation;
- same-string stale-caller identity reuse.

Focused command:

```text
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
```

Project gates:

```text
pnpm run fix:format
pnpm run build
pnpm run test
```

The owned-fork pull request has triggered the repository's existing Test, multiple-version, old-TypeScript, multiple-build, compressed-size, and preview-release workflows. Their final exact-head conclusions must be inserted here before filing.

## Compatibility

- public API: unchanged
- existing behavior retained: unchanged same-key serialized data can reuse parsed identity
- stored data: unchanged JSON format and bytes
- platform or runtime notes: uses `Map` and numeric counters only
- performance or allocation notes: one generation entry per observed key and one increment per read or terminal removal invalidation
- migration or rollback: no migration; reverting this commit restores completion-order publication while retaining the prerequisite per-key cache

## Alternatives considered

- Latest-promise identity can suppress old read completions, but completed removal has no natural promise identity and requires additional sentinel state.
- A generation covering reads, writes, removals, and subscription events would answer a broader operation-ordering question and changes more behavior than this fix requires.

## Limits

- This pull request intentionally leaves `setItem()` and subscription-event ordering unchanged.
- It depends on the per-key JSON cache change and should be submitted as a stacked pull request unless that prerequisite has already merged.
- Application frequency and dynamic-key memory growth remain unmeasured.

## Related work

- Jotai issue #1079 and pull request #1080 introduced parsed identity reuse for mount/subscription consistency. This change preserves that same-key behavior while ordering asynchronous cache publication.

---

## Submission checklist

- [x] Owned Jotai fork exists.
- [x] Unit 20 has one clean source branch on the exact inspected upstream base.
- [x] Unit 21 is a clean child of unit 20.
- [x] Unit 21 diff contains exactly one production file and one native test file.
- [x] Commit history contains one focused fix commit and one focused test commit.
- [x] Expanded eleven-case native test is present at the exact proposed head.
- [ ] Exact-head workflows completed and actual test/build coverage was recorded.
- [ ] `pnpm run fix:format`, `pnpm run build`, and `pnpm run test` coverage was confirmed at the exact proposed head.
- [ ] Complete current diff received independent review.
- [ ] Current duplicate and overlap search was repeated.
- [x] Commit history and title follow the current conventional-commit guidance.
- [ ] Current contribution and AI-disclosure policies were checked immediately before filing.
- [ ] Exact user authorization to open the public pull request is recorded.
