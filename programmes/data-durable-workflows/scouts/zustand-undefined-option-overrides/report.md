# Zustand persist undefined option overrides

State: `candidate-executed`

Fieldwork lane: #170

Programme: data-durable-workflows

Target source: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Owned implementation: `teamleaderleo/zustand#2`

Owned branch: `fieldwork/persist-undefined-option-overrides`

Exact executed owned head: `17e93d6bc9d48c39ef52d1a4735e00eabe08a06f`

Focused workflow: `30507502603` — passed

Retained receipt: `execution-receipt-30507502603.json`

Upstream contact authorized: `false`

## In simple words

Persist previously created defaults and then spread user options over them:

```ts
let options = {
  storage: defaultStorage,
  partialize: (state) => state,
  version: 0,
  merge: defaultMerge,
  ...baseOptions,
}
```

Object spread copies properties whose value is explicitly `undefined`. Runtime callers and composed configuration objects could therefore replace defaulted functions and values without supplying a usable replacement.

`persist.setOptions()` repeated the spread behavior. Its storage handling was additionally split: `options.storage` could become `undefined`, while the private storage reference changed only when `newOptions.storage` was truthy.

## Confirmed released behavior

A source-equivalent Node `v22.16.0` execution confirmed:

- constructor `merge: undefined` caused hydration failure;
- constructor `partialize: undefined` changed in-memory state and then threw before persistence;
- the same failures could be introduced through `setOptions()`;
- `setOptions({ storage: undefined })` made public options report no storage while the old private storage kept reading and writing;
- `setOptions({ version: undefined })` removed version `0` from later JSON writes;
- `setOptions({ onRehydrateStorage: undefined })` intentionally removed the optional callback.

The detailed released-source receipt is in `source-equivalent-execution.md`.

## Owned implementation

Construction uses defaulted resolution for:

- `storage`;
- `partialize`;
- `version`;
- `merge`.

`persist.setOptions()` resolves `undefined` to the current value for:

- `name`;
- `storage`;
- `partialize`;
- `version`;
- `merge`.

All other fields retain normal spread behavior. Optional callbacks such as `onRehydrateStorage` remain intentionally clearable with `undefined`.

The private active storage is assigned from the same resolved value stored in `options.storage`, keeping public and private state aligned.

## Complete-diff review repairs

Review found two compatibility gaps after the primary source change:

1. construction placed user fields before the resolved default fields, changing the observable `Object.keys(persist.getOptions())` order;
2. the tests proved built-in default preservation but did not prove custom current values survive later `undefined` updates.

The owned branch now contains an exact-anchor compatibility transformer used by the read-only focused workflow. It:

- restores the historical default-field-first option insertion order;
- adds a key-order regression;
- adds a custom current name/storage/partialize/version/merge preservation regression;
- fails closed when reviewed source or test anchors move;
- runs the target's pinned Prettier before validation.

This final compatibility slice is executed but not yet committed directly into the source and test files.

## Exact-head execution

Focused workflow run `30507502603` passed on Node 22, 24, and 26.

Each job passed:

```text
13 undefined-option regressions
22 existing sync persist tests
21 existing async persist tests
56 total focused tests
ESLint on changed source and tests
Prettier verification
```

The executed controls establish:

- construction `undefined` retains built-in storage, partialize, version, and merge defaults;
- later `undefined` updates retain custom current values;
- public and private storage remain aligned;
- historical options key order is preserved;
- optional callback removal remains possible;
- selected sync and async persist behavior remains compatible.

The broader native Test, old-TypeScript, build, multiple-version, preview, and size workflows were queued at the time this receipt was recorded.

## Harness history

Earlier exact-head runs are retained as partial receipts:

1. 51 behavior tests passed on Node 22/24/26, then one import-order lint rule failed;
2. after adding the key-order and custom-value controls, 56 behavior tests passed, then the same import-order rule failed;
3. after import ordering was corrected, 56 behavior tests and ESLint passed, then Prettier rejected the generated layout;
4. the accepted run applies the target formatter and passes every focused stage.

These failures were harness or presentation defects, not candidate behavior failures.

## Claim-scoped evidence

- released undefined-option failures: `model-executed` through source-equivalent Node execution;
- owned candidate option resolution and selected compatibility: `target-executed` through run `30507502603`;
- direct source application of the final compatibility slice: absent;
- complete repository gate: incomplete at receipt time;
- ecosystem compatibility for consumers intentionally relying on explicit `undefined`: unmeasured.

## Compatibility assessment

The repair is deliberately field-aware rather than a blanket undefined filter.

Defaulted runtime invariants are preserved when an update supplies `undefined`, while optional callbacks and other intentionally clearable fields retain their existing removal semantics.

The remaining questions are:

- whether the broader type and build matrices pass on a direct-source final head;
- whether any consumer intentionally used `version: undefined` to omit the version field;
- whether `storage: undefined` should preserve current storage or restore the platform default;
- whether any additional defaulted fields need the same policy.

## Current decision

Accept the candidate behavior and focused compatibility result.

Do not treat the current transformer-backed branch as a source-ready merge candidate. The next transition is:

1. apply the key-order and custom-current controls directly to a clean source/test branch;
2. run the broader repository gates at that exact source head;
3. perform complete-diff review;
4. keep upstream contact unauthorized unless separately approved.

## Boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.