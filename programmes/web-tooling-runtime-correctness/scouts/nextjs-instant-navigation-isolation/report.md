## In simple words

Does Next.js's experimental `@next/playwright` `instant()` helper erase navigation-testing state that belongs to another origin in the same Playwright `BrowserContext`?

Yes. `instant()` acquires `next-instant-navigation-testing` for one application hostname, while the current release path asks Playwright for the complete browser-context cookie jar and expires every entry with that name. Real Playwright + Chromium controls and the public package-level reproduction both distinguish the behavior.

The repair is narrow: retain the resolved application URL and use Playwright's URL-filtered `context.cookies(scopeURL)` lookup during stale cleanup and release. BrowserContext-wide active-call coordination remains unchanged.

The research phase is complete. A human filed the upstream issue and pull request back-to-back on 2026-08-08. Remaining Next.js CI is verification of the prepared patch, not a missing research branch.

## Current conclusion

The ordinary lifecycle is naturally symmetric:

```text
acquire: app A
release: cookies applicable to app A
```

The current implementation instead behaves like:

```text
acquire: app A
release: every same-named cookie in BrowserContext
```

Playwright already exposes the required distinction:

```text
context.cookies()     -> complete BrowserContext cookie jar
context.cookies(url)  -> cookies that affect that URL
```

`instant(page, ...)` controls one resolved application URL. Normal release should therefore undo state applicable to that URL.

If Next.js ever wants an operation that deliberately purges every Instant Navigation testing cookie in a BrowserContext, that is a different abstraction: an explicit context-wide reset/garbage-collection operation. It should not be an incidental side effect of releasing one application-scoped `instant()` call.

This conclusion does not require a claim about the original author's intent. The broad cleanup plausibly arose when the implementation moved from page-local cookie APIs to BrowserContext APIs for fresh-page support and used the unfiltered cookie lookup, but the public argument only needs the present ownership mismatch and Playwright's existing URL filter.

## Exact current source and candidate

- upstream canary pin: `a677cf66af002fbdcf49a982ef435b03554817cc` / 2026-08-08
- helper blob at base: `291afa9ef0c7b215318b36feb71af688d95f5373`
- existing test-suite base blob: `3c06a831e7c40336b67d55e66c75f991bbafb832`
- owned candidate branch: `teamleaderleo/next.js:fieldwork/instant-navigation-origin-scoped-release-current`
- squashed candidate head: `a33d51d10d212ae656a0c94a28ffe51a6e43879b`
- owned-fork review PR: https://github.com/teamleaderleo/next.js/pull/9

The candidate is exactly one commit ahead of the pinned base and changes two files:

```text
packages/next-playwright/src/index.ts
  +32 / -42

test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
  +42 / -0
```

Implementation properties:

- public `instant()` signature unchanged;
- BrowserContext-wide active-scope exclusion unchanged;
- normal cleanup selection changed to `context.cookies(scopeURL)`;
- existing individual-expiry behavior preserved;
- existing bounded retry/re-delete behavior preserved;
- regression added beside stale-cookie and separate-BrowserContext coverage;
- regression removes its synthetic other-origin cookie in `finally` so it cannot contaminate later tests;
- ownership comments were corrected so they no longer describe the cookie itself as BrowserContext-scoped.

## Public reproduction execution

Public reproduction:

https://github.com/teamleaderleo/playground/tree/repro/next-playwright-origin-cookie/next-playwright-origin-cookie-repro

The owner executed the exact public reproduction locally on 2026-08-08 with:

```text
Node.js: v22.23.1
@next/playwright: 16.3.1-canary.8
Playwright: 1.61.1
```

`npm test` failed at the intended distinguishing assertion:

```text
AssertionError: app B cookie was removed by instant() for app A
actual:   undefined
expected: '[1,"app-b",null]'
```

This upgrades the retained evidence beyond the earlier lower-level browser controls: the public reproduction against the published current-canary package reproduces the issue directly.

It still does **not** constitute `target-executed` evidence for the patched Next.js repository suite.

## Human upstream interaction

These interactions were performed manually by the human owner, outside Fieldwork automation:

- upstream issue: https://redirect.github.com/vercel/next.js/issues/96961
- upstream pull request: https://redirect.github.com/vercel/next.js/pull/96962

The filed issue is deliberately concise: public reproduction, exact failure, current vs. expected behavior, and environment. The filed PR links the issue with `Fixes #96961` and explains the URL-filtered cleanup in a minimal What/Why/Tests form.

At the first post-filing check, PR #96962 was open, mergeable, one commit, and two changed files. GitHub created `build-and-test`, `build-and-deploy`, and stats workflow runs, but they ended in `action_required` before jobs were created. The likely explanation is the normal approval gate for workflows from a fork; that is an inference, not a test failure.

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
- `public-repro-executed`
- `target-test-prepared`

No `target-executed` claim is made yet.

## History and limits

History established useful constraints:

- acquisition moved to BrowserContext APIs to support first navigation;
- individual expiry exists to avoid Playwright's historical filtered-clear empty-jar race;
- stale-cookie recovery and bounded re-delete behavior must remain intact;
- active-scope exclusion is BrowserContext-wide and remains a separate coordination rule.

Those findings constrain the patch but do not need to carry the public argument.

Unmeasured/remaining:

- frequency of multi-origin same-context use in real test suites;
- target-native Next.js suite execution on the current candidate;
- maintainer review/contract feedback;
- whether maintainers ever want an explicit context-wide Instant-cookie reset operation separate from normal release.

## Current disposition

`research-complete — upstream-open — verification/review pending`

The stop condition is met. The ownership rule is established with current source, lower-level executable controls, a real public reproduction, a focused candidate, and a regression test. Further work is reactive: target-native CI and maintainer review may confirm the patch or reveal a product-semantic contradiction worth reopening.

Third-party upstream repositories remain permanently read-only to Fieldwork automation. The upstream issue and pull request were human-created; Fieldwork only records and monitors their state.
