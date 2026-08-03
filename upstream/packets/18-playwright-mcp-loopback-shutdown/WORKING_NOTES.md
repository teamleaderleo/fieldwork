# Unit 18 working notes

Last checked: 2026-08-03

## What this is

This is Playwright's built-in MCP server and its lifecycle tests, not an implementation of the MCP protocol.

The question is narrow: how can Playwright's own test parent exercise graceful MCP shutdown without giving ordinary HTTP clients process-control authority?

## Simplified decision

Ordinary HTTP must never control process shutdown. The spawning test parent may request shutdown through a channel it already owns.

Two parent-owned candidates worked:

- strict Node IPC with an exact private message;
- readable EOF on the child's stdin pipe.

Parent stdin is preferred because it expresses parent lifetime with less mechanism. It needs no message schema, parser, version, duplicate-delivery rule, or extra IPC descriptor. The critical rule is to consume stdin only after HTTP mode is selected, so MCP stdio bytes remain exclusively owned by `StdioServerTransport`.

## Routes considered

1. Loopback-only HTTP. Rejected because a local proxy can become the final TCP peer without being the original caller.
2. Environment-gated HTTP. Workable, but it retains an opt-in network process-control route.
3. Strict parent IPC. Fully executed and accepted; retained as the polished fallback.
4. Global stdin EOF. HTTP behavior worked, but consuming stdin before transport selection could discard early stdio MCP bytes.
5. Mode-aware parent stdin. Preferred: wait until the stdio branch returns, then consume readable EOF only for HTTP under Playwright's existing test marker.

## Stable fallback

Strict parent IPC:

```text
teamleaderleo/playwright#40
fix/mcp-parent-ipc-shutdown
e99e97da2acfc6c1a67749bc749e1d0cb71b5607
```

Run `30690674059` passed exact identity/fence, locked install, complete build, Chromium, all 18 native HTTP tests, focused ESLint, clean tree, and exact diff on Ubuntu 24.04, macOS 15, and Windows Server 2025. Independent review `4834404331` records `ACCEPT`.

## Final preferred source

```text
teamleaderleo/playwright#44
fix/mcp-http-parent-stdin-native
ab855babc877909f868c0a69c2882db5fe29c50b
base 15b1aec478d90f0293dae7b7b6dafd494d9f0154
tree 5b6a5c6c9977bfafd93fb558f0b0f8f7cf158162
```

The final branch contains one commit and exactly three changed files:

- `packages/playwright-core/src/tools/utils/mcp/http.ts`
- `packages/playwright-core/src/tools/utils/mcp/server.ts`
- `tests/mcp/http.spec.ts`

The executed pre-squash source `1aed5929a40fca90d1edb12d939d814af1c515fc` resolves to the same exact Git tree `5b6a5c6c9977bfafd93fb558f0b0f8f7cf158162`. GitHub reproduced the tested head's tree with a no-op existing-blob entry before the branch moved. History cleanup changed no source or test byte.

Net behavior:

- remove `/killkillkill` from ordinary HTTP;
- leave the stdio branch unchanged;
- after HTTP mode is selected, and only when `isUnderTest()` is true, resume stdin and translate readable EOF into the existing SIGINT watchdog path;
- handle stdin that was already ended;
- replace the old route-driven native shutdown test;
- prove route inertness and MCP liveness before EOF;
- assert one graceful close and process exit code 0;
- set `PWTEST_UNDER_TEST=0`, close stdin, and prove HTTP remains alive and responsive;
- retain immediate stdio connect and ping coverage.

The watchdog is installed before configuration resolution and before `mcpServer.start()`, so the already-ended branch reaches an active SIGINT listener. Its one-shot exit guard makes readable `end`, emitted SIGINT, and later stream `close` idempotent.

Independent final review `4843181024` records `ACCEPT SOURCE / UBUNTU 24 RECEIPT PENDING` and found no source, authority, transport, lifecycle, or native-test defect.

## Exact-tree native execution

Primary carrier:

```text
teamleaderleo/fieldwork#585
ed6c719d5e908c549072f37a44d40cc20a835f5f
run 30804979200
```

Complete success:

- macOS 15 ARM64, job `91658117752`: 19/19 native HTTP tests in 38.3s; artifact `8852400569`; digest `sha256:bce0e20b6263d0b4b2b353eb9baaea7f08bda82d4b7161cede4e7b3d59b73846`;
- Windows Server 2025, job `91658117934`: 19/19 in 34.6s; artifact `8852470792`; digest `sha256:31ad6f085808d22afade66c535623f5580d72b3c630b3e6022b77e550012d240`;
- Ubuntu 22.04.5 supplemental Linux control, carrier `teamleaderleo/fieldwork#587`, run `30805972019`, job `91661312366`: 19/19 in 30.8s; artifact `8852889644`; digest `sha256:652a41381abef8e303c692d07786f446595ade0e4e99b96c4298a81f7b782486`.

Each completed job passed exact identity and three-file fence, locked install, complete build, Chromium setup, the complete native `tests/mcp/http.spec.ts` without exclusions, focused ESLint, clean tree, exact diff, and receipt upload.

The earlier research source with the same mode-aware implementation passed Ubuntu 24.04 before native test integration. The exact native Ubuntu 24.04 jobs remain queued before runner allocation:

- primary matrix job `91658117741`, run `30804979200`;
- Ubuntu-only carrier `teamleaderleo/fieldwork#586@00f0e374adc793326b93a837de93740240765d14`, run `30805606112`;
- `ubuntu-latest` alias carrier `teamleaderleo/fieldwork#588@fab54d6e5794b041d67905b263beb9f3728d7ef6`, run `30806395733`, which records `/etc/os-release` if allocated.

## Current disposition

`ACCEPT SOURCE / EXECUTE UBUNTU 24`

Remaining gates:

1. Complete one exact-tree native Ubuntu 24.04 run.
2. Synchronize the final Ubuntu receipt into PR #44, packet PR #451, and issue #435.
3. Close remaining disposable carriers without merge.
4. Follow Playwright's issue-first approval/assignment process and retain the separate public-contact authorization gate.

## Repository coordination

Fieldwork issue #404 and PRs #410/#416 retain the older environment-capability comparison. This packet retains the later route-removal work. Preserve both by chronology and scope.

Public `microsoft/playwright:main` remains exactly `15b1aec478d90f0293dae7b7b6dafd494d9f0154`.

Public upstream interaction performed: none.
