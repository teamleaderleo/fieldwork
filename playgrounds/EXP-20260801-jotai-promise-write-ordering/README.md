# Jotai promised storage write ordering

## In simple words

Jotai's `atomWithStorage` accepts a value that may itself be a promise. When that promise resolves, the current implementation updates the atom and writes storage at that later time.

This experiment asks whether an older promised update can finish after a newer direct update, reset, or promised update and become the final in-memory and persisted value. That would make promised writes follow resolution order rather than call order.

The question is narrow. It does not cover two ordinary asynchronous `storage.setItem()` calls completing out of order, read ordering, subscription ordering, or public API design.

## State

`running — characterization and candidate queued`

Last updated: `2026-08-01`  
Owner: `chatgpt:gpt-5.6-thinking`  
Claim scope: `mechanism`  
Upstream contact authorized: `no`

## Exact subject

- Target: `pmndrs/jotai`
- Pinned source: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Characterization branch: `teamleaderleo/jotai:scout/atom-with-storage-promise-write-ordering`
- Exact characterization head: `09e7964e5da9423920eedb736feb30a347eaec89`
- Characterization draft PR: `teamleaderleo/jotai#4`
- Candidate branch: `teamleaderleo/jotai:fix/utils-promise-write-generation`
- Exact candidate head: `348156c8ae9636c9ad0b43d1c0fb7343dc13a976`
- Candidate draft PR: `teamleaderleo/jotai#5`
- Product source path: `src/vanilla/utils/atomWithStorage.ts`
- Characterization test: `tests/react/vanilla-utils/atomWithStoragePromiseWriteOrdering.test.ts`
- Candidate test: `tests/react/vanilla-utils/atomWithStoragePromiseWriteGeneration.test.ts`

## Source model

The `atomWithStorage` write function computes `nextValue` and then has three paths:

1. `RESET` immediately sets the initial value and calls `removeItem`.
2. A promised value waits for resolution, then calls `set(baseAtom, resolvedValue)` and `storage.setItem`.
3. A direct value immediately calls `set(baseAtom, nextValue)` and `storage.setItem`.

No write invocation generation is recorded in the pinned source. Therefore an earlier promised update retains a later callback that can still set state and persist data after a newer operation.

## Characterization cases

1. Older promised update, then newer direct value.
2. Older promised update, then reset.
3. Older promised update, then newer promised update that resolves first.

The characterization tests assert the exact source behavior predicted by the current code path: the older promise resolves last and becomes final atom state and the final recorded storage write.

## Candidate

The candidate adds one `writeGeneration` counter inside each `atomWithStorage` instance.

- Every direct update, promised update, and reset advances the generation.
- A promised value captures its invocation generation.
- When the promise resolves, it updates atom state and calls `storage.setItem` only if its generation is still current.
- Promise rejection remains caller-visible because the candidate does not add a rejection handler.
- Direct values and reset keep their existing immediate behavior.

Candidate controls cover:

- newer direct value remains authoritative;
- reset remains authoritative;
- overlapping promises are ordered by invocation;
- stale rejection remains caller-visible without changing newer state.

The candidate intentionally does not serialize ordinary asynchronous storage writes. If `storage.setItem(1)` and `storage.setItem(2)` themselves settle out of order, that is a separate backend-operation question.

## Distinguishing result

- Characterization passes and candidate passes: retain a technically selected finding candidate, subject to complete diff review and policy/duplicate checks.
- Characterization passes and candidate fails: repair or reject the generation design without widening scope.
- Characterization does not show the predicted overwrite: retain a negative result and close the candidate.
- Setup, type, or runner failure proves neither outcome.

## Current execution

### Characterization head `09e7964e5da9423920eedb736feb30a347eaec89`

- Test Multiple Builds `30691421748` — queued at last check;
- Test Multiple Versions `30691421760` — queued;
- Preview Release `30691421778` — queued;
- Test `30691421788` — queued;
- Test Old TypeScript `30691421765` — queued;
- Compressed Size `30691421781` — queued.

### Candidate head `348156c8ae9636c9ad0b43d1c0fb7343dc13a976`

- Test `30691537697` — queued at last check;
- Test Multiple Versions `30691537706` — queued;
- Preview Release `30691537696` — queued;
- Test Multiple Builds `30691537710` — queued;
- Compressed Size `30691537704` — queued;
- Test Old TypeScript `30691537723` — queued.

No target-executed result is claimed until actual jobs complete and focused-test coverage is visible.

## Prior-art check

Searches on `2026-08-01` for Jotai `atomWithStorage` promised update ordering, stale promise writes, and related pull requests did not surface an equivalent current repair. Historical issue `pmndrs/jotai#263` discusses timing concerns around asynchronous state and external storage, but it does not establish or repair this exact built-in promised-update sequence.

This search can miss differently worded or unindexed discussions and must be repeated before promotion.

## Risks and reversing controls

- Maintainers may define promised updates as independent async actions whose resolution order intentionally controls state. That would reject the candidate even if the behavior is reproducible.
- A caller may rely on an older promised update eventually applying after a newer direct update. The current API does not document this ordering in the inspected source.
- The counter has atom-instance lifetime and increments once per update invocation.
- The candidate must not be described as solving general persistence ordering.

Reopen or reject if target tests show Jotai already suppresses the stale callback, existing tests depend on resolution-order semantics, or a simpler authority mechanism covers the same exact boundary.

## Stop condition

Stop after the characterization and candidate controls run and the behavior is classified. Do not widen this experiment into general backend write serialization, read/write ordering, subscription ordering, or upstream contact.
