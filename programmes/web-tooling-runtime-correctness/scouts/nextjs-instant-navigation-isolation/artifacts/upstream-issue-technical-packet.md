# Next.js upstream issue draft

Status: wording reviewed in chat; ready for owner editing. Not posted upstream.

## Draft

# `@next/playwright instant()` clears testing cookies for other origins

`instant()` scopes its testing cookie to the application hostname, but cleanup currently reads every cookie in the Playwright `BrowserContext` and expires every cookie named `next-instant-navigation-testing`.

Then, if the same browser context has a testing cookie for another origin, calling `instant()` for app A can delete app B’s cookie.

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

Reproduction: [link]

---

Candidate patch for reference: `teamleaderleo/next.js` PR 7.

## Internal evidence notes

- Investigated current upstream commit: `5e8f31f7bdf7f564ec98a42e205f7e5b665398da` (2026-08-07).
- Current helper: `packages/next-playwright/src/index.ts`.
- Real Playwright/Chromium control is retained in `playwright-cookie-scope-browser.json`.
- Relevant history and deeper analysis remain in `report.md` and `review-20260808.md`.
- No upstream issue, comment, or PR has been created from Fieldwork.
