# Jotai promised storage write ordering

## In simple words

Jotai's `atomWithStorage` accepts a value that may itself be a promise. When that promise resolves, the current implementation updates the atom and writes storage at that later time.

This experiment asks whether an older promised update can finish after a newer direct update, reset, or promised update and become the final in-memory and persisted value. That would make promised writes follow resolution order rather than call order.

The question is narrow. It does not cover two ordinary asynchronous `storage.setItem()` calls completing out of order, read ordering, subscription ordering, or public API design.

## State

`running`

Last updated: `2026-08-01`  
Owner: `chatgpt:gpt-5.6-thinking`  
Claim scope: `mechanism`  
Upstream contact authorized: `no`

## Exact subject

- Target: `pmndrs/jotai`
- Pinned source: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Owned fork branch: `teamleaderleo/jotai:scout/atom-with-storage-promise-write-ordering`
- Exact probe head: `09e7964e5da9423920eedb736feb30a347eaec89`
- Fork-local draft PR: `teamleaderleo/jotai#4`
- Product source path: `src/vanilla/utils/atomWithStorage.ts`
- Target-native probe: `tests/react/vanilla-utils/atomWithStoragePromiseWriteOrdering.test.ts`

## Source model

The `atomWithStorage` write function computes `nextValue` and then has three paths:

1. `RESET` immediately sets the initial value and calls `removeItem`.
2. A promised value waits for resolution, then calls `set(baseAtom, resolvedValue)` and `storage.setItem`.
3. A direct value immediately calls `set(baseAtom, nextValue)` and `storage.setItem`.

No write invocation generation is recorded in the pinned source. Therefore an earlier promised update retains a later callback that can still set state and persist data after a newer operation.

## Probe cases

1. Older promised update, then newer direct value.
2. Older promised update, then reset.
3. Older promised update, then newer promised update that resolves first.

The tests currently assert the exact observed source behavior predicted by the code path: the older promise resolves last and becomes final atom state and the final recorded storage write.

## Distinguishing result

- If the target-native test passes, resolution order controls promised update authority on the pinned source.
- If the final newer operation remains authoritative, Jotai store semantics already fence the stale callback and this becomes a negative result.
- Setup, type, or runner failure proves neither outcome.

## Current execution

The owned-fork draft PR triggered the existing Jotai workflow set at `09e7964e5da9423920eedb736feb30a347eaec89`:

- Test Multiple Builds `30691421748` — queued at last check;
- Test Multiple Versions `30691421760` — queued;
- Preview Release `30691421778` — queued;
- Test `30691421788` — queued;
- Test Old TypeScript `30691421765` — queued;
- Compressed Size `30691421781` — queued.

No result is claimed until actual jobs complete and the focused test execution is visible.

## Prior-art check

Searches on `2026-08-01` for Jotai `atomWithStorage` promised update ordering, stale promise writes, and related pull requests did not surface an equivalent current repair. Historical issue `pmndrs/jotai#263` discusses timing concerns around asynchronous state and external storage, but it does not establish or repair this exact built-in promised-update sequence.

This search can miss differently worded or unindexed discussions and must be repeated before promotion.

## Candidate boundary if confirmed

A narrow candidate would assign invocation authority inside one `atomWithStorage` instance:

- every direct value, promised value, or reset advances a write generation;
- a promised value may update atom state and call `storage.setItem` only while its captured generation remains current;
- rejection stays caller-visible;
- direct backend write completion ordering remains outside this candidate.

This is a hypothesis, not yet a selected implementation.

## Stop condition

Stop after the three target-native controls run and the behavior is classified. Do not widen this experiment into general backend write serialization, read/write ordering, subscription ordering, or upstream contact.
