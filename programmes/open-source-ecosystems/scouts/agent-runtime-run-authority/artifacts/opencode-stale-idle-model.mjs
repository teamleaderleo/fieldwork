const status = new Map()
const runners = new Map()

let releaseIdle
const idleMayFinish = new Promise((resolve) => {
  releaseIdle = resolve
})
let idlePublishStarted
const idleStarted = new Promise((resolve) => {
  idlePublishStarted = resolve
})

function createRunner(name) {
  return {
    name,
    async run(work) {
      status.set('session', 'busy')
      try {
        return await work()
      } finally {
        // Mirrors SessionRunState.onIdle ordering: the registration is removed
        // before asynchronous idle publication settles.
        runners.delete('session')
        idlePublishStarted()
        await idleMayFinish
        status.delete('session') // absence means idle
      }
    },
  }
}

const first = createRunner('A')
runners.set('session', first)
const firstRun = first.run(async () => 'first')

await idleStarted

// A has dropped the registration but has not finished publishing idle.
const second = createRunner('B')
runners.set('session', second)
let finishSecond
const secondDone = new Promise((resolve) => {
  finishSecond = resolve
})
const secondRun = second.run(async () => secondDone)
await Promise.resolve()

const beforeStaleIdle = {
  registeredRunner: runners.get('session')?.name,
  status: status.get('session') ?? 'idle',
}

releaseIdle()
await firstRun

const afterStaleIdle = {
  registeredRunner: runners.get('session')?.name,
  status: status.get('session') ?? 'idle',
}

finishSecond('second')
await secondRun

console.log(JSON.stringify({ beforeStaleIdle, afterStaleIdle }, null, 2))
