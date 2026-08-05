# Unit 20 direct-source execution receipt

Date: `2026-08-01`

State: `direct source base accepted; final upstream preparation held for unit 21 sequencing and independent review`

Upstream contact authorized: `false`

## Exact identity

- target repository: `teamleaderleo/jotai`
- public and fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- branch: `fix/key-scoped-json-cache`
- first clean product-and-test generation: `e295dc741a706153b50e7d27fbd424fcc48519cb`
- exact executed carrier head: `ac5dd98da6c3083f31560b71d84ad3bf850aaafc`
- current clean source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`
- owned-fork PR: `teamleaderleo/jotai#1`
- Fieldwork packet PR: `teamleaderleo/fieldwork#441`

## Exact retained source fence

- `src/vanilla/utils/atomWithStorage.ts`
- `tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts`
- `tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts`

The current clean head changes exactly these three files from the selected base.

## Exact execution

Workflow: `30690503592`

| Runtime | Job | Result |
| --- | --- | --- |
| Node 22 | `91344257705` | success |
| Node 24 | `91344257734` | success |
| Node 26 | `91344257736` | success |

Each job ran:

```text
pnpm install --frozen-lockfile
pnpm vitest run \
  tests/react/vanilla-utils/atomWithStorageKeyIsolation.test.ts \
  tests/react/vanilla-utils/atomWithStorageReadInvalidation.test.ts \
  tests/react/vanilla-utils/atomWithStorage.test.tsx
pnpm eslint <three changed files>
pnpm prettier --check <three changed files>
pnpm tsc --noEmit
pnpm run build
```

Each runtime passed:

- 10 key-isolation tests;
- 2 unreadable-state invalidation tests;
- 25 existing atom-with-storage tests;
- 37 total assertions in three files;
- changed-file ESLint;
- changed-file Prettier;
- repository TypeScript checking;
- complete Jotai build.

Existing React `act(...)` warnings appeared in the adjacent async suite. Assertions passed.

## Native workflow classifications

### Test `30690503622`

The carrier generation failed at repository format because temporary `UNIT20_STOP.md` required formatting. Product checks after format were skipped. Classification: execution artifact. Every temporary note was removed from the clean head.

### Preview Release `30690503585`

The complete build passed. Preview publication failed because the `pkg-pr-new` GitHub App is absent on the owned fork. Classification: fork publication setup. No product or build failure.

### Clean-head generation

At the final observation in this receipt, native clean-head runs for `9fb2e455...` were queued:

- Test `30690722042`;
- Test Multiple Versions `30690722083`;
- Test Multiple Builds `30690722063`;
- Test Old TypeScript `30690722057`;
- Compressed Size `30690722050`;
- Preview Release `30690722061`.

A later handoff must update their final states without rewriting this historical receipt.

## Cleanup

Removed after receipt transfer:

- `.github/workflows/unit20-direct-source.yml`;
- all root `UNIT20_*.md` execution notes.

Current clean source head: `9fb2e455ed844d0fb248823009714ab5084d06fc`.

## Evidence boundary

This receipt accepts unit 20's direct-source key-scoped cache base. It does not claim:

- stale asynchronous completion generation fencing;
- read versus `setItem` operation ordering;
- browser or React Native integration;
- production prevalence;
- retained-memory bounds;
- public upstream acceptance.

Unit 21 owns the accepted asynchronous generation repair. Final public preparation requires one reviewed source-head or stack decision covering that dependency.
