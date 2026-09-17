# Held upstream issue draft

Status: held; upstream contact is not authorized.

## Title

Persist hydration failures leave public completion signals inconsistent

## Summary

When the current `persist.rehydrate()` attempt fails during storage access, JSON parsing, migration, or merge, the public completion signals do not settle consistently:

- the returned promise/thenable fulfills;
- `persist.hasHydrated()` remains `false`;
- `persist.onFinishHydration()` listeners do not run;
- the current state is retained;
- the error is only observable through the optional callback returned by `onRehydrateStorage`.

This can leave one caller believing an explicit hydration attempt completed successfully while another caller waits indefinitely for the flag or finish listener.

## Reproduction

```ts
import { createStore } from 'zustand/vanilla'
import { createJSONStorage, persist } from 'zustand/middleware'

const events: string[] = []

const store = createStore(
  persist(
    () => ({ count: 0 }),
    {
      name: 'example',
      skipHydration: true,
      storage: createJSONStorage(() => ({
        getItem: async () => {
          throw new Error('storage failed')
        },
        setItem: async () => {},
        removeItem: async () => {},
      })),
      onRehydrateStorage: () => (_state, error) => {
        events.push(`callback:${String(error)}`)
      },
    },
  ),
)

store.persist.onHydrate(() => events.push('start'))
store.persist.onFinishHydration(() => events.push('finish'))

await store.persist.rehydrate()

console.log(store.persist.hasHydrated()) // false
console.log(events) // ['start', 'callback:Error: storage failed']
```

## Observed scope

The same terminal state occurs for:

- asynchronous `storage.getItem()` rejection;
- malformed JSON in `createJSONStorage()`;
- a throwing or rejected migration;
- a throwing merge function.

A later explicit retry can still succeed, set `hasHydrated()` to `true`, and fire the finish listener.

## Source mechanism

The success path sets `hasHydrated = true` and invokes `finishHydrationListeners`.

The catch path only calls the post-rehydration callback and returns normally:

```ts
.catch((error) => {
  if (currentVersion !== hydrationVersion) return
  postRehydrationCallback?.(undefined, error)
})
```

Returning normally explains why the explicit `rehydrate()` await fulfills while the other completion signals remain unset.

## Historical context

`onFinishHydration` was introduced so callers could know hydration had finished. The newer hydration-version logic correctly suppresses state application and finish callbacks for attempts superseded by a newer call. A failed current attempt is terminal and has no newer completion owner.

## Contract question

Which public contract is intended after a current hydration attempt fails?

Possible directions have different compatibility costs:

1. reject explicit `rehydrate()` calls, while containing automatic initialization failures separately;
2. mark the failed attempt complete and invoke finish listeners with retained state;
3. preserve success-only semantics but expose a separate terminal status/error signal.

The immediate request is to define and test one coherent contract so an explicit promise, `hasHydrated()`, and `onFinishHydration()` cannot silently disagree about a terminal attempt.

## Environment

- Zustand: `5.0.14`
- Source pin: `beca84e600e4e250f6b244d22878e72948f331c7`
- Vanilla store with `skipHydration: true`
