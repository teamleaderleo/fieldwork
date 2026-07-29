# Repair proposal

## Recommended planner repair

Normalize each unloadable `Deferred` runtime to `Direct` at the final tool-plan boundary, after all native, MCP, app, dynamic, and extension contributors and direct-model-only overrides.

A runtime is planner-unloadable when:

1. request search is disabled by model or provider capability; or
2. the runtime returns no `search_info()` and cannot enter the `tool_search` index.

This preserves deferral for searchable families and exposes only the runtime that would otherwise become unreachable.

## Candidate planner change

Insertion point:

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

The implementation should collect deferred metadata once if `search_info()` can be expensive.

## Required planner test

Assert over the finished `ToolRouter`:

```text
For every registered runtime:
  Direct / DirectModelOnly -> acceptable
  Hidden -> outside this invariant
  Deferred ->
    tool_search is model-visible
    tool_search is registered and executable
    this runtime contributes searchable metadata
```

The current `mcp_and_tool_search_follow_direct_and_deferred_tool_exposure` test leaves an injected deferred runtime unchanged when model search support is false. Replace that outcome with direct exposure or a typed invariant error.

Cover native V1, dynamic host, configured MCP, curated app MCP, extension deferred, missing metadata, no eligible tools, and direct-model-only override.

## Required transport test

Planner validity must survive serialization:

```text
deferred family + logical loader
    => loader appears in the generated wire request
       OR
       previous_response_id carries a verified identical loader manifest
```

Add a Responses Lite test for the first generated turn after startup prewarm:

1. build the logical request and record the sanitized loader/tool digest;
2. serialize the actual incremental request;
3. verify direct loader delivery or a matching inherited manifest receipt;
4. force a full request when inheritance cannot be verified;
5. repeat with reconnect, restart, changed manifest, and non-Lite controls.

A bare `previous_response_id` proves chain identity, not inherited tool availability.

## Zero-result and freshness controls

Keep route existence separate from outcome:

```text
missing loader:
  no effective advertised and executable tool_search
  reject when any family remains deferred

executed zero:
  effective tool_search delivered
  valid invocation
  successful tools=[]
  route invariant passes
```

Add a separate freshness check:

```text
binding_catalogue_digest == deferred_search_index_digest
search_result_generation == current_binding_generation
```

A stale but executable loader receives a typed warning or earlier-layer failure. Direct exposure cannot repair stale catalogue state.

## Saved provenance control

For dynamic tools, record saved and current host generations. A valid loader over an old saved generation satisfies L05 while triggering an L01/L06 provenance warning.

Future host APIs should distinguish:

- omitted: preserve saved declarations;
- empty: clear;
- list: replace;
- mismatch policy: preserve, replace, or reject explicitly.

## Alternative repair

Return `Result<ToolRouter, DeferredDiscoveryInvariantError>` and reject planner-unloadable runtimes. This gives a stronger failure signal and expands signatures through request planning, retries, and compaction.

At the transport boundary, reject incremental reuse or send a full request when inherited manifest verification fails.

## Rejected repairs

- Treat `tool_suggest` as equivalent to `tool_search`.
- Add a loader while omitting the affected family from its index.
- Test only built-in MCP construction.
- Assert only a logical loader name without registered runtime and wire delivery.
- Treat every successful zero-result search as proof of current catalogue convergence.
- Automatically reroute through shell or protocol without authority comparison.
