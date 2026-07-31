# Playwright MCP remote/shared-context source map

Date: 2026-07-31  
Parent finding: `F371-playwright-mcp-remote-shared-context`  
Evidence class: `source-read / upstream-test-read`

## Exact revisions

- package wrapper: `microsoft/playwright-mcp@55679f5f3d4b4f3e2534ec0ce2fc5683ba2eaf3f`;
- shared implementation: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`.

## Package wrapper paths

### `microsoft/playwright-mcp/cli.js`

The package CLI delegates to `playwright-core/lib/utilsBundle` and calls `program.parseAsync(process.argv)`. It adds no package-local transport or client-authentication decision.

### `microsoft/playwright-mcp/index.js`

The public connection factory delegates into shared core and maps config through the shared option layer.

### `microsoft/playwright-mcp/README.md`

The option table documents:

- `--port` for SSE/HTTP transport;
- `--host` with localhost default and `0.0.0.0` for all interfaces;
- `--allowed-hosts` as a comma-separated Host allowlist and `*` to disable the check;
- `--shared-browser-context` to reuse one browser context across HTTP clients.

No `authentication` wording was found in the inspected README generation.

## Shared core paths

### `packages/playwright-core/src/tools/mcp/program.ts`

The CLI option contract separates:

- transport selection;
- bind host;
- allowed Host values;
- shared browser context;
- browser/network permissions.

`--host` defaults to localhost. `--allowed-hosts` defaults to the normalized bind Host. The help text describes the allowlist as a DNS-rebinding defense.

### `packages/playwright-core/src/tools/utils/mcp/server.ts`

The server uses standard input/output when no port is configured. With a port, it creates the HTTP transport and prints the listener URL. Shared-browser-context mode selects a shared browser factory rather than one isolated factory per client.

### `packages/playwright-core/src/tools/utils/mcp/http.ts`

The HTTP handler:

1. normalizes wildcard and loopback bind addresses for presentation/default Host policy;
2. parses the request Host header;
3. rejects missing or unlisted Hosts;
4. routes accepted requests to streamable HTTP or legacy SSE session creation;
5. tracks session transports;
6. closes transports and backend state on server shutdown.

No bearer token, client certificate, user identity, or equivalent client-authentication check is visible in this handler.

This does not exclude authentication supplied by a reverse proxy or another deployment layer.

## Upstream test paths

### `tests/mcp/http.spec.ts`

The inspected target tests retain these relevant controls:

- default allowed Hosts reject a request addressed through localhost's resolved IP;
- an explicitly allowed Host passes;
- wildcard Host allowance passes;
- shared-browser-context mode lets client 2 list and use a tab created by client 1;
- client 2 continues after client 1 disconnects.

These target tests were read, not executed by Fieldwork.

## Current interpretation

Playwright MCP already separates accidental network exposure from explicit remote configuration better than Context7's inspected HTTP default:

- standard input/output by default;
- loopback HTTP default;
- explicit all-interface opt-in;
- default DNS-rebinding defense.

The remaining comparison question is client authority after deliberate remote enablement, especially when shared context turns separate MCP sessions into one browser-state authority domain.

## Missing evidence

Fieldwork has not yet established:

- the actual listener on the pinned build;
- two credential-free remote-equivalent sessions on an explicitly allowed Host;
- isolated-mode cross-client separation;
- shared-mode cross-client visibility and mutation;
- client disconnect versus browser/context cleanup order;
- final-client disconnect cleanup;
- the clarity of runtime startup/help warnings in an executable installation.

No external website, account, credential, private browser state, or public upstream interaction was used.
