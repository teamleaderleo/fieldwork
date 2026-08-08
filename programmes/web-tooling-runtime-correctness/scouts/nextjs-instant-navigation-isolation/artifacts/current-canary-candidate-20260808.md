## In simple words

The Next.js `@next/playwright` cleanup question still exists on current canary. The owned-fork candidate has now been rebuilt directly from current upstream and includes the regression in the existing Instant Navigation testing suite.

The candidate is reviewable as a two-file diff. It has not received target-native Next.js execution on this head.

## Current upstream pin

- upstream repository: `vercel/next.js`
- canary commit: `a677cf66af002fbdcf49a982ef435b03554817cc`
- retrieval date: `2026-08-08`
- helper blob: `291afa9ef0c7b215318b36feb71af688d95f5373`
- existing test-suite blob at base: `3c06a831e7c40336b67d55e66c75f991bbafb832`

The relevant helper remained unchanged at this pin.

## Canonical owned-fork candidate

- repository: `teamleaderleo/next.js`
- branch: `fieldwork/instant-navigation-origin-scoped-release-current`
- exact base branch: `fieldwork/upstream-canary-20260808-a677cf66`
- exact base SHA: `a677cf66af002fbdcf49a982ef435b03554817cc`
- owned-fork review PR: #9

Net changed-file fence against the exact base:

```text
packages/next-playwright/src/index.ts
  +25 / -23

test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
  +30 / -0
```

No temporary workflow is present in the canonical candidate diff.

## Implementation

The public `instant()` signature is unchanged. The private cleanup helper receives the already-resolved application URL and uses Playwright's URL-filtered cookie lookup:

```ts
const scopeURL = resolveURL(page, options)
const { hostname } = new URL(scopeURL)

await releaseInstantCookie(context, scopeURL)

async function releaseInstantCookie(
  context: PlaywrightBrowserContext,
  scopeURL: string
): Promise<void> {
  for (let attempt = 0; attempt < 5; attempt++) {
    const instantCookies = (await context.cookies(scopeURL)).filter(
      (cookie) => cookie.name === INSTANT_COOKIE
    )
    // existing individual-expiry behavior follows
  }
}
```

The BrowserContext-wide `contextsWithActiveScope` rule remains unchanged.

## Regression placement

The regression is folded into:

`test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

It sits immediately after same-origin stale-cookie recovery and before the separate-BrowserContext concurrency test. It seeds a `next-instant-navigation-testing` cookie that only applies to `app-b.example`, enters and exits `instant()` for the fixture app, and checks that app B's cookie survives both points.

This placement documents the intended distinction without changing the separate same-context concurrency question:

```text
stale instant cookie applicable to this app -> cleanup may remove it
same-named instant cookie applicable only to another app -> preserve it
one active instant() call per BrowserContext -> unchanged
```

## Execution state

Evidence class for the current candidate:

- `source-read`
- `target-test-prepared`

Earlier retained evidence remains:

- `model-executed`
- `integration-executed` at the real Playwright/Chromium cookie-interface boundary

No `target-executed` claim is made for this current candidate. Attempts to use temporary GitHub Actions execution carriers in the owned fork did not dispatch, and they produced no test result. Those carrier surfaces were retired.

The next technical gate remains a real Next.js run of the existing suite in the repository-declared modes, especially:

```sh
pnpm build-all
pnpm test-dev-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
pnpm test-start-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

## Boundary

Third-party upstream is read-only to Fieldwork automation. This artifact records research and an owned-fork candidate only. Any eventual upstream interaction must be performed manually by a human.
