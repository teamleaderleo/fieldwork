# Zustand persist undefined option overrides

State: `implementing`

Fieldwork lane: #170

Programme: data-durable-workflows

Target source: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Owned implementation: `teamleaderleo/zustand#2`

Owned branch: `fieldwork/persist-undefined-option-overrides`

Owned head: `278ede8b60c111ec4291b26cd95794d7bdd5da37`

Fork focused workflow: pending for corrected committed-source head

Fieldwork focused workflow: pending for Fieldwork head `b383c4b14abdf8e890616d1c040c85cb39613f6a`

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

Draft PR: `teamleaderleo/zustand#2`

Construction now uses destructuring defaults for:

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

## Regression suite

The committed test `tests/persistUndefinedOptions.test.ts` verifies:

- constructor undefined `merge` retains the default shallow merge;
- constructor undefined `partialize` retains identity persistence;
- the same defaults survive `setOptions()` updates;
- public and private storage remain aligned;
- the storage name remains stable;
- version `0` remains in serialized writes;
- `onRehydrateStorage` can still be removed intentionally.

The focused matrix runs this regression with the existing `persistAsync.test.tsx` and `persistSync.test.tsx` suites and lints the changed source and test on Node 22, 24, and 26.

## Candidate source-equivalent execution

A Node `v22.16.0` execution of the repaired option-resolution paths passed:

- construction defaults preserved;
- update defaults preserved;
- public/private storage alignment;
- optional callback removal.

A focused strict TypeScript model also compiled with TypeScript `5.8.3`.

The detailed candidate receipt is in `candidate-source-equivalent-execution.md`.

## Self-review correction

The first direct-source revision named the resolved construction storage value `storage`, colliding with the existing active storage variable later in the function. Source review caught the duplicate binding before CI. The corrected code uses `initialStorage`.

## Prior-art status

Searches for persist `merge`, `partialize`, `storage`, `setOptions`, explicit `undefined`, and default replacement found no matching current upstream issue or pull request.

## Compatibility assessment

The repair is deliberately field-aware rather than a blanket undefined filter.

Defaulted runtime invariants are preserved when an update supplies `undefined`, while optional callbacks and other intentionally clearable fields retain their existing removal semantics.

The remaining questions are repository-level:

- whether the destructuring changes affect generic inference under the project's full type matrix;
- whether any consumer intentionally used `version: undefined` to omit the version field;
- whether `storage: undefined` should preserve current storage or restore the platform default;
- whether additional defaulted fields should receive the same treatment.

## Current decision

Treat this as a confirmed source defect with a directly committed owned implementation. Keep the fork and Fieldwork PRs draft until native and focused CI are green.

## Boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.