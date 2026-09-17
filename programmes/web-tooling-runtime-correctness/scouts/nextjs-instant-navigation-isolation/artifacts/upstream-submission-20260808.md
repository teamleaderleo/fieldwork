# Human upstream submission receipt — 2026-08-08

## Boundary

This receipt records upstream interactions performed manually by the human owner. Fieldwork automation did not create, edit, comment on, react to, review, label, or otherwise mutate the third-party upstream repository.

## Filed surfaces

- issue: https://redirect.github.com/vercel/next.js/issues/96961
- pull request: https://redirect.github.com/vercel/next.js/pull/96962

The issue and PR were filed sequentially, back-to-back. The PR links the issue with `Fixes #96961`.

## Filed issue shape

Title:

```text
`@next/playwright instant()` clears testing cookies for other origins
```

The report contains:

- a public GitHub reproduction;
- exact reproduction commands;
- the distinguishing assertion failure;
- a concise current-vs-expected statement;
- Node / `@next/playwright` / Playwright versions;
- `Cookies` and `Testing` affected areas;
- `next dev (local)` and `next start (local)` stages;
- no redundant Additional context section.

Public reproduction:

https://github.com/teamleaderleo/playground/tree/repro/next-playwright-origin-cookie/next-playwright-origin-cookie-repro

Human-executed environment:

```text
Node.js: v22.23.1
@next/playwright: 16.3.1-canary.8
Playwright: 1.61.1
```

Observed result:

```text
AssertionError: app B cookie was removed by instant() for app A
actual:   undefined
expected: '[1,"app-b",null]'
```

## Filed PR shape

Title:

```text
fix(next-playwright): scope instant cookie cleanup to app URL
```

PR source:

- upstream base: `a677cf66af002fbdcf49a982ef435b03554817cc`
- candidate head: `a33d51d10d212ae656a0c94a28ffe51a6e43879b`
- commit count: 1
- changed files: 2

The body is deliberately minimal:

- What: change cleanup selection from `context.cookies()` to `context.cookies(scopeURL)`;
- Why: one app's `instant()` can otherwise remove another app's same-named testing cookie;
- Tests: regression in the existing Instant Navigation testing suite.

## Architectural rationale retained internally

The strongest invariant is ordinary operation symmetry:

```text
acquire: app A
release: cookies applicable to app A
```

The BrowserContext-wide `WeakSet` remains an active-call coordination mechanism, not proof that one call owns every same-named cookie in the context.

If a context-wide Instant-cookie purge is ever desired, it should be a separate explicit reset/garbage-collection operation. Normal release should not incidentally perform that broader operation.

The likely implementation history is that fresh-page support required moving acquisition to BrowserContext APIs and cleanup inherited an unfiltered context-level cookie query. This historical explanation is useful internally but is not required for the public bug argument.

## Initial upstream state

At the first read-only check after filing:

- issue #96961: open, no comments;
- PR #96962: open, mergeable, regular (not draft), one commit, two changed files;
- no requested reviewers, comments, or reviews yet;
- `build-and-test`, `build-and-deploy`, and stats workflow runs were created;
- those runs reached `action_required` before jobs were created.

The workflow state is not classified as a code failure or target execution. A fork-workflow approval gate is the likely explanation, but that remains an inference until GitHub/maintainer state confirms it.

## Evidence state after filing

- `source-read`
- `model-executed`
- `integration-executed`
- `public-repro-executed`
- `target-test-prepared`

No `target-executed` claim is made yet.
