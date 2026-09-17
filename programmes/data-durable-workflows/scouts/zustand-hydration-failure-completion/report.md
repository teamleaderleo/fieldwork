# Zustand persist hydration failure completion

State: `implementing`

Fieldwork lane: #158

Programme: data-durable-workflows

Target package: `zustand@5.0.14`

Source pin: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Released-package workflow: `30497117408`

Owned implementation: `teamleaderleo/zustand#1`

Owned branch: `fieldwork/persist-rehydrate-error-settlement`

Owned head: `66adffc63c8a4dd6aaee2b5c5761fb71ff35b351`

Fork candidate workflow: pending for committed-source head

Fieldwork candidate workflow: pending for Fieldwork head `52ec0427924f0da9a09c8f4c4d283ba40611edd4`

Upstream contact authorized: `false`

## In simple words

Zustand persist exposes three public hydration signals: the value returned by `rehydrate()`, the `hasHydrated()` flag, and `onFinishHydration()` listeners.

The released source catches storage, parsing, migration, and merge failures and reports them through the optional completion callback returned by `onRehydrateStorage`. It then returns normally. An explicit `await persist.rehydrate()` therefore fulfills while `hasHydrated()` remains false and finish listeners do not run.

The owned candidate makes only the explicit call observable: a current failed `persist.rehydrate()` rejects with the original error. Automatic startup hydration keeps containing errors, and the flag and finish listeners remain success-only signals.

## Confirmed source mechanism

`hydrate()` starts an attempt by incrementing `hydrationVersion`, clearing `hasHydrated`, and firing start listeners. The success path applies state, calls the post-rehydration callback, sets `hasHydrated = true`, and runs finish listeners.

The released error path is:

```ts
.catch((error) => {
  if (currentVersion !== hydrationVersion) return
  postRehydrationCallback?.(undefined, error)
})
```

Returning normally explains the fulfilled explicit await. The version check intentionally suppresses work from attempts superseded by a newer hydration.

## Released behavior probe

The exact-package probe covers:

- asynchronous storage rejection;
- malformed synchronous JSON;
- migration failure;
- merge failure;
- a failed attempt followed by a successful retry.

A source-equivalent Node 22.16.0 execution confirmed the same split state for all four failures:

- `rehydrate()` fulfilled;
- `hasHydrated()` remained false;
- `onHydrate` fired once;
- `onFinishHydration` did not fire;
- current state was retained;
- the post-`onRehydrateStorage` callback received the concrete error.

The released-package Node 22, 24, and 26 workflow remains queued at the latest recorded check, so that matrix is not yet claimed.

## Owned implementation

Draft PR: `teamleaderleo/zustand#1`

The implementation distinguishes explicit calls from automatic initialization:

```ts
const hydrate = (throwOnError = false) => {
  // existing hydration flow
  return chain.catch((error) => {
    if (currentVersion !== hydrationVersion) return
    postRehydrationCallback?.(undefined, error)
    if (throwOnError) {
      return Promise.reject(error)
    }
  })
}

persist.rehydrate = () => hydrate(true) as Promise<void>
```

Automatic initialization still calls `hydrate()` with the default `false` value.

This preserves:

- startup failure containment through `onRehydrateStorage`;
- success-only meaning for `hasHydrated()`;
- success-only meaning for `onFinishHydration()`;
- suppression of superseded attempts through `hydrationVersion`;
- recovery through a later successful retry.

## Why the rejected Promise is explicit

Zustand's synchronous `toThenable` adapter models a captured error with an object whose `.then()` does not call a rejection callback. Simply throwing again from the catch callback could produce a rejected custom thenable that does not settle correctly when consumed by `await`.

Returning `Promise.reject(error)` from the explicit failure path converts both synchronous and asynchronous failures into a real rejected Promise without changing successful synchronous hydration.

## Regression suite

The committed test `tests/persistRehydrateError.test.ts` covers:

- asynchronous storage failure rejects with the original error;
- synchronous JSON parsing failure rejects with `SyntaxError`;
- synchronous migration failure rejects with the original error;
- synchronous merge failure rejects with the original error;
- automatic hydration continues containing synchronous parsing failure;
- a rejected explicit attempt can be followed by a successful retry;
- a failed superseded attempt resolves quietly after the current attempt succeeds;
- state, hydration flags, start listeners, finish listeners, and callback arguments remain consistent.

The implementation is committed directly in `src/middleware/persist.ts`. Temporary patch and staged-test files have been removed, so both Zustand's ordinary CI and the focused matrix test the actual source change.

The focused matrix also runs the existing `persistAsync.test.tsx` and `persistSync.test.tsx` suites and lints the changed source and regression on Node 22, 24, and 26.

## Source-equivalent candidate execution

A Node `v22.16.0` execution independently exercised the patched control flow. All four failure stages rejected correctly, automatic failure remained contained, retry recovery succeeded, and a superseded failure remained suppressed.

This is a limited control-flow receipt, not a clean-checkout or package-install result.

## Compatibility assessment

This candidate changes explicit error settlement, so it remains draft. The correction is narrower than redefining `hasHydrated`, firing finish listeners after retained-state failure, or adding a new public status API.

The main review questions are:

- whether users rely on explicit `rehydrate()` swallowing errors;
- whether returning a rejected Promise from synchronous failure changes important microtask ordering;
- whether automatic hydration containment should be documented more clearly;
- whether the public type should eventually be tightened from `Promise<void> | void` when storage exists.

## Adjacent question retained separately

Explicitly supplied `undefined` values in persist options can overwrite defaults through object spreading. That behavior is tracked independently in Fieldwork lane #170 and owned fork PR #2.

## Current decision

Treat this as a confirmed source defect candidate with a directly committed owned implementation. Keep the fork PR draft until ordinary and focused CI are green and compatibility review is complete.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.