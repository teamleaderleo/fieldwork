# Unit 18 working notes

Last checked: 2026-08-05

## Question

How can Playwright's lifecycle test exercise graceful MCP HTTP shutdown without giving ordinary HTTP clients process-control authority?

## Route history

`/killkillkill` was introduced as a Windows test workaround so the HTTP and SSE lifecycle tests could enter the existing `SIGINT` cleanup path. It later changed from `GET` to `POST` plus the fixed `x-pw-mcp-kill: 1` header. That reduces browser-CSRF exposure, but the public fixed header doesn't identify the process owner.

Current upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

## Selected source

```text
teamleaderleo/playwright#48
fix/mcp-http-parent-stdin-review
base 2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2
head 10e28dfdd7758d92aeed50922fd9c7ce9596c21c
```

Exactly three files change:

- `packages/playwright-core/src/tools/utils/mcp/http.ts`
- `packages/playwright-core/src/tools/utils/mcp/server.ts`
- `tests/mcp/http.spec.ts`

The source removes the route. After the stdio branch returns, HTTP test mode consumes readable stdin EOF and emits `SIGINT`. This ties the test shutdown request to the spawning parent without adding a message protocol or changing ordinary launches.

## Final execution

Run `30855503566` passed 21/21 tests and every declared gate on:

- Ubuntu 24.04 — 34.4s;
- macOS 15 ARM64 — 37.6s;
- Windows Server 2025 — 58.6s.

Artifacts and digests are recorded in `CURRENT_EXECUTION.md` and `TESTS.md`.

## Alternatives

- strict parent IPC at `teamleaderleo/playwright#40`: fully executed fallback, but adds a private message format;
- loopback or Host restrictions: don't establish process ownership;
- preserving the endpoint with a public fixed header: still lets any reachable programmatic client reproduce the request;
- authenticated remote administration: reasonable only if Playwright later has an actual remote-shutdown requirement.

## Current disposition

`ISSUE FILED / WAITING FOR MAINTAINER APPROVAL OR ASSIGNMENT`

The next upstream action is a linked pull request after explicit maintainer approval or assignment and separate user authorization. No timed waiting period substitutes for that response.
