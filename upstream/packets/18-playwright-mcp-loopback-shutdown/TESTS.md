# Tests and receipts — Unit 18 Playwright MCP shutdown authority

## Canonical identity

- public base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact source: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- exact fence: `http.ts`, `server.ts`, `http.spec.ts`
- workflow: `30855503566`
- runtime: Node 22.23.1, npm 10.9.8, Chromium

## Final results

| Platform | Job | Test result | Artifact | Digest |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 | `91825452070` | 21/21 in 34.4s | `8874308670` | `sha256:a58a61c91437cf8571b7fa0c7216901525de2bd3abc3182067222406cc6ccd80` |
| macOS 15 ARM64 | `91825451981` | 21/21 in 37.6s | `8872445482` | `sha256:8de35c03d271b70ebed1b2a2a2595a02e7e866bb8a66f499207eb1db3a831d95` |
| Windows Server 2025 | `91825452083` | 21/21 in 58.6s | `8872373764` | `sha256:19faaded526b5f9ecd9687c3d9928f4e3f1aa57933174047eacb7007dc349d16` |

Each job passed:

- exact source/base identity and three-file fence;
- `git diff --check`;
- `npm ci`;
- complete `npm run build`;
- Chromium installation and required platform dependencies;
- full native `tests/mcp/http.spec.ts` with no exclusions;
- focused ESLint on all changed files;
- clean-tree and exact-diff verification;
- receipt upload.

## Regression assertions

- former `/killkillkill` request doesn't shut down the server;
- MCP remains responsive before EOF;
- closing the parent-owned stdin produces one graceful close and exit code 0;
- stdin EOF is inert when `PWTEST_UNDER_TEST=0`;
- immediate stdio startup and ping remain intact.

## Earlier evidence

Strict parent IPC run `30690674059` remains a complete fallback matrix. Earlier global stdin experiments established that parent EOF arrives as readable `end` and that consumption must be placed after transport selection.

## Limits

Full repository CI and Node versions outside 22 weren't run. No broader deployment or security-severity claim is made.

Current judgment: `FOCUSED THREE-PLATFORM GATE COMPLETE`.
