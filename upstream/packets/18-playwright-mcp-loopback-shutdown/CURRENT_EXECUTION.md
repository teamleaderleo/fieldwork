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
- Exact carrier head: `0323aeaadc391575b572e869258e5e1ac3c4652c`
- Workflow run: [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059)

## Declared gate

Each platform checked out the exact source and base, verified the exact three-file fence and `git diff --check`, ran `npm ci`, complete `npm run build`, Chromium installation, the complete native MCP HTTP file with `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`, focused ESLint on the three changed files, a clean source tree, and the exact diff fence. Each job uploaded the test log, exact diff, commit list, and receipt.

## Final results

| Platform | Job | Native suite | Other gates | Artifact | Digest | State |
| --- | --- | --- | --- | --- | --- | --- |
| Ubuntu 24.04, Node 22.23.1 | [`91344705054`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/job/91344705054) | 18/18 passed | exact identity, locked install, complete build, Chromium, focused ESLint, clean tree, exact diff all passed | [`8815924825`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/artifacts/8815924825) | `sha256:80ea42882f0c6ce9255d57d1a21b23e622b8f68aedda9478caacad818c124e4f` | complete success |
| macOS 15 ARM64, Node 22.23.1 | [`91344705071`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/job/91344705071) | 18/18 passed in 32.6s | same declared gates all passed | [`8815562250`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/artifacts/8815562250) | `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54` | complete success |
| Windows Server 2025 x64, Node 22.23.1 | [`91344705088`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/job/91344705088) | 18/18 passed in 34.0s | same declared gates all passed | [`8815574235`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059/artifacts/8815574235) | `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4` | complete success |

## Assertions exercised

The complete 18-test native file proves that the old HTTP shutdown request does not return 200 and MCP remains responsive; a wrong string, wrong version, extra-field object, and inherited-property object are inert; the exact plain-object type/version message sent twice produces one graceful close; IPC disconnect is inert; and the rest of the MCP HTTP lifecycle file remains green.

## Classification

- all three platform results: `target-executed`, exact current head
- complete focused file: passed on all three platforms
- build, browser setup, focused lint, clean tree, and exact diff: passed on all three platforms
- full Playwright repository CI: not run and not claimed
- Node versions outside 22: not run and not claimed
- independent source acceptance: still required

## Packet integrity

Packet head `ca95ff2bc643c040ad48a73bb1dc80cdfc64fe8c` passed Fieldwork integrity in run [`30691135221`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691135221). The latest research transfer requires another integrity run.

## Decision

Disposition is `ISSUE FIRST`. The exact execution gate is cleared. Playwright requires a corresponding issue and prior approval/assignment for substantive contributions, and a newly executed stdin-EOF alternative introduces a maintainer-level ownership choice. Public upstream contact remains unauthorized.
