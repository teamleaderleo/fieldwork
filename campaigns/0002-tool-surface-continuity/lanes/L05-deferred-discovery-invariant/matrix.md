# Deferred tool discovery matrix

Source pin: [`openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)  
Retrieval date: 2026-07-30

## Request-state classes

| Class | Family state | Initial exposure | Executable loader in the same request | Verdict |
|---|---|---:|---:|---|
| Direct exposure | present | `Direct` or `DirectModelOnly` | optional | valid |
| Deferred with discovery | present | `Deferred` | advertised, registered, executable, and able to load this family | valid |
| Deferred without discovery | present | `Deferred` | absent, non-executable, wrong semantics, or missing family metadata | reject or direct-expose |
| Genuinely absent | no eligible runtime | absent | optional | valid |

`tool_search` is the loader for already registered deferred tools. `tool_suggest` recommends or installs plugins and does not satisfy this invariant for an existing deferred runtime.

## Family and control-path map

| Family | Deferral input | Direct path | Deferred path | Discovery route | Source result |
|---|---|---|---|---|---|
| Native multi-agent V1 | `search_tool_enabled(turn)` | search disabled -> `Direct` | search enabled -> `Deferred` | `tool_search` | coupled correctly in built-in planner |
| Native multi-agent V2 | `multi_agent_v2.non_code_mode_only` | `Direct` or `DirectModelOnly` | none at this pin | none required | directly exposed |
| Native dynamic host tools | per-tool `DynamicToolFunctionSpec.defer_loading` | flag false -> `Direct` | flag true -> `Deferred` | `tool_search`, only when request search is enabled | generic gap when flag true and search disabled |
| Configured MCP functions | `search_tool_enabled` passed into `build_mcp_tool_runtimes` | search disabled -> `Direct` | search enabled -> `Deferred` | `tool_search` | coupled correctly in built-in constructor |
| Curated app functions over Codex Apps MCP | same MCP constructor after connector and policy filtering | search disabled -> `Direct` | search enabled -> `Deferred` | `tool_search` | coupled correctly in built-in constructor |
| Extension-contributed tools | contributor-supplied `ToolExposure` | contributor chooses direct | contributor may choose deferred | `tool_search` only when planner enables it and `search_info()` succeeds | generic gap |
| Namespace direct-only override | `code_mode.direct_only_tool_namespaces` | converts `Direct` or `Deferred` to `DirectModelOnly` | none after conversion | none required | valid direct recovery |
| Code-mode excluded namespace | `code_mode.excluded_tool_namespaces` | initial request exposure unchanged | deferred runtime may remain | existing `tool_search` route | affects nested code-mode surface, not request loader eligibility |
| Plugin recommendation | Apps + Plugins + ToolSuggest features and non-empty candidates | install/list tools direct | does not defer existing runtime | `request_plugin_install` / list candidate tool | adjacent mechanism; wrong loader semantics |
| No eligible MCP/app/native runtime | filtering, disabled family, or empty catalogue | absent | absent | none required | genuinely absent |

## Model and provider paths

| Path | Search decision at the pin | Consequence |
|---|---|---|
| Bundled models `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.2`, `codex-auto-review` | all advertise `supports_search_tool: true` | discovery remains eligible when provider namespace tools are supported |
| Model metadata omits `supports_search_tool` | serde default is `false` | built-in MCP/app/V1 native families become direct; dynamic/extension deferred inputs remain hazardous |
| Unknown model slug fallback | explicitly sets `supports_search_tool: false` | same compatibility path |
| Default configured provider | `namespace_tools: true` | model support controls search |
| Amazon Bedrock provider | `namespace_tools: true` | model support controls search |
| Provider implementation returning `namespace_tools: false` | search disabled | built-in families become direct; generic deferred inputs still require normalization |
| Remote/private model catalogue | may differ from bundled metadata | public reports show a `gpt-5.6-sol` request with deferred MCP tools and no `tool_search`; exact private profile remains unavailable |

## Executability matrix used by the retained probe

| Fixture | Class | Expected |
|---|---|---|
| `native-v1-direct-no-search` | direct exposure | accept |
| `native-v1-deferred-tool-search` | deferred with discovery | accept |
| `mcp-direct-no-search` | direct exposure | accept |
| `mcp-deferred-tool-search-zero-results` | deferred with discovery; executed and returned zero | accept |
| `app-direct-no-search` | direct exposure | accept |
| `app-deferred-tool-search` | deferred with discovery | accept |
| `dynamic-deferred-search-disabled` | deferred without discovery | reject |
| `extension-deferred-search-disabled` | deferred without discovery | reject |
| `deferred-missing-search-metadata` | loader exists but cannot index this family | reject |
| `deferred-tool-suggest-only` | wrong discovery semantics | reject |
| `genuinely-absent-family` | genuinely absent | accept |
| `direct-model-only-override` | direct exposure | accept |
