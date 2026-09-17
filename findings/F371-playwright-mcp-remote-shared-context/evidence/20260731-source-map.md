# Playwright MCP remote/shared-context source map

Date: 2026-07-31  
Parent finding: `F371-playwright-mcp-remote-shared-context`  
Evidence class: `source-read / upstream-test-read`, later resolved by exact target execution

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

`--host` defaults to localhost. `--allowed-hosts` defaults to the normalized bind Host. The original help text describes the allowlist as a DNS-rebinding defense.

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

Fieldwork later executed this complete file on the exact pinned target as part of the 19-test matrix retained in `20260731-target-matrix.md`.

## Source-read prediction

Playwright MCP appeared to separate accidental network exposure from explicit remote configuration more carefully than Context7's inspected HTTP default:

- standard input/output by default;
- loopback HTTP default;
- explicit all-interface opt-in;
- default DNS-rebinding defense.

The unresolved source-read question was client authority after deliberate remote enablement, especially when shared context turns separate MCP sessions into one browser-state authority domain.

## Executed resolution

Exact target run `30633739476`, job `91166043729`, resolved that question on Ubuntu 24.04, Node 22, and Chromium:

- the complete upstream HTTP suite passed;
- two explicitly remote-equivalent isolated sessions kept browser state separate;
- two explicitly remote-equivalent shared sessions used one browser authority domain;
- client 2 observed client 1's page and continued after client 1 disconnected;
- both sessions were deleted and the browser closed after the final client.

Exact help-candidate run `30634831167`, job `91169666445`, then proved the selected three-string patch applies, builds, and appears in generated runtime help.

## Remaining boundaries

Fieldwork still has not established:

- public exploitability or deployment prevalence;
- behavior behind an authenticated reverse proxy;
- risk involving real logged-in or private browser state;
- behavior on other operating systems or browsers;
- the need for a built-in authentication protocol;
- public upstream acceptance.

No external website, account, credential, private browser state, merge, deployment, spending, or public upstream interaction was used.
