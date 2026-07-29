# Commands and retrieval log

## Revisions

- Fieldwork campaign base: `aa72bd513f6664dc67517dabd9b03b4f051d8460` (`campaign/31-tool-surface-continuity`, PR #51 head at retrieval)
- Public Codex source: `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`
- Campaign-owned comparison fork pin supplied by campaign: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Retrieval date: 2026-07-30

## Source reads

All OpenAI/Codex actions were read-only. The investigation used GitHub file and issue reads at the pinned revision for:

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

The local container could not resolve `github.com`, so no source checkout or upstream build was performed. GitHub's read connector supplied the pinned source evidence.

## Retained invariant run

From the lane directory:

```sh
python3 run_invariant.py fixtures/deferred-surfaces.json --output results/latest.json
```

Observed exit code:

```text
0
```

Retained result:

```text
case_count=12
accepted=8
rejected=4
mismatches=0
passed=true
```

Rejected fixtures:

```text
dynamic-deferred-search-disabled
extension-deferred-search-disabled
deferred-missing-search-metadata
deferred-tool-suggest-only
```

## Reproduction against a future Codex checkout

The proposed source-level test belongs at the finished router/request boundary. After applying the repair proposal in a writable Codex checkout:

```sh
cargo test -p codex-core tools::spec_plan::tests::deferred_tools_require_executable_discovery_or_direct_exposure
cargo test -p codex-core tools::handlers::tool_search::tests::executed_search_with_zero_results_is_distinct_from_missing_loader
```

These commands are proposals. They were not run against upstream because the assigned work kept OpenAI/Codex read-only and the container had no source checkout.
