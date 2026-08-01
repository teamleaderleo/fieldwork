# Unit 18 continuation handoff

## Asked

Prepare only upstream unit 18 from Fieldwork issue #435, reconstruct every linked record, create the assigned packet and a clean owned-fork source branch when possible, preserve all evidence and drafts in GitHub, and avoid public upstream contact.

## Examined

- Fieldwork packet instructions and repository rules, including `START_HERE.md`, `AGENTS.md`, `CHARTER.md`, `CODE_FIRST.md`, `PLAIN_LANGUAGE.md`, `METHOD.md`, `REFERENCE_POLICY.md`, `REVIEWING.md`, `COORDINATION.md`, `upstream/README.md`, and `upstream/INDEX.md`
- owning issue #404 and comments
- characterization PR #405
- comparison PR #410
- direct source PR `teamleaderleo/playwright#37`
- platform carriers #414 and #419
- proxy discriminator #416
- parent-IPC candidate #423
- parent-IPC platform carrier #425
- one-shot hardening #430
- hardened platform carrier #432
- current exact-head execution carrier #455
- prior upstream merged PR #40551 / commit `4a80eed396071d6ed15a74c32723f2bc66849988`
- current public Playwright head `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Playwright contribution guidance requiring a corresponding issue and prior approval/assignment for substantive changes

## Strongest supported finding

The special MCP HTTP shutdown route grants process termination authority to any non-browser caller accepted by listener and Host policy. Direct loopback restriction fails through a local proxy. Parent-owned IPC removes network shutdown authority while preserving the native MCP HTTP lifecycle behavior exercised by the complete focused file.

## Canonical artifacts

- Packet directory: `upstream/packets/18-playwright-mcp-loopback-shutdown/`
- Packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Packet PR: [`teamleaderleo/fieldwork#451`](https://github.com/teamleaderleo/fieldwork/pull/451)
- Source base: `fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Source candidate: `fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Net source fence: exactly three files, with incidental comment/newline churn absent
- Current execution carrier: [`teamleaderleo/fieldwork#455@0323aeaadc391575b572e869258e5e1ac3c4652c`](https://github.com/teamleaderleo/fieldwork/pull/455)
- Current workflow: [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059)

## Failed and losing hypotheses

- Fixed POST/header as authorization: disproved by exact non-browser request.
- Host validation as authorization: protects DNS rebinding and can intentionally accept remote Hosts.
- Direct loopback peer as original-client identity: disproved by local proxy execution.
- Environment capability as final design: viable fallback, superseded because IPC removes the route.
- Bare IPC string/persistent listener: cross-platform viable, superseded by one-shot structured message.
- Matching type/version object as one exact message: review found it accepted extension fields and inherited properties.

## Current exact-head execution

Source `e99e97da2acfc6c1a67749bc749e1d0cb71b5607` has now executed unchanged on two platforms:

- macOS 15 ARM64, Node 22.23.1: exact identity and three-file fence, `npm ci`, complete `npm run build`, Chromium installation, complete native MCP HTTP file, focused ESLint, clean tree, and exact diff all passed; 18/18 tests in 32.6s; artifact `8815562250`; digest `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54`.
- Windows Server 2025 x64, Node 22.23.1: the same gates all passed; 18/18 tests in 34.0s; artifact `8815574235`; digest `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4`.
- Ubuntu 24.04 job `91344705054`: queued before runner allocation; no source execution and no product failure.

The current native test includes rejection of the old HTTP request, wrong string, wrong version, extra-field object, and inherited-property object; duplicate valid delivery closes once; IPC disconnect is inert.

## Integrity

Packet head `7fe2bb3b619e6b1675c260d0304fd262eca71f1f` passed Fieldwork integrity in run `30675345841`. The updated packet must complete a new integrity run after this evidence transfer.

## Current disposition

`EXECUTE`

Reason: exact-head macOS and Windows evidence is green, while Ubuntu remains queued. No product defect has appeared. The next route after Ubuntu success or an explicit reviewed carry-forward decision is `ISSUE FIRST`, not a direct public pull request.

## Remaining blockers in order

1. Complete Ubuntu exact-head execution or record an explicit reviewed carry-forward decision.
2. Complete Fieldwork integrity at the updated packet head.
3. Obtain independent complete-diff review and final acceptance.
4. Squash the seven-commit source history before any authorized submission, then prove exact tree equivalence or rerun declared gates.
5. Obtain Playwright issue approval/assignment.
6. Obtain separate explicit authority before any public issue, pull request, comment, or reaction.

Full Playwright repository CI and Node versions outside 22 remain evidence limits rather than claimed coverage.

## Next action

Inspect workflow `30690674059`. If Ubuntu starts, classify setup, runner, and product outcomes separately. If it passes, transfer its exact job, artifact, digest, test count, and gate results into `CURRENT_EXECUTION.md`, `TESTS.md`, `REVIEW.md`, and the packet README; move disposition to `ISSUE FIRST`; close execution carrier #455 after proving the workflow is absent from the canonical source and packet branches. If Ubuntu does not start, preserve the queue state and seek an explicit platform carry-forward review rather than silently treating it as passed.

Public upstream interaction performed: `none`.
