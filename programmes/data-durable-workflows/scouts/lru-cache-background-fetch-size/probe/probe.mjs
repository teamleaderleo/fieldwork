import assert from 'node:assert/strict'
import process from 'node:process'
import { LRUCache } from 'lru-cache'

const describeCalculatedSize = value => ({
  type: typeof value,
  string: String(value),
  finite: typeof value === 'number' && Number.isFinite(value),
  integer: typeof value === 'number' && Number.isInteger(value),
  nan: typeof value === 'number' && Number.isNaN(value),
})

const snapshot = (cache, fetchCalls) => ({
  fetchCalls,
  cacheSize: cache.size,
  calculatedSize: describeCalculatedSize(cache.calculatedSize),
  keys: [...cache.keys()],
  hasA: cache.has('a'),
  hasB: cache.has('b'),
})

const settle = promise => promise.then(
  value => ({ status: 'fulfilled', value }),
  error => ({ status: 'rejected', message: error?.message ?? String(error) }),
)

const runCase = async ({ label, value }) => {
  const pending = []
  let fetchCalls = 0
  let constructorError
  let cache

  try {
    cache = new LRUCache({
      maxSize: 10,
      sizeCalculation: () => 5,
      backgroundFetchSize: value,
      fetchMethod: key => {
        fetchCalls++
        return new Promise(resolve => {
          pending.push({ key, resolve })
        })
      },
    })
  } catch (error) {
    constructorError = error?.message ?? String(error)
  }

  if (!cache) {
    return { label, constructorError }
  }

  const first = settle(cache.fetch('a'))
  const afterFirstFetch = snapshot(cache, fetchCalls)

  const second = settle(cache.fetch('a'))
  const afterSecondFetch = snapshot(cache, fetchCalls)

  let setError
  try {
    cache.set('b', 'B')
  } catch (error) {
    setError = error?.message ?? String(error)
  }
  const afterSet = snapshot(cache, fetchCalls)

  pending.forEach(({ resolve }, index) => resolve(`A${index + 1}`))
  const outcomes = await Promise.all([first, second])
  await Promise.resolve()
  const afterSettlement = snapshot(cache, fetchCalls)

  cache.clear()

  return {
    label,
    constructorError,
    setError,
    afterFirstFetch,
    afterSecondFetch,
    afterSet,
    afterSettlement,
    outcomes,
  }
}

const cases = [
  { label: 'valid-one', value: 1 },
  { label: 'zero', value: 0 },
  { label: 'negative-one', value: -1 },
  { label: 'fractional', value: 1.5 },
  { label: 'nan', value: Number.NaN },
  { label: 'infinity', value: Number.POSITIVE_INFINITY },
  { label: 'numeric-string', value: '2' },
]

const results = []
for (const testCase of cases) {
  // Keep each case isolated so corrupted accounting cannot affect another case.
  // eslint-disable-next-line no-await-in-loop
  results.push(await runCase(testCase))
}

const byLabel = Object.fromEntries(results.map(result => [result.label, result]))

assert.equal(byLabel['valid-one'].constructorError, undefined)
assert.equal(byLabel['valid-one'].afterFirstFetch.calculatedSize.string, '1')
assert.equal(byLabel['valid-one'].afterSecondFetch.fetchCalls, 1)

assert.equal(byLabel['negative-one'].constructorError, undefined)
assert.equal(byLabel['negative-one'].afterFirstFetch.calculatedSize.string, '-1')

assert.equal(byLabel.fractional.constructorError, undefined)
assert.equal(byLabel.fractional.afterFirstFetch.calculatedSize.string, '1.5')
assert.equal(byLabel.fractional.afterFirstFetch.calculatedSize.integer, false)

assert.equal(byLabel.nan.constructorError, undefined)
assert.equal(byLabel.nan.afterFirstFetch.calculatedSize.nan, true)
assert.equal(byLabel.nan.afterSet.calculatedSize.nan, true)
assert.equal(byLabel.nan.afterSettlement.calculatedSize.nan, true)

assert.equal(byLabel.infinity.constructorError, undefined)
assert.equal(byLabel.infinity.afterFirstFetch.cacheSize, 0)
assert.equal(byLabel.infinity.afterSecondFetch.fetchCalls, 2)

assert.equal(byLabel['numeric-string'].constructorError, undefined)
assert.equal(byLabel['numeric-string'].afterFirstFetch.calculatedSize.type, 'string')
assert.equal(byLabel['numeric-string'].afterFirstFetch.calculatedSize.string, '02')

console.log(JSON.stringify({
  package: 'lru-cache',
  version: '11.5.2',
  node: process.version,
  results,
}, null, 2))
