# Zustand storage replacement during hydration

## State

`REPAIR EXECUTED — fresh exact-head repository gate pending`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-02`  
Claim scope: mechanism  
Public upstream contact authorized: `no`

## Bounded question

Can asynchronous hydration that began against one Zustand persist storage backend still apply old data, or write migrated old data, after `persist.setOptions({ storage: replacement })` transfers storage ownership?

## Exact subject

- pinned public and fork base: `beca84e600e4e250f6b244d22878e72948f331c7`;
- characterization: `teamleaderleo/zustand#6@c4b24708bc4258e9f531ab3242b6f89c40c1c75f`;
- current candidate: `teamleaderleo/zustand#7@665e0399ee5dc3e877f4cbd431a326eac56f42db`;
- exact execution carrier: `teamleaderleo/zustand#8@a9e77b3f38448440b1d4d65b227fd30397bfb445`;
- exact source fence: one production file and one focused target-native test.

## Source result

`hydrate()` captures one generation and binds the initiating storage read. A later asynchronous migration writes through the shared `setItem()`, which uses the mutable current storage reference.

Before the candidate, `setOptions()` could replace that storage reference without advancing hydration authority. Old work could therefore:

- merge data read from the previous backend into live state;
- finish an old migration and write that old data into the newly selected backend;
- publish stale hydration completion signals.

The migration case crosses backend ownership rather than producing only stale visible state.

## Candidate direction

A genuine storage-object replacement advances the existing hydration generation immediately before transferring the shared storage reference:

```ts
if (newOptions.storage && newOptions.storage !== storage) {
  hydrationVersion += 1
  storage = newOptions.storage
}
```

This reuses the generation checks already guarding state application, migrated writes, post-rehydration callbacks, `hasHydrated()`, finish listeners, and error delivery.

The operation does not automatically hydrate from the replacement backend. A later explicit `rehydrate()` establishes a new generation and uses the replacement storage normally.

## Review finding and repair

The previous candidate checked only `if (newOptions.storage)`. That invalidated hydration whenever the caller included a truthy storage value, even when it was the exact currently active storage object.

Reapplying the same object was previously a no-op assignment. Treating it as ownership transfer introduced an avoidable compatibility change: an in-flight hydration could be cancelled even though no backend changed.

The current candidate narrows invalidation to object-identity replacement and adds a reversing control proving that reapplying the identical storage object preserves:

- state publication;
- `hasHydrated() === true`;
- one post-rehydration callback;
- one finish-hydration event.

## Preserved controls

The focused test also requires:

1. delayed old-backend read suppression after actual replacement;
2. old migration suppression before it can write through replacement storage;
3. stale completion callback and listener suppression;
4. `hasHydrated() === false` for the invalidated generation;
5. replacement alone does not read the new backend;
6. later replacement-backed hydration publishes state and completion exactly once.

## Execution boundary

Prior carrier workflow `30836583456`, job `91763113716`, passed the earlier head `9b492ea...`. That receipt is provenance only because source and tests moved during review.

The reopened carrier now checks exact head `665e039...` through:

- exact public-base and two-file fence verification;
- repository format;
- repository types;
- repository lint;
- complete repository specs;
- final exact-head identity, diff hygiene, and clean tree.

Current exact carrier run: `30848819804`, queued at this update. Ordinary compatibility workflows are also queued. No pass is claimed for the repaired head until those jobs settle.

## Exclusions and stop condition

Excluded:

- `clearStorage()` ordering, which is owned by the separate completed experiment;
- changing non-storage options during hydration;
- ordinary asynchronous write settlement;
- automatic hydration on storage replacement;
- public API or storage-format changes;
- public upstream interaction.

Stop after the exact repaired head passes the complete repository gate and the final two-file diff is reviewed unchanged. Repeat public-main, overlap, and contribution-policy checks immediately before any authorized filing.
