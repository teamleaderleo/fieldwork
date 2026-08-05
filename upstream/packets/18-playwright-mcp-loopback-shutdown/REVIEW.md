# Review — Unit 18 Playwright MCP shutdown authority

## Review subject

- target: `microsoft/playwright`
- preferred source: `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact fence: `http.ts`, `server.ts`, `http.spec.ts`
- upstream issue: [submitted bug report](https://redirect.github.com/microsoft/playwright/issues/42129)

## Diff review

### `http.ts`

Deletes the special shutdown branch. Ordinary Host validation, SSE, and streamable HTTP dispatch remain unchanged.

### `server.ts`

After the stdio branch returns, HTTP test mode consumes readable stdin EOF and emits `SIGINT`. The listener is gated by `isUnderTest()` and handles an already-ended stream.

### `http.spec.ts`

The fixture exposes `closeStdin` and process exit. Tests prove route inertness, liveness before EOF, one graceful close and exit code 0, no stdin shutdown outside test mode, and immediate stdio startup.

## Execution review

Run `30855503566` passed 21/21 and every declared gate on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

No source defect was found in the exact three-file diff. Same-account reviews on earlier owned PRs are supporting records, not independent review.

## Remaining judgment

Maintainers may still prefer a different lifecycle mechanism or decide the route is intentional. The filed issue is the current decision point.

## Limits

- full repository CI wasn't run;
- only Node 22 was exercised;
- no claim is made about deployment prevalence or severity;
- the upstream PR isn't authorized until the issue is approved or assigned.

## Disposition

`ACCEPT SOURCE / WAIT FOR UPSTREAM ISSUE RESPONSE`
