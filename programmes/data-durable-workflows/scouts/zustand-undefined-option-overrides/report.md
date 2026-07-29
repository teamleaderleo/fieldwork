# Zustand persist undefined option overrides

State: `source-confirmed`

Fieldwork lane: #170

Programme: data-durable-workflows

Target source: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Owned characterization: `teamleaderleo/zustand#2`

Owned branch: `fieldwork/persist-undefined-option-overrides`

Owned head: `79ed669019eed3733361cb3a338860dc9b8353c2`

Fork workflow: `30500083370`

Fieldwork workflow: `30500148562`

Upstream contact authorized: `false`

## In simple words

Persist creates defaults and then spreads user options over them:

```ts
let options = {
  storage: defaultStorage,
  partialize: (state) => state,
  version: 0,
  merge: defaultMerge,
  ...baseOptions,
}
```

Object spread copies properties whose value is explicitly `undefined`. Runtime callers and composed configuration objects can therefore replace defaulted functions and values without supplying a usable replacement.

`persist.setOptions()` repeats the spread behavior. Its storage handling is additionally split: `options.storage` can become `undefined`, but the private `storage` reference changes only when `newOptions.storage` is truthy.

## Source-equivalent execution

A Node `v22.16.0` execution transcribed the pinned vanilla store, JSON storage adapter, synchronous thenable, persist option merge, `setItem`, hydration, and `setOptions()` paths.

The execution confirmed every prepared case. The detailed receipt is in `source-equivalent-execution.md`.

## Confirmed consequences

### Constructor `merge: undefined`

- explicit hydration fulfilled under the released error-settlement contract;
- state remained `{ count: 0 }`;
- `hasHydrated()` remained false;
- the post-rehydration callback received `TypeError: options.merge is not a function`.

### Constructor `partialize: undefined`

- `setState({ count: 1 })` changed in-memory state;
- persistence then threw a `TypeError`;
- storage `setItem` was not called.

### `setOptions({ merge: undefined })`

- `getOptions().merge` became `undefined`;
- the next hydration failed with the same merge `TypeError`.

### `setOptions({ partialize: undefined })`

- `getOptions().partialize` became `undefined`;
- the next `setState` changed in-memory state and then threw before persistence.

### `setOptions({ storage: undefined })`

- `getOptions().storage` reported `undefined`;
- the existing private storage still received a write and a later read;
- the later hydration from that storage applied `{ count: 3 }`.

### `setOptions({ version: undefined })`

- the next JSON write serialized as `{"state":{"count":1}}`;
- the default version `0` was silently omitted.

### Optional callback control

- `setOptions({ onRehydrateStorage: undefined })` intentionally removed the callback;
- later hydration succeeded without invoking it.

## Characterization matrix

The owned branch stores the characterization outside Vitest's default `tests` directory. Dedicated workflows copy it into `tests`, run it with the existing async and sync persist suites, and lint it on Node 22, 24, and 26.

Fork workflow `30500083370` and Fieldwork workflow `30500148562` were queued at the latest recorded check. No clean-checkout result is claimed yet.

## Prior-art status

Searches for persist `merge`, `partialize`, `storage`, `setOptions`, explicit `undefined`, and default replacement found no matching current upstream issue or pull request.

## Candidate repair shape

A safe repair must be field-aware.

Defaulted or invariant fields should treat `undefined` as "not supplied":

- `name` during `setOptions()`;
- `storage`;
- `partialize`;
- `version`;
- `merge`.

Intentionally clearable fields should retain normal spread semantics:

- `onRehydrateStorage`;
- `migrate`;
- other optional callbacks or flags where clearing is meaningful.

One narrow implementation direction is to use destructuring defaults for the invariant fields at construction and during `setOptions()`, then spread the remaining fields normally. This would also keep the public `options.storage` and private storage reference aligned.

Do not retain a patch until the clean-checkout characterization matrix settles.

## Boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.