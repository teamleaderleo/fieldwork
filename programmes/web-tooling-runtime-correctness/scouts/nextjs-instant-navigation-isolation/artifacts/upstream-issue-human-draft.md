# `@next/playwright instant()` clears testing cookies for other origins

`instant()` scopes its testing cookie to the application hostname, but cleanup currently reads every cookie in the Playwright `BrowserContext` and expires every cookie named `next-instant-navigation-testing`.

If the same browser context has a testing cookie for another origin, calling `instant()` for app A can delete app B’s cookie.

Suppose `pageA` is testing app A, while the same `BrowserContext` already contains app B’s testing cookie:

```ts
await context.addCookies([
  {
    name: 'next-instant-navigation-testing',
    value: '...',
    domain: 'app-b.example',
    path: '/',
  },
])

await instant(pageA, async () => {
  // Current behavior: pre-acquire cleanup has deleted app B's cookie.
})
```

That happens because cleanup starts from the full browser-context cookie jar:

```ts
const instantCookies = (await context.cookies()).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

It filters only by name, so app B’s cookie is selected even though this `instant()` call is controlling app A.

I think cleanup should be limited to cookies applicable to the application URL being controlled, for example by using Playwright’s URL-filtered cookie lookup.

Playwright already distinguishes between `context.cookies()`, which returns the context’s full cookie jar, and `context.cookies(url)`, which returns only cookies that affect that URL.

I reproduced this with Playwright/Chromium: `context.cookies()` returned the testing cookies for both origins, while `context.cookies(appAUrl)` returned only the cookies that apply to app A.

This is reproducible on current canary source.

Reproduction: https://github.com/teamleaderleo/playground/tree/repro/next-playwright-origin-cookie/next-playwright-origin-cookie-repro

Candidate patch: https://github.com/teamleaderleo/next.js/pull/9
