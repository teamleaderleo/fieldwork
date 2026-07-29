# Owned-fork implementation review

Review date: 2026-07-30  
Research dossier: PR #77  
Promoted implementation campaign: #85  
Owned-Codex implementation draft: [teamleaderleo/codex#18](https://github.com/teamleaderleo/codex/pull/18)

## Status

The first owned-Codex slice implements the planner-side compatibility repair: promote a deferred runtime to direct exposure when the Direct-mode request cannot provide an executable discovery loader.

The direction is useful, but the draft is not ready and has not produced a validated source commit.

Focused validation run: [teamleaderleo/codex Actions run 30485058646](https://github.com/teamleaderleo/codex/actions/runs/30485058646)

```text
35 planner tests passed
1 planner test failed
deferred_runtime_without_search_metadata_is_direct
```

The workflow stopped before committing the proposed source change.

## Finding 1: the failed fixture is still searchable

The shared `ToolExecutor` contract does not default `search_info()` to `None`. It derives search metadata from function and namespace tool specifications:

- [pinned `ToolExecutor::search_info()` implementation](https://github.com/teamleaderleo/codex/blob/d90ae1208acb88d26832dc5837854f622331407e/codex-rs/tools/src/tool_executor.rs#L71-L74)

The test runtime named `unsearchable_deferred` supplies a normal function specification and does not override `search_info()`. It therefore remains searchable and stays deferred. The observed visible surface still contained `tool_search`, while the runtime itself was absent from the initial direct list.

The fixture must explicitly implement:

```rust
fn search_info(&self) -> Option<ToolSearchInfo> {
    None
}
```

This is a test-construction defect, not evidence that the normalization helper failed.

## Finding 2: the proposed helper is too broad for Code Mode

The draft currently applies one rule in every mode:

```text
Deferred + search disabled or search_info absent
    => Direct
```

That rule is correct for Direct mode, where deferred reachability depends on top-level client-executed `tool_search`.

It is not the correct invariant for Code Mode or Code Mode Only. Those modes intentionally use:

```text
exec
+ ALL_TOOLS
+ global tools runtime
```

A Code Mode runtime can therefore remain deferred and callable even when ranked `tool_search` metadata is absent. Promoting it solely because `search_info()` is absent can expose its full declaration in the initial `exec` guide and undo the intended deferred-schema behavior.

Required split:

1. Restrict search-info normalization to Direct-mode surfaces.
2. Build the Code Mode runtime catalogue without forcing ranked-search metadata.
3. Validate that every deferred Code Mode runtime appears in `ALL_TOOLS` and remains dispatchable through the global runtime.
4. Add a regression proving a Code Mode deferred runtime without ranked-search metadata stays deferred and callable.

Detailed review: [comment on owned-Codex PR #18](https://github.com/teamleaderleo/codex/pull/18#issuecomment-5123037938)

## Correct planner repair

```text
Direct mode:
  deferred + no executable tool_search route
      => promote only the affected runtime to Direct
         OR return a typed planner error

Code Mode:
  deferred + present in exec/ALL_TOOLS/global runtime
      => keep Deferred

  deferred + absent from finished runtime catalogue
      => rebuild, promote, or return a typed invariant error
```

This keeps the optimization for healthy deferred tools and avoids a false repair that merely moves hidden schemas into the prompt.

## Transport work remains separate

Owned-Codex PR #18 deliberately does not change request serialization or response reuse. Campaign #85 still requires a second compiled slice covering:

- logical versus direct-wire manifest digests;
- Responses Lite `additional_tools` delivery;
- startup prewarm and first generated turn;
- verified `previous_response_id` manifest inheritance;
- changed-manifest, reconnect, restart, fresh WebSocket, HTTP, and resumed-compacted-history controls;
- full-manifest fallback when inherited identity is absent or mismatched.

A planner-only success would fix some unreachable-runtime states and improve diagnosis, but it would not explain or repair every reported Sol/Responses Lite failure.

## Coordination assessment

The parallel Campaign #85 work is going in the right general direction: it chose a bounded planner slice rather than making every MCP tool direct. The necessary correction is to make that slice mode-aware and then keep transport verification as a distinct follow-up.

No public OpenAI/Codex issue, comment, reaction, pull request, or code write occurred.