# Upstream discussion draft — createJSONStorage can share parsed object identity across different keys

Draft status: `ready after authorization and immediate current-main recheck`  
Public interaction authorized: `no`

Jotai's contribution guide asks bug reports to begin as a Discussion. This file is written for that route. No public Discussion or issue has been created.

---

## Summary

A single `createJSONStorage()` adapter can be shared by atoms using different storage keys. When two keys contain identical object JSON, the current adapter returns the same parsed object instance for both keys.

Mutating the value returned for one key then changes the object previously returned for the other key in memory, even though the second storage entry was never written and no subscription update occurred for it.

The current source keeps one parsed-string/value cache for the whole adapter. A key-scoped cache appears to preserve unchanged same-key identity while isolating independent keys.

## Reproduction

1. Create one JSON storage adapter over a string storage containing two keys.
2. Store the same object JSON under both keys.
3. Read each key through the same adapter.
4. Compare references and mutate one returned object.

Minimal example:

```ts
import { createJSONStorage } from 'jotai/vanilla/utils'

const values = new Map([
  ['alpha', JSON.stringify({ nested: { count: 1 } })],
  ['beta', JSON.stringify({ nested: { count: 1 } })],
])

const storage = createJSONStorage<{ nested: { count: number } }>(() => ({
  getItem: (key) => values.get(key) ?? null,
  setItem: (key, value) => values.set(key, value),
  removeItem: (key) => values.delete(key),
}))

const alpha = storage.getItem('alpha', { nested: { count: -1 } })
const beta = storage.getItem('beta', { nested: { count: -2 } })

console.log(alpha === beta) // true on 2.20.2
alpha.nested.count = 99
console.log(beta.nested.count) // 99
```

## Observed behavior

Exact `jotai@2.20.2` returned one object for equal JSON under different keys on Ubuntu 24.04 with Node 22, 24, and 26. Different JSON and separate adapters returned different objects.

The same adapter and same key correctly reused identity, which appears intentional and should remain.

## Expected behavior

Different storage keys should receive independent parsed values, even when their serialized bytes match. Repeated unchanged reads for one key should continue to preserve identity.

## Current source observation

`createJSONStorage()` stores one `lastStr` and `lastValue` pair in the adapter closure. `getItem()` accepts a key, while the cache comparison uses only the serialized string. Equal JSON under another key therefore reuses the same value.

The cache originated in the fix for #1079 / PR #1080 to preserve identity during a same-key mount/subscription reread. That history supports keeping memoization while including the storage key in cache ownership.

## Candidate direction

Use one adapter-local cache entry per key:

```ts
const cachedValues = new Map<string, { str: string; value: Value }>()
```

A focused candidate has passed controls for:

- same-key identity across unrelated-key reads;
- distinct values for equal JSON under different keys;
- mutation isolation;
- synchronous and asynchronous storage;
- custom revivers;
- removal and unreadable-state invalidation;
- the existing atomWithStorage mount/subscription tests.

One related ordering concern needs maintainer direction or inclusion in the final patch: older asynchronous reads can complete after newer invalidation and regain shared cache publication authority. A per-key read generation is one bounded solution. The user-visible result of each initiating read remains its backend result; only shared cache publication is fenced.

## Compatibility and risks

- Public interfaces and JSON format can remain unchanged.
- A per-key map retains one parsed value per observed key until invalidation or adapter collection.
- Any finite eviction policy would make unchanged same-key identity depend on unrelated-key activity.
- The final source change should include the asynchronous publication-order control or clearly sequence it in the same contribution.

## Evidence limits

- Application frequency and production impact have not been measured.
- Browser localStorage and React Native AsyncStorage have not yet run on a clean direct source branch.
- The complete repository build and aggregate test suite remain for the final branch.

## Versions and environment

- project version: `jotai@2.20.2`
- current source checked: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- platform: Ubuntu 24.04
- runtimes: Node 22, 24, and 26
- package manager for source candidate: pnpm 11.3.0

## Additional context

- #1079 and PR #1080 introduced same-key parsed identity reuse.
- #1815 discusses reset subscription propagation and appears distinct from this cache-identity boundary.

---

## Filing checklist

- [ ] Current upstream Discussion, issue, and PR search repeated immediately before filing.
- [ ] Reproduction rerun on the then-current public revision.
- [x] Severity and prevalence wording stays within evidence.
- [x] Private and Fieldwork-only links removed.
- [x] Target contribution policy checked: bug reports begin as a Discussion.
- [ ] Current Discussion template and AI-disclosure policy checked at filing time.
- [ ] Exact user authorization to create the public Discussion recorded.
