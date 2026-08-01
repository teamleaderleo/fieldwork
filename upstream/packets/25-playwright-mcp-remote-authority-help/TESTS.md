# Tests and receipts — Playwright MCP remote and shared-browser authority

## In simple words

Two evidence layers support this contribution. Historical exact-target execution established the runtime behavior that the help text describes. A current owned-fork carrier validates the revised one-file candidate against the current public source through installation, build, generated help, focused lint, and the complete MCP HTTP suite.

## Exact identities

### Current candidate

- Public base: `microsoft/playwright@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Clean source head: `teamleaderleo/playwright@745b4dea96ac64eeb1e92d9ce4525b995e64909f`
- Execution carrier head: `teamleaderleo/playwright@d173310733d2783347a8572271558f1328b736f7`
- Carrier PR: [`teamleaderleo/playwright#38`](https://github.com/teamleaderleo/playwright/pull/38)
- Workflow run: [`30674483330`](https://github.com/teamleaderleo/playwright/actions/runs/30674483330)
- Environment: Ubuntu 24.04, Node 22, Chromium

### Historical behavior execution

- Target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`
- Fieldwork carrier: [`teamleaderleo/fieldwork#375`](https://github.com/teamleaderleo/fieldwork/pull/375)
- Carrier head: `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`
- Run: [`30633739476`](https://github.com/teamleaderleo/fieldwork/actions/runs/30633739476)
- Job: `91166043729`
- Result: `19/19 passed in 30.4 seconds`
- Artifact: `8794430468`
- Digest: `sha256:e53fc07dbfb1dfecd98e5e4a4227c50e8774fe5fb4bc05f880f3f56c73403235`

### Historical help execution

- Target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`
- Fieldwork carrier: [`teamleaderleo/fieldwork#377`](https://github.com/teamleaderleo/fieldwork/pull/377)
- Carrier head: `204b96c94dfd2fef3ea4981796b2cb98ceae09a9`
- Run: [`30634831167`](https://github.com/teamleaderleo/fieldwork/actions/runs/30634831167)
- Job: `91169666445`
- Fieldwork integrity run: `30634831152`, job `91169666324`
- Artifact: `8794842941`
- Digest: `sha256:d0347ff4a0ed8408f9c5d01b36b703d931bc5bab8e6ac79da373a6bfcb2d0683`

## Current execution plan

The disposable workflow on PR #38 performs these phases:

```sh
# exact identity and changed-file fence
git merge-base HEAD 745b4dea96ac64eeb1e92d9ce4525b995e64909f
git diff --name-only \
  15b1aec478d90f0293dae7b7b6dafd494d9f0154..745b4dea96ac64eeb1e92d9ce4525b995e64909f
git diff --check \
  15b1aec478d90f0293dae7b7b6dafd494d9f0154..745b4dea96ac64eeb1e92d9ce4525b995e64909f

npm ci
npm run build
node packages/playwright-core/lib/entry/mcp.js --help
npx eslint packages/playwright-core/src/tools/mcp/program.ts
npx playwright install --with-deps chromium
npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium
```

Generated help is whitespace-normalized and must contain these complete phrases:

```text
This protects against DNS rebinding; it does not authenticate clients.
```

```text
Protect non-loopback HTTP with an authenticated reverse proxy or an equivalently access-controlled trusted network boundary.
```

```text
Every accepted client shares and can control the same browser context, including its tabs, cookies, storage, and page state.
```

## Current result

State: `queued`  
Run: `30674483330`  
Job: pending  
Artifact: pending  

This section must be replaced with exact step outcomes, job ID, test count, artifact ID, and digest after completion.

## Historical behavior matrix

The carrier copied one Fieldwork test file into exact Playwright source and ran it beside the complete upstream HTTP suite:

```sh
npm ci
npm run build
npx playwright install --with-deps chromium
npm run test-mcp \
  tests/mcp/http.spec.ts \
  tests/mcp/fieldwork-remote-shared.spec.ts \
  -- --project=chromium
```

### Isolated remote-equivalent control

Server configuration:

```text
--port=0 --host=0.0.0.0 --allowed-hosts=* --isolated
```

The test replaced the presented wildcard host with the runner's non-loopback IPv4, connected two distinct Streamable HTTP clients, navigated client 1 to a disposable local page, and verified client 2's tab list did not contain that page.

Cleanup assertions:

- two HTTP sessions deleted;
- one browser closed.

Evidence class: `target-executed`.

### Shared remote-equivalent control

Server configuration:

```text
--port=0 --host=0.0.0.0 --allowed-hosts=* --shared-browser-context
```

The test connected two distinct Streamable HTTP clients, navigated client 1 to the disposable local page, verified client 2 could see the page, disconnected client 1, and verified client 2 could still request a snapshot.

Lifecycle assertions:

- two HTTP sessions created;
- two HTTP sessions deleted;
- one browser closed after the final client.

Evidence class: `target-executed`.

### Directly established behavior

- default upstream HTTP tests passed unchanged at the exact historical target;
- explicit remote-equivalent isolated sessions kept tab state separate;
- explicit shared sessions exposed client 1's tab to client 2;
- client 2 continued after client 1 disconnected;
- final-session cleanup closed the browser.

### Source-backed behavior

The shared server factory supplies accepted clients with the same BrowserContext. Cookies, storage, permissions, pages, and related state belong to that context. The retained matrix directly exercised tab visibility and page continuation; cookie and origin-storage readback remain source-backed rather than target-executed.

## Historical help-patch gate

The successful historical carrier:

- verified exact Fieldwork and Playwright heads;
- required ordinary zero-fuzz `git apply --check --whitespace=error-all`;
- applied a contextual one-file patch;
- enforced the changed-file fence;
- installed dependencies;
- built Playwright;
- generated runtime `--help` from the built entrypoint;
- normalized whitespace for semantic assertions;
- passed `git diff --check`;
- uploaded help and JSON receipt.

The current candidate changes the historical wording, so this receipt establishes feasibility and prior target compatibility while the current carrier owns the revised wording.

## Failed and repaired executions

| Run | Result | Classification | Repair |
| --- | --- | --- | --- |
| `30633035608` | workflow compared synthetic merge ref with expected branch head; stopped before target install | carrier identity failure | checkout and verify exact PR head |
| `30634283260` | zero-context patch rejected by ordinary `git apply` before install | patch-carrier failure | add exact surrounding context |
| `30634703157` | target built and help contained the text, but literal line grep failed after Commander wrapping | assertion-harness failure | normalize whitespace, assert complete semantic phrases |
| `30633739476` | 19/19 behavior matrix passed | target execution | retained |
| `30634831167` | patch, build, generated help, semantic assertions, and hygiene passed | target execution | retained |

No product conclusion is borrowed from the carrier failures.

## Evidence table

| Claim | Evidence class | Receipt | Limit |
| --- | --- | --- | --- |
| current diff is one file and three strings | `source-read` | compare `15b1aec...745b4dea` | source identity only |
| current source builds | `target-executed` when current run passes | run `30674483330` | Ubuntu 24.04 / Node 22 |
| revised text appears in generated runtime help | `target-executed` when current run passes | run `30674483330` | whitespace-normalized semantic check |
| changed file passes ESLint | `target-executed` when current run passes | run `30674483330` | focused file lint, not repository-wide lint |
| current complete MCP HTTP suite passes | `target-executed` when current run passes | run `30674483330` | Chromium on Ubuntu only |
| isolated/shared tab and lifecycle behavior | `target-executed` | run `30633739476`, job `91166043729` | historical target and one platform/browser |
| cookies/storage/page-state belong to shared context | `source-read` | shared BrowserContext creation path | no direct two-client readback control |
| authenticated reverse proxy is an appropriate deployment boundary | `source-read / recommendation` | deployment composition reasoning | proxy behavior unexecuted |

## Platform and scope limits

- Current and historical target execution use Ubuntu 24.04 and Chromium.
- macOS, Windows, Firefox, and WebKit remain unexecuted for this candidate.
- The candidate changes documentation strings only; cross-browser behavioral reruns add little discrimination beyond the complete HTTP suite.
- No external site, real account, credential, private browser state, proxy, container deployment, public endpoint, or production system was used.
- No full repository gate claim is made. The current carrier names its exact build, help, lint, and HTTP-suite commands.
