import assert from 'node:assert/strict'
import process from 'node:process'
import { createStore } from 'zustand/vanilla'
import { createJSONStorage, persist } from 'zustand/middleware'

const settle = async thenable => {
  try {
    await thenable
    return { status: 'fulfilled' }
  } catch (error) {
    return {
      status: 'rejected',
      message: error?.message ?? String(error),
    }
  }
}

const runFailureCase = async ({ name, storage, version, migrate, merge }) => {
  const events = []
  const store = createStore(
    persist(
      () => ({ count: 0 }),
      {
        name: `fieldwork-${name}`,
        storage,
        version,
        migrate,
        merge,
        skipHydration: true,
        onRehydrateStorage: state => {
          events.push({ event: 'rehydrate-start-callback', count: state.count })
          return (nextState, error) => {
            events.push({
              event: 'rehydrate-end-callback',
              count: nextState?.count,
              error: error?.message ?? (error === undefined ? undefined : String(error)),
            })
          }
        },
      },
    ),
  )

  store.persist.onHydrate(state => {
    events.push({ event: 'onHydrate', count: state.count })
  })
  store.persist.onFinishHydration(state => {
    events.push({ event: 'onFinishHydration', count: state.count })
  })

  const settlement = await settle(store.persist.rehydrate())
  const result = {
    name,
    settlement,
    hasHydrated: store.persist.hasHydrated(),
    state: store.getState(),
    events,
  }

  assert.equal(result.settlement.status, 'fulfilled', `${name}: rehydrate currently resolves`)
  assert.equal(result.hasHydrated, false, `${name}: hasHydrated remains false`)
  assert.equal(
    result.events.filter(event => event.event === 'onHydrate').length,
    1,
    `${name}: hydration start fires once`,
  )
  assert.equal(
    result.events.filter(event => event.event === 'onFinishHydration').length,
    0,
    `${name}: finish listener does not fire`,
  )
  assert.equal(
    result.events.filter(event => event.event === 'rehydrate-end-callback').length,
    1,
    `${name}: onRehydrateStorage receives the failure`,
  )
  assert.equal(result.state.count, 0, `${name}: current state is retained`)

  return result
}

const storageRejection = await runFailureCase({
  name: 'async-storage-rejection',
  storage: createJSONStorage(() => ({
    getItem: async () => {
      throw new Error('storage failure')
    },
    setItem: async () => {},
    removeItem: async () => {},
  })),
})

const malformedJSON = await runFailureCase({
  name: 'malformed-json',
  storage: createJSONStorage(() => ({
    getItem: () => '{',
    setItem: () => {},
    removeItem: () => {},
  })),
})

const migrationFailure = await runFailureCase({
  name: 'migration-failure',
  version: 2,
  migrate: () => {
    throw new Error('migration failure')
  },
  storage: createJSONStorage(() => ({
    getItem: () => JSON.stringify({ state: { count: 1 }, version: 1 }),
    setItem: () => {},
    removeItem: () => {},
  })),
})

const mergeFailure = await runFailureCase({
  name: 'merge-failure',
  merge: () => {
    throw new Error('merge failure')
  },
  storage: createJSONStorage(() => ({
    getItem: () => JSON.stringify({ state: { count: 1 }, version: 0 }),
    setItem: () => {},
    removeItem: () => {},
  })),
})

let failFirstRead = true
const retryEvents = []
const retryStore = createStore(
  persist(
    () => ({ count: 0 }),
    {
      name: 'fieldwork-retry',
      skipHydration: true,
      storage: createJSONStorage(() => ({
        getItem: async () => {
          if (failFirstRead) {
            throw new Error('first read failed')
          }
          return JSON.stringify({ state: { count: 42 }, version: 0 })
        },
        setItem: async () => {},
        removeItem: async () => {},
      })),
      onRehydrateStorage: () => (state, error) => {
        retryEvents.push({
          event: 'rehydrate-end-callback',
          count: state?.count,
          error: error?.message,
        })
      },
    },
  ),
)
retryStore.persist.onFinishHydration(state => {
  retryEvents.push({ event: 'onFinishHydration', count: state.count })
})

const firstRetrySettlement = await settle(retryStore.persist.rehydrate())
const afterFailedAttempt = {
  settlement: firstRetrySettlement,
  hasHydrated: retryStore.persist.hasHydrated(),
  state: retryStore.getState(),
  events: [...retryEvents],
}

failFirstRead = false
const secondRetrySettlement = await settle(retryStore.persist.rehydrate())
const afterSuccessfulRetry = {
  settlement: secondRetrySettlement,
  hasHydrated: retryStore.persist.hasHydrated(),
  state: retryStore.getState(),
  events: [...retryEvents],
}

assert.equal(afterFailedAttempt.settlement.status, 'fulfilled')
assert.equal(afterFailedAttempt.hasHydrated, false)
assert.equal(afterSuccessfulRetry.settlement.status, 'fulfilled')
assert.equal(afterSuccessfulRetry.hasHydrated, true)
assert.equal(afterSuccessfulRetry.state.count, 42)
assert.equal(
  afterSuccessfulRetry.events.filter(event => event.event === 'onFinishHydration').length,
  1,
)

console.log(JSON.stringify({
  package: 'zustand',
  version: '5.0.14',
  node: process.version,
  failures: [storageRejection, malformedJSON, migrationFailure, mergeFailure],
  retry: {
    afterFailedAttempt,
    afterSuccessfulRetry,
  },
}, null, 2))
