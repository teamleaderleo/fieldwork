# Human draft scaffold — Next.js pull request

Suggested title:

`fix(next-playwright): scope instant cookie cleanup to app URL`

> Next.js requires the final external PR description to be human-written. This scaffold supplies the verified technical content. Replace each `YOUR WORDS` block with your own wording before opening the upstream PR.

## What?

Verified candidate facts:

- `instant()` already resolves one application URL before acquiring its testing cookie.
- the candidate retains that full URL as `scopeURL`;
- both pre-acquire stale cleanup and final release receive `scopeURL`;
- `releaseInstantCookie` changes from unfiltered `context.cookies()` to `context.cookies(scopeURL)`;
- individual cookie expiry remains unchanged;
- BrowserContext-wide active-scope exclusion remains unchanged.

Core code change:

```ts
const scopeURL = resolveURL(page, options)
const { hostname } = new URL(scopeURL)

await releaseInstantCookie(context, scopeURL)
```

and:

```ts
const instantCookies = (await context.cookies(scopeURL)).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

`YOUR WORDS:` Summarize the code change in 1–3 sentences.

## Why?

Verified current behavior:

```text
instant(app A)
  -> acquires testing cookie for A's hostname
  -> cleanup calls context.cookies()
  -> selects all cookies with the testing-cookie name
  -> can expire a B-only testing cookie stored in the same BrowserContext
```

Real Playwright Core + Chromium execution confirmed that unfiltered BrowserContext lookup returns same-named entries from unrelated domains and that individually expiring the selected entries removes both while leaving unrelated cookie names intact.

URL-filtered `context.cookies(scopeURL)` returned only cookies applicable to the requested URL and preserved the B-only testing cookie.

`YOUR WORDS:` Explain why cleanup ownership should match the application URL controlled by the helper.

## How?

The candidate delegates cookie applicability to Playwright rather than implementing domain/path matching itself.

This preserves normal browser cookie semantics:

- a parent-domain cookie that genuinely applies to app A stays in the cleanup set;
- a B-only cookie does not;
- path/secure applicability remains Playwright's responsibility.

Existing protections intentionally remain:

- hostname-scoped acquisition;
- pre-acquire stale-cookie cleanup;
- repeated read/delete loop for cookie resurrection races;
- individual expiry rather than filtered `clearCookies`;
- BrowserContext-wide active-scope tracking;
- unrelated cookie-name preservation.

`YOUR WORDS:` Describe why this is narrower than changing the cookie protocol or concurrency policy.

## Related issue

`Fixes #<human-filed issue number>`

Issue should be filed first once the public reproduction is verified on current canary.

## Tests

The regression belongs in the existing suite:

`test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

Required regression assertions:

1. use the existing Next.js fixture page;
2. seed a B-only `next-instant-navigation-testing` cookie in the same native Playwright BrowserContext;
3. optionally seed unrelated session cookies as negative controls;
4. enter `instant(pageA, ...)`;
5. assert B's cookie still exists inside the callback;
6. assert B's cookie still exists after release;
7. assert A's instant cookie is absent after release;
8. retain and pass the existing stale-cookie recovery test.

Target-native execution to capture on the final candidate head:

```sh
pnpm build-all
pnpm test-dev-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
pnpm test-start-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

Run the package-relevant type/build checks required by current repository guidance as well.

`YOUR WORDS:` Report only the commands and results you actually ran.

## Relevant history

- [PR 90613](https://redirect.github.com/vercel/next.js/pull/90613): BrowserContext-based acquisition for fresh-page loads.
- [PR 94947](https://redirect.github.com/vercel/next.js/pull/94947): individual expiry to avoid the filtered-`clearCookies` whole-jar race.
- [PR 95375](https://redirect.github.com/vercel/next.js/pull/95375): BrowserContext-keyed active-scope tracking and repeated stale-cookie cleanup.

This change preserves the protections added by all three and narrows only the cookie lookup used by cleanup.

## Candidate source

Internal fork review surface:

- branch: `fieldwork/instant-navigation-origin-scoped-release`
- exact public upstream base: `5e8f31f7bdf7f564ec98a42e205f7e5b665398da`
- current reviewed source file: `packages/next-playwright/src/index.ts`

Before opening upstream, refresh the candidate onto the then-current canary and repeat the focused tests.

## Claims to avoid

- security fix;
- production-user impact unless independently reproduced;
- support for multiple simultaneous same-context `instant()` scopes;
- changing the Navigation Inspector protocol;
- claiming target-native success before the final executions exist.
