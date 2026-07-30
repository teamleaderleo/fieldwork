import assert from 'node:assert/strict'

import { createJSONStorage } from 'jotai/vanilla/utils'

const equalJson = JSON.stringify({ nested: { count: 1 } })
const differentJson = JSON.stringify({ nested: { count: 2 } })

const data = new Map([
  ['alpha', equalJson],
  ['beta', equalJson],
  ['gamma', differentJson],
])

const stringStorage = {
  getItem: (key) => data.get(key) ?? null,
  setItem: (key, value) => data.set(key, value),
  removeItem: (key) => data.delete(key),
}

const adapter = createJSONStorage(() => stringStorage)
const alpha = adapter.getItem('alpha', { nested: { count: -1 } })
const alphaAgain = adapter.getItem('alpha', { nested: { count: -2 } })
const beta = adapter.getItem('beta', { nested: { count: -3 } })
const gamma = adapter.getItem('gamma', { nested: { count: -4 } })

const separateAdapter = createJSONStorage(() => stringStorage)
const betaFromSeparateAdapter = separateAdapter.getItem('beta', {
  nested: { count: -5 },
})

assert.equal(typeof alpha?.then, 'undefined', 'expected synchronous storage')
assert.equal(typeof beta?.then, 'undefined', 'expected synchronous storage')
assert.equal(typeof gamma?.then, 'undefined', 'expected synchronous storage')
assert.strictEqual(
  alpha,
  alphaAgain,
  'repeated reads of the same unchanged JSON should preserve adapter identity',
)
assert.notStrictEqual(
  beta,
  gamma,
  'different JSON text should not share a parsed object',
)
assert.notStrictEqual(
  beta,
  betaFromSeparateAdapter,
  'separate adapters should not share a parsed object cache',
)

const sameAdapterDifferentKeysShareIdentity = alpha === beta
alpha.nested.count = 99
const mutationCrossedKeyBoundary = beta.nested.count === 99

const result = {
  node: process.version,
  package: 'jotai@2.20.2',
  controls: {
    sameKeySameJsonPreservesIdentity: alpha === alphaAgain,
    differentJsonIsDistinct: beta !== gamma,
    separateAdaptersAreDistinct: beta !== betaFromSeparateAdapter,
  },
  disputedBoundary: {
    sameAdapterDifferentKeysSameJsonShareIdentity:
      sameAdapterDifferentKeysShareIdentity,
    mutationCrossedKeyBoundary,
    betaCountAfterAlphaMutation: beta.nested.count,
  },
}

console.log(JSON.stringify(result, null, 2))
