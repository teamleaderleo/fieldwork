import { performance } from 'node:perf_hooks'
import { pathToFileURL } from 'node:url'
const { resolveConfig } = await import(pathToFileURL(process.argv[2]))
const root = process.argv[3]
const scenario = process.argv[4]
function input() {
  const base = { root, configFile: false, envDir: false, logLevel: 'silent' }
  if (scenario === 'minimal') return base
  return {
    ...base,
    build: { ssrEmitAssets: true },
    server: { hmr: { port: 24678 }, allowedHosts: ['dev.test'], fs: { allow: [root] }, warmup: { clientFiles: ['src/client.ts'], ssrFiles: ['src/server.ts'] } },
    preview: { allowedHosts: ['preview.test'] },
    css: { transformer: 'lightningcss', lightningcss: {} },
    environments: { client: { dev: {} }, ssr: { dev: {}, build: {} }, custom: {} },
    optimizeDeps: {
      rolldownOptions: { resolve: {}, output: {}, transform: {}, moduleTypes: {}, plugins: [{ name: 'native' }] },
      esbuildOptions: { define: { __TEST__: 'true' }, loader: { '.txt': 'text' }, plugins: [{ name: 'legacy', setup() {} }] }
    }
  }
}
for (let i = 0; i < 60; i++) await resolveConfig(input(), 'serve')
global.gc?.()
const count = 200
const start = performance.now()
for (let i = 0; i < count; i++) await resolveConfig(input(), 'serve')
console.log(JSON.stringify({ scenario, count, msPerResolution: (performance.now() - start) / count }))
