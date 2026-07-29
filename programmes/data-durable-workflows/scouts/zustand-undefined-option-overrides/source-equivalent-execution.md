# Source-equivalent execution

Date: 2026-07-30

Runtime: Node `v22.16.0`

Source pin: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

## Method

A standalone Node script transcribed the pinned vanilla store, JSON storage adapter, synchronous thenable, persist option merge, `setItem`, hydration, and `setOptions()` paths.

This independently executed the exact relevant control flow. It did not install or build the package and is not a substitute for the clean-checkout matrices.

## Confirmed behavior

### Constructor `merge: undefined`

- explicit hydration fulfilled under the released error-settlement contract;
- state remained `{ count: 0 }`;
- `hasHydrated()` remained false;
- the post-rehydration callback received `TypeError: options.merge is not a function`.

### Constructor `partialize: undefined`

- `setState({ count: 1 })` changed the in-memory state;
- persistence then threw a `TypeError`;
- storage `setItem` was not called.

### `setOptions({ merge: undefined })`

- `getOptions().merge` became `undefined`;
- the next hydration failed with `TypeError: options.merge is not a function`.

### `setOptions({ partialize: undefined })`

- `getOptions().partialize` became `undefined`;
- the next `setState` changed in-memory state and then threw before persistence.

### `setOptions({ storage: undefined })`

- `getOptions().storage` reported `undefined`;
- the existing private storage still received one write and one later read;
- hydration from that old storage applied `{ count: 3 }`.

### `setOptions({ version: undefined })`

- the next JSON write serialized as `{"state":{"count":1}}`;
- the default version `0` was silently omitted.

### Optional callback control

- `setOptions({ onRehydrateStorage: undefined })` intentionally removed the callback;
- the later hydration succeeded without invoking it.

## Output

```json
{
  "node": "v22.16.0",
  "results": {
    "constructorMergeUndefined": "options.merge is not a function",
    "constructorPartializeUndefined": "state changed before persistence error",
    "setOptionsMergeUndefined": "options.merge is not a function",
    "setOptionsPartializeUndefined": "state changed before persistence error",
    "storageUndefined": "public option undefined; old private storage still active",
    "versionUndefined": "{\"state\":{\"count\":1}}",
    "callbackUndefined": "optional callback removed intentionally"
  }
}
```

## Decision effect

The execution confirms a field-aware repair is required. Ignoring every undefined update would fix defaulted runtime invariants but would also break intentional removal of optional callbacks. The clean-checkout matrix must settle before a candidate resolver is retained.