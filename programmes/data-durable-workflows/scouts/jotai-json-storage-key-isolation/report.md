# Jotai JSON storage key isolation

State: `candidate-prepared`

Fieldwork lane: #235  
Evidence PR: #228  
Playground: `EXP-20260730-jotai-json-key-isolation`  
Canonical candidate branch: `lane/235-jotai-json-storage-key-isolation-restack`  
Superseded carrier: PR #236  
Target repository: `pmndrs/jotai`  
Released package: `jotai@2.20.2`  
Exact source under candidate test: `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Upstream contact authorized: `false`

## In simple words

Jotai's released JSON storage adapter keeps one remembered JSON string and parsed value for the entire adapter. Two independent storage keys containing the same JSON therefore receive the same object instance. Mutating the object returned for one key changes the object already returned for the other key without a write or notification for that second key.

The candidate keeps the historical same-key identity behavior but scopes the cache by storage key.

## Confirmed released behavior

Workflow `30548784323` passed against exact `jotai@2.20.2` on Node 22, 24, and 26.

Every job observed:

```text
same adapter + same key + same JSON: same object
same adapter + different keys + same JSON: same object
same adapter + different keys + different JSON: different objects
separate adapters + same JSON: different objects
mutate key A object: key B object changes in memory
```

The exact machine-readable receipt is:

`playgrounds/EXP-20260730-jotai-json-key-isolation/result.json`

## Historical compatibility requirement

The JSON identity cache was introduced by Jotai PR #1080 / commit `9e336c6bd2bebf257ffca957b0af18f97444323c` to repair issue #1079.

That issue involved one atom and one storage key. Subscription setup and the mount-time reread could parse equal JSON twice and produce different references.

A repair must preserve:

- stable identity for repeated unchanged reads of one key;
- the original subscription/mount regression;
- synchronous and asynchronous storage behavior;
- custom reviver behavior.

It must add isolation between different keys whose serialized JSON is equal.

## Candidate source change

Prepared generated diff:

`candidate.patch`

The patch replaces one adapter-wide string/value pair with:

```ts
const cachedValues = new Map<string, { str: string; value: Value }>()
```

For each key:

- unchanged JSON returns that key's cached object;
- equal JSON from another key is parsed separately;
- parse failure still returns the supplied initial value;
- `removeItem(key)` deletes only that key's cached entry before delegating.

The patch does not change atom construction, subscription wiring, replacer/reviver APIs, storage write ordering, or public types.

## Native regression

Prepared test:

`atomWithStorageKeyIsolation.test.ts`

It covers:

1. same-key identity across interleaved other-key reads;
2. distinct objects for equal JSON under different keys;
3. mutation isolation;
4. sequential asynchronous storage reads;
5. reviver execution once per key plus later same-key identity;
6. invalidation of only the removed key;
7. the existing `atomWithStorage.test.tsx` suite, including the original mount behavior.

The interleaved control rejects a weaker one-entry key cache that would lose same-key identity whenever another atom reads between two reads of the first key.

## Exact-source workflow

The workflow checks out exact Jotai source `56a9cc51...`, applies the generated diff with `git apply --check`, stages the native regression, installs the exact lockfile with pnpm 11.3.0, runs the new and existing storage suites, then runs ESLint, Prettier, and TypeScript on Node 22, 24, and 26.

## Carrier history

PR #236 did not execute a candidate result:

- its first matrix stopped at `git apply` because the retained patch was syntactically corrupt;
- a corrected patch was later re-corrupted by guessed hunk metadata;
- the final corrected head became non-mergeable and received no new workflow dispatch.

This restack copies only the workflow, generated diff, native regression, and updated report onto current `main`. The PR-open event owns the fresh exact-source matrix. No result transfers from PR #236.

## Cache-lifecycle and concurrency limits

A per-key `Map` can retain entries for dynamic keys until the adapter is discarded or `removeItem(key)` is called. That memory tradeoff requires an explicit production decision.

The candidate also does not establish universal same-key identity under out-of-order asynchronous reads. A late older read can replace the per-key cache entry after a newer read resolves, causing a later current read to parse again. That race predates the candidate; it limits the claim rather than automatically rejecting the narrow cross-key repair.

## Claim-scoped evidence

- released cross-key alias: `target-executed`;
- source history and original intent: `source-read`;
- key-scoped candidate: `target-test-prepared`;
- repository-native regression: prepared, not yet executed on the restack;
- full repository test/build: absent;
- dynamic-key retention policy: unresolved;
- asynchronous completion ordering: unchanged and unresolved;
- ecosystem frequency and production impact: unmeasured;
- upstream acceptance: absent.

## Current disposition

**ACCEPT the bounded released finding. EXECUTE the restacked exact-source candidate matrix. HOLD implementation acceptance until exact tests, complete-diff review, and cache-lifecycle policy settle.**

After a focused pass:

1. retain exact job receipts;
2. review the applied source and test diff;
3. decide whether the per-key map lifecycle is acceptable;
4. prepare an owned-fork direct source branch rather than leaving the candidate only as a Fieldwork patch;
5. run Jotai's ordinary format, types, lint, specs, and build on that direct head;
6. refresh duplicate/history search before any upstream packet.

No public upstream interaction occurred.
