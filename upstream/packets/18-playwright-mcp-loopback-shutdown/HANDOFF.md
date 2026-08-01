# Unit 18 continuation handoff

## Asked

Prepare only upstream unit 18 from Fieldwork issue #435, reconstruct every linked record, create the assigned packet and a clean owned-fork source branch when possible, preserve all evidence and drafts in GitHub, avoid public upstream contact, and continue researching nearby approaches when the candidate became executable.

## Strongest supported finding

The special MCP HTTP shutdown route grants process termination authority to any non-browser caller accepted by listener and Host policy. Direct loopback restriction fails through a local proxy. The canonical parent-owned IPC candidate removes network shutdown authority while preserving the complete native MCP HTTP lifecycle file across Ubuntu, macOS, and Windows.

## Canonical artifacts

- Packet directory: `upstream/packets/18-playwright-mcp-loopback-shutdown/`
- Packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Packet PR: [`teamleaderleo/fieldwork#451`](https://github.com/teamleaderleo/fieldwork/pull/451)
- Canonical finding: [`teamleaderleo/fieldwork#404`](https://github.com/teamleaderleo/fieldwork/issues/404)
- Source base: `fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source: `fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Net source fence: exactly three files
- Exact-current execution carrier: [`teamleaderleo/fieldwork#455@0323aeaadc391575b572e869258e5e1ac3c4652c`](https://github.com/teamleaderleo/fieldwork/pull/455)
- Exact-current workflow: [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059)

## Exact-current result

Source `e99e97da2acfc6c1a67749bc749e1d0cb71b5607` passed unchanged on Ubuntu 24.04, macOS 15, and Windows Server 2025. Every platform passed exact identity and three-file fence verification, locked install, complete build, Chromium, all 18 tests in `tests/mcp/http.spec.ts`, focused ESLint, clean tree, and exact diff.

- Ubuntu: job `91344705054`, artifact `8815924825`, digest `sha256:80ea42882f0c6ce9255d57d1a21b23e622b8f68aedda9478caacad818c124e4f`
- macOS: job `91344705071`, artifact `8815562250`, digest `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54`
- Windows: job `91344705088`, artifact `8815574235`, digest `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4`

Packet head `ca95ff2bc643c040ad48a73bb1dc80cdfc64fe8c` passed Fieldwork integrity in run `30691135221`. The latest packet update requires a fresh integrity result.

## New approach research

### Parent stdin EOF

A new experiment attempted to replace the private IPC message with the already-piped parent stdin lifetime.

- research source PR: [`teamleaderleo/playwright#41`](https://github.com/teamleaderleo/playwright/pull/41)
- first head `1d6ec11...`: failed on all three platforms because parent EOF emits readable `end`, while the watchdog listened for `close`
- repaired head: `86d32569b47fd9f6e98c11517d1699cea5a2465a`
- carrier: [`teamleaderleo/fieldwork#494@2e32e643cdc6af0a322d49499b0cece3ee9e0699`](https://github.com/teamleaderleo/fieldwork/pull/494)
- workflow `30704592268`: complete success on Ubuntu, macOS, and Windows; Ubuntu ran 17/17 in 21.5s

The repair listens for stdin `end` and consumes stdin. It proves that mode-aware stdin ownership is viable for HTTP, but it is not promoted because the watchdog runs before transport selection. Globally consuming stdin can race the stdio MCP transport and discard early protocol input. See `ADJACENT_RESEARCH.md`.

### Nearby leads

- `packages/playwright-core/src/cli/driver.ts` and `packages/playwright/src/runner/testServer.ts` also use stdin `close` as parent-lifetime ownership. These are source-read leads requiring focused reproductions.
- MCP exits code 0 for SIGINT/SIGTERM while the general process launcher uses conventional SIGINT code 130 and escalation behavior. Treat this as a separate policy investigation.
- The canonical IPC listener could be additionally gated by Playwright's test marker, but that would move the fully executed head and requires another matrix.

## Current disposition

`ISSUE FIRST`

The implementation and exact-current execution gates are cleared. The remaining design decision is whether maintainers prefer the fully tested strict parent-IPC hook, a mode-aware owner-stdin hook, or removal of the lifecycle test primitive. Playwright's current contribution process requires issue approval and assignment before a substantive PR.

## Remaining blockers in order

1. Obtain independent complete-diff review and final acceptance.
2. Prepare a concise issue-first decision surface describing the current route and stdin alternative.
3. Squash the seven-commit canonical source history before any authorized submission, then prove exact tree equivalence or rerun declared gates.
4. Refresh the public upstream base and duplicate search immediately before contact.
5. Obtain Playwright issue approval/assignment.
6. Obtain separate explicit authority before any public issue, pull request, comment, or reaction.

Full Playwright repository CI and Node versions outside 22 remain evidence limits rather than claimed coverage.

## Next action

Run Fieldwork integrity at the latest packet head, obtain independent review, and keep all upstream-facing activity unposted until explicit authority. Do not replace the canonical IPC branch with the stdin experiment unless a mode-aware design is built and stdio early-message/disconnect controls pass.

Public upstream interaction performed: `none`.
