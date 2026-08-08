# Next.js upstream issue technical packet

This is a fact packet for a **human-written** Next.js bug report. It is intentionally not a submit-ready issue description.

## Suggested issue title

`@next/playwright instant() clears same-named testing cookies for unrelated URLs`

## Why issue-first

The current Next.js bug-report template requires:

- a public minimal reproduction;
- reproduction steps;
- current versus expected behavior;
- environment information;
- affected area/stage selection;
- canary verification;
- human-authored issue text for external contributors.

The Next.js pull-request checklist for a bug fix also asks for a related issue and tests. Filing the issue first gives the eventual PR a canonical `Fixes #...` target and lets maintainers reject or clarify the intended cookie-ownership contract before reviewing a patch.

## Reproduction fact set

### Current upstream source

- Repository: `vercel/next.js`
- Current investigated upstream commit: `5e8f31f7bdf7f564ec98a42e205f7e5b665398da` (2026-08-07)
- Helper path: `packages/next-playwright/src/index.ts`
- Helper blob at that commit: `291afa9ef0c7b215318b36feb71af688d95f5373`
- Source: https://redirect.github.com/vercel/next.js/blob/5e8f31f7bdf7f564ec98a42e205f7e5b665398da/packages/next-playwright/src/index.ts

### Minimal mechanism

`instant(pageA, ...)` resolves one application URL and acquires `next-instant-navigation-testing` for that URL's hostname.

Before acquisition and again during release, current `releaseInstantCookie(context)` does:

```ts
const instantCookies = (await context.cookies()).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

Because `context.cookies()` is unfiltered, the selected set may include same-named cookies for other URLs/domains stored in the same Playwright `BrowserContext`.

The helper then expires every selected domain/path entry individually.

### Real Playwright/Chromium control

Retained Fieldwork artifact: `playwright-cookie-scope-browser.json`.

Environment used:

- Playwright Core `1.57.0-beta-1764944708000`
- Chromium `144.0.7559.96`

Seeded cookie jar:

```text
app-a.example / next-instant-navigation-testing
app-b.example / next-instant-navigation-testing
app-a.example / session
app-b.example / session
```

Observed with unfiltered `context.cookies()` + current expiry selection:

```text
selected instant-cookie domains: app-a.example, app-b.example
after expiry: no instant cookies remain
session cookies on A and B remain
```

Observed with `context.cookies('https://app-a.example/')`:

```text
returned cookie domain: app-a.example
selected instant-cookie domain: app-a.example
after expiry: app-b.example instant cookie remains
session cookies on A and B remain
```

This establishes the Playwright-side cookie-selection/deletion behavior. It does not by itself claim a Next.js rendering failure.

## Human reproduction to prepare

Use a public repository derived from the Next.js reproduction template or another minimal public project accepted by the issue form.

The reproduction should:

1. use a current canary containing `@next/playwright`;
2. create one Playwright `BrowserContext`;
3. load or otherwise establish app A as the page controlled by `instant()`;
4. seed `next-instant-navigation-testing` for a B-only domain in the same context;
5. call `instant(pageA, ...)`;
6. inspect the cookie jar inside the callback and after release;
7. show that B's cookie disappears on current source;
8. include unrelated session cookies as a negative control.

The cleanest expected assertion is:

```text
A's instant scope may mutate/delete cookies applicable to A.
A's instant scope should preserve a B-only instant-navigation cookie.
Unrelated cookie names should remain preserved.
```

## Current versus expected behavior facts

### Current

The helper acquires the control cookie for one hostname, but cleanup selects same-named cookies across the complete browser context and expires all of them.

### Expected candidate contract

Cleanup should select only instant-navigation cookie entries applicable to the resolved application URL. Normal cookie applicability rules should remain authoritative: a parent-domain cookie that applies to A is still in scope; a B-only cookie is outside it.

## Likely issue-form selections

- Affected areas: `Testing`, `Cookies`, optionally `Linking and Navigating`
- Affected stage: choose only stages actually reproduced by the final public reproduction. Do not infer this from source-only evidence.

## Environment information to capture from the final reproduction

Run the issue template's requested `next info` command from the public reproduction and paste the exact output. Also record:

- Playwright / `@playwright/test` version;
- browser/version used;
- exact Next.js canary version or commit;
- whether the result reproduces in dev, start, or both.

## History useful for Additional context

### Fresh-page support

PR 90613 moved `instant()` cookie writes from page-local `document.cookie` to Playwright's BrowserContext cookie API so the cookie could be established before the first navigation. Acquisition remained scoped to the resolved hostname.

Source: https://redirect.github.com/vercel/next.js/pull/90613

### Whole-cookie-jar race repair

PR 94947 stopped using Playwright's filtered `clearCookies({ name })` because Playwright implemented that path by temporarily clearing the whole jar and restoring non-matching cookies. Next.js could react to the deletion during that empty interval and render without application cookies.

The replacement preserved unrelated cookie **names** by reading cookies and individually expiring matching entries. It retained context-wide same-name selection.

Source: https://redirect.github.com/vercel/next.js/pull/94947

### Stale-cookie recovery

PR 95375 added BrowserContext-keyed active-scope tracking and repeated re-read/re-delete cleanup to recover from instant cookies resurrected by an MPA/cookieStore race. That protection should remain intact.

Source: https://redirect.github.com/vercel/next.js/pull/95375

## Overlap search

No direct upstream issue or PR specifically covering the B-only cross-URL cleanup case was found during the 2026-08-08 reconnaissance. PR 95375 is the closest ownership precedent but addresses stale-cookie recovery and concurrent-scope tracking rather than URL-filtered cleanup.

## Claims to avoid in the human issue unless separately demonstrated

- Do not call this a security vulnerability.
- Do not claim production-user impact.
- Do not claim distinct-origin concurrent `instant()` scopes should be allowed; that is a separate contract question.
- Do not claim the issue is fixed until the target-native regression passes on the candidate.

## Upstream interaction boundary

Fieldwork has not opened or commented on any upstream Next.js issue, discussion, or pull request. External interaction remains human-controlled.