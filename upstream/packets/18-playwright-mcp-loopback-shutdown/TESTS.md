# Tests and receipts — Unit 18 Playwright MCP shutdown authority

## In simple words

The authority model and its main alternatives have extensive retained execution. Baseline characterization passed, the proxy counterexample reversed loopback selection, and parent-owned IPC passed the complete native MCP HTTP suite on Ubuntu, macOS, and Windows. The final current-source increment adds exact-own-property message rejection and still needs an exact-head run.

## Identity

- Previously executed upstream base: `368941457a82da112aa8610107e25f4bde94339a`
- Current inspected upstream base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Exact current candidate head: `c4c5e2db6f0305237be4de4c167dfb2344abb305`
- Hardened predecessor patch head: Fieldwork PR #430 `59899a28503cbe9d97811cbed103b6fc831e6663`
- Cross-platform carrier head: Fieldwork PR #432 `481c5b4a912106b4760082a061fe4ed13338bf5a`
- Test dates: `2026-07-31`; current source prepared `2026-08-01`
- Environments: Ubuntu 24.04, macOS 15, Windows 2025; Node 22; Chromium

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| accepted remote HTTP request terminates MCP | `target-executed` | PR #405 run `30649849111`, job `91220131763` | 3/3 pass | Ubuntu and deliberate remote-equivalent config |
| direct loopback check blocks direct remote peer | `target-executed` | PR #410 run `30651626301`, job `91226004779` | 19/19 pass | direct peer only |
| local proxy defeats loopback authority | `integration-executed` | PR #416 run `30656319708`, job `91241456610` | 19/19 direct + 1/1 proxy pass | Ubuntu local proxy |
| explicit capability hides route by default | `target-executed` | PR #416 job `91241456488` | 17/17 + 2/2 + 1/1 pass | enabled route remains a network primitive |
| bare parent IPC works cross-platform | `target-executed` | PR #425 run `30657930500` | 17/17 on all three platforms | bare message, persistent listener generation |
| one-shot structured IPC works cross-platform | `target-executed` | PR #432 run `30659762667` | 18/18 on all three platforms | matching type/version accepted extension fields |
| current exact-message validator rejects extra/inherited variants | `target-test-prepared` | `tests/mcp/http.spec.ts@c4c5e2d` | prepared | exact current-head run pending |
| current base is source-disjoint from executed base | `source-read` | compare `3689414...15b1aec` | two commits; candidate paths unchanged | does not replace runtime execution |

## Baseline characterization

### Command or workflow

Fieldwork PR #405 focused target workflow `30649849111` against exact Playwright `368941457a82da112aa8610107e25f4bde94339a`.

### Assertions

- accepted non-loopback exact request returns 200 `Killing process`
- process exits cleanly through graceful cleanup
- GET, missing header, and wrong header leave MCP live
- default Host policy rejects non-loopback before route handling
- loopback exact request retains behavior

### Result

- status: success
- test count: 3/3
- workflow and job: `30649849111` / `91220131763`
- artifact: `8800945684`
- digest: `sha256:ce7c9a2d02affa71367c2f1fdc56a0a338b2afcb5d50d72d72a0f6a50310cf8b`
- observed behavior: listener/Host reachability grants access to the route; fixed method/header is not client authorization

## Candidate-focused tests

### Direct repair comparison

- Exact comparison head: `f40f316224ebb526150fc87fc336486dfdf9f9bd`
- Workflow: `30651626301`
- Loopback job: `91226004779`
- Capability job: `91226004861`
- Loopback result: 19/19 in 30.6s; artifact `8801633779`; digest `sha256:11c19ee26756e11167dc9a0567ce73f975dd0de01e02ee4a19e2bd1c3c9b4c7d`
- Capability result: 17/17 upstream + 2/2 focused; artifact `8801643332`; digest `sha256:0dcc2345a6d3198bfe205961aa6d8fac0c58f90243ad8700e3c11365fd90dba5`
- Coverage limit: direct topology only

### Local proxy discriminator

- Exact executed head: `6ad6ff2b25a2ab8d3fd0bb7cbcb0fe8ce03b67f7`
- Workflow: `30656319708`
- Loopback result: 19/19 direct + 1/1 proxy; job `91241456610`; artifact `8803406788`; digest `sha256:85f09ee517eabbc258472a9deeb168f8c4f89fb495f353ac2d125b07c7a87fbb`
- Capability result: 17/17 + 2/2 + 1/1; job `91241456488`; artifact `8803413811`; digest `sha256:0d2e30c9a05ef11748771c294b8ec0ff4811602a933a188277cff40b672abbb8`
- Observed discriminator: proxy-relayed request appears loopback and shuts down the loopback candidate; default capability candidate returns 404 and remains live
- Coverage limit: one Ubuntu local reverse proxy topology

### Bare parent-owned IPC cross-platform

- Candidate head: PR #423 `bcceeadc2c806ab6e60e013d2278b7515339036d`
- Workflow: PR #425 `30657930500`
- Ubuntu: job `91246869531`, artifact `8804013479`, digest `sha256:ebf70a898d2821ff1b5f77988bc008926b558bb58b0d2df9992d7c7af16b0cbf`
- macOS: job `91246869639`, artifact `8804012978`, digest `sha256:226ca6682054d8ec7ae241ce5e732740bad467a2246870b5776756c7133b4495`
- Windows: job `91246869591`, artifact `8804032483`, digest `sha256:5d1dd6c6ed51fe99dfab840ee4e55646a2555d3b75720a5aa5c1a3beb4af04e9`
- Result: complete 17-test native suite, build, browser setup, lint, and exact diff passed on all platforms
- Harness note: predecessor Windows attempt failed before product execution due CRLF patch application; replacement normalized disposable inputs and passed unchanged candidate bytes

### Hardened one-shot IPC Linux

- Candidate head: PR #430 `59899a28503cbe9d97811cbed103b6fc831e6663`
- Workflow/job: `30659209256` / `91251086538`
- Result: 18/18 native suite; build, focused ESLint, and exact diff passed
- Artifact: `8804497263`
- Digest: `sha256:74fdf6ebb8bfbea1ccda6ab5c26d87bd469003fe0ff26d8f359997af6eeb17c5`
- Controls: old route inert, wrong string/version inert, duplicate exact message one close, disconnect inert
- Review finding: validator allowed extra fields and inherited matching properties despite exact-message wording

### Hardened one-shot IPC cross-platform

- Exact carrier head: PR #432 `481c5b4a912106b4760082a061fe4ed13338bf5a`
- Workflow: `30659762667`
- Ubuntu: job `91252909934`, artifact `8804703627`, digest `sha256:57599b2e736b10426134c424fc0a68b5af29c5bbf2e1875c188cc0dd037c67e7`
- macOS: job `91252909953`, artifact `8804712909`, digest `sha256:415d974f4d1db447b50e41a934102dde08fe9402f0b4c817d64e520749fcd826`
- Windows: job `91252909976`, artifact `8804735269`, digest `sha256:ea70fb39180a87e3cb55d0d43ce771049ed9accfd82dd09ecc5d5fb2cbbc0d8b`
- Result: exact identity, LF-normalized zero-fuzz patch, locked install, complete build, Chromium, 18/18 native suite, focused ESLint, and exact three-file diff passed on all platforms

### Current exact-message increment

- Exact source head: `c4c5e2db6f0305237be4de4c167dfb2344abb305`
- Current base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Added controls: `{ type, version, extra: true }` inert; `Object.create({ type, version })` inert
- Validator: plain object, prototype exactly `Object.prototype`, exactly two own keys, exact type/version
- Result: prepared, not executed
- Coverage limit: source-read plus historical behavior carry-forward only

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | `git diff --check` in retained workflows | passed historically | current head pending |
| lint | focused ESLint on three files | passed on predecessor across three platforms | current head pending |
| typecheck or compile | complete `npm run build` | passed on predecessor across three platforms | current head pending |
| focused package tests | `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium` | 18/18 predecessor on three platforms | current head pending |
| complete target-declared suite | full Playwright repository suite | not run | native MCP HTTP suite only |
| build or generated output | complete Playwright build | passed historically | no generated files |
| platform matrix | Ubuntu 24.04, macOS 15, Windows 2025 | passed historically | exact-own-property increment pending |

## Reversing controls

- baseline exact HTTP request returns 200; candidate exact HTTP request must not return 200 and client remains live
- ordinary MCP HTTP suite passes before and after
- malformed IPC messages leave client responsive
- duplicate valid delivery yields one graceful-close record
- IPC disconnect leaves HTTP client responsive
- local proxy distinguishes peer-locality from route absence

## Soak, leak, and cleanup controls

- iterations: one lifecycle instance per native test run; no dedicated soak
- resources observed: one real browser/context/session and graceful-close log count
- listeners: message listener removed before SIGINT; disconnect test verifies continued HTTP operation
- cancellation or interruption behavior: parent IPC disconnect inert
- immediate rerun result: repeated across three platform jobs, but no explicit same-workspace rerun receipt

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| PR #414 Windows | Bash continuation under PowerShell broke focused lint after 19/19 tests | runner shell | no source behavior failure | PR #419 reran Windows lint/diff correctly |
| PR #425 predecessor `30657528090` Windows | CRLF prevented patch apply before install/tests | packaging | no | normalize clean checkout and disposable patch; replacement passed |
| PR #430 predecessor `3c3cad4...` | stale unified-diff hunk counts | packaging | no | regenerate patch; Linux run passed |

## Checks prepared but not executed

- current source [`tests/mcp/http.spec.ts`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/tests/mcp/http.spec.ts) — extra-field and inherited-property controls await exact-head execution
- current source focused ESLint/build/diff — await exact-head execution

## Platform and integration gaps

- current exact-head Ubuntu/macOS/Windows run
- full Playwright repository CI
- Node versions outside 22
- embedding parent processes that provide IPC outside the Playwright test harness
- authenticated proxy and container topologies become irrelevant to the removed route, though ordinary MCP behavior there remains untested by this unit

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `source compare shows three-file net fence`
- Immediate rerun performed: `no`
- Remaining temporary branches or PRs: historical Fieldwork carriers #423/#425/#430/#432 remain open and should be retired only after durable receipt transfer and workflow-absence proof

## Current test judgment

`EXECUTE`

Reason: the selected authority model has strong historical cross-platform evidence, and current public source is disjoint. The final strict-validator increment changes executable behavior and therefore requires exact-head build, native suite, focused lint, and three-file diff verification before the packet can move to issue-first review.

Clearing condition: run the exact current source head unchanged through the complete native MCP HTTP suite and focused ordinary gates, including Ubuntu/macOS/Windows coverage or an explicit independently reviewed carry-forward decision.
