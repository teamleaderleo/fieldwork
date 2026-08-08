## In simple words

Does Next.js's experimental `@next/playwright` `instant()` helper erase navigation-testing state that belongs to another origin in the same Playwright `BrowserContext`?

Yes at the helper/Playwright interface boundary currently mapped. `instant()` acquires `next-instant-navigation-testing` for one hostname, while `releaseInstantCookie(context)` asks Playwright for the complete browser-context cookie jar and expires every entry with that name. Real Playwright + Chromium execution confirms that an unfiltered cookie query returns same-named entries from unrelated domains and that the current expiry pattern deletes them while preserving unrelated cookie names.

Current upstream canary still carries the same helper implementation. The current owned-fork candidate changes release lookup to `context.cookies(scopeURL)`, preserving the existing BrowserContext-wide active-scope rule. Real Playwright execution confirms the URL-filtered query selects only cookies applicable to that application URL, including parent-domain cookies that genuinely apply, while preserving testing cookies that apply only to another origin.

The research phase is complete enough for owner review and human filing. Remaining Next.js CI is verification of the prepared candidate, not a missing research branch. No target-executed claim is made yet.

## Current conclusion

The strongest design is to keep ordinary `instant()` release scoped to the application URL that the call resolved.

Playwright already exposes the distinction directly:

```text
context.cookies()     -> complete BrowserContext cookie jar
context.cookies(url)  -> cookies that affect that URL
```

`instant(page, ...)` controls one resolved application URL. Its normal release therefore has a natural URL-scoped selection primitive. If Next.js ever needs a separate context-wide reset/garbage-collection operation, that can be represented separately rather than conflated with ordinary scope release.

This argument does not depend on proving the exact historical intent of every intermediate implementation.

## Exact current source

- upstream canary pin: `a677cf66af002fbdcf49a982ef435b03554817cc` / 2026-08-08
- helper blob: `291afa9ef0c7b215318b36feb71af688d95f5373`
- existing test-suite base blob: `3c06a831e7c40336b67d55e66c75f991bbafb832`

## Canonical candidate

Owned-fork review PR: `teamleaderleo/next.js` #9

- base: `a677cf66af002fbdcf49a982ef435b03554817cc`
- branch: `fieldwork/instant-navigation-origin-scoped-release-current`
- changed files: `packages/next-playwright/src/index.ts` and the existing Instant Navigation e2e suite
- public `instant()` signature unchanged
- BrowserContext-wide active-scope exclusion unchanged
- normal cleanup selection changed to `context.cookies(scopeURL)`
- regression added beside stale-cookie and BrowserContext-isolation coverage
- regression cleans up its synthetic other-origin cookie in `finally` so it cannot contaminate later tests

## Evidence retained

- `artifacts/cookie-scope-probe.mjs`
- `artifacts/latest.json`
- `artifacts/current-helper-source-replay.json`
- `artifacts/playwright-cookie-scope-browser.json`
- `artifacts/origin-scoped-release-candidate.json`
- `artifacts/playwright-cookie-applicability-browser.json`
- `artifacts/current-canary-candidate-20260808.md`
- `artifacts/research-closeout-20260808.md`
- public minimal reproduction in `teamleaderleo/playground`

Evidence classes:

- `source-read`
- `model-executed`
- `integration-executed`
- `target-test-prepared`

No `target-executed` claim is made yet.

## History and limits

History established useful constraints:

- acquisition moved to BrowserContext APIs to support first navigation;
- the individual-expiry logic exists to avoid Playwright's historical filtered-clear empty-jar race;
- stale-cookie recovery and bounded re-delete behavior must remain intact;
- active-scope exclusion is intentionally BrowserContext-wide and remains a separate question.

Those findings constrain the patch but do not need to carry the public argument.

Unmeasured/remaining:

- frequency of multi-origin same-context use;
- target-native Next.js suite execution on the current candidate;
- maintainer contract decision, if maintainers intentionally want a separate context-wide reset operation.

## Current disposition

`research-complete — verification pending`

The research avenues needed to make the issue and candidate technically informed have been exhausted. The next technical transition is target-native verification when CI capacity is available, followed by owner review of the prepared human-facing issue/PR material.

Third-party upstream repositories are permanently read-only to Fieldwork automation. Any eventual upstream interaction must be performed manually by a human.
