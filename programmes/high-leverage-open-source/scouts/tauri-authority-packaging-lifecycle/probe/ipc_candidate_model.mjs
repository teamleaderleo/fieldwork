import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
import { fileURLToPath } from 'node:url'

const candidatePath = fileURLToPath(
  new URL('./ipc-protocol.candidate.js', import.meta.url)
)
const candidateSource = fs.readFileSync(candidatePath, 'utf8')
const TO_IPC = '__TAURI_TO_IPC_KEY__'
const CHANNEL_FETCH = 'plugin:__TAURI_CHANNEL__|fetch'

function processIpcMessageFactory(stats) {
  return function processIpcMessage(message) {
    stats.serializationCalls += 1
    if (
      message instanceof ArrayBuffer
      || ArrayBuffer.isView(message)
      || Array.isArray(message)
    ) {
      return {
        contentType: 'application/octet-stream',
        data: message
      }
    }

    return {
      contentType: 'application/json',
      data: JSON.stringify(message, (_key, value) => {
        if (value instanceof Map) return Object.fromEntries(value.entries())
        if (value instanceof Uint8Array) return Array.from(value)
        if (value instanceof ArrayBuffer) return Array.from(new Uint8Array(value))
        if (
          typeof value === 'object'
          && value !== null
          && TO_IPC in value
        ) {
          return value[TO_IPC]()
        }
        return value
      })
    }
  }
}

function response(body = { ok: true }) {
  return {
    headers: {
      get(name) {
        const key = name.toLowerCase()
        if (key === 'tauri-response') return 'ok'
        if (key === 'content-type') return 'application/json'
        return null
      }
    },
    json: async () => body,
    text: async () => JSON.stringify(body),
    arrayBuffer: async () => new ArrayBuffer(0)
  }
}

function deferred() {
  let resolve
  let reject
  const promise = new Promise((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

function renderCandidate(osName) {
  return candidateSource
    .replace('__TEMPLATE_invoke_key__', JSON.stringify('test-invoke-key'))
    .replace('__RAW_process_ipc_message_fn__', 'globalThis.__processIpcMessage')
    .replace('__TEMPLATE_os_name__', JSON.stringify(osName))
    .replace('__TEMPLATE_fetch_channel_data_command__', JSON.stringify(CHANNEL_FETCH))
}

function harness({ osName = 'windows', head = 'resolve', posts = [] } = {}) {
  const stats = {
    headRequests: 0,
    customPosts: 0,
    customPostUrls: [],
    postMessages: [],
    callbacks: [],
    serializationCalls: 0
  }
  const headDeferred = head === 'deferred' ? deferred() : null
  let postIndex = 0

  const window = {
    __TAURI_INTERNALS__: {
      convertFileSrc(cmd, protocol) {
        return `${protocol}://localhost/${encodeURIComponent(cmd)}`
      },
      runCallback(id, data) {
        stats.callbacks.push({ id, data })
      }
    },
    ipc: {
      postMessage(data) {
        stats.postMessages.push(data)
      }
    }
  }

  function fetch(_url, init) {
    if (init.method === 'HEAD') {
      stats.headRequests += 1
      if (head === 'reject') return Promise.reject(new Error('probe blocked'))
      if (head === 'deferred') return headDeferred.promise
      return Promise.resolve(response())
    }

    assert.equal(init.method, 'POST')
    stats.customPosts += 1
    stats.customPostUrls.push(_url)
    const outcome = posts[postIndex++] || 'resolve'
    if (outcome === 'reject-after-dispatch') {
      return Promise.reject(new Error('transport failed after dispatch'))
    }
    return Promise.resolve(response({ transport: 'custom' }))
  }

  const context = {
    window,
    fetch,
    Headers,
    ArrayBuffer,
    Uint8Array,
    Map,
    Object,
    Promise,
    console,
    __processIpcMessage: processIpcMessageFactory(stats)
  }
  context.globalThis = context
  vm.runInNewContext(renderCandidate(osName), context)

  return {
    send(message) {
      window.__TAURI_INTERNALS__.postMessage(message)
    },
    stats,
    resolveHead() {
      assert.ok(headDeferred)
      headDeferred.resolve(response())
    }
  }
}

async function settle() {
  await new Promise((resolve) => setTimeout(resolve, 0))
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function message({
  cmd = 'do-side-effect',
  callback = 1,
  error = 2,
  payload = {},
  headers = {}
} = {}) {
  return {
    cmd,
    callback,
    error,
    payload,
    options: { headers }
  }
}

// Probe must not serialize a custom payload before a transport is selected.
{
  const h = harness({ head: 'deferred' })
  let hookCalls = 0
  const payload = {
    value: {
      [TO_IPC]() {
        hookCalls += 1
        return 'serialized-value'
      }
    }
  }
  h.send(message({ payload }))
  assert.equal(h.stats.headRequests, 1)
  assert.equal(h.stats.serializationCalls, 0)
  assert.equal(hookCalls, 0)
  h.resolveHead()
  await settle()
  assert.equal(h.stats.customPosts, 1)
  assert.equal(hookCalls, 1)
}

// A normal desktop invoke negotiates once and dispatches exactly once.
{
  const h = harness()
  h.send(message({ headers: { 'X-Test': 'one' } }))
  await settle()
  assert.equal(h.stats.headRequests, 1)
  assert.equal(h.stats.customPosts, 1)
  assert.equal(h.stats.postMessages.length, 0)
  assert.equal(h.stats.callbacks.at(-1).id, 1)
}

// Concurrent first invokes share one capability probe and each dispatch once.
{
  const h = harness({ head: 'deferred' })
  h.send(message({ cmd: 'first' }))
  h.send(message({ cmd: 'second', callback: 3, error: 4 }))
  assert.equal(h.stats.headRequests, 1)
  assert.equal(h.stats.customPosts, 0)
  h.resolveHead()
  await settle()
  assert.equal(h.stats.customPosts, 2)
  assert.equal(h.stats.postMessages.length, 0)
}

// A blocked probe chooses postMessage before command dispatch and normalizes all
// public HeadersInit forms to the map Rust expects.
for (const [input, expected] of [
  [{ 'X-Record': 'record' }, { 'x-record': 'record' }],
  [new Headers([['X-Headers', 'headers']]), { 'x-headers': 'headers' }],
  [[['X-Tuple', 'tuple']], { 'x-tuple': 'tuple' }]
]) {
  const h = harness({ head: 'reject' })
  h.send(message({ headers: input }))
  await settle()
  assert.equal(h.stats.headRequests, 1)
  assert.equal(h.stats.customPosts, 0)
  assert.equal(h.stats.postMessages.length, 1)
  const encoded = JSON.parse(h.stats.postMessages[0])
  assert.deepEqual(encoded.options.headers, expected)
  assert.equal(encoded.options.customProtocolIpcBlocked, true)
}

// A POST that fails after dispatch is never replayed. Only future invokes switch.
{
  const h = harness({ posts: ['reject-after-dispatch'] })
  h.send(message({ cmd: 'ambiguous' }))
  await settle()
  assert.equal(h.stats.customPosts, 1)
  assert.equal(h.stats.postMessages.length, 0)
  assert.equal(h.stats.callbacks.at(-1).id, 2)

  h.send(message({ cmd: 'future', callback: 5, error: 6 }))
  await settle()
  assert.equal(h.stats.customPosts, 1)
  assert.equal(h.stats.postMessages.length, 1)
  const future = JSON.parse(h.stats.postMessages[0])
  assert.equal(future.cmd, 'future')
  assert.equal(future.options.customProtocolIpcBlocked, true)
}

// Android regular commands remain postMessage-first. Its special channel-data
// fetch is negotiated before the destructive Rust fetch command can run.
{
  const h = harness({ osName: 'android', head: 'deferred', posts: ['reject-after-dispatch'] })
  h.send(message({ cmd: 'regular-android' }))
  assert.equal(h.stats.postMessages.length, 1)
  assert.equal(JSON.parse(h.stats.postMessages[0]).options.customProtocolIpcBlocked, false)

  h.send(message({ cmd: CHANNEL_FETCH, callback: 10, error: 11, payload: null }))
  assert.equal(h.stats.headRequests, 1)
  assert.equal(h.stats.customPosts, 0)
  h.resolveHead()
  await settle()
  assert.equal(h.stats.customPosts, 1)
  assert.equal(h.stats.postMessages.length, 1, 'ambiguous channel POST must not be replayed')
  assert.equal(h.stats.callbacks.at(-1).id, 11)

  h.send(message({ cmd: 'after-channel-failure', callback: 12, error: 13 }))
  await settle()
  assert.equal(h.stats.postMessages.length, 2)
  const next = JSON.parse(h.stats.postMessages[1])
  assert.equal(next.options.customProtocolIpcBlocked, true)
}

// If Android cannot use the channel custom protocol at all, fallback happens
// before the destructive fetch command is dispatched.
{
  const h = harness({ osName: 'android', head: 'reject' })
  h.send(message({ cmd: CHANNEL_FETCH, callback: 20, error: 21, payload: null }))
  await settle()
  assert.equal(h.stats.headRequests, 1)
  assert.equal(h.stats.customPosts, 0)
  assert.equal(h.stats.postMessages.length, 1)
  assert.equal(JSON.parse(h.stats.postMessages[0]).options.customProtocolIpcBlocked, true)
}

console.log('PASS candidate probe does not serialize payload before transport selection')
console.log('PASS concurrent first invokes share one HEAD probe')
console.log('PASS blocked probe preserves record, Headers, and tuple-list headers over postMessage')
console.log('PASS ambiguous custom POST is not replayed; later invoke recovers')
console.log('PASS Android channel fetch negotiates before destructive dispatch and never replays an ambiguous POST')
