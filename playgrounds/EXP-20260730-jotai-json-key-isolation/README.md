# Jotai JSON storage key isolation

## In simple words

Jotai can save atom values as JSON. One `createJSONStorage()` object may be reused by several atoms with different storage keys. The implementation remembers the last JSON string it parsed so repeated reads can reuse the same object.

Exact released `jotai@2.20.2` now confirms that this memory crosses key boundaries: two different keys containing identical JSON receive the exact same object instance. Mutating the object returned for key A also changes the object previously returned for key B, even though B's storage entry was never written.

Current state: `target-executed` and promoted to Fieldwork lane #235. This is a bounded key-isolation finding, not an ecosystem-impact or security claim.

## Where this sits

`createJSONStorage()` adapts string storage such as `localStorage`, `sessionStorage`, or React Native AsyncStorage into Jotai's value-oriented storage interface.

The reviewed source keeps these variables once per adapter:

```ts
let lastStr: string | undefined
let lastValue: Value
```

Every `getItem(key, initialValue)` call consults the same pair. The cache is adapter-scoped rather than key-scoped.

## Why the cache exists

The JSON cache was introduced in Jotai PR #1080, commit `9e336c6bd2bebf257ffca957b0af18f97444323c`, to repair issue #1079.

That issue described one atom and one storage key:

1. storage contains value 1;
2. the atom initializes from value 1;
3. storage changes to value 2 before the atom mounts;
4. subscription setup and the mount-time read must not leave the atom at the stale value 1.

The repair re-read storage after subscribing. Because `JSON.parse()` creates a new object on each read, the same serialized object could otherwise appear as a different value during the single-key mount sequence. PR #1080 added one remembered JSON string and value to preserve identity for that repeated read.

The retained regression used only the `count` key. It did not exercise two independent keys through one adapter. The original intent therefore supports preserving identity **within one key**, but it does not establish that identity should be shared **between keys**.

The cache has remained present from Jotai 1.x through release `2.20.2`. The `2.20.2` release commit `5c4ca26b0db5571114be58393e17854a771f7790` and current reviewed main both contain the same adapter-wide cache shape.

## Duplicate and test search

Current source tests cover:

- one-key repeated initialization and mount behavior;
- synchronous and asynchronous storage;
- browser and custom subscriptions;
- reset propagation;
- validation and reviver behavior.

No retained test was found for two storage keys containing identical JSON through one `createJSONStorage()` adapter. Targeted issue and pull-request searches found no report specifically about cross-key parsed-object identity or mutation aliasing.

## Exact released-package execution

Workflow `30548784323` passed on:

- Node `v22.23.1`;
- Node `v24.18.0`;
- Node `v26.5.1`.

Each job imported exact `jotai@2.20.2`, which reported no runtime dependencies.

Observed in every job:

```text
same adapter + same key + same JSON: same object
same adapter + different keys + same JSON: same object
same adapter + different keys + different JSON: different objects
separate adapters + same JSON: different objects
mutate key A object: key B object changes in memory
```

Receipts:

- `result.json` — exact released-package matrix;
- `model-result.json` — earlier source-equivalent Node 22 control.

## Why this could matter

Jotai does not require atom values to be deeply immutable. Applications may store objects for preferences, drafts, filters, sessions, or cached UI state. Independent storage keys normally imply independent stored values.

Cross-key object aliasing makes an atom's in-memory value depend on read order and on whether another key happened to contain byte-for-byte identical JSON. It can create a change in one atom without a write, subscription event, or storage change for the other key.

This evidence supports a mechanism claim. It does not establish how often applications reuse one adapter, mutate stored objects, or experience production failures.

## Candidate repair boundary

Do not remove the unchanged-JSON identity cache. The history shows that it protects the single-key subscription/mount sequence.

The narrow direction is to scope the cache by key while preserving repeated-read identity for the same key.

A repository-native regression and candidate should prove:

- unchanged repeated reads for one key preserve the #1079 behavior;
- different keys never share a parsed object solely because their serialized text is equal;
- asynchronous string storage follows the same key-isolation rule;
- subscriptions and revivers remain compatible;
- reset/remove invalidates the right key;
- cache entries have a deliberate lifecycle or bound for dynamic keys.

## Fieldwork promotion

Promoted lane:

`teamleaderleo/fieldwork#235`

Durable report:

`programmes/data-durable-workflows/scouts/jotai-json-storage-key-isolation/report.md`

The earlier playground validator failure was metadata-only: unsupported custom `state` and `network_policy` strings. The record now uses supported values and must pass fresh repository validation on the promoted head.

## Stop condition

Stop the next implementation pass when one key-aware cache design preserves the original same-key behavior, prevents cross-key aliasing, defines cache lifecycle, and passes synchronous, asynchronous, subscription, reviver, and reset controls.

Upstream contact authorized: `false`.
