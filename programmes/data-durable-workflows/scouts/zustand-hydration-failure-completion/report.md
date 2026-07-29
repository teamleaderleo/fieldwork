# Zustand persist hydration failure completion

State: `implementing`

Fieldwork lane: #158

Programme: data-durable-workflows

Target package: `zustand@5.0.14`

Source pin: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Released-package workflow: `30497117408`

Owned implementation: `teamleaderleo/zustand#1`

Owned branch: `fieldwork/persist-rehydrate-error-settlement`

Owned head: `be961d4297fd9138a0e856009f6ec2ac1cbe455a`

Upstream contact authorized: `false`

## In simple words

Zustand persist exposes three public hydration signals: the value returned by `rehydrate()`, the `hasHydrated()` flag, and `onFinishHydration()` listeners.

The released source catches storage, parsing, migration, and merge failures and reports them through the optional completion callback returned by `onRehydrateStorage`. It then returns normally. As a result, an explicit `await persist.rehydrate()` fulfills while `hasHydrated()` remains false and finish listeners do not run.

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

This preserves the following behaviors:

- startup hydration failures remain contained and observable through `onRehydrateStorage`;
- `hasHydrated()` remains a success indicator;
- `onFinishHydration()` remains a success listener;
- superseded attempts remain suppressed by `hydrationVersion`;
- a later retry can succeed and complete normally.

## Why the rejected Promise is explicit

Zustand's synchronous `toThenable` adapter models a captured error with an object whose `.then()` does not call a rejection callback. Simply throwing again from the catch callback could therefore produce a rejected custom thenable that does not settle correctly when consumed by `await`.

Returning `Promise.reject(error)` from the explicit failure path converts both synchronous and asynchronous failures into a real rejected Promise without changing the successful synchronous hydration path.

## Owned regression suite

The fork adds `tests/persistRehydrateError.test.ts` covering:

- explicit asynchronous storage failure rejects with the original error;
- explicit synchronous JSON parsing failure rejects with `SyntaxError`;
- automatic hydration continues to contain synchronous parsing failure;
- a rejected explicit attempt can be followed by a successful retry;
- a failed superseded attempt resolves quietly after the current attempt succeeds;
- state, hydration flags, start listeners, finish listeners, and post-rehydration callback arguments remain consistent.

The exact source hunk is stored in `.fieldwork/persist-rehydrate-error-settlement.patch`. The connected editor only supports full-file replacement, so the clean-checkout workflows apply the reviewed hunk with `git apply --check` before running the tests.

## Candidate validation

The fork contains a Node 22, 24, and 26 workflow. Fieldwork also contains a separate exact-SHA workflow that checks out owned head `be961d4297fd9138a0e856009f6ec2ac1cbe455a`, applies the patch, installs with the repository lockfile, runs the focused Vitest file, and lints it.

No candidate execution result is claimed until those jobs appear and settle.

## Compatibility assessment

This candidate changes explicit error settlement, so it remains draft. The correction is narrower than redefining `hasHydrated` or firing finish listeners after retained-state failure. It also avoids adding a new public status API.

The most important review questions are:

- whether users rely on explicit `rehydrate()` swallowing errors;
- whether returning a rejected Promise from synchronous failure creates any unexpected microtask ordering;
- whether automatic hydration containment must be documented more clearly;
- whether the public type should be tightened from `Promise<void> | void` once storage exists.

## Adjacent question retained separately

Explicitly supplied `undefined` values in persist options can overwrite defaults through object spreading. That behavior is not used as evidence for this finding and should be characterized independently.

## Current decision

Treat this as a confirmed source defect candidate with an owned implementation experiment. Keep the fork PR draft until the exact clean-checkout matrix is green and compatibility review is complete.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.