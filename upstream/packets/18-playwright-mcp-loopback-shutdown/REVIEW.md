# Review — Unit 18 Playwright MCP shutdown authority

## Review subject

- Target: `microsoft/playwright`
- Inspected base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source: `fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: `teamleaderleo/playwright#40`
- Exact fence: `mcp.ts`, `http.ts`, `http.spec.ts`
- Current route: `ISSUE FIRST`
- Public-contact authority: none

## Complete-diff self-review

### `packages/playwright-core/src/entry/mcp.ts`

- Installs the private listener only when `process.send` exists.
- Accepts only a plain ordinary object with exactly two own keys and exact type/version values.
- Removes the listener before emitting SIGINT.
- Main judgment point: whether a test-only control belongs in the general MCP entrypoint and whether it should also require Playwright's under-test marker.

### `packages/playwright-core/src/tools/utils/mcp/http.ts`

- Deletes the special `/killkillkill` branch.
- Leaves Host validation, SSE, streamable HTTP sessions, and ordinary error handling unchanged.
- Main judgment point: whether any supported external workflow relies on the route despite its test-only use in the repository.

### `tests/mcp/http.spec.ts`

- Adds IPC to the test child fixture.
- Proves the old HTTP request is inert.
- Proves wrong string/version, extra fields, and inherited properties are inert.
- Proves duplicate valid delivery closes once.
- Proves IPC disconnect is inert.
- Retains the real-browser graceful shutdown receipt.

No unrelated source, workflow, dependency, lock, generated, or formatting change remains in the net diff.

## Exact-current execution

Workflow `30690674059` passed unchanged source `e99e97da...` on Ubuntu 24.04, macOS 15, and Windows 2025. Each platform passed exact identity/fence, locked install, complete build, Chromium, all 18 native MCP HTTP tests, focused ESLint, clean tree, and exact diff.

- Ubuntu: job `91344705054`, artifact `8815924825`
- macOS: job `91344705071`, artifact `8815562250`
- Windows: job `91344705088`, artifact `8815574235`

Full repository CI and Node versions outside 22 were not run.

## New alternative requiring judgment

Parent stdin EOF can replace the private IPC message only with a mode-aware design.

- naïve `close` listener: failed on all three platforms in run `30704410449`
- `end` plus global stdin consumption: passed the 17-test HTTP experiment and declared gates on all three platforms in run `30704592268`
- blocker: global consumption begins before stdio transport selection and may discard early stdio MCP protocol bytes

The positive experiment supports discussing owner-pipe lifetime with maintainers; it does not yet replace the canonical source. See `ADJACENT_RESEARCH.md`.

## Claims requiring independent judgment

| Claim or choice | Reviewer question |
| --- | --- |
| Remove the HTTP route entirely | Is `/killkillkill` strictly test machinery, or is there an intended supported external use? |
| Use private parent IPC | Is the entrypoint listener clearer and safer than a mode-aware stdin owner hook? |
| Exact plain-object validation | Is this enough for Node IPC deserialization, or should the listener also require `isUnderTest()`? |
| One-shot listener removal | Can queued duplicate messages create any observable second shutdown path? |
| Test fixture IPC fd | Does adding IPC to every child in this file affect any ordinary test behavior? |
| Stdin alternative | Can it be installed only for HTTP mode without racing stdio input? |

## Evidence limits

- self-review is not independent acceptance;
- full Playwright repository CI has not run;
- only Node 22 was exercised;
- non-test parent embeddings with `process.send` were not exercised;
- stdin alternative lacks stdio early-message and disconnect controls;
- upstream maintainer preference and issue approval are unknown.

## Reviewer disposition

`ISSUE FIRST`

Reason: the canonical candidate has a clean three-file diff and complete exact-current three-platform focused execution. The remaining decision is contribution direction and ownership mechanism, which belongs in Playwright's issue-first approval process.

Clearing conditions before an authorized PR:

1. independent complete-diff acceptance;
2. maintainer direction on IPC versus mode-aware stdin ownership;
3. squash source history and prove tree equivalence or rerun declared gates;
4. refresh upstream base and duplicate search;
5. explicit public-contact authority and Playwright assignment/approval.

Suggested independent response:

- `Accept unit 18 for issue-first discussion at e99e97da...`
- or `Revise unit 18: <specific compatibility, ownership, or test concern>`
