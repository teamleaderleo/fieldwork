# Commands and retrieval log

## Revisions

- Fieldwork campaign base at initial lane work: `aa72bd513f6664dc67517dabd9b03b4f051d8460`
- L05 merged PR #59 head: `0b10d2e94e61f07a7e24127d9bb7952b82645185`
- Public Codex source: `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`
- Campaign comparison fork: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Cross-lane review date: 2026-07-30

## Public source reads

All OpenAI/Codex actions remained read-only.

```text
codex-rs/core/src/tools/spec_plan.rs
codex-rs/core/src/tools/spec_plan_tests.rs
codex-rs/core/src/mcp_tool_exposure.rs
codex-rs/core/src/tools/handlers/dynamic.rs
codex-rs/core/src/tools/handlers/tool_search.rs
codex-rs/core/src/tools/handlers/tool_search_spec.rs
codex-rs/core/src/tools/registry.rs
codex-rs/tools/src/tool_executor.rs
codex-rs/models-manager/src/model_info.rs
codex-rs/models-manager/models.json
codex-rs/protocol/src/openai_models.rs
codex-rs/model-provider/src/provider.rs
codex-rs/model-provider/src/amazon_bedrock/mod.rs
codex-rs/features/src/lib.rs
openai/codex issues #33608 and #33609
```

## Cross-lane reads

```text
#35 / PR #61 — lifecycle provenance
#37 / PR #58 — HTTP, WebSocket, and startup prewarm
#38 / PR #64 — compaction and call/result identity
#39 / PR #62 — MCP/app catalogue convergence
#43 — diagnostics gate and receipt scope
#44 / PR #60 — fallback authority
#46 / PR #57 — ChatGPT coexistence trial
#31 / PR #51 — campaign synthesis
```

## Retained invariant runs

From the lane directory:

```sh
python3 run_invariant.py fixtures/deferred-surfaces.json --output results/latest.json
python3 run_invariant.py fixtures/cross-lane-surfaces.json --output results/cross-lane.json
```

Original pack:

```text
exit=0
case_count=12
accepted=8
rejected=4
mismatches=0
passed=true
```

Cross-lane pack:

```text
exit=0
case_count=4
accepted=3
rejected=1
warnings=2
mismatches=0
passed=true
```

Aggregate: 16 cases, 11 accepted, 5 intended rejections.

Additional rejected fixture:

```text
mcp-deferred-logical-loader-wire-omitted
```

Warning fixtures:

```text
mcp-deferred-stale-catalogue-zero-results: stale_discovery_catalogue
dynamic-deferred-stale-saved-generation: stale_saved_provenance
```

## Proposed future Codex commands

```sh
cargo test -p codex-core tools::spec_plan::tests::deferred_tools_require_executable_discovery_or_direct_exposure
cargo test -p codex-core tools::handlers::tool_search::tests::executed_search_with_zero_results_is_distinct_from_missing_loader
cargo test -p codex-core responses_websocket::tests::responses_lite_first_generated_turn_delivers_or_verifies_loader_manifest
cargo test -p codex-core mcp_tool_cache::tests::search_index_generation_matches_current_binding_catalogue
```

These are proposals and were not run against upstream.
