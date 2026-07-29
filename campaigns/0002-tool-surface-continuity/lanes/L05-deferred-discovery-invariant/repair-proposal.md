# Repair proposal

## Recommended repair

Normalize each unloadable `Deferred` runtime to `Direct` at the final tool-plan boundary, after all native, MCP, app, dynamic, and extension contributors have been collected and after direct-model-only namespace overrides have run.

A runtime is unloadable when either condition holds:

1. request search is disabled because the model or provider lacks the required capability; or
2. the runtime returns no `search_info()` and therefore cannot enter the `tool_search` index.

This compatibility-first repair preserves deferral for every searchable family and directly exposes only the family that would otherwise become unreachable.

## Candidate planner change

Insertion point in `build_tool_specs_and_registry`:

```rust
add_tool_sources(&context, &mut planned_tools);
apply_direct_model_only_namespace_overrides(turn_context, &mut planned_tools);
normalize_unloadable_deferred_tools(turn_context, &mut planned_tools);
append_tool_search_executor(&context, &mut planned_tools);
prepend_code_mode_executors(&context, &mut planned_tools);
```

Candidate helper:

```rust
fn normalize_unloadable_deferred_tools(
    turn_context: &TurnContext,
    planned_tools: &mut PlannedTools,
) {
    let search_enabled = search_tool_enabled(turn_context);
    for runtime in &mut planned_tools.runtimes {
        if runtime.exposure() != ToolExposure::Deferred {
            continue;
        }
        if search_enabled && runtime.search_info().is_some() {
            continue;
        }
        *runtime = override_tool_exposure(Arc::clone(runtime), ToolExposure::Direct);
    }
}
```

The exact implementation should avoid recomputing expensive metadata where a contributor makes `search_info()` costly. One option is to collect deferred search entries once, return both indexed identities and the handler, then normalize any deferred identity excluded from that set.

## Required invariant test

Add a black-box assertion over the finished `ToolRouter`:

```text
For every registered runtime:
  Direct / DirectModelOnly -> acceptable
  Hidden -> outside this invariant
  Deferred ->
    tool_search must be model-visible
    tool_search must be registered
    tool_search must be executable
    this runtime must contribute searchable metadata
```

The current test `mcp_and_tool_search_follow_direct_and_deferred_tool_exposure` creates a deferred runtime with `supports_search_tool = false` and only asserts that `tool_search` is absent. Replace that expectation with direct exposure, or make router construction return a typed invariant error.

Add family coverage for:

- native multi-agent V1;
- dynamic host tools with `defer_loading=true`;
- configured MCP;
- curated app MCP;
- extension contributor with `Deferred`;
- deferred contributor returning `None` from `search_info()`;
- no eligible tools;
- direct-model-only namespace override.

## Zero-result control

Keep loader presence separate from search outcome:

```text
missing loader:
  no advertised and executable tool_search
  invariant failure when any family remains deferred

executed zero:
  advertised and executable tool_search
  valid invocation
  successful output with tools=[]
  invariant satisfied
```

The production handler already returns an empty successful tool list when its search index is empty or a query has no matches. The invariant should inspect request/router availability before execution and should never infer loader absence from `tools=[]`.

## Alternative repair

Return `Result<ToolRouter, DeferredDiscoveryInvariantError>` and reject any unloadable deferred runtime. This produces a stronger failure signal, though it expands signatures through request planning and retry paths. The direct-exposure repair is smaller and keeps existing sessions usable.

## Rejected repairs

- Treat `tool_suggest` as equivalent to `tool_search`: it recommends or installs plugins and does not expose an existing deferred runtime.
- Add `tool_search` with no metadata for the affected family: the loader would execute yet could never return that family.
- Test only built-in MCP construction: dynamic and extension contributors can select `Deferred` independently.
- Assert only that `tool_search` is named in model-visible specs: a registered executable runtime is also required.
