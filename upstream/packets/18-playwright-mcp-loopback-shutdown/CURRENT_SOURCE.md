# Current source generation

## Canonical identity

- Base: `teamleaderleo/playwright:fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Source: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: `teamleaderleo/playwright#40`
- Net fence: exactly three files

## Relation to packet links pinned at `c4c5e2d...`

The earlier packet drafts were written against `c4c5e2db6f0305237be4de4c167dfb2344abb305`. The only later source change removed an unrelated comment rewrite and restored the final newline in `tests/mcp/http.spec.ts`. Production code, test assertions, message controls, and the three-file fence are unchanged. Treat `e99e97d...` as canonical and `c4c5e2d...` as a superseded diff-cleanup predecessor.

## Exact current diff judgment

- `mcp.ts`: one-shot exact parent-IPC message listener
- `http.ts`: HTTP shutdown branch removed
- `http.spec.ts`: IPC fixture and lifecycle/malformed/duplicate/disconnect controls
- unrelated comment churn: absent
- missing-final-newline churn: absent
- workflows, receipts, and evidence files: absent

## Current gate

`EXECUTE`: exact-head build, complete native MCP HTTP suite, focused ESLint, diff check, and platform decision remain pending.
