import assert from 'node:assert/strict'

function currentPostMessageHeaders(headers) {
  return JSON.parse(JSON.stringify({ options: { headers } })).options.headers
}

function normalizedPostMessageHeaders(headers) {
  const normalized = Object.fromEntries(new Headers(headers || {}).entries())
  return JSON.parse(JSON.stringify({ options: { headers: normalized } })).options.headers
}

const cases = [
  {
    name: 'record',
    input: { 'X-Record': 'record' },
    current: { 'X-Record': 'record' },
    normalized: { 'x-record': 'record' }
  },
  {
    name: 'Headers',
    input: new Headers([['X-Headers', 'headers']]),
    current: {},
    normalized: { 'x-headers': 'headers' }
  },
  {
    name: 'tuple-list',
    input: [['X-Tuple', 'tuple']],
    current: [['X-Tuple', 'tuple']],
    normalized: { 'x-tuple': 'tuple' }
  }
]

for (const test of cases) {
  const current = currentPostMessageHeaders(test.input)
  const normalized = normalizedPostMessageHeaders(test.input)
  assert.deepEqual(current, test.current, `${test.name}: unexpected current JSON shape`)
  assert.deepEqual(normalized, test.normalized, `${test.name}: normalization mismatch`)
  console.log(`${test.name}: current=${JSON.stringify(current)} normalized=${JSON.stringify(normalized)}`)
}

console.log('PASS current postMessage JSON preserves record headers but loses Headers entries and emits tuple-list as a sequence')
console.log('PASS standard Headers normalization produces a plain string map for all public HeadersInit forms')
