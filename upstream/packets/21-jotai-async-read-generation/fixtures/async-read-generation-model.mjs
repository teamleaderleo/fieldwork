import assert from 'node:assert/strict'

const deferred = () => {
  let resolve
  let reject
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

const createJSONStorageModel = (backend) => {
  const cachedValues = new Map()
  const readGenerations = new Map()
  const advance = (key) => {
    const generation = (readGenerations.get(key) ?? 0) + 1
    readGenerations.set(key, generation)
    return generation
  }
  return {
    getItem(key, initialValue) {
      const generation = advance(key)
      const parse = (raw) => {
        const str = raw || ''
        const cached = cachedValues.get(key)
        if (cached?.str === str) return cached.value
        try {
          const value = JSON.parse(str)
          if (readGenerations.get(key) === generation) {
            cachedValues.set(key, { str, value })
          }
          return value
        } catch {
          if (readGenerations.get(key) === generation) {
            cachedValues.delete(key)
          }
          return initialValue
        }
      }
      const result = backend.getItem(key)
      return result?.then ? result.then(parse) : parse(result)
    },
    async removeItem(key) {
      try {
        return await backend.removeItem(key)
      } finally {
        advance(key)
        cachedValues.delete(key)
      }
    },
  }
}

const encoded = (count) => JSON.stringify({ nested: { count } })
const makeDeferredBackend = () => {
  const reads = []
  return {
    reads,
    getItem() {
      const read = deferred()
      reads.push(read)
      return read.promise
    },
    async removeItem() {},
  }
}

let passed = 0
const test = async (name, run) => {
  await run()
  passed += 1
  console.log(`ok ${passed} - ${name}`)
}

await test('newer same-key completion remains authoritative', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const older = storage.getItem('alpha', { count: -1 })
  const newer = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve(encoded(2))
  const newerValue = await newer
  backend.reads[0].resolve(encoded(1))
  await older
  const current = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(2))
  assert.equal(await current, newerValue)
})

await test('pre-removal completion cannot republish identity', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const stale = storage.getItem('alpha', { count: -1 })
  await storage.removeItem('alpha')
  backend.reads[0].resolve(encoded(1))
  const staleValue = await stale
  const restored = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve(encoded(1))
  assert.notEqual(await restored, staleValue)
})

await test('older valid result cannot restore after newer missing result', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const older = storage.getItem('alpha', { count: -1 })
  const newer = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve(null)
  await newer
  backend.reads[0].resolve(encoded(1))
  const oldValue = await older
  const restored = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(1))
  assert.notEqual(await restored, oldValue)
})

await test('older valid result cannot restore after newer malformed result', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const older = storage.getItem('alpha', { count: -1 })
  const newer = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve('{bad')
  await newer
  backend.reads[0].resolve(encoded(1))
  const oldValue = await older
  const restored = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(1))
  assert.notEqual(await restored, oldValue)
})

await test('stale malformed result cannot delete newer valid identity', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const older = storage.getItem('alpha', { count: -1 })
  const newer = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve(encoded(2))
  const newerValue = await newer
  backend.reads[0].resolve('{bad')
  await older
  const current = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(2))
  assert.equal(await current, newerValue)
})

await test('unrelated key identity remains stable', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const beta = storage.getItem('beta', { count: -1 })
  backend.reads[0].resolve(encoded(9))
  const betaValue = await beta
  const alphaOlder = storage.getItem('alpha', { count: -2 })
  const alphaNewer = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(2))
  await alphaNewer
  backend.reads[1].resolve(encoded(1))
  await alphaOlder
  const betaAgain = storage.getItem('beta', { count: -4 })
  backend.reads[3].resolve(encoded(9))
  assert.equal(await betaAgain, betaValue)
})

await test('cached A survives newer rejected read while older B stays stale', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const seed = storage.getItem('alpha', { count: -1 })
  backend.reads[0].resolve(encoded(1))
  const seededValue = await seed
  const older = storage.getItem('alpha', { count: -2 })
  const newer = storage.getItem('alpha', { count: -3 })
  backend.reads[2].reject(new Error('read failed'))
  await assert.rejects(newer)
  backend.reads[1].resolve(encoded(2))
  await older
  const current = storage.getItem('alpha', { count: -4 })
  backend.reads[3].resolve(encoded(1))
  assert.equal(await current, seededValue)
})

await test('rejected newer read prevents older B from establishing empty cache', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const older = storage.getItem('alpha', { count: -1 })
  const newer = storage.getItem('alpha', { count: -2 })
  backend.reads[1].reject(new Error('read failed'))
  await assert.rejects(newer)
  backend.reads[0].resolve(encoded(2))
  const oldValue = await older
  const later = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(2))
  assert.notEqual(await later, oldValue)
})

await test('later successful read establishes identity after rejection', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const rejected = storage.getItem('alpha', { count: -1 })
  backend.reads[0].reject(new Error('read failed'))
  await assert.rejects(rejected)
  const good = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve(encoded(3))
  const value = await good
  const repeat = storage.getItem('alpha', { count: -3 })
  backend.reads[2].resolve(encoded(3))
  assert.equal(await repeat, value)
})

await test('rejection remains caller-visible and unrelated key stays stable', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const beta = storage.getItem('beta', { count: -1 })
  backend.reads[0].resolve(encoded(9))
  const betaValue = await beta
  const rejected = storage.getItem('alpha', { count: -2 })
  backend.reads[1].reject(new Error('read failed'))
  await assert.rejects(rejected, /read failed/)
  const betaAgain = storage.getItem('beta', { count: -3 })
  backend.reads[2].resolve(encoded(9))
  assert.equal(await betaAgain, betaValue)
})

await test('same-string stale caller can reuse newer cached identity', async () => {
  const backend = makeDeferredBackend()
  const storage = createJSONStorageModel(backend)
  const older = storage.getItem('alpha', { count: -1 })
  const newer = storage.getItem('alpha', { count: -2 })
  backend.reads[1].resolve(encoded(4))
  const newerValue = await newer
  backend.reads[0].resolve(encoded(4))
  assert.equal(await older, newerValue)
})

console.log(JSON.stringify({ passed, node: process.version }))
