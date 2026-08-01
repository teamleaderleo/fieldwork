# Tests and receipts — Unit 18 Playwright MCP shutdown authority

## In simple words

The authority model and its alternatives have retained target-native execution. Baseline characterization passed, a local proxy disproved direct loopback identity, and parent-owned IPC passed the complete native MCP HTTP file across Ubuntu, macOS, and Windows in the predecessor generation. The exact current source head has now passed the same complete file and declared gates on macOS and Windows. Ubuntu is queued before runner allocation, so the current disposition remains `EXECUTE`.

For the live exact-head state, start with [`CURRENT_EXECUTION.md`](./CURRENT_EXECUTION.md).

## Exact identities

- Historical executed public base: `368941457a82da112aa8610107e25f4bde94339a`
- Current inspected public base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical current source: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Net source fence: exactly `mcp.ts`, `http.ts`, and `http.spec.ts`
- Current carrier: `teamleaderleo/fieldwork#455@0323aeaadc391575b572e869258e5e1ac3c4652c`
- Current workflow: `30690674059`
- Environments represented: Ubuntu 24.04, macOS 15, Windows 2025; Node 22; Chromium

## Claim-to-evidence matrix

| Claim | Evidence class | Exact receipt | Result | Limit |
| --- | --- | --- | --- | --- |
| accepted non-loopback HTTP request terminates MCP | `target-executed` | PR #405, run `30649849111`, job `91220131763` | 3/3 passed | Ubuntu; deliberately permissive listener/Host configuration |
| direct loopback check blocks a direct remote peer | `target-executed` | PR #410, run `30651626301`, job `91226004779` | 19/19 passed | direct topology only |
| local proxy defeats loopback authority | `integration-executed` | PR #416, run `30656319708`, job `91241456610` | 19/19 direct plus 1/1 proxy passed | one Ubuntu local proxy topology |
| environment capability hides route by default | `target-executed` | PR #416, job `91241456488` | 17/17 plus 2/2 plus 1/1 passed | enabled route remains a network primitive |
| bare parent IPC works cross-platform | `target-executed` | PRs #423/#425, run `30657930500` | 17/17 and declared gates on Ubuntu/macOS/Windows | bare string and persistent listener generation |
| one-shot structured IPC works cross-platform | `target-executed` | PRs #430/#432, run `30659762667` | 18/18 and declared gates on Ubuntu/macOS/Windows | validator accepted extension fields |
| strict exact-own-property generation works on macOS | `target-executed` | PR #455, run `30690674059`, job `91344705071` | 18/18 plus all declared gates passed | macOS 15 ARM64, Node 22.23.1 |
| strict exact-own-property generation works on Windows | `target-executed` | PR #455, run `30690674059`, job `91344705088` | 18/18 plus all declared gates passed | Windows Server 2025 x64, Node 22.23.1 |
| strict exact-own-property generation works on Ubuntu | `runner-pending` | PR #455, job `91344705054` | queued before allocation | no source execution yet |
| complete Playwright repository is green | `not-claimed` | none | not run | focused MCP HTTP file and build only |

## Baseline characterization

Fieldwork PR #405 ran workflow `30649849111` at exact Playwright `368941457a82da112aa8610107e25f4bde94339a`.

Assertions:

- an accepted non-loopback exact POST with `x-pw-mcp-kill: 1` returns 200 and exits through graceful cleanup;
- GET, missing header, and wrong header leave MCP live;
- default Host policy rejects non-loopback before route handling;
- loopback exact request retains behavior.

Receipt: 3/3 passed; job `91220131763`; artifact `8800945684`; digest `sha256:ce7c9a2d02affa71367c2f1fdc56a0a338b2afcb5d50d72d72a0f6a50310cf8b`.

Judgment: listener and Host reachability granted access to the route; the fixed method/header was not caller authorization.

## Losing repair execution

### Direct loopback and capability comparison

- Comparison head: `f40f316224ebb526150fc87fc336486dfdf9f9bd`
- Workflow: `30651626301`
- Loopback job `91226004779`: 19/19 in 30.6s; artifact `8801633779`; digest `sha256:11c19ee26756e11167dc9a0567ce73f975dd0de01e02ee4a19e2bd1c3c9b4c7d`
- Capability job `91226004861`: 17/17 upstream plus 2/2 focused; artifact `8801643332`; digest `sha256:0dcc2345a6d3198bfe205961aa6d8fac0c58f90243ad8700e3c11365fd90dba5`
- Limit: direct topology did not reveal proxy identity loss.

### Local proxy discriminator

- Executed head: `6ad6ff2b25a2ab8d3fd0bb7cbcb0fe8ce03b67f7`
- Workflow: `30656319708`
- Loopback job `91241456610`: 19/19 direct plus 1/1 proxy; artifact `8803406788`; digest `sha256:85f09ee517eabbc258472a9deeb168f8c4f89fb495f353ac2d125b07c7a87fbb`
- Capability job `91241456488`: 17/17 plus 2/2 plus 1/1; artifact `8803413811`; digest `sha256:0d2e30c9a05ef11748771c294b8ec0ff4811602a933a188277cff40b672abbb8`
- Discriminator: the proxy-relayed request appeared loopback and terminated the loopback candidate; the default-disabled capability candidate returned 404 and stayed live.

## Selected parent-IPC execution history

### Bare parent IPC

- Candidate: PR #423 `bcceeadc2c806ab6e60e013d2278b7515339036d`
- Platform carrier: PR #425, workflow `30657930500`
- Ubuntu: job `91246869531`, artifact `8804013479`, digest `sha256:ebf70a898d2821ff1b5f77988bc008926b558bb58b0d2df9992d7c7af16b0cbf`
- macOS: job `91246869639`, artifact `8804012978`, digest `sha256:226ca6682054d8ec7ae241ce5e732740bad467a2246870b5776756c7133b4495`
- Windows: job `91246869591`, artifact `8804032483`, digest `sha256:5d1dd6c6ed51fe99dfab840ee4e55646a2555d3b75720a5aa5c1a3beb4af04e9`
- Result: complete 17-test native file, build, Chromium, focused lint, and exact diff passed on all three platforms.

### Hardened one-shot IPC

- Candidate carrier: PR #430 `59899a28503cbe9d97811cbed103b6fc831e6663`
- Linux workflow/job: `30659209256` / `91251086538`
- Linux result: 18/18; build, focused ESLint, and exact diff passed; artifact `8804497263`; digest `sha256:74fdf6ebb8bfbea1ccda6ab5c26d87bd469003fe0ff26d8f359997af6eeb17c5`
- Cross-platform carrier: PR #432 `481c5b4a912106b4760082a061fe4ed13338bf5a`
- Workflow: `30659762667`
- Ubuntu: job `91252909934`, artifact `8804703627`, digest `sha256:57599b2e736b10426134c424fc0a68b5af29c5bbf2e1875c188cc0dd037c67e7`
- macOS: job `91252909953`, artifact `8804712909`, digest `sha256:415d974f4d1db447b50e41a934102dde08fe9402f0b4c817d64e520749fcd826`
- Windows: job `91252909976`, artifact `8804735269`, digest `sha256:ea70fb39180a87e3cb55d0d43ce771049ed9accfd82dd09ecc5d5fb2cbbc0d8b`
- Result: exact identity, locked install, complete build, Chromium, 18/18 native file, focused ESLint, and exact three-file diff passed on all platforms.
- Review finding after execution: matching type/version objects with extra fields or inherited values were accepted, so exact-message wording was too broad.

## Exact current-head execution

Carrier #455 pins source `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`, base `15b1aec478d90f0293dae7b7b6dafd494d9f0154`, and the exact three-file fence.

Declared per-platform command sequence:

1. verify carrier and source SHAs;
2. verify base exists, `git diff --check`, and exact changed filenames;
3. `npm ci`;
4. `npm run build`;
5. `npx playwright install --with-deps chromium` on Linux or `npx playwright install chromium` elsewhere;
6. `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`;
7. focused `npx eslint` on the three changed files;
8. verify clean source tree, `git diff --check`, and exact changed filenames;
9. upload receipt, test log, binary diff, and commit list.

### macOS 15

- Job: `91344705071`
- Runner: macOS 15.7.7, ARM64
- Node: 22.23.1
- Native result: 18/18 passed in 32.6s
- Other gates: all passed
- Artifact: `8815562250`
- Digest: `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54`

### Windows Server 2025

- Job: `91344705088`
- Runner: Windows Server 2025, x64
- Node: 22.23.1
- Native result: 18/18 passed in 34.0s
- Other gates: all passed
- Artifact: `8815574235`
- Digest: `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4`

### Ubuntu 24.04

- Job: `91344705054`
- State: queued before runner allocation
- Test count: none yet
- Classification: runner queue; no product result

## Current strict assertions

The exact current 18-test file exercises:

- old `/killkillkill` POST/header request does not return 200;
- MCP client remains responsive after that request;
- wrong string is inert;
- wrong version is inert;
- matching object with an extra own field is inert;
- inherited-only matching properties are inert;
- exact plain-object type/version message sent twice yields one graceful close;
- IPC disconnect leaves HTTP operation live;
- ordinary isolated, persistent, multi-client, shared-context, Host, SSE, streamable, roots, and lifecycle cases in the file remain green on completed platforms.

## Setup and harness failure classifications

| Attempt | Failure | Class | Product claim | Resolution |
| --- | --- | --- | --- | --- |
| PR #414 Windows | Bash continuation under PowerShell broke focused lint after tests passed | runner shell | no source failure | PR #419 reran with correct shell |
| PR #425 predecessor run `30657528090` Windows | CRLF prevented patch application before tests | packaging | no source failure | normalized disposable input; replacement passed unchanged candidate bytes |
| PR #430 predecessor `3c3cad4...` | stale unified-diff hunk counts | packaging | no source failure | regenerated carrier; Linux passed |
| PR #455 Ubuntu current | no runner allocation yet | runner queue | no result | keep queued status explicit |

## Ordinary gates and current coverage

| Gate | macOS current | Windows current | Ubuntu current | Broader limit |
| --- | --- | --- | --- | --- |
| exact source/base identity | pass | pass | not started | — |
| `git diff --check` and exact three-file fence | pass | pass | not started | — |
| locked install | pass | pass | not started | dependency audit warnings are not candidate-specific failures |
| complete `npm run build` | pass | pass | not started | full repository test suite not run |
| Chromium installation | pass | pass | not started | other browsers not required by this focused file |
| complete native MCP HTTP file | 18/18 | 18/18 | not started | focused file only |
| focused ESLint | pass | pass | not started | repository-wide lint not run |
| clean source tree after gates | pass | pass | not started | — |

## Reversing and cleanup controls

- The historical exact HTTP request succeeds on baseline; the current candidate rejects it and remains live on completed platforms.
- Malformed/private-message variants leave the client responsive.
- Duplicate valid delivery produces one close.
- IPC disconnect is inert.
- Local proxy distinguishes peer-locality from route absence.
- Message listener is removed before SIGINT.
- No dedicated soak or repeated same-workspace rerun was performed.

## Packet and source cleanup

- Canonical target net diff contains no temporary workflow or evidence file.
- Packet head `7fe2bb3b619e6b1675c260d0304fd262eca71f1f` passed Fieldwork integrity in run `30675345841` before the current evidence transfer.
- Updated packet integrity remains required.
- Execution carrier #455 must be closed after evidence transfer and completion/classification of Ubuntu.
- Source history remains seven commits and requires squash before any authorized submission.

## Remaining gaps

1. Ubuntu exact-current-head execution or explicit reviewed carry-forward.
2. Updated packet integrity.
3. Independent complete-diff acceptance.
4. Source history squash with tree-equivalence proof or rerun.
5. Full Playwright repository CI only if required; it has not run and is not claimed.
6. Node versions outside 22 and non-test parent embeddings remain untested.
7. Playwright issue approval/assignment and explicit public-contact authority.

## Current test judgment

`EXECUTE`

Reason: exact-current-head macOS and Windows execution is fully green; Ubuntu has no product result because the job is still queued. Clearing condition: Ubuntu success or an explicit independently reviewed carry-forward decision, followed by updated packet integrity and independent complete-diff acceptance. The contribution route after that gate is `ISSUE FIRST`.
