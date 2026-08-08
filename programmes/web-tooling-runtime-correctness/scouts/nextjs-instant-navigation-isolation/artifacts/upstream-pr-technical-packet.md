# Next.js upstream pull-request technical packet

This is a fact packet for a **human-written** external pull-request description. It is intentionally not a submit-ready PR description.

## Suggested PR title

`fix(next-playwright): scope instant cookie cleanup to app URL`

## Intended sequencing

Open the bug report first once the public reproduction and exact canary execution exist. Then open the PR and reference it with `Fixes #<issue>`.

## Exact candidate

- Owned fork: `teamleaderleo/next.js`
- Internal review PR: `#7`
- Branch: `fieldwork/instant-navigation-origin-scoped-release`
- Reviewed head: `a13931921cc8dfa612ab6ca5f359b4baa350f75a`
- Exact public upstream base: `5e8f31f7bdf7f564ec98a42e205f7e5b665398da`
- Product file changed: `packages/next-playwright/src/index.ts`

## What changed

Current code resolves one application URL only to obtain its hostname for cookie acquisition, then later performs context-wide cookie lookup for cleanup.

Candidate code retains the full resolved URL:

```ts
const scopeURL = resolveURL(page, options)
const { hostname } = new URL(scopeURL)
```

Both stale cleanup before acquisition and final release receive that URL:

```ts
await releaseInstantCookie(context, scopeURL)

// ...

await step('Release Instant Lock', () =>
  releaseInstantCookie(context, scopeURL)
)
```

The helper's minimal Playwright BrowserContext interface is expanded to match Playwright's existing optional URL filter:

```ts
cookies(urls?: string | string[]): Promise<...>
```

Cleanup changes from:

```ts
const instantCookies = (await context.cookies()).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

to:

```ts
const instantCookies = (await context.cookies(scopeURL)).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

## Why this is the narrow repair

Acquisition already has one application identity: the resolved URL/hostname.

Playwright already implements cookie applicability for a URL, including domain/path/secure semantics. Passing the resolved URL into cookie lookup lets Playwright decide which entries can apply to the application instead of selecting every same-named cookie stored in the browser context.

This also handles parent-domain cookies correctly: a cookie that genuinely applies to app A remains eligible for cleanup; a B-only cookie does not.

## Behavior intentionally left unchanged

- one active `instant()` scope per Playwright `BrowserContext`;
- `WeakSet<BrowserContext>` active-scope tracking;
- hostname-scoped cookie acquisition;
- pre-acquire stale-cookie cleanup;
- repeated re-read/re-delete loop for resurrected cookies;
- individual expiry of matching cookie entries;
- avoidance of Playwright's historical filtered `clearCookies` path;
- unrelated cookie-name preservation.

## Review repairs already made

### Removed standalone test suite

An early candidate added a separate e2e test file manually. Current Next.js repository instructions say closely related checks should live in the existing suite, so that file was removed.

The correct regression location is:

`test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

### Corrected ownership comment

An inherited comment said the instant cookie itself was browser-context-scoped. That conflated browser-context storage with normal cookie domain/path applicability. The candidate now states only that active `instant()` scopes are intentionally tracked at BrowserContext granularity.

## Regression test that should accompany the upstream PR

Add a test beside the existing stale-cookie recovery and BrowserContext ownership tests.

Required assertions:

1. open the existing Next.js fixture page;
2. seed a `next-instant-navigation-testing` cookie for a B-only domain in the same native Playwright context;
3. optionally seed unrelated session cookies as negative controls;
4. enter `instant(pageA, ...)`;
5. inside the callback, assert B's cookie is still present;
6. after `instant()` returns, assert B's cookie is still present;
7. assert A's instant cookie is absent after release;
8. retain the existing stale-cookie recovery test unchanged and passing.

The regression should focus only on cleanup ownership. It should not assert that two simultaneous same-context scopes across distinct origins are supported.

## Target-native execution checklist

Follow current Next.js repository instructions and capture output once per mode.

After a clean branch/bootstrap:

```sh
pnpm build-all
```

Focused development mode:

```sh
pnpm test-dev-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

Focused production mode:

```sh
pnpm test-start-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

Also run the package-relevant type/build checks requested by current repository guidance. Record exact commands, environment, and outcomes.

## Evidence already available

- current upstream helper source mapped at exact commit;
- helper blob unchanged from the investigated 16.3 preview line through the August 7 current pin;
- exact helper-selection model reproduced;
- real Playwright Core + Chromium confirms unfiltered lookup/deletion reaches B-only cookies;
- real Playwright Core + Chromium confirms URL-filtered lookup preserves B-only cookies;
- relevant history mapped through PRs 90613, 94947, and 95375;
- no direct overlap found for this exact cross-URL cleanup case.

## PR checklist mapping

### What

Narrow Instant Navigation testing-cookie cleanup to cookie entries applicable to the resolved application URL.

### Why

Current cleanup owns a broader cookie set than acquisition: one app's `instant()` scope can expire a same-named testing cookie that applies only to another URL stored in the same BrowserContext.

### How

Thread the existing resolved application URL into `releaseInstantCookie` and use Playwright's URL-filtered `BrowserContext.cookies(scopeURL)` query before individually expiring matching entries.

### Related issue

`Fixes #<human-filed issue>`

### Tests

- existing Instant Navigation suite regression for B-only cookie preservation;
- existing stale-cookie recovery remains passing;
- focused dev and production execution on exact current head.

## Claims to avoid

- Do not claim a security fix.
- Do not broaden the PR into concurrent-scope ownership.
- Do not rewrite the cookie protocol.
- Do not replace the individual-expiry race repair from PR 94947.
- Do not state target-native pass results until they exist.

## Upstream interaction boundary

The internal fork PR is a review surface only. No upstream PR has been opened and no upstream interaction is authorized by Fieldwork.