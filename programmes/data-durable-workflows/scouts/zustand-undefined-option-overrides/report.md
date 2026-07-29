# Zustand persist undefined option overrides

State: `probe-prepared`

Fieldwork lane: #170

Programme: data-durable-workflows

Target source: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Owned characterization: `teamleaderleo/zustand#2`

Owned branch: `fieldwork/persist-undefined-option-overrides`

Owned head: `79ed669019eed3733361cb3a338860dc9b8353c2`

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

## Source consequences

### `merge: undefined`

Hydration reaches `options.merge(...)`, throws a `TypeError`, retains current state, leaves `hasHydrated()` false, and reports the failure only through the optional post-rehydration callback under the released contract.

### `partialize: undefined`

The wrapped `setState` applies the state mutation first and then calls `setItem()`. `setItem()` calls `options.partialize(...)`, so the state changes before a `TypeError` prevents persistence.

### `storage: undefined` through `setOptions`

`getOptions().storage` reports `undefined`, but the private storage reference remains unchanged because the update is guarded by a truthiness check. Later reads and writes continue using storage that the public options object says is absent.

### `version: undefined`

Later writes pass `{ version: undefined }` to JSON storage. `JSON.stringify` omits the field, silently changing the persistence format from the default version `0`.

## Characterization cases

The owned branch prepares assertions for:

- constructor `merge: undefined`;
- constructor `partialize: undefined`;
- `setOptions({ merge: undefined })`;
- `setOptions({ partialize: undefined })`;
- `setOptions({ storage: undefined })` with later reads and writes;
- `setOptions({ version: undefined })` with serialized output;
- `setOptions({ onRehydrateStorage: undefined })` as an intentional-clear control.

The control matters: a blanket rule that ignores every `undefined` update would stop callers from removing optional callbacks. Any repair must distinguish defaulted/invariant fields from intentionally clearable fields.

## Prior-art status

Searches for persist `merge`, `partialize`, `storage`, `setOptions`, and explicit `undefined` found no matching current upstream issue or pull request.

## Validation plan

The characterization source is stored outside Vitest's default `tests` directory. A clean-checkout workflow copies it into `tests`, runs it with the existing async and sync persist suites, and lints it on Node 22, 24, and 26.

Do not retain a repair before execution. Candidate directions include:

1. restore defaults only for invariant/defaulted fields when their value is `undefined`;
2. normalize construction and `setOptions()` through a shared field-aware resolver;
3. validate and reject explicit `undefined` for required runtime invariants;
4. preserve explicit removal for callbacks and other intentionally clearable fields.

## Boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.