# Tests and receipts — Unit 18 Playwright MCP shutdown authority

## Canonical identity

- Current inspected base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Exact canonical candidate: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Canonical fence: `mcp.ts`, `http.ts`, `http.spec.ts`
- Exact-current workflow: `30690674059`
- Environments: Ubuntu 24.04, macOS 15 ARM64, Windows Server 2025 x64; Node 22.23.1; Chromium

## Claim-to-evidence summary

| Claim | Evidence | Result | Limit |
| --- | --- | --- | --- |
| accepted non-browser HTTP caller can terminate reachable MCP | run `30649849111`, job `91220131763` | 3/3 passed | deliberate Ubuntu non-loopback/wildcard Host setup |
| local proxy defeats direct loopback identity | run `30656319708`, job `91241456610` | direct 19/19 plus proxy 1/1 passed | one Ubuntu local proxy topology |
| parent IPC removes route and preserves lifecycle | run `30657930500` | 17/17 and declared gates on all three platforms | bare message generation |
| one-shot structured IPC works cross-platform | run `30659762667` | 18/18 and declared gates on all three platforms | loose object validator generation |
| strict exact-message canonical candidate works | run `30690674059` | 18/18 and every declared gate on all three platforms | focused MCP HTTP file, Node 22 |
| naïve stdin-close ownership works | run `30704410449` | failed identically on all three platforms | watchdog listened for `close`, parent EOF did not trigger it |
| repaired stdin-EOF ownership works in HTTP experiment | run `30704592268` | 17/17 and declared gates on all three platforms | global stdin consumption has unresolved stdio-race risk |

## Exact-current canonical execution

Each job performed exact checkout/fence verification, `npm ci`, complete `npm run build`, Chromium installation, the complete native MCP HTTP file, focused ESLint, clean-tree verification, exact diff verification, and receipt upload.

| Platform | Job | Test result | Artifact | Digest |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 | `91344705054` | 18/18 and all declared gates passed | `8815924825` | `sha256:80ea42882f0c6ce9255d57d1a21b23e622b8f68aedda9478caacad818c124e4f` |
| macOS 15 ARM64 | `91344705071` | 18/18 in 32.6s and all declared gates passed | `8815562250` | `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54` |
| Windows Server 2025 x64 | `91344705088` | 18/18 in 34.0s and all declared gates passed | `8815574235` | `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4` |

### Canonical assertions

- old POST/header `/killkillkill` request does not return 200;
- MCP remains responsive after the old request;
- wrong string, wrong version, extra-field object, and inherited-property object are inert;
- exact plain-object message initiates graceful shutdown;
- duplicate valid delivery records one graceful close;
- IPC disconnect is inert;
- every other test in the native HTTP file remains green.

## Parent stdin EOF research

### First generation

- source: `1d6ec11b5f06df32ce5b4fa0346af7631216e79c`
- workflow: `30704410449`
- result: Ubuntu, macOS, and Windows all failed the same discriminator after successful setup/build/browser installation
- observation: closing `cp.stdin` did not trigger watchdog `process.stdin.on('close')`

### Repaired generation

- source: `86d32569b47fd9f6e98c11517d1699cea5a2465a`
- carrier: `2e32e643cdc6af0a322d49499b0cece3ee9e0699`
- workflow: `30704592268`
- change: listen for stdin `end` and consume stdin so EOF is observable
- matrix: ordinary `http.spec.ts` controls except the superseded route-based SIGINT case, plus `fieldwork-stdin-close.spec.ts`

| Platform | Result | Artifact | Digest |
| --- | --- | --- | --- |
| Ubuntu 24.04 | 17/17 in 21.5s; build, Chromium, lint, clean diff passed | `8819925107` | `sha256:e05bcd01a8f7d1d43eb516fbc7891cdb310245c68d9d8450420a85f4a9454307` |
| macOS 15 | complete success | `8819927910` | `sha256:b1099fc064a80e1a8db32c6a17e298f0c9018419ed26cb2823a43214e8fc29f9` |
| Windows 2025 | complete success | `8819934140` | `sha256:6833261278e27a3a8b1670bffdc58b2fa9eeaf4f3a03582efe4537fe32600f99` |

### Limit

The watchdog runs before transport mode is chosen. Stdio mode already owns stdin-`end` handling through `StdioServerTransport`. Global `process.stdin.resume()` may put stdin into flowing mode before that transport attaches and discard early protocol bytes. The HTTP result is valid, but the implementation is not promoted without mode-aware placement and stdio controls.

## Ordinary gates and gaps

| Gate | Canonical result |
| --- | --- |
| `git diff --check` | passed on all three platforms |
| focused ESLint | passed on all three platforms |
| complete build | passed on all three platforms |
| complete native MCP HTTP file | 18/18 on all three platforms |
| exact changed-file fence | passed on all three platforms |
| full Playwright repository CI | not run |
| Node versions outside 22 | not run |
| non-test parent embeddings with IPC | not run |
| stdio early-message control for stdin alternative | not run; required before promotion |

## Packet integrity

- packet head `ca95ff2bc643c040ad48a73bb1dc80cdfc64fe8c`: run `30691135221`, success
- latest packet head after adjacent research: fresh integrity run required

## Current test judgment

`ISSUE FIRST`

The exact canonical implementation gate is cleared. Remaining work is independent review, maintainer direction on the ownership mechanism, source-history squash/tree-equivalence proof, and authorization before public contact.
