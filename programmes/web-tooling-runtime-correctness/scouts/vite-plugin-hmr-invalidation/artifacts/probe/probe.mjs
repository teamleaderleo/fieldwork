import assert from 'node:assert/strict'
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

const targetRevision = '8a245726944ed29225920d49be77c33c6e03afc8'
const viteEntry = process.env.VITE_ENTRY || 'vite'
const { build, createLogger, createServer } = await import(viteEntry)

const results = {
  targetRevision,
  viteEntry,
  node: process.version,
  cases: [],
}

await runCase('watchChange rejection preserves stale transform cache', probeWatchChangeFailure)
await runCase('post-order transform escapes dev import analysis', probePostTransformOrdering)
await runCase('bundled dev omits plugin hot-update hooks', probeBundledDevHotUpdate)

process.stdout.write(`${JSON.stringify(results, null, 2)}\n`)

async function runCase(name, fn) {
  const started = Date.now()
  try {
    const detail = await fn()
    results.cases.push({ name, status: 'reproduced', durationMs: Date.now() - started, detail })
  } catch (error) {
    results.cases.push({
      name,
      status: 'failed',
      durationMs: Date.now() - started,
      error: serializeError(error),
    })
    process.exitCode = 1
  }
}

async function probeWatchChangeFailure() {
  const control = await runWatchChangeScenario(false)
  const rejection = await runWatchChangeScenario(true)

  assert.equal(control.invalidatedAfterEvent, true)
  assert.equal(control.refreshedValue, 'beta')
  assert.equal(rejection.loggedError, true)
  assert.equal(rejection.invalidatedAfterEvent, false)
  assert.equal(rejection.refreshedValue, 'alpha')

  return { control, rejection }
}

async function runWatchChangeScenario(rejectWatchChange) {
  return withProject(async (root) => {
    const stateFile = path.join(root, 'state.txt')
    const virtualId = '\0virtual:fieldwork-state'
    await writeProject(root, {
      'index.html': '<script type="module" src="/src/main.js"></script>',
      'src/main.js': "import { value } from 'virtual:fieldwork-state'; console.log(value); if (import.meta.hot) import.meta.hot.accept('virtual:fieldwork-state', () => {});",
      'state.txt': 'alpha\n',
    })

    const logger = createLogger('silent')
    let resolveLoggedError
    const loggedError = new Promise((resolve) => {
      resolveLoggedError = resolve
    })
    logger.error = () => resolveLoggedError(true)

    const plugin = {
      name: 'fieldwork-state-plugin',
      resolveId(id) {
        if (id === 'virtual:fieldwork-state') return virtualId
      },
      async load(id) {
        if (id !== virtualId) return
        this.addWatchFile(stateFile)
        const value = (await readFile(stateFile, 'utf8')).trim()
        return `export const value = ${JSON.stringify(value)}`
      },
      watchChange(id) {
        if (rejectWatchChange && path.resolve(id) === stateFile) {
          throw new Error('fieldwork-watchChange-rejection')
        }
      },
    }

    const server = await createServer({
      root,
      configFile: false,
      logLevel: 'silent',
      customLogger: logger,
      plugins: [plugin],
      server: { middlewareMode: true, ws: false },
    })

    try {
      await server.transformRequest('/src/main.js')
      const virtualUrl = '/@id/__x00__virtual:fieldwork-state'
      const first = await server.transformRequest(virtualUrl)
      assert.match(first?.code || '', /alpha/)

      const environment = server.environments.client
      const mod = environment.moduleGraph.getModuleById(virtualId)
      assert.ok(mod)
      assert.ok(mod.transformResult)
      const previousTransform = mod.transformResult

      await writeFile(stateFile, 'beta\n')
      server.watcher.emit('change', stateFile)

      let didLogError = false
      if (rejectWatchChange) {
        didLogError = await withTimeout(loggedError, 2_000, 'watchChange error was not logged')
      } else {
        await waitUntil(() => mod.transformResult === null, 2_000, 'module was not invalidated')
      }

      const invalidatedAfterEvent = mod.transformResult === null
      if (rejectWatchChange) assert.equal(mod.transformResult, previousTransform)

      const refreshed = await server.transformRequest(virtualUrl)
      const refreshedValue = /beta/.test(refreshed?.code || '') ? 'beta' : 'alpha'
      return { loggedError: didLogError, invalidatedAfterEvent, refreshedValue }
    } finally {
      await server.close()
    }
  })
}

async function probePostTransformOrdering() {
  const normal = await runTransformOrderingScenario(undefined)
  const post = await runTransformOrderingScenario('post')

  assert.equal(normal.graphContainsInjectedDependency, true)
  assert.equal(post.graphContainsInjectedDependency, false)
  assert.equal(post.devOutputContainsInjectedImport, true)
  assert.equal(post.buildOutputContainsDependencySentinel, true)

  return { normal, post }
}

async function runTransformOrderingScenario(order) {
  return withProject(async (root) => {
    await writeProject(root, {
      'index.html': '<script type="module" src="/src/main.js"></script>',
      'src/main.js': "console.log('main')",
      'src/dep.js': "export const dep = 'FIELDWORK_DEP_SENTINEL'",
    })

    const handler = (code, id) => {
      if (id !== normalizePath(path.join(root, 'src/main.js'))) return
      return `${code}\nimport { dep } from './dep.js'; console.log(dep); if (import.meta.hot) import.meta.hot.accept('./dep.js', () => {});`
    }
    const plugin = {
      name: `fieldwork-inject-import-${order || 'normal'}`,
      transform: order ? { order, handler } : handler,
    }

    const server = await createServer({
      root,
      configFile: false,
      logLevel: 'silent',
      plugins: [plugin],
      server: { middlewareMode: true, ws: false },
    })

    let devCode
    let graphContainsInjectedDependency
    try {
      const transformed = await server.transformRequest('/src/main.js')
      devCode = transformed?.code || ''
      const main = server.environments.client.moduleGraph.getModuleById(
        normalizePath(path.join(root, 'src/main.js')),
      )
      assert.ok(main)
      graphContainsInjectedDependency = [...main.importedModules].some((mod) =>
        mod.id?.endsWith('/src/dep.js'),
      )
    } finally {
      await server.close()
    }

    const output = await build({
      root,
      configFile: false,
      logLevel: 'silent',
      plugins: [plugin],
      build: { write: false },
    })
    const outputs = Array.isArray(output) ? output : [output]
    const buildCode = outputs
      .flatMap((entry) => ('output' in entry ? entry.output : []))
      .filter((entry) => entry.type === 'chunk')
      .map((entry) => entry.code)
      .join('\n')

    return {
      hookOrder: order || 'normal',
      graphContainsInjectedDependency,
      devOutputContainsInjectedImport: devCode.includes('./dep.js'),
      buildOutputContainsDependencySentinel: buildCode.includes('FIELDWORK_DEP_SENTINEL'),
    }
  })
}

async function probeBundledDevHotUpdate() {
  const classic = await runHotUpdateDeliveryScenario(false)
  const bundled = await runHotUpdateDeliveryScenario(true)

  assert.ok(classic.hotUpdateCalls > 0)
  assert.equal(bundled.hotUpdateCalls, 0)
  assert.ok(classic.watchChangeCalls > 0)
  assert.ok(bundled.watchChangeCalls > 0)

  return { classic, bundled }
}

async function runHotUpdateDeliveryScenario(bundledDev) {
  return withProject(async (root) => {
    const watchedFile = path.join(root, 'watched.txt')
    await writeProject(root, {
      'index.html': '<script type="module" src="/src/main.js"></script>',
      'src/main.js': "console.log('main')",
      'watched.txt': 'one\n',
    })

    let watchChangeCalls = 0
    let hotUpdateCalls = 0
    let resolveWatchChange
    const watchChangeSeen = new Promise((resolve) => {
      resolveWatchChange = resolve
    })
    const plugin = {
      name: 'fieldwork-hot-update-delivery',
      buildStart() {
        this.addWatchFile(watchedFile)
      },
      watchChange(id) {
        if (path.resolve(id) === watchedFile) {
          watchChangeCalls++
          resolveWatchChange()
        }
      },
      hotUpdate({ file }) {
        if (path.resolve(file) === watchedFile) hotUpdateCalls++
      },
    }

    const server = await createServer({
      root,
      configFile: false,
      logLevel: 'silent',
      plugins: [plugin],
      experimental: { bundledDev },
      server: { middlewareMode: true, ws: false },
    })

    try {
      server.watcher.emit('change', watchedFile)
      await withTimeout(watchChangeSeen, 2_000, 'watchChange hook was not delivered')
      await new Promise((resolve) => setTimeout(resolve, 50))
      return { bundledDev, watchChangeCalls, hotUpdateCalls }
    } finally {
      await server.close()
    }
  })
}

async function withProject(fn) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'fieldwork-vite-'))
  try {
    return await fn(root)
  } finally {
    await rm(root, { recursive: true, force: true })
  }
}

async function writeProject(root, files) {
  for (const [relative, content] of Object.entries(files)) {
    const filename = path.join(root, relative)
    await mkdir(path.dirname(filename), { recursive: true })
    await writeFile(filename, content)
  }
}

async function waitUntil(predicate, timeoutMs, message) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    if (predicate()) return
    await new Promise((resolve) => setTimeout(resolve, 10))
  }
  throw new Error(message)
}

async function withTimeout(promise, timeoutMs, message) {
  let timer
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(message)), timeoutMs)
      }),
    ])
  } finally {
    clearTimeout(timer)
  }
}

function normalizePath(filename) {
  return filename.split(path.sep).join('/')
}

function serializeError(error) {
  return {
    name: error?.name || 'Error',
    message: error?.message || String(error),
    stack: error?.stack,
  }
}
