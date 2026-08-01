# Unit 18 continuation handoff

## Asked

Prepare only upstream unit 18 from Fieldwork issue #435, reconstruct every linked record, create the assigned packet and a clean owned-fork source branch when possible, preserve all evidence and drafts in GitHub, and avoid public upstream contact.

## Examined

- Fieldwork instructions and packet workflow on `p0/435-upstream-packet-workflow@920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
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
- prior upstream merged PR #40551 / commit `4a80eed396071d6ed15a74c32723f2bc66849988`
- current public Playwright head `15b1aec478d90f0293dae7b7b6dafd494d9f0154`

## Strongest supported finding

The special MCP HTTP shutdown route grants process termination authority to any non-browser caller accepted by listener and Host policy. Direct loopback restriction fails through a local proxy. Parent-owned IPC removes network shutdown authority and preserved the complete native MCP HTTP lifecycle suite on Ubuntu, macOS, and Windows in the retained predecessor generation.

## Retained artifacts

- Packet directory: `upstream/packets/18-playwright-mcp-loopback-shutdown/`
- Packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Source base: `fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Source candidate: `fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: `teamleaderleo/playwright#40`
- Net source fence: three files, with incidental comment/newline churn removed

## Failed and losing hypotheses

- Fixed POST/header as authorization: disproved by exact non-browser request.
- Host validation as authorization: protects DNS rebinding and can intentionally accept remote Hosts.
- Direct loopback peer as original-client identity: disproved by local proxy execution.
- Environment capability as final design: viable fallback, superseded because IPC removes the route.
- Bare IPC string/persistent listener: cross-platform viable, superseded by one-shot structured message.
- Matching type/version object as one exact message: review found it accepted extension fields and inherited properties.

## Current source increment

The current source validator requires a plain object with prototype `Object.prototype`, exactly two own keys, and exact type/version. The native test sends extra-field and inherited-property variants and requires MCP to remain responsive before sending the valid message twice.

## Unresolved uncertainty

- Exact current-head execution has not run.
- Source history still requires squash before any authorized submission.
- Full Playwright repository CI has not run.
- Maintainer preference and issue approval are unknown.

## Blockers

1. Run current-head build, complete native MCP HTTP suite, focused ESLint, and diff checks.
2. Repeat or explicitly review carry-forward of the Ubuntu/macOS/Windows matrix.
3. Obtain independent complete-diff review.
4. Follow Playwright's issue-first approval policy before any upstream PR.
5. Public upstream interaction remains unauthorized.

## Next decision

Keep disposition `EXECUTE`. Do not redesign the authority model unless exact current-head execution fails or current upstream source/maintainer policy supplies a narrower existing test primitive.
