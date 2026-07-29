# Commands and retrieval log

## Revisions

- Fieldwork campaign base at initial lane work: `aa72bd513f6664dc67517dabd9b03b4f051d8460`
- L05 merged PR #59 head: `0b10d2e94e61f07a7e24127d9bb7952b82645185`
- Original public Codex pin: `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`
- Meta-review public Codex pin: `a05bcda3dbd68729caa2f11027b7f43974fda298`
- Campaign comparison fork: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Review date: 2026-07-30

## Public source reads

All OpenAI/Codex actions remained read-only.

```text
codex-rs/core/src/tools/spec_plan.rs
codex-rs/core/src/tools/spec_plan_tests.rs
codex-rs/core/src/mcp_tool_exposure.rs
codex-rs/core/src/tools/handlers/dynamic.rs
codex-rs/core/src/tools/handlers/tool_search.rs
codex-rs/core/src/tools/registry.rs
codex-rs/tools/src/tool_executor.rs
codex-rs/tools/src/code_mode.rs
codex-rs/tools/src/code_mode_tests.rs
codex-rs/code-mode-protocol/src/description.rs
codex-rs/core/src/client.rs
codex-rs/models-manager/models.json
```

Design and report reads:

- [Codex PR #29486: use tool search for MCP tools by default](https://redirect.github.com/openai/codex/pull/29486)
- [Codex PR #27946: use input items for Responses Lite tools](https://redirect.github.com/openai/codex/pull/27946)
- [Codex PR #23605: hide deferred tools from the Code Mode prompt](https://redirect.github.com/openai/codex/pull/23605)
- [Codex PR #31745: retain shared MCP types for deferred tools](https://redirect.github.com/openai/codex/pull/31745)
- [Codex issue #33679: Responses Lite hides custom MCP tools](https://redirect.github.com/openai/codex/issues/33679)
- [Codex issue #35751: resumed compacted thread loses Code Mode tools on WebSocket](https://redirect.github.com/openai/codex/issues/35751)
- [Codex issue #31894: Responses Lite does not expose exec](https://redirect.github.com/openai/codex/issues/31894)
- [Codex issue #32086: deferred MultiAgent V1 tools become unreachable](https://redirect.github.com/openai/codex/issues/32086)
- [Codex issue #33609: Sol hides discovered MCP tools](https://redirect.github.com/openai/codex/issues/33609)
- [Codex issue #19425: custom MCP tools absent from Desktop threads](https://redirect.github.com/openai/codex/issues/19425)
- [Codex issue #32101: Code Mode omits ranked tool search](https://redirect.github.com/openai/codex/issues/32101)

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

## Retained Python invariant runs

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

## Rust contract probe

The local analysis container did not contain `rustc` or `cargo`, so compilation was delegated to the repository's GitHub Actions runner rather than claimed locally.

Commands executed by `.github/workflows/l05-rust-probe.yml`:

```sh
cargo fmt --check
cargo test --all-targets --locked
```

Successful run:

```text
workflow: L05 Rust probe
run_id: 30484711557
job_id: 90687370218
runner: ubuntu-24.04
format: passed
integration tests: 8 passed; 0 failed; 0 ignored
```

The passing cases are:

```text
code_mode_all_tools_is_valid_without_nested_tool_search
code_mode_missing_all_tools_rejects_deferred_runtime
deferred_runtime_without_search_metadata_is_promoted_only_as_needed
direct_mode_tool_search_keeps_deferred_mcp_reachable
responses_lite_additional_tools_counts_as_direct_delivery
search_disabled_promotes_deferred_runtime_without_disabling_direct_tools
stale_catalogue_is_separate_from_route_existence
websocket_incremental_reuse_requires_matching_manifest_receipt
```

The repository integrity workflow and external-reference policy also passed on the corrected branch state.

## Proposed future upstream Codex commands

```sh
cargo test -p codex-core tools::spec_plan::tests::deferred_tools_require_mode_specific_executable_route
cargo test -p codex-core code_mode_only_guides_all_tools_search_and_calls_deferred_app_tools
cargo test -p codex-core responses_websocket::tests::responses_lite_first_generated_turn_delivers_or_verifies_effective_manifest
cargo test -p codex-core responses_websocket::tests::resumed_compacted_history_preserves_code_mode_runtime_manifest
cargo test -p codex-core mcp_tool_cache::tests::search_index_generation_matches_current_binding_catalogue
```

These upstream commands are proposals and were not run against OpenAI/Codex.
