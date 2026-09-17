const INSTANT_COOKIE = 'next-instant-navigation-testing'

class FakeContext {
  constructor(cookies = []) {
    this.jar = cookies.map((cookie) => ({ path: '/', ...cookie }))
  }

  async cookies() {
    return this.jar.map((cookie) => ({ ...cookie }))
  }

  async addCookies(cookies) {
    for (const cookie of cookies) {
      const normalized = { path: '/', ...cookie }
      const index = this.jar.findIndex(
        (existing) =>
          existing.name === normalized.name &&
          existing.domain === normalized.domain &&
          existing.path === normalized.path
      )
      if (normalized.expires !== undefined && normalized.expires <= 1) {
        if (index !== -1) this.jar.splice(index, 1)
        continue
      }
      const stored = {
        name: normalized.name,
        value: normalized.value,
        domain: normalized.domain,
        path: normalized.path,
      }
      if (index === -1) this.jar.push(stored)
      else this.jar[index] = stored
    }
  }
}

const contextsWithActiveScope = new WeakSet()

async function releaseInstantCookie(context) {
  for (let attempt = 0; attempt < 5; attempt++) {
    const instantCookies = (await context.cookies()).filter(
      (cookie) => cookie.name === INSTANT_COOKIE
    )
    if (instantCookies.length === 0) return
    await context.addCookies(
      instantCookies.map((cookie) => ({
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        expires: 1,
      }))
    )
  }
}

async function instant(page, fn) {
  const context = page.context()
  if (contextsWithActiveScope.has(context)) {
    throw new Error('already active')
  }
  const { hostname } = new URL(page.url())
  contextsWithActiveScope.add(context)
  try {
    await releaseInstantCookie(context)
    await context.addCookies([
      {
        name: INSTANT_COOKIE,
        value: JSON.stringify([0, 'probe']),
        domain: hostname,
        path: '/',
      },
    ])
    try {
      return await fn()
    } finally {
      await releaseInstantCookie(context)
    }
  } finally {
    contextsWithActiveScope.delete(context)
  }
}

function page(url, context) {
  return { url: () => url, context: () => context }
}

function findCookie(jar, name, domain) {
  return jar.find((cookie) => cookie.name === name && cookie.domain === domain)
}

const shared = new FakeContext([
  {
    name: INSTANT_COOKIE,
    value: JSON.stringify([1, 'other-app', null]),
    domain: 'app-b.example',
    path: '/',
  },
  { name: 'session', value: 'keep-me', domain: 'app-b.example', path: '/' },
  { name: 'session', value: 'keep-me-too', domain: 'app-a.example', path: '/' },
])

const before = await shared.cookies()
let inside
await instant(page('https://app-a.example/', shared), async () => {
  inside = await shared.cookies()
})
const after = await shared.cookies()

let sameContextDistinctOriginSecondScopeError = null
const concurrencyContext = new FakeContext()
let releaseFirst
const firstHeld = new Promise((resolve) => {
  releaseFirst = resolve
})
const first = instant(page('https://app-a.example/', concurrencyContext), async () => {
  await firstHeld
})
await new Promise((resolve) => setTimeout(resolve, 0))
try {
  await instant(page('https://app-b.example/', concurrencyContext), async () => {})
} catch (error) {
  sameContextDistinctOriginSecondScopeError = error.message
}
releaseFirst()
await first

const contextA = new FakeContext()
const contextB = new FakeContext()
let separateContextsConcurrentScopesSucceed = false
await Promise.all([
  instant(page('https://app-a.example/', contextA), async () => {}),
  instant(page('https://app-b.example/', contextB), async () => {}),
]).then(() => {
  separateContextsConcurrentScopesSucceed = true
})

const result = {
  model_of: {
    repository: 'vercel/next.js',
    tag: 'v16.3.0-preview.9',
    commit: '838bd19bdef0e41254f0868516b0c6c6e59e70d7',
    source_path: 'packages/next-playwright/src/index.ts',
  },
  environment: { node: process.version },
  observations: {
    other_origin_instant_cookie_survives_acquire: Boolean(
      findCookie(inside, INSTANT_COOKIE, 'app-b.example')
    ),
    unrelated_app_b_cookie_preserved_inside:
      findCookie(inside, 'session', 'app-b.example')?.value === 'keep-me',
    unrelated_app_a_cookie_preserved_inside:
      findCookie(inside, 'session', 'app-a.example')?.value === 'keep-me-too',
    unrelated_cookies_preserved_after:
      findCookie(after, 'session', 'app-b.example')?.value === 'keep-me' &&
      findCookie(after, 'session', 'app-a.example')?.value === 'keep-me-too',
    same_context_distinct_origin_second_scope_error:
      sameContextDistinctOriginSecondScopeError,
    separate_contexts_concurrent_scopes_succeed:
      separateContextsConcurrentScopesSucceed,
  },
  snapshots: { before, inside, after },
}

console.log(JSON.stringify(result, null, 2))

if (
  result.observations.other_origin_instant_cookie_survives_acquire !== false ||
  result.observations.unrelated_app_b_cookie_preserved_inside !== true ||
  result.observations.unrelated_app_a_cookie_preserved_inside !== true ||
  result.observations.unrelated_cookies_preserved_after !== true ||
  result.observations.same_context_distinct_origin_second_scope_error !==
    'already active' ||
  result.observations.separate_contexts_concurrent_scopes_succeed !== true
) {
  process.exitCode = 1
}
