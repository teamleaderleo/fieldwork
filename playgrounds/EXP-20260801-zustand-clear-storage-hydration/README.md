# Zustand clear-storage hydration ordering

## In simple words

Zustand's persist middleware already uses a generation counter so a newer `rehydrate()` call can invalidate older in-flight hydration work. The public `clearStorage()` operation removes the stored entry but does not advance that generation.

This experiment asks whether a stored read or migration that began before `clearStorage()` can still apply the just-cleared snapshot to live store state afterward.

The question is narrow. `clearStorage()` is not assumed to reset state that was already live before the clear. Ordinary asynchronous write completion, storage replacement through `setOptions`, and application-level sign-out sequencing are excluded.

## State

`repair`

Last updated: `2026-08-02`  
Owner: `chatgpt:gpt-5.6-thinking`  
Claim scope: `mechanism`  
Upstream contact authorized: `no`

## Why this target

The current npm package page reported roughly 46–48 million weekly downloads for Zustand during the intake pass, compared with roughly 4.1 million for Jotai. Popularity was used only as a targeting signal; it is not evidence that this behavior is common or severe.

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

## Project instructions read

At the pinned public source, `CONTRIBUTING.md` requires:

- conventional commits;
- a focused PR;
- failing tests before implementation;
- `pnpm run fix:format`;
- `pnpm run build`;
- `pnpm run test`.

Those gates control this experiment. The current target heads have not cleared the full sequence because both primary test workflows stop at formatting.

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

These assertions are source-derived characterization until a target-native semantic test job runs them successfully.

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

## Exact execution classification

### Characterization head `9c5039e...`

Successful:

- Test Multiple Versions `30692436573`;
- Test Old TypeScript `30692436571`;
- Test Multiple Builds `30692436591`;
- Compressed Size `30692436621`.

Classified failures:

- Test `30692436576`, job `91349433692`: dependency installation passed, then `pnpm run test:format` reported only `tests/persistClearStorageHydrationOrdering.test.ts`. Type, lint, spec, and build steps were skipped.
- Preview Release `30692436570`, job `91349433703`: the complete package build passed; publication failed because the `pkg-pr-new` GitHub App is not installed on `teamleaderleo/zustand`.

### Candidate head `d009aa2...`

Successful:

- Test Old TypeScript `30692520845`;
- Compressed Size `30692520829`;
- Test Multiple Versions `30692520839`;
- Test Multiple Builds `30692520824`.

Classified failures:

- Test `30692520819`, job `91349676750`: dependency installation passed, then `pnpm run test:format` reported only `tests/persistClearStorageHydrationGeneration.test.ts`. Type, lint, spec, and build steps were skipped.
- Preview Release `30692520832`, job `91349677085`: the complete package build passed; publication failed because the `pkg-pr-new` GitHub App is not installed on the fork.

The preview failures are repository-hosting limits after successful builds. The primary test failures are owned formatting defects and block semantic acceptance.

## Exact review

### Source ownership

Incrementing `hydrationVersion` synchronously before `removeItem` uses the same authority already selected for newer `rehydrate()` calls. It cancels publication by older stored reads and migrations while allowing a later explicit hydration to establish a newer generation.

The source location is coherent and narrowly scoped. Moving the increment after an asynchronous removal would leave the existing stale-publication window open.

### Remaining semantic decisions

The current four candidate cases prove only state publication behavior. Before acceptance, tests or explicit disposition must settle:

1. **Hydration lifecycle state.** `hydrate()` sets `hasHydrated = false`; an invalidated hydration returns before setting it true or notifying `onFinishHydration`. This matches the existing newer-hydration cancellation model, but `clearStorage()` is a different public operation and the expected observable state should be recorded.
2. **Callbacks.** `onRehydrateStorage` starts before the clear, while its completion callback is skipped by the version guard. The candidate should state and test whether this is intentional.
3. **Removal failure.** The generation increments before `removeItem`. A synchronous throw or ignored asynchronous rejection therefore revokes the in-flight hydration even when storage was not successfully cleared. That may be the correct request-authority rule, but it is currently untested and undocumented.
4. **No widening.** Storage replacement through `setOptions`, ordinary write settlement, and resetting already-live state remain separate lanes.

## Repair sequence

1. Run the repository formatter on both new test files and keep the resulting diffs target-native.
2. Rerun the primary `Test` workflow for characterization and candidate heads so type, lint, spec, and build steps execute.
3. Add focused controls for `hasHydrated`, `onFinishHydration`, and the post-rehydration callback when clear invalidates an active hydration, or document an explicit reason to inherit current concurrent-rehydrate behavior without new assertions.
4. Add and decide at least one `removeItem` failure control. Keep the source one-line only if the chosen request-authority behavior remains correct.
5. Review the complete exact candidate diff after the repair and repeat the current issue/PR search before any promotion.

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

Stop after the formatting repair, complete primary test execution, lifecycle/failure-semantics disposition, and exact complete-diff review. Do not widen this experiment into general persistence serialization, storage replacement, sign-out APIs, or public upstream contact.
