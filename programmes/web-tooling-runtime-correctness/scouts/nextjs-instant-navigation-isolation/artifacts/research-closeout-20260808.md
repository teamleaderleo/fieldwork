## In simple words

The research phase is complete. The public reproduction has now been executed successfully as a distinguishing failure, and the human owner filed the upstream issue and pull request back-to-back on 2026-08-08.

Remaining Next.js CI is verification of the prepared patch, not a missing research branch.

## Research conclusion

The current helper acquires `next-instant-navigation-testing` for one application hostname but releases by enumerating every same-named cookie in the Playwright BrowserContext.

The strongest repair is to scope normal release to the resolved application URL via Playwright's URL-filtered cookie lookup. This keeps Playwright's native domain/path applicability semantics, including parent-domain cookies that genuinely affect the app URL, while preserving same-named cookies that do not apply to that URL.

The BrowserContext-wide active-scope exclusion remains a separate coordination rule and is unchanged by the candidate.

A useful way to state the ownership model is:

```text
acquire: app A
release: cookies applicable to app A
```

The existing implementation broadens the second line to every same-named cookie in the context. The candidate restores symmetry.

## Separate context-wide reset question

A deliberate operation that means “purge every Instant Navigation testing cookie from this BrowserContext” could be valid as a separate reset/garbage-collection primitive.

That is not the same operation as releasing one `instant(pageA, ...)` scope. Normal release should not use a context-wide purge as an incidental substitute for application-scoped cleanup.

This distinction also avoids overclaiming concurrency support: the candidate does not change the one-active-`instant()`-call-per-BrowserContext rule.

## Why further archaeology is not required

History was useful to establish how the broad cleanup arose and to identify the stale-cookie, individual-expiry, retry, and active-scope constraints that the candidate must preserve. It does not need to carry the public argument.

The current design argument is sufficient on its own:

- `context.cookies()` asks for the complete BrowserContext cookie jar;
- `context.cookies(url)` asks for cookies that affect one URL;
- `instant(page, ...)` controls one resolved application URL;
- normal release therefore has a natural URL-scoped selection primitive;
- a context-wide reset, if desired, is a distinct operation.

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

This is direct execution of the public package-level reproduction against current canary. It is recorded as `public-repro-executed`, not as patched Next.js `target-executed` evidence.

## Human upstream filing

The human owner created:

- issue: https://redirect.github.com/vercel/next.js/issues/96961
- pull request: https://redirect.github.com/vercel/next.js/pull/96962

The PR uses the squashed candidate commit `a33d51d10d212ae656a0c94a28ffe51a6e43879b`, based directly on upstream canary `a677cf66af002fbdcf49a982ef435b03554817cc`.

At the first check after filing, the PR was open, mergeable, one commit, and two changed files. Its GitHub workflow runs were created but reached `action_required` before any jobs appeared; this is not recorded as a code/test failure.

## Evidence retained

- current-canary source map;
- dependency-free selection model;
- real Playwright/Chromium cross-origin cookie control;
- parent-domain applicability control;
- human-executed public package-level reproduction;
- current-canary one-commit/two-file owned-fork candidate;
- regression in the existing Instant Navigation suite;
- human-filed upstream issue and PR.

Evidence classes:

- `source-read`
- `model-executed`
- `integration-executed`
- `public-repro-executed`
- `target-test-prepared`

## Remaining gate

Target-native Next.js execution is still pending. No `target-executed` claim should be made until the existing suite runs on the current candidate.

If target-native CI later reveals a product-semantic contradiction, reopen the analysis. Infrastructure/setup gating should be classified separately and should not automatically weaken the ownership conclusion.

Automated third-party upstream contact remains prohibited. The upstream filing was a manual human action; Fieldwork may record and monitor it but never mutate it.
