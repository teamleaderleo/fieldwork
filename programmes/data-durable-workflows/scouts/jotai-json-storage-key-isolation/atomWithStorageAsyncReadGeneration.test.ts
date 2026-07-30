import { describe, expect, it } from 'vitest'
import { createJSONStorage } from 'jotai/vanilla/utils'

type StoredValue = {
  nested: {
    count: number
  }
}

type Deferred<T> = {
  promise: Promise<T>
  resolve: (value: T) => void
  reject: (reason?: unknown) => void
}

const deferred = <T>(): Deferred<T> => {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

const encoded = (count: number) => JSON.stringify({ nested: { count } })

const createDeferredStorage = () => {
  const reads: Deferred<string | null>[] = []
  const storage = createJSONStorage<StoredValue>(() => ({
    getItem: () => {
      const read = deferred<string | null>()
      reads.push(read)
      return read.promise
    },
    setItem: async () => {},
    removeItem: async () => {},
  }))
  return { reads, storage }
}

describe('createJSONStorage async read generation characterization', () => {
  it('lets an older same-key completion replace the newer cached identity', async () => {
    const { reads, storage } = createDeferredStorage()

    const olderRead = storage.getItem('alpha', { nested: { count: -1 } })
    const newerRead = storage.getItem('alpha', { nested: { count: -2 } })

    reads[1]!.resolve(encoded(2))
    const newerValue = await newerRead
    reads[0]!.resolve(encoded(1))
    const olderValue = await olderRead

    const currentRead = storage.getItem('alpha', { nested: { count: -3 } })
    reads[2]!.resolve(encoded(2))
    const currentValue = await currentRead

    expect(olderValue).toEqual({ nested: { count: 1 } })
    expect(currentValue).toEqual({ nested: { count: 2 } })
    expect(currentValue).not.toBe(newerValue)
  })

  it('lets a pre-removal read repopulate identity after removal settles', async () => {
    const { reads, storage } = createDeferredStorage()

    const preRemovalRead = storage.getItem('alpha', {
      nested: { count: -1 },
    })
    await storage.removeItem('alpha')

    reads[0]!.resolve(encoded(1))
    const staleValue = await preRemovalRead

    const restoredRead = storage.getItem('alpha', {
      nested: { count: -2 },
    })
    reads[1]!.resolve(encoded(1))
    const restoredValue = await restoredRead

    expect(restoredValue).toBe(staleValue)
  })

  it('lets an older valid completion restore cache authority after a newer missing read', async () => {
    const { reads, storage } = createDeferredStorage()

    const olderRead = storage.getItem('alpha', { nested: { count: -1 } })
    const newerRead = storage.getItem('alpha', { nested: { count: -2 } })

    reads[1]!.resolve(null)
    const newerValue = await newerRead
    reads[0]!.resolve(encoded(1))
    const olderValue = await olderRead

    const restoredRead = storage.getItem('alpha', {
      nested: { count: -3 },
    })
    reads[2]!.resolve(encoded(1))
    const restoredValue = await restoredRead

    expect(newerValue).toEqual({ nested: { count: -2 } })
    expect(restoredValue).toBe(olderValue)
  })

  it('lets an older valid completion restore cache authority after a newer malformed read', async () => {
    const { reads, storage } = createDeferredStorage()

    const olderRead = storage.getItem('alpha', { nested: { count: -1 } })
    const newerRead = storage.getItem('alpha', { nested: { count: -2 } })

    reads[1]!.resolve('{malformed')
    const newerValue = await newerRead
    reads[0]!.resolve(encoded(1))
    const olderValue = await olderRead

    const restoredRead = storage.getItem('alpha', {
      nested: { count: -3 },
    })
    reads[2]!.resolve(encoded(1))
    const restoredValue = await restoredRead

    expect(newerValue).toEqual({ nested: { count: -2 } })
    expect(restoredValue).toBe(olderValue)
  })

  it('keeps an unrelated key stable through same-key completion reordering', async () => {
    const { reads, storage } = createDeferredStorage()

    const firstBetaRead = storage.getItem('beta', { nested: { count: -1 } })
    reads[0]!.resolve(encoded(9))
    const firstBeta = await firstBetaRead

    const olderAlphaRead = storage.getItem('alpha', {
      nested: { count: -2 },
    })
    const newerAlphaRead = storage.getItem('alpha', {
      nested: { count: -3 },
    })
    reads[2]!.resolve(encoded(2))
    await newerAlphaRead
    reads[1]!.resolve(encoded(1))
    await olderAlphaRead

    const secondBetaRead = storage.getItem('beta', {
      nested: { count: -4 },
    })
    reads[3]!.resolve(encoded(9))
    const secondBeta = await secondBetaRead

    expect(secondBeta).toBe(firstBeta)
  })
})
