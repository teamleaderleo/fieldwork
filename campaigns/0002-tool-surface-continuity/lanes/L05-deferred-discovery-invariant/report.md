## In simple words

A tool may be deferred only when the effective model request contains a working route that can load it. The public Codex planner couples this rule correctly for built-in configured MCP tools, curated app tools, and native multi-agent V1 tools. Dynamic host tools and extension contributors can still remain `Deferred` while `tool_search` is unavailable, and a deferred runtime whose `search_info()` is absent stays registered while becoming undiscoverable.

Cross-lane evidence adds two separate lookalikes. L02 (#37 / PR #58) shows a loader can exist in the logical planner and still be omitted from an incremental Responses Lite wire request unless previous-response inheritance preserves it. L04 (#39 / PR #62) shows an executable loader can search a stale thread binding. These failures need different receipts and different repairs.

The lane now retains the original 12 request-state cases plus four cross-lane cases covering verified inherited delivery, unverified wire omission, stale catalogue, and stale saved provenance.

## Scope and claim

- Fieldwork issue: #40
- Campaign: #31
- Lane: `campaigns/0002-tool-surface-continuity/lanes/L05-deferred-discovery-invariant/`
- Claim supported: planner-to-wire exposure and executable-discovery invariants across native, MCP, app, dynamic, and extension families
- Adjacent boundaries recorded: catalogue convergence from L04 and saved/current provenance from L01
- Boundary: model behaviour after valid tool delivery remains outside this lane
- Upstream interaction: read-only

## Evidence pins

| Source | Revision or record | Retrieved | Label |
|---|---|---|---|
| Fieldwork campaign base | `aa72bd513f6664dc67517dabd9b03b4f051d8460` | 2026-07-30 | repository fact |
| OpenAI Codex public source | `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc` | 2026-07-30 | primary source |
| Campaign comparison fork | `2b7b93081361b77f8ddaceaf362a09765b4153bf` | campaign-provided | repository fact |
| Codex reports | #33608 and #33609 | 2026-07-30 | reported observation |
| Lifecycle provenance | #35 / PR #61 | 2026-07-30 | cross-lane evidence |
| Transport and prewarm | #37 / PR #58 | 2026-07-30 | cross-lane evidence |
| Compaction identity | #38 / PR #64 | 2026-07-30 | cross-lane boundary |
| Catalogue convergence | #39 / PR #62 | 2026-07-30 | cross-lane evidence |
| Fallback authority | #44 / PR #60 | 2026-07-30 | cross-lane boundary |
| Coexistence trial | #46 / PR #57 | 2026-07-30 | integration negative result |

Primary source links:

- [`spec_plan.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/spec_plan.rs)
- [`mcp_tool_exposure.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/mcp_tool_exposure.rs)
- [`dynamic.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/handlers/dynamic.rs)
- [`tool_search.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/handlers/tool_search.rs)
- [`tool_executor.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/tools/src/tool_executor.rs)
- [`models.json`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/models-manager/models.json)
- [Observed report #33608](https://redirect.github.com/openai/codex/issues/33608)
- [Observed report #33609](https://redirect.github.com/openai/codex/issues/33609)

## Mechanism map

`search_tool_enabled` combines model metadata (`supports_search_tool`) and provider namespace-tool capability. Native multi-agent V1, configured MCP, and curated app tools use that value to choose `Deferred` or `Direct`.

The final planner scans registered `Deferred` runtimes, calls `search_info()`, and creates `tool_search` only when search is enabled and at least one entry exists. Direct tools become model-visible; deferred tools remain registered and initially invisible.

Three planner hazards remain:

1. Dynamic host tools read `defer_loading` and select `Deferred` independently.
2. Extension contributors can select `ToolExposure::Deferred` directly.
3. A deferred runtime returning `None` from `search_info()` is omitted from the search index.

A fourth hazard appears after planning. A logical request can contain `tool_search` while an incremental wire request omits it and relies on earlier response state. That route is valid only when inheritance is verified for the same effective tool manifest.

## Strongest supported finding

The public source contains a generic planner invariant gap. Dynamic and extension runtimes may remain `Deferred` while request search is disabled. Any deferred runtime may also be excluded when `search_info()` returns `None`. In both cases the runtime remains registered and invisible to the model.

The existing `mcp_and_tool_search_follow_direct_and_deferred_tool_exposure` test injects a deferred runtime under a search-disabled model and confirms only that `tool_search` is absent. It leaves the unreachable runtime uncorrected.

Cross-lane evidence strengthens the boundary: planner correctness must be checked against the effective wire request or a verified inherited response manifest. A logical-only loader is insufficient.

## Is this one issue?

There is one clear generic defect class: `present + deferred + no executable delivery route`. Direct exposure or typed planner rejection can repair it.

Several similar symptoms have different owners:

- loader absent in the logical planner: L05;
- loader present logically but omitted on the wire: L02;
- loader executable against a stale binding or search index: L04;
- loader valid for saved dynamic tools whose host generation is stale: L01;
- tool result identity lost after execution or compaction: L03;
- a shell, protocol, connector, browser, or subagent workaround changes authority: L07.

The public `gpt-5.6-sol` reports prove the symptom class. They do not identify which planner, private profile, host transform, or transport path caused those exact sessions.

## Invariant

For each family in the finished planner/router and effective delivery pair:

```text
present + Direct/DirectModelOnly
    => accept

present + Deferred
    => require searchable metadata for this family
    => require an advertised, registered, executable loader
    => require loader semantics that expose existing deferred tools
    => require direct wire delivery or verified previous-response inheritance

absent
    => accept
```

`tool_search` executed with `tools=[]` satisfies route availability. A stale catalogue can still produce a valid zero-result call, so freshness receives a separate warning and diagnostic owner.

## Retained results

Original request-state pack:

```sh
python3 run_invariant.py fixtures/deferred-surfaces.json --output results/latest.json
```

```text
12 cases; 8 accepted; 4 rejected; 0 mismatches; exit 0
```

Cross-lane follow-up pack:

```sh
python3 run_invariant.py fixtures/cross-lane-surfaces.json --output results/cross-lane.json
```

```text
4 cases; 3 accepted; 1 rejected; 2 warnings; 0 mismatches; exit 0
```

Aggregate coverage is 16 cases: 11 accepted and 5 intended rejections.

The added rejection is `mcp-deferred-logical-loader-wire-omitted`. The added warning codes are `stale_discovery_catalogue` and `stale_saved_provenance`.

## Repair direction

Normalize planner-unloadable deferred runtimes to `Direct` after all contributors and direct-model-only overrides, before `tool_search` and code-mode entrypoints are built.

Add a transport assertion for incremental requests: the effective request must carry the loader directly or include a verified inheritance receipt binding `previous_response_id` to the same tool-manifest digest.

Catalogue freshness and saved/current generation mismatches need typed diagnostics and their owning repair paths. Direct exposure cannot refresh a stale binding or replace sticky host declarations.

A typed planner error remains the stricter alternative.

## Ranked continuation

Highest information gain:

1. Pair logical-planner, wire-delivery, and inherited-manifest digests for the first generated Responses Lite turn.
2. Pair current binding/catalogue digest with the `tool_search` index digest and search result generation.
3. Add saved/current dynamic-tool generation and selected-root provenance to the diagnostic receipt.
4. Integrate fallback authority deltas before automatic shell or protocol workarounds.

Lower information gain:

- sustained same-conversation calls and a context-summary boundary alone; L08 completed both without divergence;
- planner-only configured-MCP tests without transport or catalogue controls;
- model-behaviour studies after valid tool delivery.

## Negative results

- Built-in configured MCP and curated app construction already falls back to direct exposure when search is unavailable.
- Native multi-agent V1 follows the same coupling.
- Bundled model metadata does not reproduce a search-disabled `gpt-5.6-sol`.
- `tool_suggest` cannot load an existing deferred runtime.
- An empty discovery result does not imply an absent loader.
- The L08 sustained coexistence and context-summary trial produced no capability loss.

## Uncertainty

The exact private model profile, catalogue override, host transform, inherited response state, or server-side handling behind the 0.144.5 reports remains unavailable. The probes validate the request and delivery contract model; they do not compile or run proposed Rust changes against upstream.

Transport serialization is owned by L02. Catalogue convergence is owned by L04. Lifecycle provenance is owned by L01. Result identity is owned by L03. Diagnostics synthesis is owned by L06.

## Durable artifacts

- `report.md` — findings, cross-lane synthesis, scope, and uncertainty
- `matrix.md` — family/model/provider/configuration matrix
- `cross-lane-followup.md` — ranked exploration and diagnostic handoff
- `fixtures/deferred-surfaces.json` and `results/latest.json` — original request-state pack
- `fixtures/cross-lane-surfaces.json` and `results/cross-lane.json` — delivery and adjacent-state pack
- `run_invariant.py` — executable invariant checker
- `repair-proposal.md` — planner repair and source-test proposal
- `commands.md` — revisions, reads, commands, and execution record
