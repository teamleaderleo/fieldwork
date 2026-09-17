# Intent audit — instant cookie cleanup ownership

Date: 2026-08-08

## Finding

The cross-origin deletion behavior is real, but the intended ownership contract is not settled enough to call it an unambiguous bug yet.

Current canary still scopes acquisition to the resolved application hostname, while `releaseInstantCookie(context)` selects every same-named cookie returned by unfiltered `context.cookies()`.

Historical evidence cuts both ways:

- PR 90613 moved acquisition to BrowserContext cookies specifically so the cookie could be installed before first navigation, but still scoped acquisition to the resolved hostname.
- PR 94947 intentionally replaced filtered `clearCookies({ name })` with individual expiry. Its prior cleanup comment explicitly described clearing the cookie regardless of which domain variant it was stored under.
- PR 95375 intentionally made active-scope ownership BrowserContext-wide and described the context as the natural granularity because same-context scopes share one conceptual instant-navigation lock.
- The current `@next/playwright` README describes the mechanism as a single cookie and shows `document.cookie` set/clear semantics, which are origin-applicable in the current document. DevTools likewise observes the cookie through `document.cookie` / CookieStore in the current page.

## Interpretation

A B-only `next-instant-navigation-testing` cookie in the same BrowserContext is not necessarily legitimate independent active state under the current helper contract: simultaneous same-context `instant()` scopes are rejected. If such a B cookie is residue from an earlier scope, clearing it before entering A may be intentional stale-state cleanup. Narrowing cleanup to A's URL would preserve that B residue and could leave B unexpectedly locked on a later visit.

Conversely, the browser cookie itself is domain/path scoped, and current-page consumers only observe the cookie applicable to their own URL. So context-wide deletion reaches state that the controlled app cannot itself observe. A multi-origin BrowserContext or another actor can therefore lose same-named state outside A's URL.

## Disposition

Do not treat the URL-scoped patch as contract-proven yet. Keep the issue framed as a factual behavior report plus proposed expectation ("I think cleanup should..."). Hold the upstream PR until maintainers confirm whether `instant()` owns all same-named cookie state in a BrowserContext or only entries applicable to its resolved application URL.

The candidate patch remains useful as a concrete alternative, but adding a regression that asserts B-cookie preservation would encode the unresolved contract rather than merely characterize current behavior.

No upstream contact performed.