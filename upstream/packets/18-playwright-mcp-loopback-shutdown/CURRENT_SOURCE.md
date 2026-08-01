# Current source generation

## Canonical identity

- Base: `teamleaderleo/playwright:fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Source: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Net fence: exactly three files
- Public Playwright head checked on `2026-08-01`: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`

## Relation to packet links pinned at `c4c5e2d...`

Earlier packet drafts were written against `c4c5e2db6f0305237be4de4c167dfb2344abb305`. The only later source change removed an unrelated comment rewrite and restored the final newline in `tests/mcp/http.spec.ts`. Production code, test assertions, message controls, and the three-file fence are unchanged. Treat `e99e97d...` as canonical and `c4c5e2d...` as a superseded diff-cleanup predecessor.

## Exact current diff judgment

- `packages/playwright-core/src/entry/mcp.ts`: installs a one-shot parent-IPC listener; accepts only a plain ordinary object with exactly own `type` and `version` keys and exact values; removes the listener before emitting SIGINT.
- `packages/playwright-core/src/tools/utils/mcp/http.ts`: removes the HTTP shutdown branch.
- `tests/mcp/http.spec.ts`: gives the spawned test child an IPC channel and covers the old route, malformed messages, extension fields, inherited properties, duplicate valid delivery, graceful cleanup, and disconnect.
- Unrelated comment churn: absent.
- Missing-final-newline churn: absent.
- Workflows, receipts, and Fieldwork evidence files: absent from the target net diff.

## Exact-head execution

Execution carrier [`teamleaderleo/fieldwork#455`](https://github.com/teamleaderleo/fieldwork/pull/455) pins source head `e99e97da...` and base `15b1aec...`.

- macOS 15 ARM64: 18/18 native MCP HTTP tests passed; locked install, complete build, Chromium, focused ESLint, clean tree, and exact three-file diff passed.
- Windows Server 2025 x64: 18/18 native MCP HTTP tests passed; locked install, complete build, Chromium, focused ESLint, clean tree, and exact three-file diff passed.
- Ubuntu 24.04: queued before runner allocation; no source execution and no product failure yet.

See [`CURRENT_EXECUTION.md`](./CURRENT_EXECUTION.md) for exact run, job, artifact, and digest records.

## History cleanliness

The net source diff is clean, but the branch remains seven commits ahead of its exact base. Those commits include transient preparation and cleanup. Squash to one reviewable commit before any authorized upstream submission, then prove tree equivalence or rerun the declared gates at the resulting exact head.

## Current gate

`EXECUTE`: complete Ubuntu exact-head execution or record an explicit reviewed carry-forward decision. The next contribution route after that gate is `ISSUE FIRST` under Playwright's contribution policy. Independent complete-diff acceptance and public-contact authority remain separate requirements.
