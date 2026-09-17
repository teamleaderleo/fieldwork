# Upstream issue result — Playwright MCP remote and shared-browser authority

## Disposition

`NO NEW ISSUE DRAFT — DIRECT DOCUMENTATION PR PREFERRED`

## Reason

Playwright's current contribution policy requires a corresponding issue for most contributions and explicitly exempts minor documentation fixes. This candidate changes three CLI descriptions in one file and changes no behavior.

A directly relevant upstream issue already exists:

- [`microsoft/playwright#41915`](https://github.com/microsoft/playwright/issues/41915) — “Security: No authentication on HTTP/SSE transport — unauthenticated remote browser control.”

That issue requested built-in token authentication. A maintainer closed it as working as intended, citing opt-in HTTP transport, localhost default binding, and deliberate non-loopback configuration as the trust boundary.

The unit 25 candidate accepts that runtime decision. It clarifies the CLI help so operators can distinguish DNS-rebinding protection from client authentication and understand the authority shared by accepted clients under `--shared-browser-context`.

Opening a second issue with the same premise would duplicate prior discussion and add review cost. The proposed PR draft references #41915 as context without reopening the built-in-authentication proposal.

## Policy risk

The same contribution policy states that unsolicited PRs without a linked issue or prior approval will close. The minor-documentation exception and existing relevant issue support a direct PR, yet a human submitter should make the final routing choice.

Use an issue-first route only when:

- current maintainers indicate that this wording exceeds the minor-documentation exception;
- the candidate expands into runtime behavior, authentication, deployment configuration, or a larger guide;
- issue #41915 is judged insufficient as the discussion record.

## Contingency issue draft

Use only after explicit public-interaction authorization and a human decision that fresh approval is required.

### Proposed title

`Clarify remote HTTP and shared-browser authority in MCP CLI help`

### Proposed body

Playwright MCP uses stdio by default. HTTP transport is opt-in and binds to localhost unless an operator deliberately selects a broader host. The CLI also supports Host-header validation and an optional browser context shared across connected HTTP clients.

The current help text leaves two relationships implicit:

- `--allowed-hosts` protects against DNS rebinding; it does not authenticate clients;
- `--shared-browser-context` gives every accepted client authority over the same browser context, including tabs, cookies, storage, and page state.

Would a small documentation-only change to the three related option descriptions be welcome?

Proposed direction:

- identify the Host check as DNS-rebinding protection rather than client authentication;
- recommend an authenticated reverse proxy or equivalently access-controlled trusted network boundary for non-loopback HTTP;
- name the browser-context state shared by accepted clients.

The change would affect only `packages/playwright-core/src/tools/mcp/program.ts` help strings. It would change no option, default, transport, session, browser, or authentication behavior.

Related discussion: #41915.

## Authority

This file is a draft and routing record only. No upstream issue, comment, reaction, or other public interaction has been created by unit 25.
