import assert from 'node:assert/strict'

function oldTransport(scenario) {
  let customProtocolFailed = false
  let rustDispatches = 0
  let postDispatches = 0

  async function send() {
    if (!customProtocolFailed) {
      try {
        if (scenario === 'csp-block') throw new Error('CSP')
        rustDispatches++
        if (scenario === 'reload-after-dispatch') throw new Error('navigation abort')
        if (scenario === 'late-break') throw new Error('transport broke after dispatch')
        return 'custom-ok'
      } catch (error) {
        customProtocolFailed = true
        return send()
      }
    }
    postDispatches++
    rustDispatches++
    return 'post-ok'
  }

  return { send, stats: () => ({ rustDispatches, postDispatches }) }
}

function negotiatedTransport(scenario) {
  let rustDispatches = 0
  let postDispatches = 0
  let probeRequests = 0
  let state = 'unknown'
  let probePromise
  let failureInjected = false

  async function probe() {
    if (state !== 'unknown') return state
    if (!probePromise) {
      probePromise = (async () => {
        probeRequests++
        // This models a side-effect-free HEAD request through the IPC custom
        // protocol. Tauri dispatches commands only for POST requests.
        if (scenario === 'csp-block') state = 'post-message'
        else state = 'custom-protocol'
        return state
      })()
    }
    return probePromise
  }

  async function send() {
    const selected = await probe()
    if (selected === 'post-message') {
      postDispatches++
      rustDispatches++
      return 'post-ok'
    }

    rustDispatches++
    if (!failureInjected && scenario === 'reload-after-dispatch') {
      failureInjected = true
      state = 'post-message'
      throw new Error('navigation abort')
    }
    if (!failureInjected && scenario === 'late-break') {
      failureInjected = true
      state = 'post-message'
      throw new Error('transport broke after dispatch')
    }
    return 'custom-ok'
  }

  return {
    send,
    stats: () => ({ rustDispatches, postDispatches, probeRequests, state })
  }
}

const oldNormal = oldTransport('normal')
assert.equal(await oldNormal.send(), 'custom-ok')
assert.deepEqual(oldNormal.stats(), { rustDispatches: 1, postDispatches: 0 })

const oldCsp = oldTransport('csp-block')
assert.equal(await oldCsp.send(), 'post-ok')
assert.deepEqual(oldCsp.stats(), { rustDispatches: 1, postDispatches: 1 })

const oldReload = oldTransport('reload-after-dispatch')
assert.equal(await oldReload.send(), 'post-ok')
assert.deepEqual(oldReload.stats(), { rustDispatches: 2, postDispatches: 1 })

const proposedNormal = negotiatedTransport('normal')
assert.equal(await proposedNormal.send(), 'custom-ok')
assert.deepEqual(proposedNormal.stats(), {
  rustDispatches: 1,
  postDispatches: 0,
  probeRequests: 1,
  state: 'custom-protocol'
})

const proposedCsp = negotiatedTransport('csp-block')
assert.equal(await proposedCsp.send(), 'post-ok')
assert.deepEqual(proposedCsp.stats(), {
  rustDispatches: 1,
  postDispatches: 1,
  probeRequests: 1,
  state: 'post-message'
})

const proposedReload = negotiatedTransport('reload-after-dispatch')
await assert.rejects(proposedReload.send(), /navigation abort/)
assert.deepEqual(proposedReload.stats(), {
  rustDispatches: 1,
  postDispatches: 0,
  probeRequests: 1,
  state: 'post-message'
})

const proposedLateBreak = negotiatedTransport('late-break')
await assert.rejects(proposedLateBreak.send(), /transport broke after dispatch/)
assert.equal(await proposedLateBreak.send(), 'post-ok')
assert.deepEqual(proposedLateBreak.stats(), {
  rustDispatches: 2,
  postDispatches: 1,
  probeRequests: 1,
  state: 'post-message'
})

console.log('PASS normal: one custom-protocol dispatch')
console.log('PASS CSP block: HEAD probe selects postMessage before command dispatch')
console.log('PASS reload after dispatch: ambiguous invoke rejects after one Rust dispatch')
console.log('PASS later transport break: failed invoke is not replayed; next invoke recovers via postMessage')
