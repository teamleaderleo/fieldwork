# Instant cookie cleanup scope — intent audit (2026-08-08)

## Question

Is `@next/playwright` intentionally supposed to delete every `next-instant-navigation-testing` cookie in a Playwright `BrowserContext`, including entries for unrelated origins, or did that breadth arise as an implementation side effect?

## Current conclusion

The evidence favors **application/origin-local cookie ownership**, while **active `instant()` coordination is separately BrowserContext-wide**. The current context-wide cleanup is therefore plausible as an inherited implementation side effect rather than a clearly established cross-origin contract. This is still not explicit enough to treat the contract as settled without maintainer confirmation.

## Evidence

1. Original MPA lock implementation used `document.cookie` to set and clear the testing cookie. Both operations were necessarily current-origin/current-path scoped. See https://redirect.github.com/vercel/next.js/pull/89469.
2. The cookie-as-sole-protocol refactor described the external test framework as setting/clearing the cookie and the page reacting through CookieStore. Browser runtime state is per page/origin. See https://redirect.github.com/vercel/next.js/pull/89871.
3. The initial `@next/playwright` package implementation again used `page.evaluate(... document.cookie ...)` for both acquisition and release. Its README still presents that origin-local protocol as the reference implementation for other frameworks/devtools. See https://redirect.github.com/vercel/next.js/pull/90470.
4. Fresh-page support then moved acquisition to Playwright `BrowserContext.addCookies()` because no document origin exists before first navigation. That same change replaced release with context-level `clearCookies({ name })`, broadening cleanup. The PR motivation was fresh-page setup, not cross-origin ownership. See https://redirect.github.com/vercel/next.js/pull/90613.
5. PR 94947 replaced filtered `clearCookies` with individual expiry to avoid the transient whole-cookie-jar empty window. It preserved the prior same-name selection behavior; it did not revisit unrelated-origin ownership. See https://redirect.github.com/vercel/next.js/pull/94947.
6. PR 95375 introduced BrowserContext-wide `WeakSet` tracking for **active `instant()` calls** and reused the existing cleanup helper for stale-cookie recovery. Its wording says the cookie is context-scoped, but this is not literally how browser cookie visibility works across unrelated origins. See https://redirect.github.com/vercel/next.js/pull/95375.
7. Current runtime consumers are origin-local: the server sees the cookie only when that origin receives it; `navigation-testing-lock.ts` reads/writes/deletes via document/CookieStore; server recovery emits a Path=/ deletion for the current host; DevTools toggles the cookie via `document.cookie` on the current page.

## How stale cookies would be handled under URL-local cleanup

A URL-local design does not proactively garbage-collect unrelated origins. Instead:

- the current `instant(A)` release deletes A-applicable entries and retries to defeat resurrection;
- A's browser-side delete handler defensively clears the current-origin entry;
- server recovery can clear A's entry on blocking-route failure;
- if a stale B entry exists, a future `instant(B)` pre-acquire cleanup removes B-applicable stale state before acquiring B;
- a stale B cookie left by an abnormal/external actor can still affect a normal later visit to B. The current context-wide sweep opportunistically fixes that, but doing so makes A responsible for state it did not create and can interrupt another tool/devtools capture on B.

## Key architectural observation

The helper currently forbids two simultaneous `instant()` calls in one BrowserContext, but one `instant()` scope does **not** actually span unrelated origins: acquisition sets a cookie only for the resolved application hostname. Cross-origin navigation during the same callback would not automatically place the lock cookie on the destination origin. Therefore BrowserContext-wide coordination does not by itself imply BrowserContext-wide cookie ownership.

## Candidate implications

- Keep PR #7 as a contract candidate, not yet an asserted fix.
- If maintainers confirm per-app cleanup, add the regression to the existing Instant Navigation suite and use URL-filtered `context.cookies(scopeURL)`.
- If maintainers confirm context-wide cleanup, do not land the current candidate; instead document that unrelated same-name entries are intentionally invalidated and consider whether interaction with DevTools/other tools needs explicit tests/docs.
- A third design is possible: track origins touched by `@next/playwright` itself and clean only helper-owned origins, but current code has no such ownership registry and there is no evidence this complexity is required.
