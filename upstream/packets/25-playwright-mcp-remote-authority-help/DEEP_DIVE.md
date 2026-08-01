# Deep dive — Playwright MCP remote and shared-browser authority

## In simple words

Playwright MCP exposes several independent controls. Transport selection decides whether a network listener exists. Bind host decides which interfaces can reach it. Host-header validation limits accepted Host values and reduces DNS-rebinding risk. Client authentication decides who may use the listener. Session identity separates MCP connections. Browser-context selection decides which browser state those sessions can observe and control.

The current CLI help names transport, bind host, Host validation, and shared context, yet it leaves two operator-critical relationships implicit: Host validation does not authenticate clients, and shared context joins accepted clients into one browser-context authority domain. The candidate adds those facts to the generated CLI help without changing runtime behavior.

## Exact source state

- Public base: [`microsoft/playwright@15b1aec478d90f0293dae7b7b6dafd494d9f0154`](https://github.com/microsoft/playwright/commit/15b1aec478d90f0293dae7b7b6dafd494d9f0154)
- Clean candidate: [`teamleaderleo/playwright@745b4dea96ac64eeb1e92d9ce4525b995e64909f`](https://github.com/teamleaderleo/playwright/commit/745b4dea96ac64eeb1e92d9ce4525b995e64909f)
- Changed source: [`packages/playwright-core/src/tools/mcp/program.ts`](https://github.com/teamleaderleo/playwright/blob/745b4dea96ac64eeb1e92d9ce4525b995e64909f/packages/playwright-core/src/tools/mcp/program.ts)
- Complete compare: [`15b1aec...745b4dea`](https://github.com/teamleaderleo/playwright/compare/15b1aec478d90f0293dae7b7b6dafd494d9f0154...745b4dea96ac64eeb1e92d9ce4525b995e64909f)

The public file retained the original strings at the current inspected head, so the historical patch premise still applies. The intervening public commits since the historical execution base did not alter these three option declarations.

## Control model

### 1. Transport selection

Without a configured port, the server uses standard input/output. Configuring `--port` creates HTTP transport. This choice determines whether a network-reachable service exists.

Evidence: `source-read`, historically exercised by the complete MCP HTTP suite.

### 2. Bind authority

`--host` defaults to localhost. An operator may explicitly use `0.0.0.0` to bind all interfaces. The default therefore bounds network reach; it does not establish caller identity on the local machine.

Evidence: `source-read`, with target-executed controls for explicit non-loopback binding.

### 3. Host-header validation

`--allowed-hosts` checks the request Host value. The handler uses this check as DNS-rebinding protection. A client able to send an accepted Host value still reaches the MCP transport. The check supplies no bearer token, client certificate, user identity, or equivalent authentication decision.

Evidence: `source-read`; Host acceptance/rejection is covered by target tests. The candidate says this directly:

> This protects against DNS rebinding; it does not authenticate clients.

### 4. Client authentication

Playwright MCP does not add a built-in client-authentication protocol to the inspected HTTP handler. Deployment can supply an authenticated reverse proxy or an equivalently access-controlled trusted network boundary. The candidate recommends that boundary for deliberate non-loopback HTTP while avoiding a claim that Playwright itself must implement authentication.

Evidence: `source-read`; reverse-proxy behavior remains unexecuted.

### 5. Session identity

Streamable HTTP creates distinct server sessions. Historical Fieldwork controls retained separate client/session lifecycles, two creation/deletion events, continued service for the remaining client, and final browser cleanup.

Evidence: `target-executed` at exact historical target `368941457a82da112aa8610107e25f4bde94339a`.

### 6. Browser-context authority

In isolated mode, clients receive separate browser contexts. In shared mode, accepted HTTP clients receive backends over the same browser context. A BrowserContext owns tabs/pages, cookies, storage, permissions, and related page state.

The retained matrix directly proved:

- client 1 opened a disposable local page;
- client 2 could not see it in isolated mode;
- client 2 could see it in shared mode;
- client 2 continued after client 1 disconnected;
- both sessions were deleted;
- the browser closed after the final client.

Cookies, origin storage, and arbitrary page-state mutation were not separately exercised by that matrix. Their inclusion in help is supported by the shared BrowserContext source contract rather than promoted to target-executed evidence.

## Change thesis

### Current behavior

The runtime already keeps HTTP local by default, validates Host values, supports deliberate non-loopback binding, creates distinct MCP sessions, and optionally reuses one browser context across clients.

### Consequence

An operator reading only `--help` can mistake Host validation for a caller-authentication boundary or enable shared context without seeing that all accepted clients receive authority over the same browser context.

### Proposed improvement

Add three precise help clauses:

1. `--allowed-hosts`: identify DNS-rebinding protection and separate it from client authentication;
2. `--host`: recommend an authenticated reverse proxy or equivalently access-controlled trusted network boundary for non-loopback HTTP;
3. `--shared-browser-context`: name the shared browser context and its tabs, cookies, storage, and page state.

### Evidence

- current source inspection at `15b1aec...`;
- historical 19/19 HTTP and two-client matrix at `3689414...`;
- historical exact patch/build/generated-help execution;
- current exact-source carrier for build, generated help, focused lint, and complete HTTP suite.

### Boundary

The evidence does not establish deployment prevalence, public exploitability, behavior behind a proxy, cross-platform behavior beyond retained runs, risk involving real logged-in browser data, or a requirement for built-in authentication.

## Exact candidate wording

```text
--allowed-hosts ... This protects against DNS rebinding; it does not authenticate clients.
```

```text
--host ... Protect non-loopback HTTP with an authenticated reverse proxy or an equivalently access-controlled trusted network boundary.
```

```text
--shared-browser-context ... Every accepted client shares and can control the same browser context, including its tabs, cookies, storage, and page state.
```

## Why the wording changed from the historical patch

The historical candidate said:

```text
Non-loopback HTTP should be protected by a trusted authenticated network boundary or reverse proxy.
```

That grammar allowed “reverse proxy” to read as an unauthenticated alternative. The current wording requires authentication or equivalent access control in either deployment form.

The historical finding also described cookies, storage, and page state too broadly as executed. The current packet separates direct tab/session execution from source-backed BrowserContext authority.

## Prior art and project direction

Upstream issue [`#41915`](https://github.com/microsoft/playwright/issues/41915) requested built-in authentication for HTTP/SSE. A maintainer closed it as working as intended, citing opt-in HTTP, localhost default, and deliberate non-loopback binding as the trust boundary.

That precedent weakens token-authentication or fail-closed redesigns for this unit. A narrow documentation change complements the stated runtime direction by telling operators what deliberate remote configuration means.

No equivalent current documentation implementation or open replacement PR surfaced in the 2026-08-01 search.

## Compatibility and review cost

- One source file changes.
- Three option description strings change.
- No option name, parser, default, transport, handler, browser factory, session lifecycle, authentication protocol, generated file, snapshot, lockfile, or dependency changes.
- Commander may wrap the rendered strings differently by terminal width; semantic whitespace-normalized assertions avoid line-wrap coupling.
- Existing scripts or tests that snapshot full help text could observe the additional wording. No repository snapshot file was found for these lines; current generated-help execution is the discriminating check.

## Adjacent excluded work

Fieldwork issue [`#404`](https://github.com/teamleaderleo/fieldwork/issues/404) studies the `/killkillkill` shutdown route and selects loopback-only shutdown authority. It owns upstream unit 18. This unit changes no route, peer-address check, process signal, or shutdown behavior.

## Contribution policy

Current Playwright contribution policy:

- requires a corresponding issue for most contributions;
- exempts minor documentation fixes;
- warns that unsolicited PRs without linked issue or approval will close;
- requires Node 20+, installation, build, lint, small readable diffs, and human oversight.

The direct-PR draft relies on the minor-documentation exception and cites existing issue #41915 as relevant context. Human review should decide whether seeking fresh approval first would better respect maintainer expectations.
