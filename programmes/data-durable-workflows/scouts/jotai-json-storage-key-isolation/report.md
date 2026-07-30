# Jotai JSON storage key isolation

State: `target-confirmed`

Fieldwork lane: #235

Programme: data-durable-workflows

Evidence PR: #228

Playground: `EXP-20260730-jotai-json-key-isolation`

Target repository: `pmndrs/jotai`

Released package: `jotai@2.20.2`

Release source: `5c4ca26b0db5571114be58393e17854a771f7790`

Current reviewed source: `56a9cc51de8a5dd762b95a145820f12589cc47c9`

Upstream contact authorized: `false`

## In simple words

Jotai's `createJSONStorage()` converts string storage into JavaScript values. It remembers the last JSON string it parsed so reading unchanged storage can return the same object again.

That memory belongs to the entire storage adapter, not one key.

When two independent keys contain the same JSON text, exact released `jotai@2.20.2` returns the same object instance for both. Mutating the object returned for key A therefore also changes the in-memory object already returned for key B, even though key B was not written and no key-B subscription ran.

This is a bounded object-identity and key-isolation defect. It is not evidence of remote code execution, data exfiltration, or broad ecosystem impact.

## Source mechanism

The adapter owns one cache pair:

```ts
let lastStr: string | undefined
let lastValue: Value
```

`getItem(key, initialValue)` reads the selected key but compares the returned string with the adapter-wide `lastStr`:

```ts
const str = getStringStorage()?.getItem(key) ?? null
if (isPromiseLike(str)) {
  return str.then(parse)
}
return parse(str)
```

The parser returns `lastValue` whenever the new string equals `lastStr`, regardless of which key produced that string.

The same cache shape exists in release source `5c4ca26...` and current reviewed source `56a9cc51...`.

## Why the cache exists

The cache was added by Jotai PR #1080 / commit `9e336c6bd2bebf257ffca957b0af18f97444323c` to repair issue #1079.

That issue involved one atom and one `count` key:

1. storage supplied one object value during atom creation;
2. storage changed before the atom mounted;
3. mount subscribed and then reread storage;
4. repeated `JSON.parse()` calls could create distinct object identities and leave the atom at the wrong pre-mount value.

PR #1080 deliberately preserved identity for the repeated same-key read. Its retained regression used only one key. It did not test multiple keys through one adapter.

The compatibility requirement is therefore:

- preserve unchanged repeated-read identity for one key;
- do not share parsed object identity across independent keys solely because their serialized bytes are equal.

## Exact released-package execution

Workflow:

`30548784323`

Exact Fieldwork head under test:

`118d428122efe8b7aa2d3fef505f904e4976760a`

All jobs passed:

| Node | Job | Result |
| --- | --- | --- |
| `v22.23.1` | `90891718906` | success |
| `v24.18.0` | `90891719038` | success |
| `v26.5.1` | `90891719348` | success |

The probe imported exact `jotai@2.20.2`. The installed package reported no runtime dependencies.

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

## Source-equivalent control

Before the package matrix, Node `v22.16.0` executed the exact cache and parse logic transcribed from source.

That model produced the same result and is retained separately in:

`playgrounds/EXP-20260730-jotai-json-key-isolation/model-result.json`

The package execution supersedes the model for the released-behavior claim. The model remains useful as a minimal mechanism receipt.

## Why this can matter

One `createJSONStorage()` adapter is commonly intended to serve multiple atom keys. Independent keys ordinarily imply independent stored values and independent update histories.

Cross-key aliasing makes the in-memory value depend on read order and byte-for-byte JSON equality:

```text
key A contains {"nested":{"count":1}}
key B contains {"nested":{"count":1}}
read A
read B
mutate object returned for A
object already returned for B changes too
```

No storage write, subscription event, or key-B update explains that change.

The consequence requires mutable object use. Primitive values do not expose object aliasing, and immutable application discipline can reduce practical impact. The experiment does not measure how frequently applications share one adapter or mutate returned stored objects.

## Duplicate and history review

Targeted current and historical searches found:

- the original one-key identity issue #1079;
- the implementing PR #1080;
- no retained test for two keys containing equal JSON through one adapter;
- no matching current issue or pull request specifically about cross-key parsed-object identity or mutation aliasing.

Refresh this search before preparing any public packet.

## Narrow repair direction

Do not remove JSON memoization.

The first candidate should scope cached parsed identity by storage key while retaining the same-key behavior from #1079.

Possible forms include:

- a `Map<string, { lastStr, lastValue }>`;
- a bounded key-aware cache;
- storage-key lifecycle cleanup tied to remove/reset behavior.

The simplest map may retain entries indefinitely for unbounded dynamic keys. Memory lifecycle is therefore part of the repair contract, not an afterthought.

## Required target-native matrix

Before retaining a patch, add repository-native tests for:

1. synchronous storage, same key, unchanged object JSON preserves identity;
2. synchronous storage, different keys, equal object JSON returns distinct objects;
3. mutating one returned object does not affect another key's returned object;
4. asynchronous string storage follows the same rule;
5. subscription-delivered equal JSON is isolated by key;
6. custom reviver output is isolated by key;
7. reset/remove invalidates only the affected key cache;
8. dynamic-key use has a deliberate memory-retention policy;
9. the original #1079 pre-mount subscription regression remains fixed;
10. primitive values remain behaviorally unchanged.

## Evidence classification

- cache source shape and history: `source-read`;
- source-equivalent mechanism: `model-executed`;
- exact released package on Node 22/24/26: `target-executed`;
- repository-native regression: absent;
- repair candidate: absent;
- integration or ecosystem impact: unmeasured;
- security impact: not claimed.

## Harness note

The package workflow, Fieldwork integrity, and external-reference policy passed on the executed head.

The separate playground/context validator failed because the experiment used unsupported custom metadata values:

```text
state = model-confirmed-package-pending
network_policy = dependency-install-only; ...
```

That was a Fieldwork metadata defect, not a target-probe failure. The experiment has been repaired to supported values and promoted to lane #235. Fresh repository validation must settle on the repaired head.

## Current disposition

**ACCEPT the bounded key-isolation finding. PREPARE a repository-native regression and key-scoped cache experiment. HOLD impact claims, upstream wording, and public contact.**

## Stop condition

Stop the next implementation pass when one key-aware cache design simultaneously:

- preserves the #1079 same-key identity behavior;
- prevents cross-key object aliasing;
- defines cache cleanup or bounds;
- passes synchronous, asynchronous, subscription, reviver, and reset controls.

No public upstream interaction occurred.