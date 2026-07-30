# Zustand persist undefined option overrides

State: `validated-candidate`

Fieldwork lane: #170

Programme: data-durable-workflows

Target source: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Owned implementation: `teamleaderleo/zustand#2`

Owned branch: `fieldwork/persist-undefined-option-overrides`

Validated direct head: `9eb5e57318d765ceb0343944992551385a0aeb55`

Direct focused workflow: `30548049634` — passed

Ordinary Test workflow: `30548052302` — passed

Direct receipt: `direct-head-execution-receipt.json`

Upstream contact authorized: `false`

## In simple words

Zustand persist supplies useful defaults for storage, selecting state, versioning saved data, and merging saved state back into memory.

Explicit JavaScript properties whose value is `undefined` were still spread over those defaults. That could erase a required function or value without supplying a usable replacement.

The released behavior could therefore:

- make later hydration fail because `merge` disappeared;
- change in-memory state and then throw before persistence because `partialize` disappeared;
- make public options say no storage exists while private code keeps using the old storage;
- silently omit the default version from saved JSON.

The owned fork now has a direct, field-aware repair with native regression coverage and full repository validation.

## Confirmed released behavior

A source-equivalent Node `v22.16.0` execution confirmed:

- constructor `merge: undefined` caused hydration failure;
- constructor `partialize: undefined` changed state and then threw before persistence;
- both failures could be introduced through `setOptions()`;
- `setOptions({ storage: undefined })` split public options from private active storage;
- `setOptions({ version: undefined })` removed version `0` from later JSON writes;
- `setOptions({ onRehydrateStorage: undefined })` intentionally removed the optional callback.

Detailed receipt:

`source-equivalent-execution.md`

## Validated repair contract

At construction, explicit `undefined` preserves built-in defaults for:

- `storage`;
- `partialize`;
- `version`;
- `merge`.

During `persist.setOptions()`, explicit `undefined` preserves the current value for:

- `name`;
- `storage`;
- `partialize`;
- `version`;
- `merge`.

Other fields retain ordinary spread semantics. Optional callbacks such as `onRehydrateStorage` remain clearable with `undefined`.

The repair also:

- assigns public and private storage from the same resolved value;
- preserves explicit replacement values;
- does not reinterpret `null`;
- preserves historical default-field-first option key order;
- preserves custom current values rather than only built-in defaults;
- covers runtime JavaScript input despite `exactOptionalPropertyTypes` preventing ordinary typed callers from spelling some explicit-undefined cases.

## Canonical source state

The final owned fork diff contains only:

- `src/middleware/persist.ts`;
- `tests/persistUndefinedOptions.test.ts`;
- `.github/workflows/fieldwork-persist-undefined-options.yml`.

Temporary transformer and finalizer files are absent.

Complete-diff review found no accidental whole-file churn or execution-carrier material.

## Exact direct-head execution

### Focused matrix

Workflow `30548049634` passed on Node 22, 24, and 26.

| Node | Job | Result |
| --- | --- | --- |
| 22 | `90889203224` | success |
| 24 | `90889203354` | success |
| 26 | `90889203340` | success |

Every focused job passed:

- direct candidate formatting and diff hygiene;
- the undefined-option regression suite;
- existing synchronous persist tests;
- existing asynchronous persist tests;
- ESLint;
- Prettier;
- TypeScript checks.

### Ordinary repository Test

Workflow `30548052302`, job `90889211792`, passed:

- `test:format`;
- `test:types`;
- `test:lint`;
- `test:spec`;
- build.

### Adjacent repository gates

Passed:

- multiple builds `30548050329`;
- multiple versions `30548049523`;
- old TypeScript `30548049441`;
- compressed size `30548048680`.

Preview Release `30548053498` failed because the user-owned fork lacks the publishing application/configuration. It is classified separately as optional fork publishing infrastructure, not product evidence.

## Earlier transformed-candidate receipt

Before direct publication, workflow `30507502603` passed the selected compatibility slice on Node 22, 24, and 26.

That receipt remains useful history but is no longer needed to infer direct-head correctness. The direct source itself now has complete target and repository execution.

Retained file:

`execution-receipt-30507502603.json`

## Review disposition

Final exact-head review at `9eb5e57318d765ceb0343944992551385a0aeb55`:

**VALIDATED CANDIDATE. ACCEPT THE OWNED CODE/TEST RESULT. HOLD UPSTREAM PREPARATION.**

The candidate mechanism, compatibility slice, canonical source state, focused matrix, and ordinary repository Test all refer to the same unchanged head.

## Remaining policy questions

These do not invalidate the candidate, but they matter before public upstream preparation:

- whether any consumer deliberately used `version: undefined` to omit the version field;
- whether a consumer expected `storage: undefined` to restore the platform default rather than preserve current storage;
- whether other defaulted persist fields should share this policy;
- whether the change belongs in one patch or separate construction and `setOptions()` patches.

Refresh duplicate/history search and upstream contribution requirements before preparing any external packet.

## Evidence classification

- released behavior: `model-executed` through source-equivalent Node execution;
- direct implementation mechanism: `source-reviewed`;
- focused direct candidate: `target-executed` on Node 22/24/26;
- full repository format/types/lint/spec/build: `target-executed`;
- adjacent build/version/old-TS/size checks: `target-executed`;
- ecosystem compatibility for intentional explicit-undefined use: unmeasured;
- upstream acceptance: absent.

## Current decision

The owned candidate is validated.

Next decisions are separate:

1. whether to merge `teamleaderleo/zustand#2` in the owned fork;
2. whether to prepare an upstream issue or pull request;
3. how to word the compatibility boundary;
4. whether additional ecosystem sampling is warranted.

No merge or upstream contact is implied by validation.

## Boundary

No public upstream issue, pull request, comment, review, reaction, branch, or message has been created.