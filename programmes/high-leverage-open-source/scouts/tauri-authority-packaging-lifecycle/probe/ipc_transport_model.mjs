import assert from 'node:assert/strict'

async function oldTransport(scenario) {
  let customProtocolFailed = false
  let rustDispatches = 0
  let postDispatches = 0

  async function send(message) {
    if (!customProtocolFailed) {
      try {
        if (scenario === 'csp-block') throw new Error('CSP')
        rustDispatches++
        if (scenario === 'reload-after-dispatch') throw new Error('navigation abort')
        if (scenario === 'late-break') throw new Error('transport broke after dispatch')
        return 'custom-ok'
      } catch (error) {
        customProtocolFailed = true
        return send(message)
      }
    }
    postDispatches++
    rustDispatches++
    return 'post-ok'
  }

  const result = await send({ cmd: 'side-effect' })
  return { result, rustDispatches, postDispatches }
}

async function negotiatedTransport(scenario) {
  let rustDispatches = 0
  let postDispatches = 0
  let probeRequests = 0
  let state = 'unknown'
  let probePromise

  async function probe() {
    if (state !== 'unknown') return state
    if (!probePromise) {
      probePromise = (async () => {
        probeRequests++
        // This models Tauri's existing side-effect-free OPTIONS branch.
        if (scenario === 'csp-block') {
          state = 'post-message'
        } else {
          state = 'custom-protocol'
        }
        return state
      })()
    }
    return probePromise
  }

  async function send(message) {
    const selected = await probe()
    if (selected === 'post-message') {
      postDispatches++
      rustDispatches++
      return 'post-ok'
    }

    // Once a side-effecting request may have reached Rust, do not retry it
    // over the other transport. Surface failure instead.
    rustDispatches++
    if (scenario === 'reload-after-dispatch') throw new Error('navigation abort')
    if (scenario === 'late-break') throw new Error('transport broke after dispatch')
    return 'custom-ok'
  }

  try {
    const result = await send({ cmd: 'side-effect' })
    return { result, rustDispatches, postDispatches, probeRequests }
  } catch (error) {
    return { result: 'rejected', rustDispatches, postDispatches, probeRequests }
  }
}

const oldNormal = await oldTransport('normal')
assert.equal(oldNormal.rustDispatches, 1)

const oldCsp = await oldTransport('csp-block')
assert.equal(oldCsp.rustDispatches, 1)
assert.equal(oldCsp.postDispatches, 1)

const oldReload = await oldTransport('reload-after-dispatch')
assert.equal(oldReload.rustDispatches, 2)
assert.equal(oldReload.postDispatches, 1)

const proposedNormal = await negotiatedTransport('normal')
assert.deepEqual(proposedNormal, {
  result: 'custom-ok',
  rustDispatches: 1,
  postDispatches: 0,
  probeRequests: 1
})

const proposedCsp = await negotiatedTransport('csp-block')
assert.deepEqual(proposedCsp, {
  result: 'post-ok',
  rustDispatches: 1,
  postDispatches: 1,
  probeRequests: 1
})

const proposedReload = await negotiatedTransport('reload-after-dispatch')
assert.deepEqual(proposedReload, {
  result: 'rejected',
  rustDispatches: 1,
  postDispatches: 0,
  probeRequests: 1
})

const proposedLateBreak = await negotiatedTransport('late-break')
assert.deepEqual(proposedLateBreak, {
  result: 'rejected',
  rustDispatches: 1,
  postDispatches: 0,
  probeRequests: 1
})

console.log('PASS normal: one custom-protocol dispatch')
console.log('PASS CSP block: OPTIONS probe selects postMessage before command dispatch')
console.log('PASS reload after dispatch: no cross-transport retry; Rust sees one command')
console.log('PASS late transport break: invoke rejects instead of risking duplicate side effect')
