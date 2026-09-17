## In simple words

The Next.js `@next/playwright` cleanup issue still exists on the pinned current canary. The candidate has been reduced to one commit, keeps the regression in the existing Instant Navigation suite, and has now been submitted upstream manually by the human owner.

The candidate remains a two-file diff. The public reproduction has been executed and fails in the expected way. The patched Next.js target suite has not yet run.

## Current upstream pin

- upstream repository: `vercel/next.js`
- canary commit: `a677cf66af002fbdcf49a982ef435b03554817cc`
- retrieval date: `2026-08-08`
- helper blob: `291afa9ef0c7b215318b36feb71af688d95f5373`
- existing test-suite blob at base: `3c06a831e7c40336b67d55e66c75f991bbafb832`

The relevant helper remained unchanged at this pin.

## Canonical candidate

- owned repository: `teamleaderleo/next.js`
- branch: `fieldwork/instant-navigation-origin-scoped-release-current`
- exact base SHA: `a677cf66af002fbdcf49a982ef435b03554817cc`
- squashed head SHA: `a33d51d10d212ae656a0c94a28ffe51a6e43879b`
- owned-fork review PR: https://github.com/teamleaderleo/next.js/pull/9
- human-filed upstream PR: https://redirect.github.com/vercel/next.js/pull/96962
- related upstream issue: https://redirect.github.com/vercel/next.js/issues/96961

The branch is exactly one commit ahead of the pinned base.

Net changed-file fence:

```text
packages/next-playwright/src/index.ts
  +32 / -42

test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
  +42 / -0
```

No temporary workflow is present in the candidate diff.

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

The comments were also tightened to remove an inaccurate inherited claim that the cookie itself is BrowserContext-scoped. The code now documents two separate facts:

- active `instant()` calls are tracked per BrowserContext;
- cleanup operates on Instant-cookie entries applicable to the resolved application URL.

## Regression placement

The regression is folded into:

`test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

It sits immediately after same-origin stale-cookie recovery and before the separate-BrowserContext concurrency test. It seeds a `next-instant-navigation-testing` cookie that applies to `app-b.example`, enters and exits `instant()` for the fixture app, and checks that app B's cookie survives both points.

The test removes its synthetic app-B cookie in a `finally` block after the preservation assertions so the shared BrowserContext cannot contaminate later tests.

This placement documents the intended distinction without changing the separate same-context concurrency question:

```text
stale instant cookie applicable to this app -> cleanup may remove it
same-named instant cookie applicable to another app -> preserve it
one active instant() call per BrowserContext -> unchanged
```

## Architectural boundary

The candidate treats ordinary release as the inverse of one application-scoped acquisition:

```text
acquire: app A
release: cookies applicable to app A
```

A hypothetical operation that deliberately purges every Instant Navigation cookie in a BrowserContext would be a separate reset/garbage-collection API. The candidate does not add such an operation and does not use global cleanup as a side effect of normal release.

## URL-filter semantics control

Real Playwright/Chromium applicability controls established that URL filtering follows normal cookie applicability rather than exact hostname equality.

For an app-A URL under `app-a.example.com`:

- an app-B-only same-named cookie was excluded and survived scoped expiry;
- a `.example.com` parent-domain same-named cookie that genuinely applies to app A was included and removed;
- unrelated session cookies survived.

This is why `context.cookies(scopeURL)` is preferable to an exact-domain string comparison.

## Public reproduction execution

Public reproduction:

https://github.com/teamleaderleo/playground/tree/repro/next-playwright-origin-cookie/next-playwright-origin-cookie-repro

Human-executed environment:

```text
Node.js: v22.23.1
@next/playwright: 16.3.1-canary.8
Playwright: 1.61.1
```

Observed result:

```text
AssertionError: app B cookie was removed by instant() for app A
actual:   undefined
expected: '[1,"app-b",null]'
```

This is direct execution of the public package-level repro against current canary.

## Execution state

Evidence class for the current work:

- `source-read`
- `model-executed`
- `integration-executed`
- `public-repro-executed`
- `target-test-prepared`

No `target-executed` claim is made for the patched Next.js candidate.

The remaining target-native commands are the repository-declared focused modes:

```sh
pnpm build-all
pnpm test-dev-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
pnpm test-start-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

After the human opened upstream PR #96962, GitHub created its main workflow runs but they reached `action_required` before jobs were created. This is not treated as target-native execution or as a test failure.

## Boundary

Third-party upstream is read-only to Fieldwork automation. The issue and PR above were opened manually by the human owner. Fieldwork records their state but performs no upstream mutation.
