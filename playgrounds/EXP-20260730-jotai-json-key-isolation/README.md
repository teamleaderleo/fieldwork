# Jotai JSON storage key isolation

## In simple words

Jotai can save atom values as JSON. One `createJSONStorage()` object may be reused by several atoms with different storage keys. The implementation remembers the last JSON string it parsed so repeated reads can reuse the same object. We are testing whether that memory is accidentally shared across keys. If two independent keys receive the same object instance, changing a mutable object obtained from one atom can also change what the other atom appears to contain even though its storage entry was never updated.

Current state: prepared for exact released-package execution. No defect is claimed yet.

## Where this sits

`createJSONStorage()` adapts string storage such as `localStorage`, `sessionStorage`, or React Native AsyncStorage into Jotai's value-oriented storage interface.

The reviewed source keeps these variables once per adapter:

```ts
let lastStr: string | undefined
let lastValue: Value
```

Every `getItem(key, initialValue)` call consults the same pair. The cache is therefore visibly adapter-scoped. The unresolved question is whether the released runtime returns one parsed object across independent keys when their serialized text is equal, and whether that identity sharing has a meaningful observable consequence.

## Hypotheses

### H1 — adapter-wide identity sharing

Two different keys containing the same JSON text return the exact same object reference. Mutating the object returned for key A is immediately observable through the value previously returned for key B.

### H2 — key isolation survives

The package or runtime creates distinct objects per key despite the source-level cache shape.

## Controls

The probe compares:

1. the same adapter, same key, same JSON — repeated reads may intentionally preserve identity;
2. the same adapter, different keys, same JSON — the disputed boundary;
3. the same adapter, different keys, different JSON — should not share identity;
4. separate adapters, different keys, same JSON — should not share identity;
5. mutation of the first returned object — records whether the second returned object aliases it.

## Why this could matter

Jotai does not require atom values to be deeply immutable. Applications commonly store objects for preferences, drafts, filters, sessions, or cached UI state. Independent storage keys normally imply independent stored values. Cross-key object aliasing would make the in-memory result depend on read order and on whether another key happened to contain byte-for-byte identical JSON.

This experiment supports only a mechanism claim. It will not establish how often applications reuse one adapter, mutate stored objects, or experience production failures.

## Stop condition

Stop after the released package answers the identity question and the controls establish whether the behavior comes from one shared adapter cache. Promote only if the result survives duplicate/history review and a target-native regression can express the intended key-isolation contract.

Upstream contact authorized: `false`.
