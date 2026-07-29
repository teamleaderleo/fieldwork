# L05 report: deferred discovery must remain executable

## In simple words

Codex intentionally hides many tool schemas and loads them later. That is not the defect.

The defect class is narrower: a runtime remains present and deferred, but the effective generated model turn has no usable route to discover and invoke it.

The route depends on the mode:

- Direct mode uses a model-visible, registered client-executed `tool_search`.
- Code Mode may omit nested `tool_search` and instead use `exec`, `ALL_TOOLS`, and the global `tools` runtime.
- Responses Lite may carry tool definitions through an `additional_tools` developer input item.
- WebSocket incremental reuse may omit an already-sent manifest only when `previous_response_id` inheritance is verified for the identical effective manifest.

Top-level `tools: null`, missing nested `tool_search` in Code Mode, or an empty search result are not sufficient evidence of tool loss by themselves.

## Scope

- Fieldwork issue: #40
- Campaign: #31
- Lane: `campaigns/0002-tool-surface-continuity/lanes/L05-deferred-discovery-invariant/`
- Upstream interaction: read-only
- Claim: mode-aware planner-to-runtime-to-transport reachability for deferred tools
- Adjacent owners: lifecycle provenance L01, transport L02, result identity L03, catalogue convergence L04, diagnostics L06, fallback authority L07

## Evidence pins

| Source | Revision or record | Date | Role |
|---|---|---|---|
| Initial Fieldwork campaign base | `aa72bd513f6664dc67517dabd9b03b4f051d8460` | 2026-07-30 | repository fact |
| Original public Codex pin | `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc` | 2026-07-30 | primary source |
| Meta-review public Codex pin | `a05bcda3dbd68729caa2f11027b7f43974fda298` | 2026-07-30 | primary source |
| Intended MCP deferral | `openai/codex#29486` | reviewed 2026-07-30 | merged design |
| Responses Lite framing | `openai/codex#27946` | reviewed 2026-07-30 | merged design |
| Code Mode deferred runtime path | `openai/codex#23605`, `#31745` | reviewed 2026-07-30 | merged design |
| Fresh-turn A/B | `openai/codex#33679` | reviewed 2026-07-30 | targeted report |
| Resume/WebSocket A/B | `openai/codex#35751` | reviewed 2026-07-30 | targeted report |
| Supporting reports | `#31894`, `#32086`, `#33609`, `#19425` | reviewed 2026-07-30 | reported observations |
| Ranked-search degradation | `#32101` | reviewed 2026-07-30 | narrower related issue |

Primary source areas:

```text
codex-rs/core/src/tools/spec_plan.rs
codex-rs/tools/src/code_mode.rs
codex-rs/tools/src/code_mode_tests.rs
codex-rs/code-mode-protocol/src/description.rs
codex-rs/core/src/client.rs
codex-rs/models-manager/models.json
```

## Intended architecture confirmed

### MCP deferral

When model and provider capabilities support searched tools, configured MCP tools are intentionally deferred rather than dumped into the initial request.

### Responses Lite

Responses Lite intentionally moves client tool declarations and developer instructions into input items. Absence of top-level `tools` is expected in that request shape.

### Code Mode

Current Code Mode conversion intentionally skips `ToolSpec::ToolSearch`. Deferred nested tools are expected to remain callable through `ALL_TOOLS` and the global `tools` object. Therefore, `openai/codex#32101` supports a ranked-discovery degradation, not total unreachability by itself.

### WebSocket reuse

The first generated request may reuse a prewarm response and send only incremental input. That optimization is valid only while the referenced response carries the same effective tool surface.

## Defect invariant

For each present runtime in the finished planner, mode transform, runtime catalogue, and effective delivery:

```text
Direct / DirectModelOnly
    => effective surface delivered directly
       OR identically inherited with verification

Deferred in Direct mode
    => searchable metadata for this runtime
    => top-level tool_search advertised, registered, executable
    => effective surface delivered directly
       OR identically inherited with verification

Deferred in Code Mode
    => searchable/runtime metadata for this runtime
    => exec advertised and executable
    => runtime appears in ALL_TOOLS/global tools catalogue
    => effective surface delivered directly
       OR identically inherited with verification

Hidden
    => outside this invariant
```

Catalogue freshness is separate:

```text
route exists + search returns [] + stale generation
    => route invariant passes
    => catalogue warning or earlier-layer failure
```

## Strongest targeted evidence

### Fresh Responses Lite path

`openai/codex#33679` changes only `use_responses_lite` while holding the model slug, prompt, MCP server, authentication, sandbox, and working directory constant. The MCP call fails with Lite and succeeds without Lite. GPT-5.4 is a working control. A separate Xcode MCP reproduction reports all 47 tools discovered internally, no MCP call under Sol, and a successful call under GPT-5.4.

### Resumed compacted WebSocket path

`openai/codex#35751` replays the same stored compacted history. The WebSocket path loses execution tools, the HTTP path succeeds, and a fresh WebSocket thread succeeds. That isolates the resume/prewarm/incremental boundary much more narrowly than a generic MCP or permission failure.

## Source-supported generic planner gap

The public planner still permits a generic invalid state for contributed runtimes:

- dynamic tools may select `Deferred` independently;
- extension contributors may select `Deferred` directly;
- a deferred runtime with no `search_info()` stays registered but does not enter the search index;
- search-disabled combinations can therefore leave a deferred runtime without a logical loader unless the final planner normalizes or rejects it.

Built-in configured MCP, curated app, and native V1 construction generally couple exposure to search capability correctly. The final invariant must cover every contributor, not only those built-ins.

## Executable artifacts

### Python state packs

```sh
python3 run_invariant.py fixtures/deferred-surfaces.json --output results/latest.json
python3 run_invariant.py fixtures/cross-lane-surfaces.json --output results/cross-lane.json
```

Retained results:

```text
original:   12 cases; 8 accepted; 4 intended rejects; 0 mismatches
cross-lane: 4 cases; 3 accepted; 1 intended reject; 2 warnings; 0 mismatches
aggregate:  16 cases; 11 accepted; 5 intended rejects
```

### Rust contract probe

`rust-probe/` is a zero-dependency executable contract model. It tests:

1. Direct-mode `tool_search` reachability.
2. Valid Code Mode `ALL_TOOLS` reachability without nested `tool_search`.
3. Rejection when Code Mode loses the runtime catalogue entry.
4. Valid direct Responses Lite `additional_tools` delivery.
5. Rejection of unverified WebSocket omission.
6. Acceptance of verified identical inheritance.
7. Narrow promotion of missing-metadata or search-disabled deferred runtimes.
8. Separate stale-catalogue warnings.

Run:

```sh
cd rust-probe
cargo test --all-targets --locked
```

A pull-request workflow compiles, formats, and executes the probe.

## Repair direction

Preserve the intended architecture and repair only the first divergent boundary:

1. **Logical planner:** promote only unloadable deferred runtimes to `Direct`, or return a typed invariant error.
2. **Code Mode runtime:** reject or rebuild when `exec` does not receive the matching `ALL_TOOLS` runtime entry.
3. **Transport:** send the full manifest when inherited identity cannot be verified.
4. **Catalogue:** rebuild the binding/search index and publish a new generation when stale.
5. **Lifecycle:** distinguish preserve, clear, and replace for saved dynamic declarations.

Do not:

- make every MCP tool direct;
- require nested `tool_search` in Code Mode when `ALL_TOOLS` is complete;
- reject Responses Lite solely because top-level `tools` is absent;
- disable WebSocket incremental reuse globally;
- treat every zero-result search as a missing loader;
- reroute through a changed authority path automatically.

## Uncertainty

The public evidence does not yet identify whether fresh Sol failures are owned by client serialization, service-side interpretation of `additional_tools`, originator-specific model metadata, or model-visible handling after delivery. The resume report does not yet distinguish lost service inheritance from incorrect client chain reconstruction.

The defensible claim is:

> Codex intentionally defers and incrementally carries tools, but controlled reports show effective generated turns where internally discovered tools have no usable model-executable route. This cross-layer invariant is directly testable and repairable without exposing hidden schemas or undoing deferred discovery.

## Durable artifacts

- `report.md` — current synthesis and claim
- `meta-review.md` — intended behavior versus targeted defect analysis
- `matrix.md` — request and family matrix
- `cross-lane-followup.md` — ranked diagnostics handoff
- `fixtures/` and `results/` — retained Python packs
- `run_invariant.py` — Python invariant checker
- `rust-probe/` — zero-dependency Rust contract model and integration tests
- `repair-proposal.md` — mode-aware repair proposal
- `commands.md` — revisions, commands, and execution record
