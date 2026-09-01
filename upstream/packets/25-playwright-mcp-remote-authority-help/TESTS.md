# Tests and receipts — Playwright MCP remote and shared-browser authority

## In simple words

Current exact-source execution validates the revised one-file help candidate against the current public base. Historical exact-target execution establishes the shared/isolated runtime behavior described by the help text. Every claim below is scoped to the evidence that actually ran.

## Exact identities

### Current candidate

- Public base: `microsoft/playwright@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Clean source head: `teamleaderleo/playwright@745b4dea96ac64eeb1e92d9ce4525b995e64909f`
- Execution carrier head: `teamleaderleo/playwright@d173310733d2783347a8572271558f1328b736f7`
- Carrier PR: [`teamleaderleo/playwright#38`](https://github.com/teamleaderleo/playwright/pull/38), closed without merge
- Run: [`30674483330`](https://github.com/teamleaderleo/playwright/actions/runs/30674483330)
- Job: `91298776583`
- Environment: Ubuntu 24.04, Node 22.23.1, Chromium 152.0.7977.8
- Artifact: `8810504057`
- Artifact digest: `sha256:01231f3607e7f56b7e110307fc36c1dfb4aaef7a686b940c8ba34304c23da6bf`

### Historical behavior execution

- Target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`
- Carrier: [`teamleaderleo/fieldwork#375`](https://github.com/teamleaderleo/fieldwork/pull/375)
- Carrier head: `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`
- Run/job: `30633739476` / `91166043729`
- Result: `19/19 passed in 30.4s`
- Artifact: `8794430468`
- Digest: `sha256:e53fc07dbfb1dfecd98e5e4a4227c50e8774fe5fb4bc05f880f3f56c73403235`

### Historical help execution

- Target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`
- Carrier: [`teamleaderleo/fieldwork#377`](https://github.com/teamleaderleo/fieldwork/pull/377)
- Carrier head: `204b96c94dfd2fef3ea4981796b2cb98ceae09a9`
- Run/job: `30634831167` / `91169666445`
- Fieldwork integrity run/job: `30634831152` / `91169666324`
- Artifact: `8794842941`
- Digest: `sha256:d0347ff4a0ed8408f9c5d01b36b703d931bc5bab8e6ac79da373a6bfcb2d0683`

## Current exact-source commands and results

The disposable carrier checked out exact carrier head `d173310733d2783347a8572271558f1328b736f7`, verified that source head `745b4dea96ac64eeb1e92d9ce4525b995e64909f` was its merge base, and enforced this exact source fence:

```sh
git diff --name-only \
  15b1aec478d90f0293dae7b7b6dafd494d9f0154..745b4dea96ac64eeb1e92d9ce4525b995e64909f
# packages/playwright-core/src/tools/mcp/program.ts

git diff --check \
  15b1aec478d90f0293dae7b7b6dafd494d9f0154..745b4dea96ac64eeb1e92d9ce4525b995e64909f
```

All phases passed:

```sh
npm ci
npm run build
node packages/playwright-core/lib/entry/mcp.js --help
npx eslint packages/playwright-core/src/tools/mcp/program.ts
npx playwright install --with-deps chromium
npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium
```

The complete MCP HTTP suite result was:

```text
Running 17 tests using 1 worker
17 passed (31.7s)
```

Generated help was whitespace-normalized and contained all three complete statements:

```text
This protects against DNS rebinding; it does not authenticate clients.
```

```text
Protect non-loopback HTTP with an authenticated reverse proxy or an equivalently access-controlled trusted network boundary.
```

```text
Every accepted client shares and can control the same browser context, including its tabs, cookies, storage, and page state.
```

Evidence class for the current build, help, lint, and HTTP-suite results: `target-executed`.

## Historical behavior matrix

The historical carrier copied the retained Fieldwork controls into exact Playwright source and ran them beside the complete upstream HTTP suite:

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

Configuration:

```text
--port=0 --host=0.0.0.0 --allowed-hosts=* --isolated
```

Two distinct Streamable HTTP clients connected through the runner's non-loopback address. Client 1 navigated to a disposable local page; client 2's tab list did not contain it. Cleanup recorded two deleted HTTP sessions and one closed browser.

Evidence class: `target-executed`.

### Shared remote-equivalent control

Configuration:

```text
--port=0 --host=0.0.0.0 --allowed-hosts=* --shared-browser-context
```

Two distinct clients connected. Client 1 navigated to the disposable page; client 2 saw that page. After client 1 disconnected, client 2 still requested a snapshot. Cleanup recorded two created and deleted sessions and one browser close after the final client.

Evidence class: `target-executed`.

### Directly established behavior

- existing HTTP tests passed on the exact historical target;
- isolated sessions kept tab state separate;
- shared sessions exposed client 1's tab to client 2;
- client 2 continued after client 1 disconnected;
- final-session cleanup closed the browser.

### Source-backed behavior

The shared server factory supplies accepted clients with the same BrowserContext. Cookies, storage, permissions, pages, and related state belong to that context. The retained matrix directly exercised tab visibility and page continuation; cookie and origin-storage readback remain `source-read`, not `target-executed`.

## Historical help-patch gate

The successful historical carrier:

- verified exact Fieldwork and Playwright heads;
- required ordinary zero-fuzz `git apply --check --whitespace=error-all`;
- applied a contextual one-file patch;
- enforced the changed-file fence;
- installed dependencies and built Playwright;
- generated runtime help from the built entrypoint;
- normalized whitespace for semantic assertions;
- passed `git diff --check`;
- uploaded the retained help and JSON receipt.

That receipt established patch feasibility on the historical target. The current run owns the revised wording and current base.

## Failed and repaired executions

| Run | Result | Classification | Repair |
| --- | --- | --- | --- |
| `30633035608` | synthetic merge ref did not match expected branch head; stopped before target install | carrier identity failure | check out and verify exact PR head |
| `30634283260` | zero-context patch rejected before install | patch-carrier failure | add exact surrounding context |
| `30634703157` | build and help succeeded, but literal grep failed after Commander line wrapping | assertion-harness failure | normalize whitespace and assert full phrases |
| `30633739476` | 19/19 behavior matrix passed | target execution | retained |
| `30634831167` | patch, build, generated help, semantic assertions, and hygiene passed | target execution | retained |
| `30674483330` | current exact-source build, help, lint, and 17/17 HTTP suite passed | target execution | retained; carrier closed |

No product conclusion is borrowed from the carrier or assertion-harness failures.

## Evidence table

| Claim | Evidence class | Receipt | Limit |
| --- | --- | --- | --- |
| current diff is one file and three strings | `source-read` | compare `15b1aec...745b4dea` | source identity only |
| current source installs and builds | `target-executed` | run `30674483330`, job `91298776583` | Ubuntu 24.04 / Node 22.23.1 |
| revised text appears in generated runtime help | `target-executed` | same run/job | whitespace-normalized semantic check |
| changed file passes ESLint | `target-executed` | same run/job | focused file lint, not repository-wide lint |
| complete current MCP HTTP suite passes | `target-executed` | same run/job; 17/17 | Chromium on Ubuntu only |
| isolated/shared tab and lifecycle behavior | `target-executed` | run `30633739476`, job `91166043729` | historical target and one platform/browser |
| cookies/storage/page state belong to shared context | `source-read` | shared BrowserContext path | no direct two-client cookie/storage readback |
| authenticated reverse proxy or equivalent boundary is appropriate | `source-read / recommendation` | transport and authority reasoning | deployment path unexecuted |

## Platform and scope limits

- Current and historical target execution use Ubuntu 24.04 and Chromium.
- macOS, Windows, Firefox, and WebKit remain unexecuted for this documentation-only candidate.
- No external site, real account, credential, private browser state, proxy, container deployment, public endpoint, or production system was used.
- No full-repository-gate claim is made. The exact named build, help, lint, and HTTP-suite commands are the claim boundary.
