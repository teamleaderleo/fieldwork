# Zustand clear-storage hydration ordering

## State

`COMPLETE — source candidate technically ready; public contact unauthorized`

Owner: `chatgpt:gpt-5.6-thinking`  
Created: `2026-08-01`  
Claim scope: `mechanism`  
Upstream contact authorized: `no`

## In simple words

Zustand persist already prevents an older `rehydrate()` call from publishing after a newer hydration starts. `clearStorage()` removed the persisted item without advancing that same generation, so a delayed read or migration could still apply the snapshot that the caller had just cleared.

The accepted candidate increments the existing hydration generation immediately before storage removal. The clear request therefore revokes older hydration work without resetting state that is already live.

## Exact subject

- pinned public and fork base: `beca84e600e4e250f6b244d22878e72948f331c7`;
- characterization: `teamleaderleo/zustand#4@9402e61c20266395d6e8190841ae924274f03ff1`;
- accepted candidate: `teamleaderleo/zustand#5@001900bb01102417c016afa3341e384f53474492`;
- retired execution carrier: `teamleaderleo/zustand#8@828226b0e66b396a0a0826a182fb23982828556a`;
- exact candidate fence: one production addition and one target-native test file.

The candidate changes only:

- `src/middleware/persist.ts`;
- `tests/persistClearStorageHydrationGeneration.test.ts`.

No dependency, lockfile, workflow, generated-output, storage-format, or public-API change is present.

## Current behavior

Each hydration captures a newly incremented `hydrationVersion`. Every later state-application and completion boundary checks that its captured version is still current.

Before this candidate, `clearStorage()` called `removeItem()` without advancing `hydrationVersion`. A hydration that began before the clear therefore remained authorized to:

- merge a delayed stored value into live state;
- merge a delayed migration result;
- publish its post-rehydration callback;
- mark hydration complete and notify finish listeners.

## Selected repair and policy

The candidate adds one operation before `removeItem()`:

```ts
++hydrationVersion
```

This uses the middleware's existing publication-authority mechanism rather than adding a second cancellation path.

The selected policy is explicit:

- the caller's clear intent immediately revokes the active hydration generation;
- revocation remains effective when synchronous `removeItem()` throws;
- physical removal failure does not give older hydration work permission to republish the logically cleared snapshot;
- clearing storage does not reset state that completed hydration already made live;
- a later explicit hydration may establish a new generation and publish normally.

## Target-native controls

The accepted test proves:

1. a delayed stored read cannot hydrate state after clear;
2. a delayed migration cannot hydrate state after clear;
3. synchronous removal failure still revokes the older hydration;
4. clearing after completed hydration leaves live state unchanged;
5. stale post-rehydration callbacks and finish listeners are suppressed;
6. `hasHydrated()` remains false for the invalidated generation;
7. a later hydration succeeds, applies state, and publishes each completion signal exactly once.

These controls settle the lifecycle, callback, and synchronous-removal policy questions that blocked the earlier generation.

## Exact execution

Execution carrier `teamleaderleo/zustand#8` first published repository-formatted test bytes under exact predecessor-head guards, then ran the exact candidate matrix.

Workflow `30836583456`, clear-storage job `91763113773`, passed directly against `001900bb...`:

- exact public-base and two-file fence verification;
- dependency installation;
- complete repository format gate;
- complete repository type gate;
- complete repository lint gate;
- complete repository spec gate;
- final exact-head identity, diff hygiene, and clean-tree verification.

The behavior-identical predecessor also passed Multiple Versions, Multiple Builds, Old TypeScript, and Compressed Size. The exact-head carrier is the controlling source receipt because ordinary workflows on the formatter-authored head were marked `action_required` without executing.

The execution carrier is closed without merge. The source candidate contains no workflow file.

## Review

Complete-diff technical review accepts the exact two-file candidate. The increment sits at the existing authority boundary and is checked by every later state, persistence, callback, error, and completion publication path.

The ordering before `removeItem()` is deliberate and covered by a reversing failure control. No narrower placement closes the stale-publication window while preserving clear intent after synchronous removal failure.

This is same-account technical acceptance. Human review, merge authority, and public filing authority remain separate and unclaimed.

## Compatibility and limits

Established:

- stale pre-clear reads and migrations lose publication authority;
- lifecycle observers follow the same generation rule as concurrent rehydration;
- already-live state is preserved;
- later hydration remains available;
- the complete repository format/type/lint/spec gates pass at the exact source head.

Excluded:

- storage replacement through `setOptions({ storage })`;
- ordinary asynchronous write settlement;
- application-level sign-out or state-reset policy;
- changing the return type or error handling of `clearStorage()`;
- public upstream interaction.

Immediately before any authorized filing, refresh public main and overlap, read current contribution policy, verify the exact two-file fence, and obtain explicit authority for that interaction.
