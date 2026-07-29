# Deferred tool discovery matrix

Source pin: [`openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)  
Retrieval and cross-lane review date: 2026-07-30

## Request and delivery classes

| Class | Family state | Planner exposure | Effective loader delivery | Verdict |
|---|---|---:|---:|---|
| Direct exposure | present | `Direct` or `DirectModelOnly` | optional | valid |
| Deferred with direct discovery | present | `Deferred` | advertised, registered, executable, searchable for this family, directly delivered | valid |
| Deferred with verified inheritance | present | `Deferred` | same loader manifest inherited through a verified previous-response receipt | valid |
| Deferred without discovery | present | `Deferred` | absent, non-executable, wrong semantics, missing family metadata, or omitted from wire without verified inheritance | reject or direct-expose |
| Genuinely absent | no eligible runtime in the current authoritative input | absent | optional | valid |
| Internally consistent but stale | present in an older binding or saved generation | any valid route for that stale state | route invariant passes; emit adjacent warning | diagnose at earlier lifecycle/catalogue layer |

`tool_search` loads already registered deferred tools. `tool_suggest` recommends or installs plugins and does not satisfy this invariant.

## Family and control-path map

| Family | Deferral input | Direct path | Deferred path | Discovery route | Result |
|---|---|---|---|---|---|
| Native multi-agent V1 | `search_tool_enabled(turn)` | search disabled -> `Direct` | search enabled -> `Deferred` | `tool_search` | coupled correctly in built-in planner |
| Native multi-agent V2 | `multi_agent_v2.non_code_mode_only` | `Direct` or `DirectModelOnly` | none at this pin | none required | directly exposed |
| Native dynamic host tools | per-tool `defer_loading` | false -> `Direct` | true -> `Deferred` | `tool_search` when request search exists | generic planner gap; saved generation may also be stale |
| Configured MCP functions | `search_tool_enabled` passed to `build_mcp_tool_runtimes` | search disabled -> `Direct` | search enabled -> `Deferred` | `tool_search` | constructor safe; wire and catalogue controls still required |
| Curated app functions | same MCP constructor after filtering | search disabled -> `Direct` | search enabled -> `Deferred` | `tool_search` | constructor safe; wire and catalogue controls still required |
| Extension-contributed tools | contributor-supplied exposure | contributor chooses direct | contributor may choose deferred | `tool_search` only when enabled and indexed | generic planner gap |
| Namespace direct-only override | config override | converts to `DirectModelOnly` | none after conversion | none required | valid direct recovery |
| Code-mode excluded namespace | exclusion list | initial request unchanged | may remain deferred | existing route | affects nested surface only |
| Plugin recommendation | Apps + Plugins + ToolSuggest | install/list tools direct | does not defer existing runtime | install/recommend tools | wrong loader semantics |
| No authoritative runtime | disabled, filtered, or current catalogue empty | absent | absent | none required | genuinely absent |
| Stale thread binding | reused client/binding | old direct tools | old deferred tools | loader over old index | L04 warning, not loader absence |
| Sticky saved dynamic generation | recovered `SessionMeta` | saved direct tools | saved deferred tools | loader over saved generation | L01 warning, not loader absence |

## Model, provider, and transport paths

| Path | Decision | Consequence |
|---|---|---|
| Bundled models at the pin | all eight advertise `supports_search_tool: true` | discovery eligible when namespace tools are supported |
| Missing model field | serde default false | built-in families direct; dynamic/extension deferral needs normalization |
| Unknown model slug fallback | search support false | same compatibility path |
| Default configured provider | namespace tools true | model metadata controls search |
| Amazon Bedrock | namespace tools true | model metadata controls search |
| Custom provider with namespace tools false | search disabled | built-ins direct; generic deferred inputs hazardous |
| Remote/private model catalogue | may differ | public reports show the symptom; exact profile unavailable |
| Full HTTP or full WebSocket request | tool manifest sent directly | planner and wire can be compared directly |
| Responses Lite incremental request | may send suffix plus `previous_response_id` | require verified inherited loader manifest |
| Reconnect/restart/changed tool manifest | full request control in L02 | useful discriminator |
| Stable endpoint with changed server catalogue | client may be reused | loader can be executable over a stale index |

## Executability matrix

| Fixture | Class | Expected |
|---|---|---|
| `native-v1-direct-no-search` | direct | accept |
| `native-v1-deferred-tool-search` | deferred, direct loader | accept |
| `mcp-direct-no-search` | direct | accept |
| `mcp-deferred-tool-search-zero-results` | executed current-catalogue zero | accept |
| `app-direct-no-search` | direct | accept |
| `app-deferred-tool-search` | executed current catalogue | accept |
| `dynamic-deferred-search-disabled` | loader absent | reject |
| `extension-deferred-search-disabled` | loader absent | reject |
| `deferred-missing-search-metadata` | family omitted from index | reject |
| `deferred-tool-suggest-only` | wrong semantics | reject |
| `genuinely-absent-family` | absent | accept |
| `direct-model-only-override` | direct | accept |
| `mcp-deferred-loader-inherited-verified` | verified incremental inheritance | accept |
| `mcp-deferred-logical-loader-wire-omitted` | logical-only loader | reject |
| `mcp-deferred-stale-catalogue-zero-results` | valid route, stale catalogue | accept + warning |
| `dynamic-deferred-stale-saved-generation` | valid route, stale saved generation | accept + warning |
