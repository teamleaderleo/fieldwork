# F239 current-evidence reconciliation — 2026-07-31

## Scope

This note reconciles the Codex work completed after the first composed F239 snapshot. It updates execution state, source successors, losing reasons, and the current public-source fence without combining independent technical findings.

Upstream contact authorized: `no`.

## Exact identities

- Composed Fieldwork base reviewed: PR #283 at `c2946c71b7330b74d326deb7af18a5ae55afce99`.
- Current read-only public Codex head: `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`.
- Prior terminal/portfolio source pin: `97576b1794872e342450ebd577123e052ab57626`.
- Current append/deferred/MCP source pin: `a01a2d91461a57809e944de7758477b92617ab01`.
- Public drift `97576b... -> 413492...`: five commits.

A complete GitHub compare shows no changed file in these active source fences:

- terminal retention: `core/src/unified_exec/{process.rs,process_tests.rs,async_watcher.rs,async_watcher_tests.rs}`;
- append acknowledgement: `core/src/session/mod.rs`, `core/src/session/turn_tests.rs`, `thread-store/src/in_memory.rs`;
- deferred exposure: `core/src/tools/spec_plan.rs`, `core/src/tools/spec_plan_tests.rs`;
- MCP publication: `codex-mcp/src/runtime.rs`;
- MCP reconnect source: `core/src/codex_thread.rs`, `core/tests/suite/mcp_tool_exposure.rs`.

The drift changes app-server schemas and account surfaces, rollout normalization, Windows permission/sandbox policy, status, analytics, and path-URI code. This supports a file-disjoint carry-forward classification only. Every proposal still needs complete direct-diff and compatibility review against the current head.

## Candidate reconciliation

### Append acknowledgement

- Execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`.
- Authoritative run: `30583967538`, job `91010830120`.
- Result: source reconstruction, formatting, four exact append controls, complete `codex-thread-store` package, and clean source publication all passed.
- Clean source PR: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`.
- Evidence class: `target-executed` at the published source tree.
- Remaining gate: complete current-head review and compatibility classification.
- Boundary: acknowledgement only; typed `Persisted/Ambiguous`, retry authority, duplicate reconciliation, compaction, replay, and remote-effect settlement remain separate.

### Producer-owned terminal retention

- Reconstruction carrier: `teamleaderleo/codex#53@c4e0de2e54d804d1054afb90c30b7150a774151c`.
- Authoritative Fieldwork run: `30587866332`, job `91023382172`.
- Result: exact refs, reconstruction, `just fmt`, four-file fence, nine uniquely resolved exact controls through `just test`, Codex core library/integration compile gates, exact source export, and artifact upload all passed.
- Exported source commit: `8c7ea38419d790032db459816980e6b4dd38f574`.
- Exported source tree: `563f90ea0b4bec779446aa0ce4497e8011acb0e3`.
- Artifact digest: `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`.
- Materialization carrier: `teamleaderleo/codex#85@965a79cc2cd389aca05c3753f52510ac63a4110a`; workflow `30589829555` pending at this reconciliation.
- Evidence class: `target-executed` for the exported exact source; owned source-branch materialization remains pending.
- Remaining gates: materialize and verify the exact Git object, review the complete four-file diff against current public head, then retire temporary carriers.
- Boundary: normal-close producer retention. Hard termination, Windows containment races, restart reattachment, and remote settlement remain separate findings.

### MCP publication and call authority

- Current publication source: `teamleaderleo/codex#75@c3373c717f3138ff5f0a979d12836f60800d2bcf`.
- Exact publication receipt: run `30584055792`, job `91011123543`, `5/5`; complete `codex-mcp` package passed.
- Publication execution carrier #77 was cleaned to an empty direct diff and closed.
- The full serialized-`ToolInfo` live-rebind carrier #79 failed before source execution and was retired with an empty direct diff.
- Retained direction: captured `PreparedMcpCall` authority for ordinary calls; live rebinding only for cached-before-startup advertisements, with callable-authority equality checked before approval, hooks, rewriting, or dispatch.
- Canonical sibling finding: Fieldwork PR #290 at `809673e507a0dad064620bf765a7108060ab6b16`.
- Evidence class: publication primitive `target-executed`; full live-rebind direction `stopped` with carrier-only failure and source-precedent rejection.

### MCP reconnect

- Current source: `teamleaderleo/codex#76@7e9d80c4965a76b802f02d7bace17ea1c4a8931c`.
- Current app-server carrier: `teamleaderleo/codex#82@feb0c46d3b88e03c94cb9f07d6ba903205e73f05`.
- First run `30584136349`, job `91011387716`: both direct reconnect controls passed `2/2`; the public-route fixture failed before handler execution because it sent obsolete method `mcpServer/refresh`.
- Correct current wire method: `config/mcpServer/reload`.
- Repaired run: `30589313367`, job `91027881827`, queued at this reconciliation.
- Evidence class: direct source behavior `target-executed`; app-server route pending.

### Deferred executable exposure

- Current source PR: `teamleaderleo/codex#81@8f73d8e0bb9a61e7dec7b1367d13649a88615dea` on `a01a2d...`.
- Transferred immutable receipt: run `30580836079`, job `91000366783`; four exact planner controls passed.
- Standalone-host classifier: default worker stack failed with the shared overflow signature; 16 MiB stack passed.
- Source boundary: exposure normalization only. Searchable deferred runtimes stay deferred; runtimes lacking a loader become direct in effective Direct mode.
- Evidence class: target-executed identical source with current file-disjoint renewal.

## Portfolio consequences

1. Append acknowledgement and terminal producer retention have moved from pending execution to exact target-executed source states.
2. Terminal publication is now a Git-object materialization task, not a source-behavior research task.
3. MCP publication has a complete bounded receipt; the broad live-rebind experiment has an evidenced losing reason and should stay retired.
4. Reconnect now has a clean split result: direct boundary proven, public app-server route still executing.
5. Deferred exposure has a current source PR and transferred exact receipt; its stack classifier remains evidence about the test path, not the exposure invariant.
6. The current public-head delta is file-disjoint from all named active source fences, while semantic compatibility review remains required.

## Remaining autonomous work

- verify terminal materialization and close superseded terminal carriers after evidence transfer;
- complete current-head direct-diff review for append, terminal, publication, reconnect, and deferred source PRs;
- settle repaired reconnect app-server execution;
- incorporate PR #290 after exact-head review and keep timeout certainty separate from cancellation delivery;
- split accepted bounded candidates into dedicated canonical findings or stopped records;
- keep receipt-wire/replay work independent from append acknowledgement;
- refresh F239 whenever a source head, execution result, public pin, or losing reason changes.

## Stop and reopening rules

- Do not reopen the full live-rebind direction unless current source removes captured call authority or a counterexample proves cached-only fallback cannot be isolated.
- Reopen terminal source behavior only if materialized Git objects differ from the exported commit/tree, current-head compatibility reveals an overlap, or an exact control regresses.
- Reopen append acknowledgement only if current-head compatibility changes the three-file contract or execution cannot be reproduced from the clean source PR.
- Public upstream interaction remains prohibited without separate exact authorization.
