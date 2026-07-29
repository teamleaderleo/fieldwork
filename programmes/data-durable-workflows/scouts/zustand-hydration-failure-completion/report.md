# Zustand persist hydration failure completion

State: `probe-prepared`

Fieldwork lane: #158

Programme: data-durable-workflows

Target package: `zustand@5.0.14`

Source pin: `pmndrs/zustand@beca84e600e4e250f6b244d22878e72948f331c7`

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

Current PR #3336 adds hydration-version checks so superseded attempts do not apply state or fire finish listeners. A failed current attempt is different from a superseded attempt: it is terminal and no newer hydration owns completion.

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

## Contract options to compare after execution

### Reject explicit calls

Allow `persist.rehydrate()` to reject so callers using `await` receive the error. Automatic initialization would need a separate containment path to prevent unhandled rejection.

### Complete the attempt on failure

Set `hasHydrated = true` and call finish listeners with the retained current state after reporting the error. This treats the flag and listener as attempt-completion signals rather than success signals.

### Add explicit terminal status

Preserve current success-only semantics while exposing a separate status or error channel. This is clearest but broadest and is unlikely to be a narrow maintenance fix.

## Decision boundary

Do not select a repair until the released package executes. The minimum acceptable contract is that public completion signals must not contradict one another without documentation and an observable terminal error path.

## Contact boundary

No upstream issue, pull request, comment, review, reaction, or message has been created.