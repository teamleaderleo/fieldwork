# Candidate source-equivalent execution

Date: 2026-07-30

Runtime: Node `v22.16.0`

Candidate head: `teamleaderleo/zustand@047425c2d909eefaf712046b4b4021062f6e8cff`

Candidate patch: `.fieldwork/persist-rehydrate-error-settlement.patch`

## Method

A standalone Node script transcribed the pinned Zustand vanilla store, `createJSONStorage`, synchronous `toThenable`, and persist hydration control flow, then applied the candidate's private `throwOnError` behavior.

This was an independent execution of the exact relevant control flow. It did not install or build the released package and is not a substitute for either clean-checkout workflow.

## Passing cases

- asynchronous storage rejection rejected the explicit hydration with the original error;
- synchronous malformed JSON rejected with the native `SyntaxError`;
- synchronous migration failure rejected with the original error;
- synchronous merge failure rejected with the original error;
- every failed explicit attempt retained current state and left `hasHydrated()` false;
- automatic synchronous parsing failure remained contained and reached the post-rehydration callback;
- a failed explicit read was followed by a successful retry that applied `{ count: 42 }` and set `hasHydrated()` true;
- a failed superseded attempt resolved quietly after the current attempt applied `{ count: 2 }`.

## Output

```json
{
  "node": "v22.16.0",
  "cases": [
    "async storage",
    "sync parse",
    "migration",
    "merge"
  ],
  "automaticContained": true,
  "retryRecovered": true,
  "supersededSuppressed": true
}
```

## Boundary

The source-equivalent execution supports the candidate design and specifically verifies the synchronous thenable-to-rejected-Promise bridge. The candidate remains unconfirmed until the exact fork workflows apply the real patch to a clean checkout and run the repository's test suites.