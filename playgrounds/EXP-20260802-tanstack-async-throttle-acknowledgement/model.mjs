const deferred = () => {
  let resolve
  const promise = new Promise((resolvePromise) => {
    resolve = resolvePromise
  })
  return { promise, resolve }
}

const currentThrottle = (func, interval = 0) => {
  let nextExecutionTime = 0
  let lastArgs = null
  let isExecuting = false
  let isScheduled = false
  return async (...args) => {
    lastArgs = args
    if (isScheduled) return
    isScheduled = true
    while (isExecuting) await new Promise((done) => setTimeout(done, interval))
    while (Date.now() < nextExecutionTime) {
      await new Promise((done) =>
        setTimeout(done, nextExecutionTime - Date.now()),
      )
    }
    isScheduled = false
    isExecuting = true
    await func(...lastArgs)
    nextExecutionTime = Date.now() + interval
    isExecuting = false
  }
}

const candidateThrottle = (func, interval = 0) => {
  let nextExecutionTime = 0
  let lastArgs = null
  let isExecuting = false
  let scheduledPromise
  return (...args) => {
    lastArgs = args
    if (scheduledPromise) return scheduledPromise
    scheduledPromise = Promise.resolve().then(async () => {
      while (isExecuting) await new Promise((done) => setTimeout(done, interval))
      while (Date.now() < nextExecutionTime) {
        await new Promise((done) =>
          setTimeout(done, nextExecutionTime - Date.now()),
        )
      }
      scheduledPromise = undefined
      isExecuting = true
      await func(...lastArgs)
      nextExecutionTime = Date.now() + interval
      isExecuting = false
    })
    return scheduledPromise
  }
}

const run = async (name, createThrottle) => {
  const firstStarted = deferred()
  const releaseFirst = deferred()
  const executions = []
  const throttled = createThrottle(async (value) => {
    executions.push(value)
    if (value === 1) {
      firstStarted.resolve()
      await releaseFirst.promise
    }
  })

  const first = throttled(1)
  await firstStarted.promise
  const scheduled = throttled(2)
  const coalesced = throttled(3)
  let coalescedSettled = false
  void coalesced.then(() => {
    coalescedSettled = true
  })
  await Promise.resolve()
  const beforeRelease = { coalescedSettled, executions: [...executions] }
  releaseFirst.resolve()
  await Promise.all([first, scheduled, coalesced])
  return { name, beforeRelease, after: { executions } }
}

console.log(JSON.stringify(await run('current', currentThrottle)))
console.log(JSON.stringify(await run('candidate', candidateThrottle)))
