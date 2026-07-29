# Zustand persist hydration failure completion

State: `source-confirmed`

Fieldwork lane: #158

Programme: data-durable-workflows

Target package: `zustand@5.0.14`

Source pin: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

Released-package workflow: `30497117408`

Upstream contact authorized: `false`

## In simple words

Zustand's persist middleware offers three public completion signals: the promise returned by `rehydrate()`, the `hasHydrated()` flag, and `onFinishHydration()` listeners.

The current failure path catches an error and calls the post-`onRehydrateStorage` callback, but it does not reject the public promise, set `hasHydrated`, or call finish listeners. Different callers can therefore reach incompatible conclusions about the same terminal attempt.

## Source map

`hydrate()` sets `hasHydrated = false`, increments the hydration version, fires `onHydrate`, and enters a thenable chain around storage retrieval, migration, merge, and optional persistence.

The successful terminal path:

1. calls the post-rehydration callback;
2. refreshes the retained state reference;
3. sets `hasHydrated = true`;
4. calls every `onFinishHydration` listener.

The error path only calls:

```ts
postRehydrationCallback?.(undefined, e)
```

Because the catch callback returns normally, the `rehydrate()` thenable resolves.

## Historical precedent

Merged PR #646 introduced `onFinishHydration` after identifying that callers needed a way to know hydration had finished. Its stated purpose was completion observation, and its tests wait on the finish listener before asserting `hasHydrated()`.

Merged PR #3336 added hydration-version checks so superseded attempts do not apply state or fire finish listeners. A failed current attempt is different from a superseded attempt: it is terminal and no newer hydration owns completion.

No matching current issue or pull request was found for the combination of resolved promise, false flag, and absent finish event after failure.

## Probe contract

The released-package probe uses vanilla stores with `skipHydration: true` and covers:

- asynchronous storage rejection;
- synchronous malformed JSON through `createJSONStorage`;
- migration failure;
- merge failure;
- a failed attempt followed by a successful retry.

For each failure it records:

- promise settlement;
- `hasHydrated()`;
- current state;
- `onHydrate` calls;
- `onFinishHydration` calls;
- post-`onRehydrateStorage` arguments.

The probe was corrected after review so optional `version`, `migrate`, and `merge` fields are omitted rather than passed as explicit `undefined`. That prevents the probe itself from overwriting Zustand's defaults and keeps each failure isolated.

## Source-equivalent execution

A local Node 22.16.0 execution used the current vanilla store and persist runtime paths transcribed from the pinned source. It is not presented as a released-package install receipt, but it independently exercised the exact thenable and hydration control flow.

All four failure classes produced the same terminal state:

- `rehydrate()` fulfilled;
- `hasHydrated()` remained `false`;
- `onHydrate` fired once;
- `onFinishHydration` did not fire;
- the current state remained unchanged;
- the post-`onRehydrateStorage` callback received the concrete error.

The malformed-JSON case surfaced the native `JSON.parse` error. Storage, migration, and merge cases surfaced their supplied errors.

A failed read followed by a later successful retry remains supported by the prepared released-package probe: the first attempt retains the split state, while the second attempt should set stored state, set `hasHydrated()` to true, and fire one finish listener.

## Released-package matrix

Workflow `30497117408` pins `zustand@5.0.14` and runs the corrected probe on Node 22, 24, and 26. The jobs were queued at the latest recorded check; no released-package matrix result is claimed yet.

## Adjacent question retained separately

The first probe revision exposed another source behavior: spreading `baseOptions` means explicitly supplied `undefined` can overwrite defaults such as `version` and `merge`. That is not folded into this finding because it changes the failure being measured. It should be characterized separately before any claim or patch is retained.

## Contract options

### Reject explicit calls

Allow `persist.rehydrate()` to reject so callers using `await` receive the error. Automatic initialization would need a separate containment path to prevent unhandled rejection.

This keeps `hasHydrated` and finish listeners success-oriented, but it changes the promise contract and requires careful compatibility review.

### Complete the attempt on failure

Set `hasHydrated = true` and call finish listeners with the retained current state after reporting the error. This treats the flag and listener as attempt-completion signals rather than success signals.

This is narrow and avoids unhandled rejection, but callers could mistake retained initial state for successfully loaded state unless they also register `onRehydrateStorage`.

### Add explicit terminal status

Preserve current success-only semantics while exposing a separate status or error channel. This is the clearest contract but the broadest API change.

## Current decision

Do not select a repair from source reasoning alone. The completion signals are demonstrably split in the pinned runtime path, but the correct compatibility contract depends on whether `hasHydrated` and `onFinishHydration` mean successful hydration or terminal completion.

Promote the finding after the exact released-package matrix confirms the same behavior. An issue-first packet is more appropriate than an immediate code patch because each plausible repair changes public lifecycle semantics.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.