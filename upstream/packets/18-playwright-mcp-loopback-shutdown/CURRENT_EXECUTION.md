# Current exact-head execution — Unit 18

## Identity

- source base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact source: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- execution carrier: `teamleaderleo/fieldwork#603@00b2f0547f260e2bc317ac37acf443af866048a2`
- workflow: `30855503566`
- runtime: Node 22.23.1, npm 10.9.8, Chromium

Each job verified the exact source, base, and three-file fence; ran `npm ci`, the complete build, Chromium setup, the full native `tests/mcp/http.spec.ts`, focused ESLint, clean-tree verification, exact diff verification, and receipt upload.

## Results

| Platform | Job | Native suite | Artifact | Digest |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 | `91825452070` | 21/21 in 34.4s | `8874308670` | `sha256:a58a61c91437cf8571b7fa0c7216901525de2bd3abc3182067222406cc6ccd80` |
| macOS 15 ARM64 | `91825451981` | 21/21 in 37.6s | `8872445482` | `sha256:8de35c03d271b70ebed1b2a2a2595a02e7e866bb8a66f499207eb1db3a831d95` |
| Windows Server 2025 | `91825452083` | 21/21 in 58.6s | `8872373764` | `sha256:19faaded526b5f9ecd9687c3d9928f4e3f1aa57933174047eacb7007dc349d16` |

## Assertions

- `/killkillkill` no longer returns the successful shutdown response;
- MCP remains responsive before parent EOF;
- parent stdin EOF produces one graceful browser close and process exit code 0;
- `PWTEST_UNDER_TEST=0` leaves HTTP responsive after EOF;
- immediate MCP stdio startup and ping remain intact;
- the rest of the native MCP HTTP suite remains green.

## Limits

Full Playwright repository CI and Node versions outside 22 weren't run. The focused source and lifecycle gate is complete on all three supported operating-system families.
