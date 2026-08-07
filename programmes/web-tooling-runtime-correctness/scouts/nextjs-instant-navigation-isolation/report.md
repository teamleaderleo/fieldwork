## In simple words

Does Next.js's experimental `@next/playwright` `instant()` helper keep its testing state scoped to the application origin it was asked to control?

At `v16.3.0-preview.9`, acquisition is hostname-scoped, while release is browser-context-wide for every cookie named `next-instant-navigation-testing`. A dependency-free model of that exact selection logic shows that entering `instant()` for app A deletes an existing instant-navigation cookie for app B on another origin in the same Playwright `BrowserContext`. Unrelated cookies survive. The helper also rejects a simultaneous `instant()` scope for app B solely because the two pages share a browser context.

The result now has `source-read`, `model-executed`, and `target-test-prepared` evidence. A one-file characterization test is retained on the owned Next.js fork at exact preview source. Target-native execution remains the promotion gate.

## Assignment

- Programme: `web-tooling-runtime-correctness` / issue #15
- Scout issue: #693
- Fieldwork PR: #694
- Worker: ChatGPT research assistant
- Owned path: `programmes/web-tooling-runtime-correctness/scouts/nextjs-instant-navigation-isolation/`
- Target: Next.js
- Target tag: `v16.3.0-preview.9`
- Exact target commit: `838bd19bdef0e41254f0868516b0c6c6e59e70d7`
- Retrieval date: `2026-08-08`
- Intended claim scope: `interface`
- Upstream contact authorized: `false`

## Question

When one Playwright `BrowserContext` contains pages for two application origins, should `instant(pageA, ...)` preserve an existing `next-instant-navigation-testing` cookie belonging to app B?

A related question remains separate: should app A and app B be able to hold independent instant-navigation scopes at the same time when they share a browser context?

```text
one BrowserContext
├── app-a.example ── instant(A) may mutate A's testing cookie
└── app-b.example ── B's testing cookie remains owned by B

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

`instant()` resolves one hostname and writes the testing cookie for that hostname at `/`.

```text
page A URL ──▶ hostname A ──▶ next-instant-navigation-testing @ A /
```

### Release

`releaseInstantCookie(context)` calls `context.cookies()` with no URL filter, selects every entry whose name is `next-instant-navigation-testing`, and expires each selected domain/path pair. The same routine runs before acquisition and during callback cleanup.

```text
BrowserContext cookie jar
   │
   ├── A / next-instant-navigation-testing ── expire
   ├── B / next-instant-navigation-testing ── expire
   ├── A / session ────────────────────────── keep
   └── B / session ────────────────────────── keep
```

### Scope ownership

The helper tracks active scopes in a `WeakSet<BrowserContext>`. Any second `instant()` call in the same browser context throws before considering whether the pages have different origins.

The existing suite covers nested-scope rejection, stale-cookie recovery, and concurrent scopes across separate browser contexts. This reconnaissance pass found no same-context, distinct-origin isolation control.

### Client lock

The client navigation lock lives in each page runtime and preserves the observed cookie entry's domain/path when rewriting its captured value. That page-local behavior makes the package-level context-wide cleanup boundary independently testable.

## Relevant history

The current cleanup algorithm came from [PR 94947, “Release the instant navs lock without clearing the whole cookie jar”](https://redirect.github.com/vercel/next.js/pull/94947), landed in commit [`82cd9945b2c374dd2fb9c335617bf486cac690dc`](https://redirect.github.com/vercel/next.js/commit/82cd9945b2c374dd2fb9c335617bf486cac690dc).

That repair replaced Playwright's filtered `clearCookies` path because Playwright temporarily emptied the complete cookie jar before restoring non-matching cookies. Next.js could react during that interval and render without application cookies. The replacement reads matching entries and individually expires them, preserving unrelated cookie names.

The retained question is narrower: the replacement still matches by name across the complete browser context, so another origin's same-named instant-navigation cookie enters the deletion set.

## Model probe

Artifact: `artifacts/cookie-scope-probe.mjs`

Command:

```sh
node programmes/web-tooling-runtime-correctness/scouts/nextjs-instant-navigation-isolation/artifacts/cookie-scope-probe.mjs
```

Executed environment: Node `v22.16.0`.

Retained machine result: `artifacts/latest.json`.

| Observation | Result |
| --- | --- |
| app B instant cookie survives A acquire | `false` |
| app B unrelated session cookie survives | `true` |
| app A unrelated session cookie survives | `true` |
| unrelated cookies survive final release | `true` |
| second origin in same context can enter concurrently | `false` — `already active` |
| separate contexts can enter concurrently | `true` |

Evidence class: `model-executed` for these exact selection and ownership semantics. The model deliberately leaves browser CookieStore timing and Next.js rendering behavior outside its claim.

## Target-native characterization test

Owned fork: `teamleaderleo/next.js`.

Exact base branch:

```text
fieldwork/instant-navigation-origin-isolation-base
838bd19bdef0e41254f0868516b0c6c6e59e70d7
```

Characterization branch/head:

```text
fieldwork/instant-navigation-origin-isolation
b1257ec33f56b7aa67bff2b87531c0ad70f84b01
```

Owned-fork draft PR: `teamleaderleo/next.js` PR 1.

Changed file fence:

```text
test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-origin-isolation.test.ts
```

The prepared test uses the actual Next.js e2e harness and native Playwright browser context. It seeds another domain with an existing `next-instant-navigation-testing` cookie, enters `instant()` for the Next.js page, and expects the other-domain cookie to remain. On the pinned implementation, source analysis predicts that assertion will fail during `instant()`'s pre-acquire cleanup.

Evidence class: `target-test-prepared`. No target-native execution receipt exists yet, so this is not described as a failing target test.

## Competing explanations

### H1 — cleanup ownership is broader than the acquired resource

The helper should release only the cookie entry or origin it acquired. The browser-context-wide name filter accidentally couples distinct origins.

Distinguishing evidence: the prepared target test executes and observes B's cookie disappearing when A enters `instant()`.

### H2 — browser-context-global ownership is intentional

`@next/playwright` intentionally defines one instant-navigation scope per Playwright context, even when the context hosts several origins. Under this contract, deleting every same-named instant cookie and rejecting cross-origin concurrency is expected.

Distinguishing evidence: source, tests, or target-native behavior demonstrates a protocol requirement for context-global ownership.

### H3 — cleanup and concurrency have separate boundaries

Global active-scope exclusion could be intentional while cookie cleanup still needs origin scoping, or vice versa. Keep the two properties independently falsifiable.

## Negative results and controls

- The current selection algorithm preserves unrelated cookie names; the earlier empty-cookie-jar failure addressed by PR 94947 is absent from the model.
- Separate browser contexts remain isolated in the model.
- The model establishes no user-visible rendering failure.
- The target test is prepared and unexecuted.
- Multi-origin same-context frequency remains unmeasured.

## Ranked branch candidates

### 1. Origin-scoped release control

**Consequence:** one app's helper scope can delete another origin's same-named testing-control cookie inside a shared context.

**Likely owning boundary:** `packages/next-playwright/src/index.ts`, specifically the identity passed from acquisition into `releaseInstantCookie`.

**Evidence needed:** execute the prepared test, then retain stale-cookie and unrelated-cookie controls around any candidate.

**Rank:** strongest candidate.

### 2. Distinct-origin concurrency ownership

**Consequence:** independent origins sharing one browser context cannot hold simultaneous `instant()` scopes because activity is keyed only by `BrowserContext`.

**Likely owning boundary:** `contextsWithActiveScope` and the relation between one scope and one cookie origin.

**Evidence needed:** an independently prepared target control that distinguishes same-origin conflict from distinct-origin independence.

**Rank:** strong adjacent candidate.

### 3. Explicit context-global contract

If target-native evidence demonstrates that the protocol requires one context-global scope, retain the result as a contract finding and stop implementation work.

**Rank:** fallback interpretation.

## Next gate

Execute the owned-fork characterization test at `b1257ec33f56b7aa67bff2b87531c0ad70f84b01` using the target repository's e2e harness. Classify setup/harness failures separately from the assertion.

If the assertion fails for the predicted cookie deletion and no protocol constraint requires global ownership, promote the narrow isolation finding. If runtime evidence contradicts the source/model consequence, revise or stop the branch.

## Current disposition

`research-active`

The source/model result and exact target test are durable. Upstream contact remains unauthorized, and no upstream interaction has occurred.
