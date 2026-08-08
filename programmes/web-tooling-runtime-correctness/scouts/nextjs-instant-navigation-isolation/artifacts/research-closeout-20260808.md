## In simple words

The research phase is complete enough for owner review and human filing. The remaining Next.js CI work is verification of the prepared candidate, not a missing research branch.

## Research conclusion

The current helper acquires `next-instant-navigation-testing` for one application hostname but releases by enumerating every same-named cookie in the Playwright BrowserContext.

The strongest candidate is to scope normal release to the resolved application URL via Playwright's URL-filtered cookie lookup. This keeps Playwright's native domain/path applicability semantics, including parent-domain cookies that genuinely affect the app URL, while preserving same-named cookies that do not apply to that URL.

The BrowserContext-wide active-scope exclusion remains a separate design decision and is unchanged by the candidate.

## Why further archaeology is not required

History was useful to establish how the broad cleanup arose and to identify the stale-cookie and active-scope constraints that the candidate must preserve. It does not need to carry the public argument.

The current design argument is sufficient on its own:

- `context.cookies()` asks for the complete BrowserContext cookie jar;
- `context.cookies(url)` asks for cookies that affect one URL;
- `instant(page, ...)` controls one resolved application URL;
- normal release therefore has a natural URL-scoped selection primitive;
- if a separate context-wide reset is ever required, that is a distinct operation and need not be conflated with ordinary scope release.

## Evidence retained

- current-canary source map;
- dependency-free selection model;
- real Playwright/Chromium cross-origin cookie control;
- parent-domain applicability control;
- minimal public reproduction;
- current-canary two-file owned-fork candidate;
- regression in the existing Instant Navigation suite.

## Remaining gate

Target-native Next.js execution is still pending. No `target-executed` claim should be made until the existing suite runs on the current candidate.

Automated third-party upstream contact is prohibited. Any filing or submission is a manual human action.
