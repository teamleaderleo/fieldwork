# Local reverse-proxy shutdown authority discriminator

## Result

`test-capability` wins this topology. `loopback-only` does not identify the end
client once a local reverse proxy terminates the TCP connection and opens a new
loopback connection to MCP.

## Exact execution

- Fieldwork branch: `experiment/410-playwright-shutdown-proxy-discriminator`
- executed head: `6ad6ff2b25a2ab8d3fd0bb7cbcb0fe8ce03b67f7`
- generated merge: `175c1fa492e258ac3caad98ad5569f9e94ad8868`
- exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`
- runner: Ubuntu 24.04
- Node: 22
- project: Chromium
- Fieldwork integrity: `30656318538` / 1626, success
- discriminator workflow: `30656319708` / 5, success

The previous execution `30653335981` / 2 reached and passed both target
comparisons but failed only focused ESLint. The current head changed test/workflow
formatting only. Run 5 passed verification, installation, complete build,
Chromium installation, candidate controls, proxy topology, focused ESLint, diff
hygiene, receipt assembly, and upload for both candidates.

## Candidate A — loopback-only

- patch: `candidate-loopback-only.patch`
- direct job: `91241456610`
- direct candidate/upstream tests: 19/19 passed
- proxy test: 1/1 passed
- artifact: `8803406788`
- digest: `sha256:85f09ee517eabbc258472a9deeb168f8c4f89fb495f353ac2d125b07c7a87fbb`
- receipt: every named workflow step `success`
- `reusableDiscriminatorEvidence: true`

Observed through the shared local-proxy test:

1. one MCP client created one owned browser page;
2. a Node HTTP proxy listened on the runner's non-loopback IPv4;
3. that proxy relayed the remote-originated shutdown request to MCP over its own
   loopback upstream connection;
4. MCP saw a loopback peer and accepted the fixed POST/header;
5. the request returned HTTP 200 with `Killing process`;
6. MCP exited with code 0;
7. the log recorded one graceful browser close.

This is mechanically correct for direct-peer locality and still loses the
end-client-authority requirement.

## Candidate B — explicit process capability

- patch: `candidate-test-capability.patch`
- direct job: `91241456488`
- upstream HTTP controls under enabled capability: 17/17 passed
- Fieldwork capability controls: 2/2 passed
- proxy test: 1/1 passed
- artifact: `8803413811`
- digest: `sha256:0d2e30c9a05ef11748771c294b8ec0ff4811602a933a188277cff40b672abbb8`
- receipt: every named workflow step `success`
- `reusableDiscriminatorEvidence: true`

Observed through the same proxy without the explicit capability:

1. the relayed shutdown request returned HTTP 404;
2. MCP remained live and responsive to an MCP ping;
3. the owned browser session remained under ordinary client authority until
   controlled cleanup.

Enabling `PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN=1` remains a deliberate process
configuration choice and is covered by the direct positive controls.

## Decision

The parent comparison's provisional loopback selection is reversed.

A direct peer address is transport topology, not end-client identity. A local
reverse proxy can make a remote-originated request appear loopback without
forging an address or bypassing Host validation. Therefore loopback alone cannot
own process shutdown authority in deployments that place a local proxy beside
MCP.

The explicit capability is the selected research direction because ordinary
processes hide the route regardless of accepted Host or proxy topology. It does
not by itself authenticate an individual remote caller; it makes shutdown route
availability an explicit operator-owned process decision.

## Limits

- Linux/Ubuntu local HTTP proxy only;
- no proxy authentication or trusted-forwarded-header design;
- no containers, Windows, macOS, or production deployment;
- no public exploitability, frequency, or harmful-impact claim;
- no target-wide test suite beyond complete build, complete HTTP suite,
  candidate controls, Chromium proxy topology, lint, and diff hygiene;
- no public-upstream review or acceptance.

A later product candidate should make the capability externally visible in
configuration/help, name its deployment consequences, and test Windows/macOS or
retain those platform limits explicitly.

## Workflow retirement

The temporary execution workflow is removed after this durable receipt. The
shared target-native proxy test remains as the reusable discriminator.

No merge, release, deployment, credential use, private browser-state access,
spending, or public-upstream contact is authorized or performed by this result.
