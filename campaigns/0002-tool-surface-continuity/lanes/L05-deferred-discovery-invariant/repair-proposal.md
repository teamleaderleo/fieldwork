# Repair proposal

## Goal

Preserve Codex's intended deferred-discovery architecture while preventing the invalid state:

```text
runtime present
+ exposure deferred
+ no usable mode-specific route
= unreachable runtime
```

The repair must distinguish Direct mode, Code Mode, Responses Lite delivery, WebSocket inheritance, and catalogue freshness.

## Mode-aware logical routes

### Direct mode

A deferred runtime is logically reachable only when:

```text
search_enabled
+ runtime.search_info() is present
+ top-level client-executed tool_search is model-visible
+ tool_search is registered and executable
```

### Code Mode

A deferred runtime is logically reachable without nested `tool_search` when:

```text
exec is model-visible and executable
+ runtime is included in ALL_TOOLS
+ runtime is callable through the global tools object
```

Current Code Mode intentionally skips `ToolSpec::ToolSearch`. Do not treat that omission as a planner failure while the `ALL_TOOLS` route is complete.

## Recommended planner repair

Normalize only logically unloadable `Deferred` runtimes to `Direct` after all native, MCP, app, dynamic, and extension contributors and direct-model-only overrides, but before the mode-specific model surface is finalized.

A runtime is logically unloadable when:

1. its mode-specific discovery mechanism is disabled or unavailable;
2. it returns no searchable/runtime metadata required by that mechanism; or
3. the final Code Mode runtime catalogue does not contain the deferred runtime.

This preserves deferral for valid families and exposes only the runtime that would otherwise become unreachable.

## Candidate planner structure

```rust
add_tool_sources(&context, &mut planned_tools);
apply_direct_model_only_namespace_overrides(turn_context, &mut planned_tools);
normalize_logically_unloadable_deferred_tools(turn_context, &mut planned_tools);
append_tool_search_executor(&context, &mut planned_tools);
prepend_code_mode_executors(&context, &mut planned_tools);
validate_mode_specific_deferred_routes(turn_context, &planned_tools)?;
```

A possible Direct-mode normalization helper remains:

```rust
fn normalize_direct_mode_unloadable_deferred_tools(
    turn_context: &TurnContext,
    planned_tools: &mut PlannedTools,
) {
    if matches!(effective_tool_mode(turn_context), ToolMode::CodeMode | ToolMode::CodeModeOnly) {
        return;
    }

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

Code Mode requires a separate finished-catalogue validation because `search_info()` alone does not prove that the runtime entered `ALL_TOOLS`.

## Required logical tests

Assert over the finished router and mode-specific surface:

```text
Direct / DirectModelOnly
    -> model-visible through the effective delivered surface

Deferred + Direct mode
    -> searchable metadata
    -> top-level tool_search advertised
    -> tool_search registered and executable
    -> runtime returned by the search index

Deferred + Code Mode
    -> exec advertised and executable
    -> runtime listed in ALL_TOOLS
    -> runtime callable through the global tools object

Hidden
    -> outside this invariant
```

Required cases:

- configured MCP;
- curated app MCP;
- native multi-agent V1;
- dynamic host runtime;
- extension-contributed runtime;
- missing `search_info()`;
- search-disabled model/provider combination;
- Code Mode with complete `ALL_TOOLS` and no nested `tool_search`;
- Code Mode missing the deferred runtime from `ALL_TOOLS`;
- direct-model-only namespace override.

## Required transport invariant

Logical validity must survive serialization and incremental reuse:

```text
effective mode-specific surface
    => complete manifest appears in the generated request
       OR
       previous_response_id carries a verified identical manifest
```

A bare `previous_response_id` proves chain identity, not tool-manifest identity.

Add a Responses Lite/WebSocket integration test for the first generated turn after startup prewarm:

1. build the logical effective surface;
2. record a sanitized manifest digest;
3. serialize the actual generated WebSocket request;
4. when the delta omits the manifest, require a matching inherited-manifest receipt;
5. force a full request when the receipt is absent or mismatched;
6. have the simulated model invoke the route, not merely inspect request JSON;
7. repeat with reconnect, restart, changed manifest, non-Lite HTTP, and resumed compacted history controls.

## Required end-to-end model-visible tests

### Direct Responses Lite

```text
additional_tools contains the ordinary client tools
+ top-level client-executed tool_search remains usable when required
+ deferred search result returns the target runtime
+ target runtime executes
```

### Code Mode Responses Lite

```text
additional_tools contains exec
+ exec description/runtime exposes ALL_TOOLS
+ deferred target appears in ALL_TOOLS
+ JavaScript invokes tools[target]
+ target runtime executes
```

This test prevents a false repair that injects nested `tool_search` while leaving the actual runtime catalogue broken.

## Zero-result and freshness controls

Keep route existence separate from outcome:

```text
missing route:
  no effective mode-specific discovery path
  reject while any runtime remains deferred

executed zero:
  effective route delivered
  valid invocation
  successful empty result
  route invariant passes
```

Add a separate freshness check:

```text
binding_catalogue_digest == deferred_runtime_catalogue_digest
search_result_generation == current_binding_generation
```

A stale but executable route receives a typed warning or earlier-layer failure. Promoting to direct exposure cannot refresh a stale catalogue.

## Saved provenance control

For dynamic tools, record saved and current host generations. A valid route over an old saved generation satisfies this lane's reachability invariant while triggering a lifecycle warning.

Future host APIs should distinguish:

- omitted: preserve saved declarations;
- empty: clear;
- list: replace;
- mismatch policy: preserve, replace, or reject explicitly.

## Alternative strict repair

Return a typed error from finished planning or request construction:

```rust
Result<ToolRouter, DeferredDiscoveryInvariantError>
Result<ResponseCreateWsRequest, ToolManifestInheritanceError>
```

This is stricter than silent promotion and makes the first divergent boundary explicit, but expands signatures through planning, retries, compaction, and resume.

## Rejected repairs

- Make all MCP tools direct.
- Require nested `tool_search` in Code Mode despite a complete `ALL_TOOLS` route.
- Treat top-level `tools: null` as invalid for Responses Lite.
- Disable WebSocket incremental reuse globally.
- Add a loader while omitting the affected runtime from its index/catalogue.
- Test only built-in MCP construction.
- Assert only a logical loader name without executing the model-visible route.
- Treat every successful zero-result search as proof of current catalogue convergence.
- Automatically reroute through shell, protocol, browser, connector, or subagent without authority comparison.

## Fieldwork executable model

The zero-dependency `rust-probe/` crate encodes the repair split:

```text
PromoteToDirect(runtime)  -> logical route absent
SendFullManifest          -> transport inheritance unverified
RebuildCatalogue          -> route exists but generation is stale
```

It also locks the intended case that Code Mode remains valid without nested `tool_search` when `exec` and `ALL_TOOLS` are complete.
