# Candidate source-equivalent execution

Date: 2026-07-30

Runtime: Node `v22.16.0`

Candidate head: `teamleaderleo/zustand@278ede8b60c111ec4291b26cd95794d7bdd5da37`

## Method

A standalone Node script transcribed the pinned vanilla store, JSON storage adapter, synchronous thenable, persist construction, `setItem`, hydration, and `setOptions()` paths, then applied the field-aware option resolution used by the owned candidate.

A focused strict TypeScript model of the construction and `setOptions()` declarations also compiled with TypeScript `5.8.3`.

This is an independent control-flow and type-shape receipt. It is not a substitute for the repository's native or focused CI.

## Passing behavior

- constructor `merge: undefined` retained the default shallow merge;
- constructor `partialize: undefined` retained identity persistence;
- `setOptions()` preserved `name`, `storage`, `partialize`, `version`, and `merge` when their supplied value was `undefined`;
- public `options.storage` and the private active storage remained the same object;
- writes retained version `0`;
- later hydration continued reading from the reported storage;
- `onRehydrateStorage: undefined` still removed the optional callback intentionally.

## Output

```json
{
  "node": "v22.16.0",
  "constructionDefaultsPreserved": true,
  "updateDefaultsPreserved": true,
  "storageAligned": true,
  "optionalCallbackClearable": true
}
```

## Review correction

The first direct-source revision reused the identifier `storage` for both the resolved construction option and the later active storage variable. Source review caught the duplicate binding before CI. The corrected implementation names the construction value `initialStorage`.

## Boundary

The candidate remains draft until native and focused Node 22, 24, and 26 matrices settle.