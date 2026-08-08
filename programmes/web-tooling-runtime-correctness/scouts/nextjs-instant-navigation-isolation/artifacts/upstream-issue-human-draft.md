# Human draft scaffold — Next.js bug issue

Suggested title:

`@next/playwright instant() clears same-named testing cookies for unrelated URLs`

> Next.js requires the final issue description from an external contributor to be human-written. This scaffold supplies the verified facts, ordering, commands, and evidence. Replace each `YOUR WORDS` block with your own wording before filing.

## Link to the code that reproduces this issue

`YOUR WORDS / LINK:` Add the public minimal reproduction URL once created and verified on current canary.

Reproduction requirements already established:

- current canary containing `@next/playwright`;
- one native Playwright `BrowserContext`;
- app A controlled by `instant()`;
- a B-only `next-instant-navigation-testing` cookie seeded in the same context;
- optional unrelated session cookies on A and B as negative controls;
- assert B's testing cookie inside `instant(pageA, ...)` and after release.

## To Reproduce

Use this factual sequence, but write the final prose yourself:

1. Start the public reproduction on current Next.js canary.
2. Open app A with Playwright and obtain its `BrowserContext`.
3. Add a cookie named `next-instant-navigation-testing` for a domain that does not apply to app A.
4. Confirm that cookie exists in the BrowserContext.
5. Call `instant(pageA, async () => { ... })`.
6. Inspect the BrowserContext cookie jar inside the callback.
7. Inspect it again after `instant()` returns.
8. Observe whether the B-only testing cookie survives.

`YOUR WORDS:` Briefly narrate those steps as something you personally ran.

## Current vs. Expected behavior

Verified current behavior:

- `instant()` resolves one application URL and acquires the testing cookie for that URL's hostname.
- Before acquisition and again at release, `releaseInstantCookie(context)` calls unfiltered `context.cookies()`.
- It filters only by cookie name and individually expires every matching domain/path entry.
- Real Playwright Core + Chromium execution confirms that unfiltered lookup can return same-named cookies from unrelated domains in one BrowserContext and that the current expiry pattern deletes both.

Expected contract supported by the candidate:

- cleanup should select testing-cookie entries applicable to the application URL controlled by this `instant()` call;
- a B-only cookie should survive A's scope;
- a parent-domain/path cookie that genuinely applies to A should remain eligible for cleanup;
- unrelated cookie names should remain untouched.

`YOUR WORDS:` State what you expected and what you observed in 2–4 sentences.

## Environment information

Run the issue template's requested `next info` command in the final reproduction and paste the exact output.

Also record:

- exact Next.js canary version/commit;
- `@playwright/test` version;
- browser/version;
- which modes reproduce: `next dev`, `next start`, or both.

Current research pin only:

- upstream commit: `5e8f31f7bdf7f564ec98a42e205f7e5b665398da` (2026-08-07)
- helper blob: `291afa9ef0c7b215318b36feb71af688d95f5373`

## Affected areas

Likely selections after the final reproduction confirms them:

- Testing
- Cookies
- Linking and Navigating (optional if the reproduction exercises navigation)

Choose only execution stages that the final reproduction actually demonstrates.

## Additional context

Useful history to mention in your own words:

- [PR 90613](https://redirect.github.com/vercel/next.js/pull/90613) moved acquisition from `document.cookie` to Playwright BrowserContext cookies so `instant()` can work before first navigation. Acquisition is scoped to the resolved hostname.
- [PR 94947](https://redirect.github.com/vercel/next.js/pull/94947) stopped using Playwright's filtered `clearCookies({ name })` because it temporarily emptied the entire cookie jar. The replacement individually expires matching entries, preserving unrelated cookie names but still selecting same-named entries context-wide.
- [PR 95375](https://redirect.github.com/vercel/next.js/pull/95375) added BrowserContext-keyed active-scope tracking and repeated cleanup for resurrected stale cookies. This report does not challenge that concurrency policy.

No direct upstream issue or PR covering this exact B-only cross-URL cleanup case was found during the 2026-08-08 overlap search.

`YOUR WORDS:` Explain why you think cleanup ownership should follow the application URL, and mention any final reproduction result.

## Claims to avoid

- security vulnerability;
- production-user impact unless separately demonstrated;
- claim that distinct-origin same-context concurrent `instant()` scopes should be allowed;
- claim that the bug is fixed before the target-native regression passes.
