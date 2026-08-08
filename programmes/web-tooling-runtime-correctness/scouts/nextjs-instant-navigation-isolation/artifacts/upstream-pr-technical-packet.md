# Next.js upstream pull-request technical packet

This packet records the technical basis for the human-written upstream pull request and its current submitted state.

## Filed surfaces

- human-filed issue: https://redirect.github.com/vercel/next.js/issues/96961
- human-filed PR: https://redirect.github.com/vercel/next.js/pull/96962
- owned-fork review PR: https://github.com/teamleaderleo/next.js/pull/9

The issue and PR were opened manually by the human owner, sequentially and back-to-back on 2026-08-08. The PR uses `Fixes #96961`.

## Exact candidate

- owned fork: `teamleaderleo/next.js`
- branch: `fieldwork/instant-navigation-origin-scoped-release-current`
- exact public upstream base: `a677cf66af002fbdcf49a982ef435b03554817cc`
- squashed head: `a33d51d10d212ae656a0c94a28ffe51a6e43879b`
- commit count over base: 1
- changed files:
  - `packages/next-playwright/src/index.ts`
  - `test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

Net stats:

```text
packages/next-playwright/src/index.ts
  +32 / -42

test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
  +42 / -0
```

## What changed

Current code resolves one application URL only to obtain its hostname for cookie acquisition, then performs context-wide cookie lookup for cleanup.

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

The helper's local structural BrowserContext interface matches Playwright's optional URL filter:

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

Playwright already distinguishes between the complete BrowserContext cookie jar and cookies that affect a supplied URL. `instant(page, ...)` controls one resolved application URL, so ordinary scope release has a natural URL-scoped selection primitive.

The useful symmetry is:

```text
acquire: app A
release: cookies applicable to app A
```

This delegates domain/path/secure applicability to Playwright. A parent-domain cookie that genuinely applies to app A remains eligible; a B-only cookie does not.

If Next.js ever needs a context-wide reset or garbage-collection operation that deliberately purges every Instant Navigation testing cookie in a BrowserContext, that should be represented separately rather than conflated with normal release of one `instant()` scope.

## Behavior left unchanged

- one active `instant()` scope per Playwright `BrowserContext`;
- `WeakSet<BrowserContext>` active-scope tracking;
- hostname-scoped cookie acquisition;
- pre-acquire stale-cookie cleanup for entries applicable to the selected application URL;
- repeated re-read/re-delete loop for resurrected cookies;
- individual expiry of matching cookie entries;
- avoidance of Playwright's historical filtered `clearCookies` path;
- unrelated cookie-name preservation.

## Source-comment review

The source comments now separate two concepts that the inherited text conflated:

- active-call tracking is BrowserContext-wide;
- cookie entries retain ordinary URL/domain/path applicability.

The updated comments no longer claim that the Instant cookie itself is BrowserContext-scoped or that every same-named cookie present when no helper call is active is necessarily stale.

The remaining comment detail is limited to behavior that constrains the implementation: stale-cookie resurrection, individual expiry, and bounded retry.

## Regression placement and coverage

The regression is in:

`test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

It is placed immediately after same-origin stale-cookie recovery and before separate-BrowserContext concurrency coverage.

The test:

1. opens the existing fixture page;
2. seeds a `next-instant-navigation-testing` cookie for a B-only domain in the same native Playwright context;
3. enters `instant(pageA, ...)`;
4. asserts B's cookie survives inside the callback;
5. asserts B's cookie survives final release;
6. removes only its synthetic B cookie in `finally` so later tests cannot be contaminated.

The regression intentionally does not assert that simultaneous same-context scopes across different origins are supported.

## Public reproduction execution

Public reproduction:

https://github.com/teamleaderleo/playground/tree/repro/next-playwright-origin-cookie/next-playwright-origin-cookie-repro

Human-executed environment:

```text
Node.js: v22.23.1
@next/playwright: 16.3.1-canary.8
Playwright: 1.61.1
```

Observed failure:

```text
AssertionError: app B cookie was removed by instant() for app A
actual:   undefined
expected: '[1,"app-b",null]'
```

This is direct package-level reproduction against current canary and is recorded as `public-repro-executed`.

## Evidence available

- current upstream helper source mapped at exact commit;
- dependency-free selection model;
- real Playwright/Chromium unfiltered lookup/deletion control;
- real Playwright/Chromium URL-filtered preservation control;
- parent-domain applicability control;
- human-executed public current-canary reproduction;
- one-commit/two-file candidate;
- regression in the existing Instant Navigation suite.

Evidence classes:

- `source-read`
- `model-executed`
- `integration-executed`
- `public-repro-executed`
- `target-test-prepared`

No `target-executed` claim is made yet.

## Target-native verification still pending

The remaining verification is the existing Next.js suite in repository-declared modes, especially:

```sh
pnpm build-all
pnpm test-dev-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
pnpm test-start-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

At the first read-only check after the human filed PR #96962, GitHub created `build-and-test`, `build-and-deploy`, and stats runs, but they reached `action_required` before jobs were created. This is not a target-native test result and is not classified as a code failure.

## Filed PR structure

The human-written PR body uses a minimal shape:

### What

Change cleanup selection from `context.cookies()` to `context.cookies(scopeURL)` so release only expires Instant-cookie entries applicable to the application URL being controlled.

### Why

One app's `instant()` call can otherwise delete another origin's same-named testing cookie in the same BrowserContext.

### Tests

A regression in the existing Instant Navigation suite verifies that the other origin's testing cookie survives both entering and leaving the scope.

Related issue: `Fixes #96961`.

## Claims intentionally avoided

- no security-fix claim;
- no claim that same-context concurrent `instant()` scopes are supported;
- no cookie-protocol rewrite;
- no replacement of the individual-expiry race repair;
- no target-native pass claim before target execution exists.

## Upstream interaction boundary

Third-party upstream repositories are permanently read-only to Fieldwork automation. The upstream issue and PR were created manually by the human owner. This packet records their technical basis and state only.
