# Zustand persist undefined option overrides

State: `direct-candidate-validating`

Fieldwork lane: #170

Programme: data-durable-workflows

Target source: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Owned implementation: `teamleaderleo/zustand#2`

Owned branch: `fieldwork/persist-undefined-option-overrides`

Current direct owned head: `9eb5e57318d765ceb0343944992551385a0aeb55`

Earlier transformed candidate head: `17e93d6bc9d48c39ef52d1a4735e00eabe08a06f`

Earlier focused workflow: `30507502603` — passed

Retained transformed-candidate receipt: `execution-receipt-30507502603.json`

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

Object spread copies properties whose value is explicitly `undefined`. Runtime callers and composed configuration objects could therefore replace useful functions and values without supplying a usable replacement.

`persist.setOptions()` repeated the spread behavior. Its storage handling was additionally split: `options.storage` could become `undefined`, while the private storage reference changed only when `newOptions.storage` was truthy.

The owned fork now contains the field-aware repair directly in source, with native tests and no temporary transformer or publishing workflow remaining.

## Confirmed released behavior

A source-equivalent Node `v22.16.0` execution confirmed:

- constructor `merge: undefined` caused hydration failure;
- constructor `partialize: undefined` changed in-memory state and then threw before persistence;
- the same failures could be introduced through `setOptions()`;
- `setOptions({ storage: undefined })` made public options report no storage while the old private storage kept reading and writing;
- `setOptions({ version: undefined })` removed version `0` from later JSON writes;
- `setOptions({ onRehydrateStorage: undefined })` intentionally removed the optional callback.

The detailed released-source receipt is in `source-equivalent-execution.md`.

## Direct owned implementation

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

## Review compatibility slice

Complete-diff review found two compatibility gaps in the first direct implementation:

1. construction placed user fields before the resolved default fields, changing the observable `Object.keys(persist.getOptions())` order;
2. the first tests proved built-in default preservation but did not prove custom current values survive later `undefined` updates.

The accepted slice:

- preserves the historical default-field-first option insertion order;
- adds a key-order regression;
- proves custom current name, storage, partialize, version, and merge values survive later undefined updates;
- preserves explicit replacement storage and public/private alignment;
- continues allowing optional callback removal.

That slice is now committed directly at `9eb5e57318d765ceb0343944992551385a0aeb55`.

## Execution-carrier retirement

The earlier branch used `.fieldwork/apply_persist_options_review_repair.py` and a one-shot finalizer workflow to apply and validate the reviewed slice.

At the current direct head:

- the transformer is absent;
- the finalizer workflow is absent;
- the complete pull-request diff contains only:
  - `src/middleware/persist.ts`;
  - `tests/persistUndefinedOptions.test.ts`;
  - the permanent read-only focused workflow.

This establishes canonical source application. It does not by itself establish the fresh direct-head test result.

## Earlier transformed-candidate execution

Focused workflow `30507502603` passed on Node 22, 24, and 26.

Each job passed:

```text
13 undefined-option regressions
22 existing sync persist tests
21 existing async persist tests
56 total focused tests
ESLint on changed source and tests
Prettier verification
```

The executed controls established the intended behavior and compatibility slice before direct publication. This receipt remains useful evidence for the transformation, but it is not reused as the full-gate result for the new direct head.

## Direct-head review

An exact-head complete-diff review at `9eb5e57318d765ceb0343944992551385a0aeb55` accepts the code and test shape:

- no accidental whole-file churn;
- no surviving carrier material;
- field-aware rather than blanket undefined handling;
- no reinterpretation of `null`;
- explicit replacement values still work;
- optional callbacks remain clearable;
- native tests cover JavaScript/runtime inputs despite `exactOptionalPropertyTypes` rejecting explicit undefined in ordinary typed calls.

Disposition from that review:

**ACCEPT the direct candidate shape. EXECUTE fresh exact-head workflows. HOLD landing until the focused and ordinary Test gates settle.**

## Current direct-head workflows

At the latest check, these runs for `9eb5e57318d765ceb0343944992551385a0aeb55` were queued:

- focused Node 22/24/26 persist matrix: `30548049634`;
- ordinary Test: `30548052302`;
- multiple versions: `30548049523`;
- multiple builds: `30548050329`;
- old TypeScript: `30548049441`;
- compressed size: `30548048680`;
- preview publication: `30548053498`.

Preview publication remains optional fork configuration rather than product evidence. The focused and ordinary Test workflows are the immediate acceptance gates.

## Claim-scoped evidence

- released undefined-option failures: `model-executed` through source-equivalent Node execution;
- intended candidate behavior and selected compatibility: `target-executed` through transformed-candidate run `30507502603`;
- direct source application and carrier retirement: `source-read` and complete-diff reviewed at `9eb5e573...`;
- direct exact-head focused execution: queued;
- direct ordinary full Test gate: queued;
- ecosystem compatibility for consumers intentionally relying on explicit `undefined`: unmeasured.

## Compatibility assessment

The repair is deliberately field-aware rather than a blanket undefined filter.

Defaulted runtime invariants are preserved when an update supplies `undefined`, while optional callbacks and other intentionally clearable fields retain their existing removal semantics.

Remaining questions after the direct matrix:

- whether any consumer intentionally used `version: undefined` to omit the version field;
- whether `storage: undefined` should preserve current storage or restore the platform default;
- whether any additional defaulted fields need the same policy.

Those are compatibility questions, not reasons to misclassify the confirmed released failures.

## Current decision

Accept the direct code and test shape. Keep both PRs draft while the fresh exact-head focused and ordinary Test workflows run.

If those gates pass:

1. retain their exact run and job receipts;
2. refresh the complete-diff review against the unchanged head;
3. update Fieldwork #170 and #172 to `validated-candidate`;
4. decide owned-fork landing separately from upstream preparation;
5. keep public upstream contact unauthorized unless separately approved.

## Boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.