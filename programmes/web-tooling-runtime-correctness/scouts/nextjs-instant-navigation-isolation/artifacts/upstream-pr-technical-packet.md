# Next.js upstream pull-request technical packet

This is a fact packet for a **human-written** external pull-request description. It is intentionally not a submit-ready PR description.

## Suggested PR title

`fix(next-playwright): scope instant cookie cleanup to app URL`

## Intended sequencing

Open the human-written bug report first, then open the upstream pull request and reference it with `Fixes #<issue>`.

If the real upstream PR is opened immediately after the issue, the issue body does not need to link the owned-fork review PR; GitHub will connect the upstream PR through `Fixes #<issue>`.

## Exact candidate

- Owned fork: `teamleaderleo/next.js`
- Canonical owned-fork review PR: `#9`
- Branch: `fieldwork/instant-navigation-origin-scoped-release-current`
- Current head: `6780339f9b3eec5de43cb26a368ec4a8d3b405cb`
- Exact public upstream base: `a677cf66af002fbdcf49a982ef435b03554817cc`
- Changed files:
  - `packages/next-playwright/src/index.ts`
  - `test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

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

The helper's local structural BrowserContext interface is expanded to match Playwright's existing optional URL filter:

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

This delegates domain/path/secure applicability to Playwright. A parent-domain cookie that genuinely applies to app A remains eligible; a B-only cookie does not.

If Next.js ever needs a context-wide reset or garbage-collection operation, that can be represented separately rather than conflated with normal release of one `instant()` scope.

## Behavior intentionally left unchanged

- one active `instant()` scope per Playwright `BrowserContext`;
- `WeakSet<BrowserContext>` active-scope tracking;
- hostname-scoped cookie acquisition;
- pre-acquire stale-cookie cleanup for entries applicable to the selected application URL;
- repeated re-read/re-delete loop for resurrected cookies;
- individual expiry of matching cookie entries;
- avoidance of Playwright's historical filtered `clearCookies` path;
- unrelated cookie-name preservation.

## Source-comment review

The source comments are intentionally narrow:

- active-call tracking is described as BrowserContext-wide without claiming that the cookie itself is BrowserContext-scoped;
- stale cleanup is described in terms of the current application URL;
- `releaseInstantCookie` documents that it deletes matching entries applicable to that URL;
- historical cleanup details are retained only where they explain the individual-expiry and retry invariants.

No additional comment archaeology is needed in the product patch.

## Regression placement and coverage

The regression is folded into the existing suite:

`test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`

It is placed immediately after the same-origin stale-cookie recovery case and before the separate-BrowserContext concurrency case.

The test:

1. opens the existing fixture page;
2. seeds a `next-instant-navigation-testing` cookie for a B-only domain in the same native Playwright context;
3. enters `instant(pageA, ...)`;
4. asserts B's cookie survives inside the callback;
5. asserts B's cookie survives final release;
6. removes only its synthetic B cookie in `finally` so later tests cannot be contaminated.

Existing suite coverage separately verifies normal same-origin cookie release and stale-cookie recovery. The regression intentionally does not assert that simultaneous same-context scopes across different origins are supported.

## Evidence already available

- current upstream helper source mapped at exact commit;
- real Playwright/Chromium confirms unfiltered lookup/deletion reaches B-only cookies;
- real Playwright/Chromium confirms URL-filtered lookup preserves B-only cookies;
- an additional browser applicability control confirms a parent-domain cookie that genuinely applies to app A remains selected while a B-only cookie is excluded;
- deterministic model and source replay reproduce the current selection behavior;
- no direct overlap found for this exact cross-origin cleanup case.

Evidence classes: `source-read`, `model-executed`, `integration-executed`, `target-test-prepared`.

No `target-executed` claim is made yet.

## Target-native verification still pending

When CI capacity is available, the remaining verification is the existing Next.js suite in repository-declared modes, especially:

```sh
pnpm build-all
pnpm test-dev-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
pnpm test-start-turbo test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
```

The absence of this receipt is a verification gap, not an unresolved research branch.

## PR checklist mapping

### What

Narrow Instant Navigation testing-cookie cleanup to entries applicable to the resolved application URL.

### Why

Current cleanup owns a broader cookie set than acquisition: one app's `instant()` scope can expire a same-named testing cookie that applies only to another URL in the same BrowserContext.

### How

Thread the existing resolved application URL into `releaseInstantCookie` and use Playwright's URL-filtered `BrowserContext.cookies(scopeURL)` query before individually expiring matching entries.

### Related issue

`Fixes #<human-filed issue>`

### Tests

A regression is present in the existing Instant Navigation suite for B-only cookie preservation. Existing cleanup/stale-cookie tests remain in place. Do not claim target-native pass results until they exist.

## Submission mechanics

The current Next.js pull-request template requires external contributor PR descriptions to be written by the human contributor. It also asks bug-fix PRs to link the related issue using `Fixes #number`, include tests, and use verified commit signatures.

Opening a PR triggers repository CI on the `opened` event, including draft PRs, and the repository has an automatic file-based PR labeler. No repository CODEOWNERS assignment is configured for this path, and no repository workflow was found that automatically assigns a human reviewer on open.

A reasonable human sequence is therefore:

1. file the human-written issue;
2. open the upstream PR immediately afterward as a draft with `Fixes #<issue>`;
3. let CI queue while the PR is visibly not yet marked ready for human review;
4. after verification is satisfactory, the human may mark it ready for review.

## Claims to avoid

- Do not claim a security fix.
- Do not broaden the PR into concurrent-scope ownership.
- Do not rewrite the cookie protocol.
- Do not replace the individual-expiry race repair.
- Do not state target-native pass results until they exist.

## Upstream interaction boundary

This packet and owned-fork PR are preparation/review surfaces only. Third-party upstream repositories are read-only to Fieldwork automation. Any upstream issue or PR must be created and managed manually by a human.
