## In simple words

Does Next.js's experimental `@next/playwright` `instant()` helper keep its testing state scoped to the application origin it was asked to control?

At `v16.3.0-preview.9`, acquisition is hostname-scoped, while release is browser-context-wide for every cookie named `next-instant-navigation-testing`. A dependency-free model of that exact selection logic shows that entering `instant()` for app A deletes an existing instant-navigation cookie for app B on another origin in the same Playwright `BrowserContext`. Unrelated cookies survive. The package also rejects a simultaneous `instant()` scope for app B solely because the two pages share a browser context.

This establishes an interface-level isolation candidate with `source-read` and `model-executed` evidence. Target-native Next.js/Playwright execution remains the promotion gate.

## Assignment

- Programme: `web-tooling-runtime-correctness` / issue #15
- Scout issue: #693
- Worker: ChatGPT research assistant
- Owned path: `programmes/web-tooling-runtime-correctness/scouts/nextjs-instant-navigation-isolation/`
- Target: Next.js
- Target tag: `v16.3.0-preview.9`
- Exact target commit: `838bd19bdef0e41254f0868516b0c6c6e59e70d7`
- Retrieval date: `2026-08-08`
- Intended claim scope: `interface`
- Upstream contact authorized: `false`

## Question

When one Playwright `BrowserContext` contains pages for two application origins, should `instant(pageA, ...)` preserve an existing `next-instant-navigation-testing` cookie belonging to app B, and should app B be able to hold an independent instant-navigation scope at the same time?

The candidate invariant is:

```text
one BrowserContext
├── app-a.example ── instant(A) may mutate A's testing cookie
└── app-b.example ── B's testing cookie and lock remain owned by B

unrelated cookies remain untouched on both origins
```

## Source and test map

Pinned source:

- [`@next/playwright` helper](https://redirect.github.com/vercel/next.js/blob/v16.3.0-preview.9/packages/next-playwright/src/index.ts)
- [Instant Navigation Testing API suite](https://redirect.github.com/vercel/next.js/blob/v16.3.0-preview.9/test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts)
- [client navigation-testing lock](https://redirect.github.com/vercel/next.js/blob/v16.3.0-preview.9/packages/next/src/client/components/segment-cache/navigation-testing-lock.ts)
- [exact preview source commit](https://redirect.github.com/vercel/next.js/commit/838bd19bdef0e41254f0868516b0c6c6e59e70d7)

The same `packages/next-playwright/src/index.ts` blob is present in `v16.3.0-canary.97` at retrieval time.

### Acquisition

`instant()` resolves the page or supplied base URL, extracts one `hostname`, and writes the testing cookie with that hostname and path `/`.

```text
page A URL
   │
   ▼
hostname A
   │
   ▼
next-instant-navigation-testing @ A /
```

### Release

`releaseInstantCookie(context)` calls `context.cookies()` with no URL filter, selects every entry whose name is `next-instant-navigation-testing`, and expires each selected domain/path pair.

```text
BrowserContext cookie jar
   │
   ├── A / next-instant-navigation-testing ── expire
   ├── B / next-instant-navigation-testing ── expire
   ├── A / session ────────────────────────── keep
   └── B / session ────────────────────────── keep
```

That release routine runs both before acquisition and in the callback cleanup path.

### Scope ownership

The helper tracks active scopes in a `WeakSet<BrowserContext>`. Any second `instant()` call in the same browser context throws before considering whether the two pages have different origins.

The current test suite covers nested-scope rejection, stale-cookie recovery, and concurrent scopes across separate browser contexts. This reconnaissance pass found no same-context, distinct-origin isolation control.

### Client lock

The client-side navigation lock is local to a page runtime and preserves the domain/path of the cookie entry it observes when Next.js rewrites the captured value. This makes the package-level browser-context cleanup boundary worth testing independently: the external helper aggregates cookie ownership more broadly than each page's client runtime.

## Relevant history

The current cleanup algorithm came from [PR 94947, “Release the instant navs lock without clearing the whole cookie jar”](https://redirect.github.com/vercel/next.js/pull/94947), landed in commit [`82cd9945b2c374dd2fb9c335617bf486cac690dc`](https://redirect.github.com/vercel/next.js/commit/82cd9945b2c374dd2fb9c335617bf486cac690dc).

That repair replaced Playwright's filtered `clearCookies` path because Playwright temporarily emptied the complete cookie jar before restoring non-matching cookies. Next.js could react to the instant-cookie deletion during that empty interval and render without application cookies. The replacement reads matching entries and individually expires them, successfully preserving unrelated cookie names.

The retained question is narrower: the replacement still matches by name across the complete browser context, so another origin's same-named instant-navigation cookie enters the deletion set.

## Model probe

Artifact: `artifacts/cookie-scope-probe.mjs`

Command:

```sh
node programmes/web-tooling-runtime-correctness/scouts/nextjs-instant-navigation-isolation/artifacts/cookie-scope-probe.mjs
```

Executed environment:

```text
Node v22.16.0
```

The probe mirrors the relevant pinned helper operations with an in-memory Playwright-cookie model:

1. seed app B with an existing instant-navigation cookie;
2. seed unrelated session cookies on apps A and B;
3. enter `instant()` for app A;
4. inspect the jar while A owns the scope and after release;
5. attempt a distinct-origin second scope in the same browser context;
6. run the same concurrency control using separate contexts.

Retained result: `artifacts/latest.json`.

Observed outcomes:

| Observation | Result |
| --- | --- |
| app B instant cookie survives A acquire | `false` |
| app B unrelated session cookie survives | `true` |
| app A unrelated session cookie survives | `true` |
| unrelated cookies survive final release | `true` |
| second origin in same context can enter concurrently | `false` — `already active` |
| separate contexts can enter concurrently | `true` |

Evidence class: `model-executed` for these exact selection and ownership semantics. The probe deliberately does not claim browser CookieStore timing, Next.js rendering behavior, or production impact.

## Competing explanations

### H1 — cleanup ownership is broader than the acquired resource

The helper should release only the cookie entry or origin it acquired. The browser-context-wide name filter accidentally couples distinct origins.

Distinguishing evidence: a real Playwright context with two Next.js origins shows B's instant cookie disappearing when A enters or leaves `instant()`.

### H2 — browser-context-global ownership is intentional

`@next/playwright` intentionally defines one instant-navigation scope per Playwright context, even when the context hosts several origins. Under this contract, deleting every same-named instant cookie and rejecting cross-origin concurrency is expected.

Distinguishing evidence: source, tests, or documented design explicitly require global ownership, or a target-native experiment demonstrates that origin-local ownership breaks the protocol.

### H3 — cleanup and concurrency have separate boundaries

Global active-scope exclusion could be intentional while cookie cleanup still needs origin scoping, or vice versa. The two observations should remain separable during target-native testing.

Distinguishing evidence: test each property independently instead of treating one as proof of the other.

## Negative results and controls

- The current algorithm does preserve unrelated cookie names; the earlier empty-cookie-jar defect addressed by PR 94947 is absent from this model.
- Separate Playwright browser contexts remain isolated and can run concurrent model scopes.
- The probe establishes no cross-origin user-visible rendering failure yet.
- No target-native test has run in this scout yet.
- No claim is made about the frequency of multi-origin same-context use.

## Ranked branch candidates

### 1. Origin-scoped release control

**Consequence:** one app's helper scope can delete another origin's same-named testing-control cookie inside a shared context.

**Likely owning boundary:** `packages/next-playwright/src/index.ts`, specifically the resource identity passed from acquisition into `releaseInstantCookie`.

**Evidence needed:** real Playwright + two origins in one context; preserve app B's cookie through app A acquire/release; retain existing stale-cookie and unrelated-cookie controls.

**Current rank:** strongest candidate.

### 2. Distinct-origin concurrency ownership

**Consequence:** independent app origins sharing one browser context cannot hold simultaneous `instant()` scopes because activity is keyed only by `BrowserContext`.

**Likely owning boundary:** `contextsWithActiveScope` ownership key and the relationship between one scope and one cookie origin.

**Evidence needed:** two actual Next.js pages on different origins; verify each page's client lock remains independent when both cookies exist; test same-origin concurrency as the negative control.

**Current rank:** strong adjacent candidate, likely coupled to candidate 1 but independently falsifiable.

### 3. Explicit context-global contract

If target-native behavior proves that the protocol requires one context-global scope, the useful outcome becomes a contract/test result instead of an implementation change.

**Evidence needed:** demonstrate why domain-local cleanup or concurrency violates a real Next.js invariant.

**Current rank:** fallback interpretation.

## Next gate

Run one target-native Next.js/Playwright fixture with two origins inside the same `BrowserContext` and distinguish:

```text
A acquire/release ──▶ does B retain its cookie and lock?
A + B concurrent  ──▶ independent by origin, or intentionally global?
```

If the target-native result matches the model and no protocol constraint requires global ownership, promote the narrow isolation finding. If actual runtime behavior contradicts the model-level consequence, retain the source observation and stop or revise the hypothesis.

## Current disposition

`research-active`

The source/model result is durable and specific enough to justify target-native execution. No upstream issue, pull request, comment, review, reaction, or message has been created or authorized.
