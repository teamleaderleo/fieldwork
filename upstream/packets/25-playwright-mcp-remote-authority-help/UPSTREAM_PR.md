# Upstream pull-request draft — Playwright MCP remote and shared-browser authority

## Proposed title

`docs(cli): document remote and shared-browser authority`

## Proposed body

## Summary

Clarify three Playwright MCP CLI options that participate in remote HTTP and shared-browser configuration:

- describe `--allowed-hosts` as DNS-rebinding protection rather than client authentication;
- recommend an authenticated reverse proxy or equivalently access-controlled trusted network boundary for non-loopback HTTP;
- state that every accepted `--shared-browser-context` client shares and can control the same browser context, including tabs, cookies, storage, and page state.

The change updates help text only. It changes no option, parser, default, transport, session lifecycle, browser behavior, Host policy, or authentication mechanism.

## Why

HTTP transport is opt-in and localhost-bound by default. Operators can deliberately bind to a non-loopback interface and can choose to share one browser context across HTTP clients.

The existing option descriptions name those controls but leave their authority relationship implicit. Host validation accepts or rejects Host values; it does not establish client identity. Shared browser context intentionally places accepted clients in the same browser-context authority domain.

Making those boundaries visible in `--help` keeps the current runtime model intact while giving operators the information at configuration time.

Related to #41915.

## Testing

- `npm ci`
- `npm run build`
- generated `Playwright MCP --help` semantic checks for all three complete statements
- `npx eslint packages/playwright-core/src/tools/mcp/program.ts`
- `npx playwright install --with-deps chromium`
- `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`

## Changed files

- `packages/playwright-core/src/tools/mcp/program.ts`

## Submission notes

- Target base prepared from `microsoft/playwright@15b1aec478d90f0293dae7b7b6dafd494d9f0154`.
- Candidate commit: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`.
- Keep the submitted diff to the one source file above.
- Exclude the owned-fork execution workflow and all Fieldwork packet files.

## Draft verification checklist

- [x] Uses Playwright option names and current source terminology.
- [x] Describes a documentation-only diff.
- [x] Avoids a vulnerability, prevalence, or built-in-authentication claim.
- [x] Separates Host validation from authentication.
- [x] Separates directly executed tab/session behavior from source-backed BrowserContext authority in the retained packet.
- [x] References the existing relevant upstream issue.
- [ ] Replace the test list only if the final exact-source receipt differs.
- [ ] Confirm the public base remains current immediately before submission.
- [ ] Obtain explicit public-upstream authorization.

## Authority

This is a draft only. Unit 25 has opened no public upstream pull request and sent no upstream comment, review, reaction, or message.
