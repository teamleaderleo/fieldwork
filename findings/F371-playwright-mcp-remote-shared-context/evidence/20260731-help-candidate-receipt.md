# Playwright MCP HTTP client-authority help candidate receipt

Date: 2026-07-31  
Parent finding: `F371-playwright-mcp-remote-shared-context`  
Evidence class: `target-executed documentation/runtime-help candidate`

## Exact identities

- Fieldwork carrier PR: `#377`;
- exact carrier head: `204b96c94dfd2fef3ea4981796b2cb98ceae09a9`;
- exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`;
- changed target file: `packages/playwright-core/src/tools/mcp/program.ts`;
- target run: `30634831167`;
- target job: `91169666445`;
- Fieldwork integrity: `30634831152`, job `91169666324`;
- artifact: `8794842941`;
- artifact digest: `sha256:d0347ff4a0ed8408f9c5d01b36b703d931bc5bab8e6ac79da373a6bfcb2d0683`.

## Candidate

The retained patch changes three CLI descriptions only:

1. `--allowed-hosts` states that Host checking is DNS-rebinding protection and does not authenticate clients;
2. `--host` states that non-loopback HTTP should use a trusted authenticated network boundary or reverse proxy;
3. `--shared-browser-context` states that every accepted client can observe and control shared tabs, cookies, storage, and page state.

No transport, session, authentication, browser, or default behavior changes.

## Exact gate

The successful run:

- verified exact Fieldwork and Playwright heads;
- required ordinary zero-fuzz, whitespace-clean `git apply --check`;
- applied the patch successfully;
- required the target diff to contain only `packages/playwright-core/src/tools/mcp/program.ts`;
- installed 638 target dependencies;
- built exact Playwright source;
- generated runtime `Playwright MCP --help` from the built entrypoint;
- normalized only whitespace for semantic assertions;
- found all three required authority-boundary phrases;
- passed `git diff --check`;
- assembled and uploaded the generated help and JSON receipt;
- passed Fieldwork integrity.

Generated help retained these statements:

```text
This is DNS-rebinding protection and does not authenticate clients.
```

```text
Non-loopback HTTP should be protected by a trusted authenticated network boundary or reverse proxy.
```

```text
Every accepted client can observe and control the shared tabs, cookies, storage, and page state.
```

## Carrier repair history

### Run 30634283260 — zero-context patch carrier

The first retained patch used one-line zero-context hunks. Ordinary `git apply` rejected the patch before target installation. The artifact was repaired with exact surrounding source context rather than enabling `--unidiff-zero`.

Evidence class: `carrier failure / no target build`.

### Run 30634703157 — line-wrapped help assertion

The repaired patch applied and exact source built. Generated help contained every required sentence, but Commander wrapped two phrases across lines and literal line-based `grep` failed.

The workflow retained the raw help and changed only the assertion method: collapse whitespace, then require the complete semantic phrases.

Evidence class: `target build success / assertion harness failure`.

### Run 30634831167 — final success

Exact patch application, target build, generated help, semantic assertions, receipt upload, and Fieldwork integrity all passed.

## Claim boundary

Established:

- the three-string patch applies cleanly to the exact pinned target;
- target source builds;
- the built runtime help displays all three authority-boundary statements;
- the candidate changes one target file and no runtime behavior.

Not established:

- upstream acceptance;
- compatibility with later Playwright generations;
- production deployment prevalence;
- the need for built-in authentication;
- behavior behind a reverse proxy;
- public exploitability.

No merge, release, deployment, real credential, private browser data, spending, or public upstream interaction occurred.
