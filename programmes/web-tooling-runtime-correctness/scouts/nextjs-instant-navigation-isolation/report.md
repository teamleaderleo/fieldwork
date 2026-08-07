## In simple words

Does Next.js's experimental `@next/playwright` `instant()` helper erase navigation-testing state that belongs to another origin in the same Playwright `BrowserContext`?

Yes at the helper/Playwright interface boundary currently mapped. `instant()` acquires `next-instant-navigation-testing` for one hostname, while `releaseInstantCookie(context)` asks Playwright for the complete browser-context cookie jar and expires every entry with that name. Real Playwright + Chromium execution confirms that an unfiltered cookie query returns same-named entries from two unrelated domains and that the current expiry pattern deletes both while preserving unrelated cookie names.

Current upstream canary still carries the same helper blob. A narrow candidate on the owned fork changes release lookup to `context.cookies(scopeURL)`, preserving the existing context-wide active-scope rule. Real Playwright execution confirms the URL-filtered query selects only cookies applicable to that application URL and preserves the other origin's testing cookie.

Evidence is `source-read` + `model-executed` + `integration-executed` + `target-test-prepared`. The exact-current Next.js e2e carrier is queued for target execution; no target-executed claim is made yet.

## Assignment

- Programme: `web-tooling-runtime-correctness` / issue #15
- Scout issue: #693
- Fieldwork PR: #694
- Worker: ChatGPT research assistant
- Owned path: `programmes/web-tooling-runtime-correctness/scouts/nextjs-instant-navigation-isolation/`
- Target: Next.js
- Historical preview pin: `v16.3.0-preview.9` / `838bd19bdef0e41254f0868516b0c6c6e59e70d7`
- Current upstream pin: `5e8f31f7bdf7f564ec98a42e205f7e5b665398da` / 2026-08-07
- Current helper blob: `291afa9ef0c7b215318b36feb71af688d95f5373`
- Retrieval date: `2026-08-08`
- Claim scope: `interface`
- Upstream contact authorized: `false`

## Question

When one Playwright `BrowserContext` contains cookies for several application origins, should `instant(pageA, ...)` remove a `next-instant-navigation-testing` cookie that belongs to app B?

Keep a related question separate: should two distinct origins in one browser context be allowed to hold concurrent `instant()` scopes?

```text
one BrowserContext
├── app-a.example ── instant(A) owns A's testing-cookie lifecycle
└── app-b.example ── B's testing cookie remains B's state

context-wide active-scope exclusion is a separate design decision
```

## Current source map

Current public source:

- [`@next/playwright` helper](https://redirect.github.com/vercel/next.js/blob/5e8f31f7bdf7f564ec98a42e205f7e5b665398da/packages/next-playwright/src/index.ts)
- [Instant Navigation Testing API suite](https://redirect.github.com/vercel/next.js/blob/5e8f31f7bdf7f564ec98a42e205f7e5b665398da/test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts)
- [client navigation-testing lock](https://redirect.github.com/vercel/next.js/blob/5e8f31f7bdf7f564ec98a42e205f7e5b665398da/packages/next/src/client/components/segment-cache/navigation-testing-lock.ts)
- [exact current upstream commit](https://redirect.github.com/vercel/next.js/commit/5e8f31f7bdf7f564ec98a42e205f7e5b665398da)

The helper blob at this current upstream commit is identical to the blob mapped from the 16.3 preview line.

### Acquisition

`instant()` resolves `baseURL` or `page.url()`, extracts one hostname, and creates the testing cookie for that hostname at path `/`.

```text
app A URL ──▶ hostname A ──▶ next-instant-navigation-testing @ A /
```

### Current release

Both pre-acquire stale cleanup and final release call the same helper:

```text
context.cookies()
  └── filter name === next-instant-navigation-testing
        ├── A / matching name ── expire
        └── B / matching name ── expire
```

No URL, hostname, domain, or acquired-cookie identity participates in selection.

### Active-scope ownership

A `WeakSet<BrowserContext>` rejects a second simultaneous `instant()` call in the same browser context. That remains a separate property from which cookie entries release is allowed to delete.

## History and competing contract evidence

[PR 90613](https://redirect.github.com/vercel/next.js/pull/90613) moved acquisition from page-local `document.cookie` to Playwright's BrowserContext API so the testing cookie could exist before a first navigation. It explicitly scopes acquisition with the resolved hostname.

[PR 94947](https://redirect.github.com/vercel/next.js/pull/94947) replaced Playwright's filtered `clearCookies` call after observing that Playwright temporarily cleared the whole jar and re-added non-matching cookies. The replacement individually expires matching entries and correctly preserves unrelated cookie names.

[PR 95375](https://redirect.github.com/vercel/next.js/pull/95375) later moved nesting detection into a `WeakSet<BrowserContext>` and deliberately made active-scope ownership context-wide. Its rationale says scopes in one context “share one cookie and genuinely conflict.” Real Playwright behavior shows a browser context can hold distinct same-named cookie entries for unrelated domains, so that rationale does not by itself establish that cleanup should delete every domain's entry.

An overlap search found no direct current issue or pull request addressing multi-origin same-context cleanup ownership.

## Evidence 1 — deterministic selection model

Artifacts:

- `artifacts/cookie-scope-probe.mjs`
- `artifacts/latest.json`

Command:

```sh
node programmes/web-tooling-runtime-correctness/scouts/nextjs-instant-navigation-isolation/artifacts/cookie-scope-probe.mjs
```

Environment: Node `v22.16.0`.

Observed:

| Property | Result |
| --- | --- |
| app B instant cookie survives app A acquire | `false` |
| unrelated app A cookie survives | `true` |
| unrelated app B cookie survives | `true` |
| app B instant cookie survives release | `false` |
| separate browser contexts can run concurrently | `true` |
| second scope in same context is rejected | `already active` |

Evidence class: `model-executed`.

## Evidence 2 — current helper control-flow replay

Artifact: `artifacts/current-helper-source-replay.json`.

Pinned inputs:

```text
upstream commit  5e8f31f7bdf7f564ec98a42e205f7e5b665398da
helper blob      291afa9ef0c7b215318b36feb71af688d95f5373
step blob        a0e46afaacf6645c16d51f8dbb039a5bd712243a
Node             v22.16.0
TypeScript       5.8.3
```

The current helper's operative `instant()` / `releaseInstantCookie` path was compiled and exercised against a deterministic BrowserContext cookie implementation. The result matched the first model: app B's instant cookie disappeared before app A's callback while unrelated cookies survived.

Evidence class remains `model-executed` because this control does not use a real browser.

## Evidence 3 — real Playwright + Chromium cookie semantics

Artifact: `artifacts/playwright-cookie-scope-browser.json`.

Executed environment:

```text
Playwright Core  1.57.0-beta-1764944708000
Chromium         144.0.7559.96
```

Baseline browser control:

```text
BrowserContext cookie jar
├── app-a.example / next-instant-navigation-testing
├── app-b.example / next-instant-navigation-testing
├── app-a.example / session
└── app-b.example / session

context.cookies()
  └── same-name selection sees A and B
      └── expire returned entries
          ├── A testing cookie gone
          ├── B testing cookie gone
          ├── A session preserved
          └── B session preserved
```

Candidate browser control:

```text
context.cookies(['https://app-a.example/'])
  └── returns only app-a.example entries
      └── expire matching testing cookie
          ├── A testing cookie gone
          ├── B testing cookie preserved
          ├── A session preserved
          └── B session preserved
```

Evidence class: `integration-executed` for the Playwright/Chromium interface semantics. This does not exercise Next.js rendering or CookieStore lock delivery.

## Target characterization

### Preview characterization

Owned fork PR 1 retains a one-file target test against exact preview source:

```text
base  838bd19bdef0e41254f0868516b0c6c6e59e70d7
head  b1257ec33f56b7aa67bff2b87531c0ad70f84b01
```

### Current upstream characterization

The current source test is retained on owned-fork execution surfaces pinned from public upstream `5e8f31f7...`. The focused workflow checks out that exact public revision, injects the test, runs `pnpm install --frozen-lockfile`, `pnpm build`, then:

```sh
pnpm test-start test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-origin-isolation.test.ts
```

Workflow run `31225454341` is currently queued. This is an execution carrier, not evidence that the test ran.

Evidence class: `target-test-prepared` until a retained job receipt proves execution.

## Candidate

Owned-fork branch:

```text
fieldwork/instant-navigation-origin-scoped-release
base  5e8f31f7bdf7f564ec98a42e205f7e5b665398da
head  bd961e77ce8d47c881a83e5c240053e1f63d6a44
```

Changed behavior:

```ts
const scopeURL = resolveURL(page, options)

await releaseInstantCookie(context, scopeURL)

// release helper
const instantCookies = (await context.cookies(scopeURL)).filter(
  (cookie) => cookie.name === INSTANT_COOKIE
)
```

The candidate keeps `contextsWithActiveScope` keyed by `BrowserContext`. It changes only release selection.

Artifact `artifacts/origin-scoped-release-candidate.json` records a model control where:

- a stale app A testing cookie is cleared before acquisition;
- app A receives its pending testing cookie;
- app B's testing cookie survives acquisition and release;
- unrelated cookies survive;
- app A's testing cookie is removed on release.

A target-native regression test is prepared on the same candidate branch.

## Competing explanations

### H1 — cleanup ownership is broader than the acquired resource

Supported by current source plus real Playwright cookie semantics. The helper acquires for one application URL but deletes matching state across unrelated domains.

### H2 — all instant-navigation state in one browser context is deliberately global

PR 95375 supports context-wide **active-scope** exclusion. Evidence is weaker for context-wide **cookie deletion**, because acquisition is hostname-scoped and Playwright stores separate domain entries.

### H3 — URL-scoped cleanup breaks a stale-cookie or resurrection invariant

The candidate model preserves same-origin stale-cookie cleanup. Target execution must still cover the existing stale-cookie recovery test, MPA resurrection behavior, and normal release.

## Negative results and limits

- The earlier whole-cookie-jar race from PR 94947 remains repaired: unrelated cookie names survive current cleanup.
- No evidence currently supports changing the context-wide concurrency rule.
- No current upstream duplicate for the cross-origin cleanup question was found in the searched issue/PR terms.
- Frequency of multi-origin same-context use is unmeasured.
- Browser execution established Playwright cookie semantics but did not execute the Next.js e2e harness.
- Hosted target execution remains queued, so there is no `target-executed` claim yet.

## Ranked branches

### 1. Origin-scoped release

Strongest branch. Current source and browser behavior agree, a narrow candidate exists, and its browser-side selection primitive has been executed successfully.

Remaining gate: target-native current-source baseline and candidate regression, including stale-cookie recovery.

### 2. Context-wide active-scope ownership

Retain as a separate design question. PR 95375 provides direct precedent for the existing behavior. Do not fold it into the cleanup repair without evidence that independent-origin concurrency is useful and safe.

### 3. Stop with contract result

If target execution reveals that URL-filtered cleanup violates the lock protocol, retire the implementation candidate and retain the interface finding plus the context-global contract rationale.

## Current disposition

`research-active — narrow candidate prepared`

The interface-level cleanup candidate is now supported by current source, two deterministic controls, and a real Playwright/Chromium cookie-boundary control. Exact-current Next.js target execution remains the next promotion gate. Upstream contact remains unauthorized and no upstream interaction has occurred.
