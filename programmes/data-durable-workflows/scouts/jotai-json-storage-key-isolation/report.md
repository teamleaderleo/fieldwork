# Jotai JSON storage key isolation

State: `candidate-prepared`

Fieldwork lane: #235

Programme: data-durable-workflows

Evidence playground: #228 / `EXP-20260730-jotai-json-key-isolation`

Canonical implementation branch: `lane/235-jotai-json-storage-key-isolation`

Target repository: `pmndrs/jotai`

Released package: `jotai@2.20.2`

Release source: `5c4ca26b0db5571114be58393e17854a771f7790`

Exact source under candidate test: `56a9cc51de8a5dd762b95a145820f12589cc47c9`

Upstream contact authorized: `false`

## In simple words

Jotai converts JSON strings from browser or application storage into JavaScript values. It remembers the last parsed JSON so repeated reads can return the same object instead of creating a fresh object every time.

The released adapter keeps one remembered string and object for the entire adapter. Two independent storage keys containing the same JSON therefore receive the same object instance. Mutating the object returned for one key also changes the object already returned for the other key, even though the second key was not written or notified.

The first repair experiment keeps the useful identity behavior but scopes it by storage key.

## Confirmed released behavior

Workflow `30548784323` passed against exact `jotai@2.20.2` on:

- Node `v22.23.1`;
- Node `v24.18.0`;
- Node `v26.5.1`.

Every job observed:

```text
same adapter + same key + same JSON: same object
same adapter + different keys + same JSON: same object
same adapter + different keys + different JSON: different objects
separate adapters + same JSON: different objects
mutate key A object: key B object changes in memory
```

Exact receipt:

`playgrounds/EXP-20260730-jotai-json-key-isolation/result.json`

The target result matches the earlier source-equivalent Node 22 model.

## Historical compatibility requirement

The JSON identity cache was introduced by Jotai PR #1080 / commit `9e336c6bd2bebf257ffca957b0af18f97444323c` to repair issue #1079.

That issue involved one atom and one storage key. Subscription setup and the mount-time reread could parse the same object JSON twice and produce different references, leaving the atom with an incorrect pre-mount value.

The repair must therefore preserve:

- stable object identity for repeated unchanged reads of one key;
- the original subscription/mount regression;
- synchronous and asynchronous storage behavior;
- custom reviver behavior.

It must add:

- isolation between different keys whose serialized JSON is equal.

## Candidate source change

Prepared patch:

`candidate.patch`

The patch replaces one adapter-wide pair:

```ts
let lastStr: string | undefined
let lastValue: Value
```

with a key-scoped cache:

```ts
const cachedValues = new Map<string, { str: string; value: Value }>()
```

For each key:

- unchanged JSON returns that key's cached object;
- equal JSON from another key is parsed separately;
- parse failure still returns the supplied initial value;
- `removeItem(key)` deletes only that key's cached entry before delegating to storage.

The patch does not change:

- atom construction;
- subscription wiring;
- JSON replacer or reviver calls;
- storage write ordering;
- reset semantics beyond affected-key cache invalidation;
- public types.

## Prepared native regression

Prepared test:

`atomWithStorageKeyIsolation.test.ts`

It covers:

1. same-key identity survives an interleaved read of another key;
2. different keys with equal JSON return distinct objects;
3. mutation does not cross the key boundary;
4. asynchronous string storage follows the same rule;
5. a custom reviver runs once per key and later same-key reads retain identity;
6. removing one key invalidates only that key's cache.

The interleaved control matters. A one-entry cache that stores only the latest key would fix the simplest two-key example but would lose the original same-key identity when another atom reads between two reads of the first key.

## Exact-source workflow

Workflow:

`.github/workflows/fieldwork-jotai-key-scoped-json-cache.yml`

Matrix:

- Node 22;
- Node 24;
- Node 26.

Each job:

1. checks out exact Jotai source `56a9cc51...`;
2. applies `candidate.patch` with `git apply --check`;
3. stages the prepared regression under Jotai's native test tree;
4. installs the exact repository lockfile with pnpm 11.3.0;
5. runs the candidate regression and the existing `atomWithStorage.test.tsx` suite;
6. runs ESLint and Prettier on changed files;
7. runs `tsc --noEmit`.

## Cache-lifecycle boundary

A per-key `Map` can retain entries for dynamic keys until the adapter is discarded or `removeItem(key)` is called.

This candidate clears explicit removals but does not bound arbitrary key churn. That is acceptable only as an experiment. Before a production patch is accepted, review whether:

- adapters normally serve a bounded key set;
- reset/remove covers ordinary lifecycle;
- subscription-only keys can remain cached;
- an alternative weak or bounded representation is needed;
- caching primitives is worth the same retention cost.

Do not hide this memory tradeoff behind a correctness fix.

## Claim-scoped evidence

- released cross-key alias: `target-executed`;
- source history and original intent: `source-read`;
- key-scoped candidate: `target-test-prepared`;
- repository-native regression: prepared, not yet executed;
- full repository test/build: absent;
- ecosystem frequency and production impact: unmeasured;
- upstream acceptance: absent.

## Current disposition

**ACCEPT the bounded released finding. EXECUTE the key-scoped candidate matrix. HOLD implementation acceptance until exact-source tests and cache-lifecycle review settle.**

If the focused matrix passes:

1. retain exact job receipts;
2. complete-diff review the patch and test;
3. decide whether the per-key `Map` lifecycle is acceptable;
4. if retained, prepare an owned-fork direct source branch rather than leaving the patch only in Fieldwork;
5. run Jotai's ordinary format, types, lint, specs, and build on that direct head;
6. refresh duplicate/history search before any upstream packet.

## Stop condition

Stop the first implementation pass when one candidate simultaneously:

- preserves #1079 same-key identity;
- prevents cross-key object aliasing;
- passes synchronous, asynchronous, reviver, reset, and existing atomWithStorage controls;
- states a deliberate cache-retention policy.

No public upstream interaction occurred.