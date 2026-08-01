# Zustand clear-storage hydration ordering

## In simple words

Zustand's persist middleware already uses a generation counter so a newer `rehydrate()` call can invalidate older in-flight hydration work. The public `clearStorage()` operation removes the stored entry but does not advance that generation.

This experiment asks whether a stored read or migration that began before `clearStorage()` can still apply the just-cleared snapshot to live store state afterward.

The question is narrow. `clearStorage()` is not assumed to reset state that was already live before the clear. Ordinary asynchronous write completion, storage replacement through `setOptions`, and application-level sign-out sequencing are excluded.

## State

`running`

Last updated: `2026-08-01`  
Owner: `chatgpt:gpt-5.6-thinking`  
Claim scope: `mechanism`  
Upstream contact authorized: `no`

## Why this target

The current npm package page reports roughly 46–48 million weekly downloads for Zustand, compared with roughly 4.1 million for Jotai. Zustand is therefore the hotter same-vein state-management target inspected in this pass.

Popularity is only a targeting signal; it is not evidence that the behavior is common or severe.

## Exact subject

- Target: `pmndrs/zustand`
- Pinned public source: `beca84e600e4e250f6b244d22878e72948f331c7`
- Clean fork base branch: `teamleaderleo/zustand:base/upstream-20260801`
- Characterization branch: `teamleaderleo/zustand:scout/persist-clear-storage-hydration-ordering`
- Characterization head: `9c5039ebf594f15b0fbb5d5e39d59f4e70dd6e96`
- Characterization draft PR: `teamleaderleo/zustand#4`
- Candidate branch: `teamleaderleo/zustand:fix/persist-clear-storage-hydration-generation`
- Candidate head: `d009aa203e357d83a61350ce85d7db29aa05ff8a`
- Candidate draft PR: `teamleaderleo/zustand#5`

The fork's default branch contains unrelated prior work, so both PRs target the pinned clean base branch instead of fork `main`.

## Source model

At the pinned source:

1. each `hydrate()` call captures `const currentVersion = ++hydrationVersion`;
2. the async read, optional migration, state merge, callbacks, and errors are suppressed when `currentVersion !== hydrationVersion`;
3. `clearStorage()` calls `storage?.removeItem(options.name)` without changing `hydrationVersion`.

Therefore a hydration that began before the clear still retains current publication authority unless another hydration starts.

## Characterization cases

The test-only branch adds `tests/persistClearStorageHydrationOrdering.test.ts` with three deterministic controls:

1. a delayed stored value resolves after `clearStorage()` and becomes live state;
2. a delayed migration resolves after `clearStorage()` and becomes live state;
3. clearing after hydration leaves already-live state unchanged.

The first two assertions describe the source path under test. They are not yet target-executed findings until the exact workflow jobs complete.

## Candidate

The candidate adds one production statement in `clearStorage()`:

```ts
++hydrationVersion
```

This reuses the existing invalidation mechanism. The candidate test covers:

1. delayed stored read suppression;
2. delayed migration suppression;
3. no reset of already-live state;
4. successful later rehydration after the older work was invalidated.

Relative to the pinned source, the candidate is two commits, ahead by two and behind by zero, changing exactly:

- `src/middleware/persist.ts` — one addition;
- `tests/persistClearStorageHydrationGeneration.test.ts` — 139 additions.

## Current execution

### Characterization head `9c5039e...`

- Test Multiple Versions `30692436573` — queued at last check;
- Test Old TypeScript `30692436571` — queued;
- Test `30692436576` — queued;
- Preview Release `30692436570` — queued;
- Test Multiple Builds `30692436591` — queued;
- Compressed Size `30692436621` — queued.

### Candidate head `d009aa2...`

- Preview Release `30692520832` — queued at last check;
- Test Old TypeScript `30692520845` — queued;
- Compressed Size `30692520829` — queued;
- Test Multiple Versions `30692520839` — queued;
- Test Multiple Builds `30692520824` — queued;
- Test `30692520819` — queued.

No execution conclusion is claimed while these runs are queued.

## Prior-art and ownership check

- Zustand PR `#3336` introduced the current hydration generation specifically for concurrent `rehydrate()` calls.
- Searches on `2026-08-01` for clear-storage hydration races and equivalent repairs did not surface a current issue or pull request for this exact operation crossing.
- No open Fieldwork lane was found for this exact boundary.

Search can miss differently worded or unindexed discussion and must be repeated before promotion.

## Compatibility and limits

- `clearStorage()` still does not reset already-live state.
- The return type and asynchronous removal behavior are unchanged.
- A later explicit `rehydrate()` remains possible and is covered.
- Storage replacement through `setOptions({ storage })` may have a similar authority question but is excluded from this experiment.
- Ordinary `setItem` completion ordering remains separate.
- No claim is made about prevalence, user impact, or security severity.

## Stop condition

Stop after the characterization and candidate exact-head workflows are classified and their primary test jobs inspected. Do not widen this experiment into general persistence serialization, storage replacement, sign-out APIs, or public upstream contact.
