# Jotai JSON storage key isolation

State: `design-decision-ready`

Fieldwork lane: #235  
Evidence PR: #228  
Canonical candidate PR: #252  
Canonical candidate branch: `lane/235-jotai-json-storage-key-isolation-restack`  
Superseded carriers: PR #236 and PR #242  
Target repository: `pmndrs/jotai`  
Released package: `jotai@2.20.2`  
Exact source under candidate test: `56a9cc51de8a5dd762b95a145820f12589cc47c9`  
Candidate source/test head: `a2c836fcd6eba43cf03e0e8a94c9cc374dcbdb1e`  
Candidate execution run: `30579399493`  
Fieldwork integrity run: `30579399390`  
Upstream contact authorized: `false`

## In simple words

Jotai's released JSON storage adapter keeps one remembered JSON string and parsed value for the entire adapter. Two independent storage keys containing the same JSON therefore receive the same object instance. Mutating the object returned for one key changes the object already returned for the other key without a write or notification for that second key.

The executed candidate keeps the historical same-key identity behavior, scopes parsed identity by storage key, invalidates the affected key after every terminal removal outcome, and clears stale identity when a later read observes missing or malformed storage state.

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
- the original subscription and mount regression;
- synchronous and asynchronous storage behavior;
- custom reviver behavior.

It must add isolation between different keys whose serialized JSON is equal.

## Candidate source change

Executed generated diff:

`candidate.patch`

The patch replaces one adapter-wide string/value pair with:

```ts
const cachedValues = new Map<string, { str: string; value: Value }>()
```

For each key:

- unchanged JSON returns that key's cached object;
- equal JSON from another key is parsed independently;
- missing or malformed storage state deletes only that key's cached object before returning the supplied initial value;
- `removeItem(key)` preserves cached identity while an asynchronous removal is unresolved;
- normal return, fulfillment, synchronous throw, and rejection all delete only the affected key on settlement;
- the original removal error is rethrown unchanged;
- unrelated keys retain their cached identity.

Storage removal is an outcome receipt, not a transaction receipt. A rejection can follow a durable delete, so every terminal outcome invalidates the affected key.

The patch leaves atom construction, subscription wiring, replacer and reviver APIs, storage write ordering, and public types unchanged.

## Native regressions

Executed tests:

- `atomWithStorageKeyIsolation.test.ts`
- `atomWithStorageReadInvalidation.test.ts`
- existing `atomWithStorage.test.tsx`

The matrix covers:

1. same-key identity across interleaved other-key reads;
2. distinct objects for equal JSON under different keys;
3. mutation isolation;
4. sequential asynchronous storage reads;
5. reviver execution once per key plus later same-key identity;
6. affected-key invalidation after successful synchronous removal;
7. affected-key invalidation after synchronous removal throw;
8. affected-key invalidation after asynchronous removal rejection;
9. cache reuse while asynchronous removal remains pending;
10. affected-key invalidation after asynchronous fulfillment;
11. commit-then-reject removal followed by recreation of identical JSON;
12. out-of-band removal followed by recreation of identical JSON;
13. malformed JSON followed by restoration of identical JSON;
14. unrelated-key identity preservation through every affected-key transition;
15. the existing mount and subscription suite.

The interleaved control rejects a weaker one-entry key cache that would lose same-key identity whenever another atom reads between two reads of the first key.

## Exact-source execution

Run `30579399493` checked out exact Jotai source `56a9cc51...`, applied the generated diff with `git apply --check`, staged both native regressions, installed the exact lockfile with pnpm 11.3.0, and passed on Node 22, 24, and 26:

- key isolation;
- removal settlement;
- unreadable-state invalidation;
- the existing `atomWithStorage.test.tsx` suite;
- ESLint on changed source and tests;
- Prettier on changed source and tests;
- `tsc --noEmit`.

Fieldwork integrity run `30579399390` passed on the same source/test head.

## Retention policy decision

A per-key `Map` strongly retains one serialized string and parsed value for every observed key until one of these events occurs:

- `removeItem(key)` settles;
- a later read observes missing or malformed storage state;
- the adapter becomes unreachable.

Three viable policies remain:

### A. Accept adapter-lifetime per-key retention

This preserves same-key identity across arbitrary interleaving and fits adapters whose key set is bounded. Dynamic key churn can retain values for the adapter lifetime.

### B. Add a bounded cache

An LRU or fixed-capacity cache bounds memory. Eviction intentionally breaks same-key identity after sufficient unrelated-key activity, weakening the compatibility behavior introduced for mount-time rereads.

### C. Add explicit lifecycle authority

A disposal or key-release primitive can preserve identity while giving callers deterministic cleanup. This widens the public or semi-public adapter contract and requires subscriber, shared-adapter, and backward-compatibility design.

Weak references do not provide a reliable compatibility answer: object identity can disappear according to garbage-collection timing, primitive parsed values cannot be weakly referenced, and supported runtime boundaries require separate review.

The evidence supports selecting among A, B, and C. It does not support silently presenting unbounded retention as cost-free.

## Other concurrency limits

The candidate does not establish universal same-key identity under out-of-order asynchronous reads. A late older read can replace the per-key cache entry after a newer read resolves, causing a later current read to parse again. That race predates the candidate and remains outside this narrow repair.

Concurrent `setItem` and `removeItem` authority remains unchanged. This candidate owns parsed-object identity and read/removal invalidation, not a general storage-operation generation protocol.

## Direct-source status

No owned `teamleaderleo/jotai` working copy exists at this review boundary. The exact candidate remains a Fieldwork patch carrier over immutable source. Production promotion requires a direct owned source branch, ordinary repository-wide gates on that branch, and complete-diff review of the direct implementation.

## Claim-scoped evidence

- released cross-key alias: `target-executed`;
- source history and original intent: `source-read`;
- key-scoped candidate: `target-executed`;
- removal settlement candidate: `target-executed`;
- out-of-band and malformed-read invalidation: `target-executed`;
- focused native regression: `target-executed` on Node 22, 24, and 26;
- changed-file lint, formatting, and type checks: `target-executed`;
- full repository test and build: absent;
- direct owned source branch: absent;
- dynamic-key retention policy: `needs-decision`;
- asynchronous read completion ordering: unchanged and unresolved;
- concurrent set/remove ordering: unchanged and unresolved;
- ecosystem frequency and production impact: unmeasured;
- upstream acceptance: absent.

## Current disposition

**ACCEPT the bounded released finding and exact-source candidate execution. DESIGN-DECISION-READY for cache retention policy. HOLD production implementation acceptance until policy A, B, or C is selected, a direct owned source branch passes ordinary repository gates, and its complete diff receives independent review.**

Smallest next steps:

1. select the retention contract;
2. create or identify an owned Jotai working copy without contacting public upstream;
3. transfer the exact source and tests to a direct branch;
4. run ordinary format, types, lint, specs, and build gates;
5. complete-diff review the direct head.

No public upstream interaction occurred.
