# `@next/playwright instant()` clears testing cookies for other origins

`instant()` scopes its testing cookie to the application hostname, but cleanup currently reads every cookie in the Playwright `BrowserContext` and expires every cookie named `next-instant-navigation-testing`.

If the same browser context has a testing cookie for another origin, calling `instant()` for app A can delete app B’s cookie.

For example:

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
  // app-b.example's testing cookie has already been removed
})
```

The cleanup currently does:

```ts
const instantCookies = (await context.cookies()).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

I think cleanup should be limited to cookies applicable to the application URL being controlled, for example by using Playwright’s URL-filtered cookie lookup.

I reproduced this with Playwright/Chromium: `context.cookies()` returned the testing cookies for both origins, while `context.cookies(appAUrl)` returned only the cookies that apply to app A.

This is reproducible on current canary source.

Reproduction: https://github.com/teamleaderleo/playground/tree/repro/next-playwright-origin-cookie/next-playwright-origin-cookie-repro

Candidate patch: https://github.com/teamleaderleo/next.js/pull/9
