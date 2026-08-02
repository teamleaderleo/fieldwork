# Local reverse-proxy shutdown authority discriminator

Result state: `repair exact-target artifact identity`  
Parent comparison: Fieldwork PR `#410`  
Canonical result PR: Fieldwork PR `#416`  
Upstream contact authorized: `no`

## Result

The explicit process capability is the selected **research direction** for the tested local reverse-proxy topology.

`loopback-only` does not identify the original client once a local reverse proxy terminates the TCP connection and opens a new loopback connection to MCP. The target behavior is established, but the uploaded applied diffs are not self-contained exact-target packages because they omit the copied target-native tests.

The immutable receipt fields `reusableDiscriminatorEvidence: true` are superseded by this durable record with `false` for exact-target replayability. This is an evidence-transfer correction, not a behavioral reversal.

## Exact execution

- Fieldwork branch: `experiment/410-playwright-shutdown-proxy-discriminator`;
- executed head: `6ad6ff2b25a2ab8d3fd0bb7cbcb0fe8ce03b67f7`;
- generated merge: `175c1fa492e258ac3caad98ad5569f9e94ad8868`;
- exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`;
- runner: Ubuntu 24.04;
- Node: 22;
- project: Chromium;
- Fieldwork integrity: `30656318538` / 1626, success;
- discriminator workflow: `30656319708` / 5, success.

The previous execution `30653335981` reached and passed both target comparisons but failed focused ESLint only. Run 5 passed exact verification, installation, complete build, Chromium installation, candidate controls, proxy topology, focused ESLint, target diff hygiene, receipt assembly, and upload for both candidates.

## Candidate A — loopback-only

- patch: `candidate-loopback-only.patch`;
- job: `91241456610`;
- direct candidate/upstream tests: 19/19 passed;
- proxy test: 1/1 passed;
- artifact: `8803406788`;
- digest: `sha256:85f09ee517eabbc258472a9deeb168f8c4f89fb495f353ac2d125b07c7a87fbb`;
- named workflow steps: success;
- behavior evidence class: `target-executed`;
- exact-target replayable artifact: `false`.

Observed through the shared local-proxy test:

1. one MCP client created one owned browser page;
2. a Node HTTP proxy listened on the runner's non-loopback IPv4;
3. that proxy relayed the remote-originated shutdown request to MCP over its own loopback upstream connection;
4. MCP saw a loopback peer and accepted the fixed POST/header;
5. the request returned HTTP 200 with `Killing process`;
6. MCP exited with code 0;
7. the log recorded one graceful browser close.

This is mechanically correct for direct transport-peer locality and loses the end-client-authority requirement when a local proxy is present.

## Candidate B — explicit process capability

- patch: `candidate-test-capability.patch`;
- job: `91241456488`;
- upstream HTTP controls under enabled capability: 17/17 passed;
- Fieldwork capability controls: 2/2 passed;
- proxy test: 1/1 passed;
- artifact: `8803413811`;
- digest: `sha256:0d2e30c9a05ef11748771c294b8ec0ff4811602a933a188277cff40b672abbb8`;
- named workflow steps: success;
- behavior evidence class: `target-executed`;
- exact-target replayable artifact: `false`.

Observed through the same proxy without the explicit capability:

1. the relayed shutdown request returned HTTP 404;
2. MCP remained live and responsive to an MCP ping;
3. the owned browser session remained under ordinary client authority until controlled cleanup.

Enabling `PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN=1` remains a deliberate process configuration choice and is covered by the direct positive controls.

## Artifact inspection and durable override

Direct inspection of artifacts `8803406788` and `8803413811` established that each `*-applied.diff` contains only:

`packages/playwright-core/src/tools/utils/mcp/http.ts`

Neither applied diff contains:

- `tests/mcp/fieldwork-loopback-only.spec.ts` or `tests/mcp/fieldwork-test-capability.spec.ts`;
- `tests/mcp/fieldwork-reverse-proxy.spec.ts`.

The execution workflow copied those files as untracked paths and then ran plain `git diff --binary` without first using `git add -N`. It also did not record a patch SHA-256 or exact changed-file list in the JSON receipt.

Therefore:

- the behavior logs remain valid `target-executed` evidence for the named steps and topology;
- the Fieldwork branch retains the exact patch and test source blobs;
- the uploaded applied diffs are incomplete and not replayable exact-target generations;
- custom conditional evidence strings in the immutable receipts are replaced here by claim-scoped `target-executed` rows tied to actual step status;
- `reusableDiscriminatorEvidence` is **false** for exact-target replayability despite the immutable receipt field saying true;
- no source-promotion claim may rely on those artifacts as complete packages.

## Decision

The parent comparison's provisional loopback selection is reversed for the governing end-client-authority invariant in the tested topology.

A direct peer address is transport topology, not end-client identity. A local reverse proxy can make a remote-originated request appear loopback without forging an address or bypassing Host validation.

The explicit process capability is the selected research direction because ordinary processes hide the route regardless of accepted Host or proxy topology. It does not authenticate an individual remote caller; it makes shutdown-route availability an explicit operator-owned process decision.

The loopback candidate remains retained as a valid direct-peer control and historical losing alternative.

## Required next transition

Choose one exact-target evidence path:

1. rerun a corrected temporary workflow that:
   - uses `git add -N` for both copied tests;
   - asserts the exact changed-file set;
   - records patch SHA-256 and byte identity;
   - uploads a self-contained applied diff and typed receipt; or
2. reconstruct the complete target generation in the later clean selected source carrier from the exact Fieldwork patch/test blobs, then run the target-declared gates there.

After exact-target identity is restored:

- create one clean selected capability composition;
- make the capability visible in configuration/help and document its deployment consequence;
- run focused Windows/macOS coverage where available or retain those limits explicitly;
- refresh exact public target source before any upstream packet is considered.

## Limits

- Linux/Ubuntu local HTTP proxy only;
- no proxy authentication or trusted-forwarded-header design;
- no containers, Windows, macOS, or production deployment;
- no public exploitability, frequency, or harmful-impact claim;
- no target-wide suite beyond complete build, complete HTTP suite, candidate controls, Chromium proxy topology, lint, and diff hygiene;
- no public-upstream review or acceptance.

## Workflow retirement

The temporary execution workflow was removed after execution. The shared target-native proxy test remains as the reusable discriminator source, but the previous uploaded applied diffs remain non-self-contained.

No merge, release, deployment, credential use, private browser-state access, spending, or public-upstream contact is authorized or performed by this result.
