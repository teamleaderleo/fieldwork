# Zustand storage replacement during hydration

## State

`COMPLETE — repaired source candidate technically accepted; public contact unauthorized`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-02`  
Completed: `2026-08-05`  
Claim scope: mechanism  
Public upstream contact authorized: `no`

## Bounded question

Can asynchronous hydration that began against one Zustand persist storage backend still apply old data, or write migrated old data, after `persist.setOptions({ storage: replacement })` transfers storage ownership?

## Exact subject

- pinned public and fork base: `beca84e600e4e250f6b244d22878e72948f331c7`;
- characterization: `teamleaderleo/zustand#6@c4b24708bc4258e9f531ab3242b6f89c40c1c75f`;
- accepted candidate: `teamleaderleo/zustand#7@665e0399ee5dc3e877f4cbd431a326eac56f42db`;
- exact execution carrier: `teamleaderleo/zustand#8@a9e77b3f38448440b1d4d65b227fd30397bfb445`;
- exact source fence: one production file and one focused target-native test.

The accepted candidate changes only:

- `src/middleware/persist.ts`;
- `tests/persistStorageReplacementHydrationGeneration.test.ts`.

No dependency, lockfile, workflow, generated-output, storage-format, or public-API change is present.

## Source result

`hydrate()` captures one generation and binds the initiating storage read. A later asynchronous migration writes through the shared `setItem()`, which uses the mutable current storage reference.

Before the candidate, `setOptions()` could replace that storage reference without advancing hydration authority. Old work could therefore:

- merge data read from the previous backend into live state;
- finish an old migration and write that old data into the newly selected backend;
- publish stale hydration completion signals.

The migration case crosses backend ownership rather than producing only stale visible state.

## Accepted repair

A genuine storage-object replacement advances the existing hydration generation immediately before transferring the shared storage reference:

```ts
if (newOptions.storage && newOptions.storage !== storage) {
  hydrationVersion += 1
  storage = newOptions.storage
}
```

This reuses the generation checks already guarding state application, migrated writes, post-rehydration callbacks, `hasHydrated()`, finish listeners, and error delivery.

The operation does not automatically hydrate from the replacement backend. A later explicit `rehydrate()` establishes a new generation and uses the replacement storage normally.

## Review repair

The prior candidate checked only `if (newOptions.storage)`. That invalidated hydration whenever the caller included a truthy storage value, including the exact currently active storage object.

Reapplying the same object was previously a no-op assignment. Treating it as ownership transfer introduced an avoidable compatibility change: an in-flight hydration could be cancelled even though no backend changed.

The accepted candidate narrows invalidation to object-identity replacement and adds a reversing control proving that reapplying the identical storage object preserves:

- state publication;
- `hasHydrated() === true`;
- one post-rehydration callback;
- one finish-hydration event.

## Target-native controls

The exact two-file test proves:

1. a delayed old-backend read cannot hydrate after actual replacement;
2. an old migration cannot write through replacement storage;
3. stale completion callbacks and finish listeners are suppressed;
4. `hasHydrated() === false` for the invalidated generation;
5. replacement alone does not read the new backend;
6. a later replacement-backed hydration publishes state and completion exactly once;
7. identical-storage reapplication preserves the active hydration and exact completion signals.

## Exact execution

Carrier workflow `30848819804`, storage-replacement job `91803592339`, passed directly against `665e039...`:

- exact public-base and two-file fence verification;
- dependency installation;
- repository format gate;
- repository type gate;
- repository lint gate;
- complete repository spec gate;
- final exact-head identity, diff hygiene, and clean tree.

The unchanged clear-storage control job `91803592238` also passed in the same matrix. The earlier storage-replacement receipt for `9b492ea...` remains provenance only because review changed the source and test.

Fieldwork validation at head `8de02c3c366e618826056a4d5566f809a7703248` also passed:

- Playground and context integrity `30848938441`;
- Fieldwork integrity `30848937669`.

## Review conclusion

Complete-diff technical review accepts the repaired two-file candidate.

The generation transfer occurs only for an actual backend identity change and before the shared reference is exposed. This prevents old asynchronous work from publishing into the new ownership domain while preserving the prior no-op behavior for identical storage reapplication.

This is same-account technical acceptance. Human review, merge authority, and public filing authority remain separate and unclaimed.

## Exclusions and next transition

Excluded:

- `clearStorage()` ordering, owned by the separate completed experiment;
- changing non-storage options during hydration;
- ordinary asynchronous write settlement;
- automatic hydration on storage replacement;
- public API or storage-format changes;
- public upstream interaction.

Immediately before any authorized filing:

- refresh public main and overlap state;
- read the current contribution and disclosure policy;
- verify the exact two-file candidate fence and head;
- obtain explicit authority for the public interaction.

No canonical-upstream issue, pull request, comment, review, reaction, release, or deployment was created.
