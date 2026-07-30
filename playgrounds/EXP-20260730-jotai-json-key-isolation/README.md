# Jotai JSON storage key isolation

## In simple words

Jotai can save atom values as JSON. One `createJSONStorage()` object may be reused by several atoms with different storage keys. The implementation remembers the last JSON string it parsed so repeated reads can reuse the same object.

A source-equivalent Node 22 control now confirms that this memory crosses key boundaries: two different keys containing identical JSON receive the exact same object instance. Mutating the object returned for key A also changes the object previously returned for key B, even though B's storage entry was never written.

Current state: `model-executed`; exact released-package Node 22/24/26 execution remains queued. This is a mechanism finding, not yet a target-executed defect or an ecosystem-impact claim.

## Where this sits

`createJSONStorage()` adapts string storage such as `localStorage`, `sessionStorage`, or React Native AsyncStorage into Jotai's value-oriented storage interface.

The reviewed source keeps these variables once per adapter:

```ts
let lastStr: string | undefined
let lastValue: Value
```

Every `getItem(key, initialValue)` call consults the same pair. The cache is adapter-scoped rather than key-scoped.

## Model execution

Environment:

- Node.js `v22.16.0`;
- Linux `6.12.13 x86_64`;
- exact `createJSONStorage()` cache and parse logic transcribed from source revision `56a9cc51de8a5dd762b95a145820f12589cc47c9`;
- synthetic in-memory string storage;
- no network access.

Observed:

```text
same adapter + same key + same JSON: same object
same adapter + different keys + same JSON: same object
same adapter + different keys + different JSON: different objects
separate adapters + same JSON: different objects
mutate key A object: key B object changes in memory
```

The machine-readable receipt is `model-result.json`.

## Hypotheses

### H1 — adapter-wide identity sharing

Two different keys containing the same JSON text return the exact same object reference. The model execution supports this hypothesis.

### H2 — key isolation survives

The package or runtime creates distinct objects per key despite the source-level cache shape. The source-equivalent control does not support this hypothesis, but the released package still needs to run before H2 is rejected at the target boundary.

## Controls

The released-package probe compares:

1. the same adapter, same key, same JSON — repeated reads may intentionally preserve identity;
2. the same adapter, different keys, same JSON — the disputed boundary;
3. the same adapter, different keys, different JSON — should not share identity;
4. separate adapters, different keys, same JSON — should not share identity;
5. mutation of the first returned object — records whether the second returned object aliases it.

## Why this could matter

Jotai does not require atom values to be deeply immutable. Applications may store objects for preferences, drafts, filters, sessions, or cached UI state. Independent storage keys normally imply independent stored values.

Cross-key object aliasing would make an atom's in-memory value depend on read order and on whether another key happened to contain byte-for-byte identical JSON. It can create a change in one atom without a write, subscription event, or storage change for the other key.

This experiment supports only a mechanism claim. It does not establish how often applications reuse one adapter, mutate stored objects, or experience production failures.

## Candidate repair boundary

Do not remove the unchanged-JSON identity cache without checking why it exists. The narrow direction is to scope the cache by key, for example one cached string/value pair per storage key, while preserving repeated-read identity for the same key.

A target-native regression should prove:

- unchanged repeated reads for one key preserve current behavior;
- different keys never share a parsed object solely because their serialized text is equal;
- asynchronous string storage follows the same key-isolation rule;
- subscriptions and revivers remain compatible.

No patch is selected until released-package execution and history review complete.

## Stop condition

Stop after the released package answers the identity question and the controls establish whether the behavior comes from one shared adapter cache. Promote only if the result survives duplicate/history review and a target-native regression can express the intended key-isolation contract.

Upstream contact authorized: `false`.
