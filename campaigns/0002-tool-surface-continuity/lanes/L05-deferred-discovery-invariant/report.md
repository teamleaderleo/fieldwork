## In simple words

A tool may be hidden from the first model request only when that same request gives the model a working way to load it. The pinned Codex source couples this rule correctly for built-in configured MCP tools, curated app tools, and native multi-agent V1 tools. The final planner still accepts deferred dynamic or extension tools when `tool_search` is unavailable, and it silently drops any deferred runtime whose `search_info()` cannot be built. Those tools stay registered for dispatch while the model receives neither the tool nor a loader.

The lane adds a request-state matrix and an executable invariant probe. The probe accepts direct tools, searchable deferred tools, genuinely absent families, and a discovery call that successfully returns zero matches. It rejects four states: deferred dynamic tools without search, deferred extension tools without search, deferred tools missing searchable metadata, and `tool_suggest` presented as the only route to an already registered deferred tool.

## Scope and claim

- Fieldwork issue: #40
- Campaign: #31
- Lane: `campaigns/0002-tool-surface-continuity/lanes/L05-deferred-discovery-invariant/`
- Claim supported: request-level exposure and executable discovery invariants across native, MCP, app, dynamic, and extension families
- Boundary: model behaviour after a valid tool has been delivered remains outside this lane
- Upstream interaction: read-only

## Evidence pins

| Source | Revision | Retrieved | Label |
|---|---|---|---|
| Fieldwork campaign synthesis base | `aa72bd513f6664dc67517dabd9b03b4f051d8460` | 2026-07-30 | repository fact |
| OpenAI Codex public source | `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc` | 2026-07-30 | primary source |
| Campaign comparison fork | `2b7b93081361b77f8ddaceaf362a09765b4153bf` | campaign-provided | repository fact |
| Codex issue #33608 | issue state retrieved 2026-07-30 | 2026-07-30 | reported observation |
| Codex issue #33609 | issue state retrieved 2026-07-30 | 2026-07-30 | reported observation |

Primary source links:

- [`spec_plan.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs)
- [`mcp_tool_exposure.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/mcp_tool_exposure.rs)
- [`dynamic.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/handlers/dynamic.rs)
- [`tool_search.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/handlers/tool_search.rs)
- [`tool_executor.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/tools/src/tool_executor.rs)
- [`model_info.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/models-manager/src/model_info.rs)
- [`models.json`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/models-manager/models.json)
- [Observed report #33608](https://redirect.github.com/openai/codex/issues/33608)
- [Observed report #33609](https://redirect.github.com/openai/codex/issues/33609)

## Mechanism map

`search_tool_enabled` is the conjunction of model metadata (`supports_search_tool`) and provider support for namespace tools. Built-in multi-agent V1 tools use that value to choose `Deferred` or `Direct`. Configured MCP and curated app tools receive the same value and choose `Deferred` or `Direct` together.

The final planner then scans every registered `Deferred` runtime, calls `search_info()`, and creates `tool_search` only when search is enabled and at least one search entry exists. Direct tools become model-visible; deferred tools remain registered and initially invisible.

Two independent paths can bypass the built-in coupling:

1. Dynamic host tools read their own `defer_loading` field and select `Deferred` without consulting request search capability.
2. Extension contributors can return `ToolExposure::Deferred` directly.

A third failure appears when a deferred runtime returns `None` from `search_info()`. The planner filters it out. Another searchable family may still create `tool_search`, yet the omitted family can never appear in search results.

## Model, profile, and configuration findings

All eight bundled model entries at the public pin advertise `supports_search_tool: true`: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.2`, and `codex-auto-review`.

Missing model metadata deserializes `supports_search_tool` as false. Unknown model slugs use fallback metadata with the field set to false. Default configured providers and Amazon Bedrock advertise namespace-tool support at this pin. A custom provider can lower that capability.

`code_mode.direct_only_tool_namespaces` converts a direct or deferred namespace to `DirectModelOnly`, which satisfies the callable-route requirement. `code_mode.excluded_tool_namespaces` changes nested code-mode exposure and does not repair an unavailable request loader.

The legacy `tool_search` and `tool_search_always_defer_mcp_tools` feature flags are removed compatibility flags at this pin. Effective search eligibility comes from model and provider capabilities. `tool_suggest` remains separately gated by Apps, Plugins, and ToolSuggest features and serves plugin recommendation/install flows.

## Strongest supported finding

The public source contains a generic request-planning invariant gap even though its built-in MCP/app constructor is defensive. Any dynamic or extension runtime may remain `Deferred` while `search_tool_enabled` is false. Any deferred runtime may also be excluded from discovery when `search_info()` returns `None`. In both cases the runtime is registered for dispatch and omitted from the initial model-visible request, with no executable route that can expose it.

The existing `mcp_and_tool_search_follow_direct_and_deferred_tool_exposure` test demonstrates the first state: it injects a deferred runtime, disables model search capability, confirms `tool_search` is absent, and leaves the deferred runtime uncorrected. The test therefore records the gap without asserting the desired invariant.

## Observed reports and source relation

Issues #33608 and #33609 report Codex 0.144.5 sessions where `gpt-5.6-sol` had configured MCP functions marked deferred while the request lacked `tool_search`; comparison models received the native loader. These reports are evidence of the same request-level failure class.

The pinned public catalogue now advertises search support for `gpt-5.6-sol`, so this lane cannot identify the exact private or remote profile mutation that produced those sessions. The source-level invariant remains useful because it prevents any model catalogue, provider capability, dynamic tool, or extension contributor from recreating an unloadable deferred state.

## Invariant

For each family in the finished request/router pair:

```text
present + Direct/DirectModelOnly
    => accept

present + Deferred
    => require an advertised, registered, executable loader
    => require loader semantics that expose existing deferred tools
    => require this family to contribute searchable metadata

absent
    => accept
```

`tool_search` executed with `tools=[]` satisfies route availability. The model had a callable loader and the loader produced a valid zero-match result. Absence means the request never advertised an executable loader.

## Retained result

Command:

```sh
python3 run_invariant.py fixtures/deferred-surfaces.json --output results/latest.json
```

Result:

```text
12 cases
8 accepted
4 rejected
0 expectation mismatches
exit 0
```

The four rejected cases are the intended negative fixtures:

- `dynamic-deferred-search-disabled`
- `extension-deferred-search-disabled`
- `deferred-missing-search-metadata`
- `deferred-tool-suggest-only`

## Repair proposal

Normalize each unloadable deferred runtime to `Direct` at the final planner boundary. Run the normalization after all tool contributors and direct-model-only overrides, and before building `tool_search` and code-mode entrypoints.

A runtime stays deferred only when request search is enabled and its own searchable metadata exists. This preserves prompt savings for valid families and exposes only the tools that would otherwise become unreachable.

A typed planner error is the stricter alternative. It requires broader signature changes through request planning, retry, and compaction paths. The compatibility-first direct-exposure repair fits the present API and the expected behaviour in issue #33608.

## Negative results

- The built-in configured MCP and curated app constructor already falls back to direct exposure when search is unavailable.
- Native multi-agent V1 already follows the same coupling.
- Bundled model metadata at the pin does not reproduce a search-disabled `gpt-5.6-sol`.
- Provider defaults and Bedrock retain namespace-tool support.
- `tool_suggest` cannot load an existing deferred runtime.
- An empty discovery result does not imply an absent discovery tool.

## Uncertainty

The exact runtime model profile, catalogue override, or host transform behind the 0.144.5 reports is unavailable in the public source. The synthetic probe validates the request-state invariant and repair policy; it does not compile or run the proposed Rust test against upstream. Transport serialization belongs to lane L03, and catalogue freshness/convergence belongs to lane L04.

## Durable artifacts

- `report.md` — findings, evidence labels, scope, and uncertainty
- `matrix.md` — family/model/provider/configuration matrix
- `fixtures/deferred-surfaces.json` — direct, deferred, absent, and zero-result fixtures
- `run_invariant.py` — executable invariant checker
- `results/latest.json` — retained run result
- `repair-proposal.md` — planner repair and upstream test proposal
- `commands.md` — revisions, reads, commands, and execution record
