# Current exact-head execution — Unit 18

## Identity

- Source repository: `teamleaderleo/playwright`
- Source base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Source branch: `fix/mcp-parent-ipc-shutdown`
- Exact source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Exact changed-file fence:
  1. `packages/playwright-core/src/entry/mcp.ts`
  2. `packages/playwright-core/src/tools/utils/mcp/http.ts`
  3. `tests/mcp/http.spec.ts`
- Execution carrier: [`teamleaderleo/fieldwork#455`](https://github.com/teamleaderleo/fieldwork/pull/455)
- Carrier branch: `p0/435-unit-18-execute-e99e97d`
- Exact carrier head: `0323aeaadc391575b572e869258e5e1ac3c4652c`
- Workflow run: [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059)

## Declared gate

Each platform checks out the exact source and base, verifies the exact three-file fence and `git diff --check`, runs `npm ci`, runs the complete `npm run build`, installs Chromium, runs the complete native MCP HTTP file with `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`, runs focused ESLint on the three changed files, verifies a clean source tree and the exact diff fence, and uploads the test log, exact diff, commit list, and machine-readable receipt.

## Current results

| Platform | Job | Native suite | Other gates | Artifact | Digest | State |
| --- | --- | --- | --- | --- | --- | --- |
| macOS 15, ARM64, Node 22.23.1 | [`91344705071`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/job/91344705071) | 18/18 passed in 32.6s | exact identity, locked install, complete build, Chromium, focused ESLint, clean tree, exact diff all passed | [`8815562250`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/artifacts/8815562250) | `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54` | complete success |
| Windows Server 2025, x64, Node 22.23.1 | [`91344705088`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/job/91344705088) | 18/18 passed in 34.0s | exact identity, locked install, complete build, Chromium, focused ESLint, clean tree, exact diff all passed | [`8815574235`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/artifacts/8815574235) | `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4` | complete success |
| Ubuntu 24.04 | [`91344705054`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/job/91344705054) | not started | runner allocation pending | none yet | none yet | queued; no product failure |

## Assertions exercised by the current source

The 18-test native file includes the current strict controls: the old HTTP shutdown request does not return 200 and MCP remains responsive; a wrong string, wrong version, extra-field object, and inherited-property object are inert; the exact plain-object type/version message sent twice produces one graceful close; IPC disconnect is inert; and the rest of the MCP HTTP lifecycle file remains green.

## Classification

- macOS result: `target-executed`, exact current head
- Windows result: `target-executed`, exact current head
- Ubuntu status: `runner-queued`, no source or test execution yet
- Full Playwright repository CI: not run and not claimed
- Source acceptance: not claimed

## Packet integrity

The prior canonical packet head `7fe2bb3b619e6b1675c260d0304fd262eca71f1f` passed Fieldwork integrity in run [`30675345841`](https://github.com/teamleaderleo/fieldwork/actions/runs/30675345841). The packet must re-run integrity after this execution transfer.

## Current decision

Disposition remains `EXECUTE` until Ubuntu completes successfully or an explicit reviewed platform carry-forward decision is recorded. After that, the contribution route is `ISSUE FIRST` because Playwright requires a corresponding issue and prior approval/assignment for substantive changes. Public upstream contact remains unauthorized.
