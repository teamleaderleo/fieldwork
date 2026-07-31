# F239 convergence thesis and reconnect success — 2026-07-31

## The compact conclusion

Codex should preserve explicit facts at every lifecycle boundary instead of collapsing the whole operation into one success flag.

The important facts are:

1. which capability definition authorized the call;
2. which runtime and client binding received it;
3. which logical operation was dispatched;
4. what execution, cancellation, transport, and remote-effect state is known;
5. which result reached the model;
6. whether durable history acknowledged the result;
7. what resume, fork, compaction, rollback, and replay can reconstruct;
8. which process owner retains output and performs cleanup.

A fact from one boundary cannot prove a stronger fact owned by another boundary. The useful source candidates each repair one missing fact or one incorrect owner. This is the portfolio's current convergence thesis and the reason one combined patch remains the losing direction.

Finding state: `comparative-evaluation-active`.

Upstream contact authorized: `no`.

## Reconnect gate cleared

The corrected app-server MCP reload execution completed successfully.

- Source PR: `teamleaderleo/codex#89`.
- Live exact PR head: `51883318c606bfb60444032d16e500d51ff71da0`.
- Exact base: `a01a2d91461a57809e944de7758477b92617ab01`.
- Execution carrier: `teamleaderleo/codex#82@feb0c46d3b88e03c94cb9f07d6ba903205e73f05`.
- Workflow run/job: `30589313367` / `91027881827`.
- Exact receipt: `FIELDWORK_MCP_RECONNECT_EXACT=3/3`.
- V8 canary: run `30589313384`, passed.
- Focused MCP exposure module: passed.
- Clean source publication: passed.

The exact controls establish:

- explicit host MCP configuration reload reconnects a ready client;
- ordinary runtime configuration refresh reuses a healthy unchanged client;
- app-server wire method `config/mcpServer/reload` reaches the production reload owner and causes one additional initialization.

The first app-server fixture used obsolete method `mcpServer/refresh` and was rejected before handler execution. That failure supplied fixture evidence only. The corrected method passed.

## Independent complete-diff review

Review `4824415897` examined the complete three-file diff at live head `51883318c606bfb60444032d16e500d51ff71da0`.

Disposition: `ACCEPT` the bounded explicit-reload reconnect rule; `REPAIR` the acceptance matrix before proposal packaging.

Remaining controls:

- prove exactly one initial initialization;
- prove exactly one replacement initialization;
- retain a bounded quiet interval and prove no third initialization;
- force planning or configuration failure and prove an error, zero reconnect attempts, preservation of the existing client, and no partial publication.

Publication generation, captured ordinary-call authority, cached-before-startup fallback, cancellation, timeout, and remote-effect certainty remain independent findings.

## Current public source relation

Current read-only public Codex head: `4642370542739d5dd080b0c87a9de06a6435d3db`.

The complete compare from `a01a2d91461a57809e944de7758477b92617ab01` to `4642370542739d5dd080b0c87a9de06a6435d3db` contains three commits and zero file overlap with the reconnect source fence:

- `codex-rs/app-server/tests/suite/v2/mcp_tool.rs`;
- `codex-rs/core/src/codex_thread.rs`;
- `codex-rs/core/tests/suite/mcp_tool_exposure.rs`.

The newest public commit refreshes app-server protocol exports. File-disjointness preserves the bounded source conclusion while direct current-head materialization and semantic compatibility review remain proposal gates.

## Coordination status

PR #292 is the active canonical F239 carrier. This note supersedes its earlier exact fields that described reconnect execution as queued and public Codex as `413492cd...`. The canonical `finding.md` should absorb these facts before exact-head acceptance.

PR #297 remains closed and superseded. A matching note was accidentally committed to its old branch before the live successor relationship was observed; it carries no current canonical authority.

Public upstream interaction performed: none.