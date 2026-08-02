# Zustand storage replacement during hydration

## State

`running`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-02`  
Claim scope: mechanism  
Public upstream contact authorized: `no`

## Bounded question

Can an asynchronous hydration that began against one Zustand persist storage backend still apply old data, or write migrated old data, after `persist.setOptions({ storage: replacement })` transfers storage ownership?

## Exact subject

- target: `pmndrs/zustand`;
- pinned public source: `beca84e600e4e250f6b244d22878e72948f331c7`;
- clean fork base: `teamleaderleo/zustand:base/upstream-20260801`;
- characterization PR/head: `teamleaderleo/zustand#6` at `c4b24708bc4258e9f531ab3242b6f89c40c1c75f`;
- candidate PR/head: `teamleaderleo/zustand#7` at `4869662812291fec9ef42529ca64db00d0710ed5`.

## Source model

`hydrate()` captures authority with `currentVersion = ++hydrationVersion` and binds the current storage's `getItem`. The later migration write calls the shared `setItem()`, which reads the mutable `storage` variable at settlement time.

`setOptions()` updates `options`, then replaces `storage` without advancing `hydrationVersion`.

Consequences predicted by the source:

1. a delayed value read from the old backend may still merge into live state after replacement;
2. a delayed migration of old-backend data may call `setItem()` after replacement and write the migrated old state into the new backend;
3. a later explicit rehydrate reads the replacement backend normally.

The second consequence is a cross-backend ownership error, not merely a stale UI update.

## Characterization

Target-native test: `tests/persistStorageReplacementHydrationOrdering.test.ts`.

Cases:

1. delayed old-backend read applies after replacement;
2. delayed old-backend migration writes into replacement backend;
3. later rehydrate uses replacement backend.

The characterization branch changes no production source.

## Candidate

The candidate advances the existing hydration generation immediately before transferring the storage reference:

```ts
if (newOptions.storage) {
  hydrationVersion += 1
  storage = newOptions.storage
}
```

Exact candidate diff:

- `src/middleware/persist.ts` — one addition;
- `tests/persistStorageReplacementHydrationGeneration.test.ts` — 133 additions.

The candidate blocks old read publication and old migration writes while allowing a later rehydrate to use the replacement backend.

## Exclusions

- `clearStorage()` ordering is a separate experiment;
- changing non-storage options during hydration is not repaired here;
- ordinary asynchronous write settlement ordering is not addressed;
- no automatic rehydrate is triggered by storage replacement;
- no public API or storage format change is proposed.

## Prior-art and ownership check

Searches on `2026-08-02` found no equivalent current Zustand issue, pull request, or Fieldwork lane using the searched storage-replacement and hydration-race terms. Differently worded or unindexed work may exist; repeat before promotion.

The merged concurrent-`rehydrate()` generation repair is direct adjacent prior art. This experiment extends the same authority model to storage ownership transfer.

## Execution

Both fork-local PRs triggered the repository workflow set at their exact heads. At the time this record was created, all workflows were queued.

Characterization run IDs:

- Test `30753546797`;
- Test Multiple Versions `30753546839`;
- Test Old TypeScript `30753546780`;
- Test Multiple Builds `30753546808`;
- Compressed Size `30753546811`;
- Preview Release `30753546824`.

Candidate run IDs:

- Test `30753554588`;
- Test Multiple Versions `30753554584`;
- Test Old TypeScript `30753554616`;
- Test Multiple Builds `30753554615`;
- Compressed Size `30753554603`;
- Preview Release `30753554593`.

No target-executed result is claimed until the primary Test jobs and final conclusions are inspected.

## Stop condition

Stop after the three characterization cases and three candidate cases execute and the source boundary is reviewed. Do not widen into all runtime option mutation or general persistence serialization without a separate bounded experiment.
