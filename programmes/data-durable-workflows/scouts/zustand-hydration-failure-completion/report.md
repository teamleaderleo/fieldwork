# Zustand persist hydration failure completion

State: `implementing`

Fieldwork lane: #158

Programme: data-durable-workflows

Target package: `zustand@5.0.14`

Source pin: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Released-package workflow: `30497117408`

Owned implementation: `teamleaderleo/zustand#1`

Owned branch: `fieldwork/persist-rehydrate-error-settlement`

Owned head: `047425c2d909eefaf712046b4b4021062f6e8cff`

Fork candidate workflow: `30499684939`

Fieldwork candidate workflow: `30499703171`

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

## Owned candidate contract

Draft PR: `teamleaderleo/zustand#1`

The candidate distinguishes explicit calls from automatic initialization:

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

## Owned regression suite

The candidate-only source file `.fieldwork/persistRehydrateError.vitest.ts` covers:

- asynchronous storage failure rejects with the original error;
- synchronous JSON parsing failure rejects with `SyntaxError`;
- synchronous migration failure rejects with the original error;
- synchronous merge failure rejects with the original error;
- automatic hydration continues containing synchronous parsing failure;
- a rejected explicit attempt can be followed by a successful retry;
- a failed superseded attempt resolves quietly after the current attempt succeeds;
- state, hydration flags, start listeners, finish listeners, and callback arguments remain consistent.

The candidate regression is intentionally kept outside Vitest's default `tests` directory while the source change is stored as a patch. Dedicated workflows apply the source hunk, copy the candidate test into `tests`, and then run it. This prevents normal repository CI from testing an unapplied patch and failing by construction.

The dedicated matrix also runs the existing `persistAsync.test.tsx` and `persistSync.test.tsx` suites after applying the patch.

## Source application state

The exact source hunk is stored in `.fieldwork/persist-rehydrate-error-settlement.patch`. The connected editor supports complete-file replacement only, so the clean-checkout workflows apply the reviewed hunk with `git apply --check` rather than mechanically rewriting the entire source file.

## Candidate validation

Fork workflow `30499684939` and Fieldwork workflow `30499703171` both pin owned head `047425c2d909eefaf712046b4b4021062f6e8cff`, apply the patch, stage the candidate-only regression, install from the lockfile, run the new and existing persist suites on Node 22, 24, and 26, and lint the candidate test.

The jobs were queued at the latest recorded check. No candidate execution result is claimed yet.

## Compatibility assessment

This candidate changes explicit error settlement, so it remains draft. The correction is narrower than redefining `hasHydrated`, firing finish listeners after retained-state failure, or adding a new public status API.

The main review questions are:

- whether users rely on explicit `rehydrate()` swallowing errors;
- whether returning a rejected Promise from synchronous failure changes important microtask ordering;
- whether automatic hydration containment should be documented more clearly;
- whether the public type should eventually be tightened from `Promise<void> | void` when storage exists.

## Adjacent question retained separately

Explicitly supplied `undefined` values in persist options can overwrite defaults through object spreading. That behavior is not used as evidence for this finding and should be characterized independently.

## Current decision

Treat this as a confirmed source defect candidate with an owned implementation experiment. Keep the fork PR draft until the exact clean-checkout matrix is green and compatibility review is complete.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.