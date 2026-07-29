# Meta-review: intended deferral versus actual tool loss

Review date: 2026-07-30  
Campaign: #31  
Lane: L05 / issue #40  
Original Codex pin: `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`  
Follow-up Codex pin: `a05bcda3dbd68729caa2f11027b7f43974fda298`

## Question

The targeted question is not whether Codex intentionally hides some tools. It does. The question is whether an effective generated turn can retain a deferred runtime while losing every model-executable route to discover and invoke it.

## Intended behavior confirmed in source and merged PRs

### MCP deferral is intentional

PR `openai/codex#29486` made searched-tool flow the default whenever model and provider capabilities support it. MCP schemas are deliberately omitted from the initial request and loaded later.

### Responses Lite `additional_tools` is intentional

PR `openai/codex#27946` moved Responses Lite instructions and client tool schemas into developer input items. Top-level `tools: null` is therefore not sufficient evidence of a defect.

### WebSocket incremental reuse is intentional

The Responses WebSocket path may prewarm with `generate=false`, retain the response ID, and send only incremental input on the generated request. `previous_response_id` reuse is an optimization, not itself a bug.

### Code Mode has an alternative discovery route

Current Code Mode conversion intentionally does not turn `ToolSpec::ToolSearch` into a nested function. Its documented route is instead:

```text
exec
  -> ALL_TOOLS metadata
  -> global tools object
  -> deferred runtime invocation
```

PRs `openai/codex#23605` and `openai/codex#31745` deliberately keep deferred runtime definitions out of the initial `exec` guide while retaining them in the runtime catalogue. Therefore, missing nested `tools.tool_search(...)` is a discovery-quality regression, not proof of complete unreachability.

## Correct defect boundary

A deferred runtime is valid only when the effective generated turn has at least one usable route:

```text
Direct mode:
  top-level client-executed tool_search

Code Mode:
  model-visible exec
  + ALL_TOOLS entry
  + callable global tools runtime

Transport:
  complete effective manifest sent directly
  OR
  previous_response_id inheritance verified against the identical manifest
```

The invalid state is:

```text
runtime present
+ exposure deferred
+ no usable mode-specific discovery route
+ no direct or verified inherited delivery
= unreachable tool
```

This is different from intentionally omitting a schema, omitting ranked search in Code Mode, or receiving a valid zero-result search.

## Targeted reports

### Strongest fresh-turn A/B: `openai/codex#33679`

The report holds the model slug, prompt, MCP server, authentication, sandbox, and working directory constant. Changing only `use_responses_lite` from `true` to `false` restores the MCP call. GPT-5.4 is also a working control. An independent Xcode MCP reproduction reports 47 tools discovered internally, no MCP call under Sol, and a successful call under GPT-5.4.

This is the strongest evidence that the fresh Responses Lite path can produce an unusable effective tool surface.

### Strongest resume/transport A/B: `openai/codex#35751`

The same compacted stored history loses execution tools on the Responses WebSocket path while succeeding over HTTP. A fresh WebSocket thread also succeeds. That isolates resumed compacted history plus WebSocket reuse more narrowly than generic MCP or permission failures.

### Supporting direct reports

- `openai/codex#31894`: Sol Responses Lite request contains `exec` inside `additional_tools`, but the generated turn behaves as though no shell/code-mode tool is callable.
- `openai/codex#32086`: V1 collaboration tools are deferred while the client-executed search entrypoint is not usable in the effective Lite surface.
- `openai/codex#33609`: MCP discovery succeeds internally, but a fresh Sol session has neither callable MCP tools nor a usable search route.
- `openai/codex#19425`: custom MCP tools are returned by `tools/list` but absent from the thread/search surface.

### Related but narrower: `openai/codex#32101`

This issue correctly identifies that Code Mode drops the ranked `tool_search` primitive. Current source and tests confirm that behavior. However, Code Mode is expected to retain deferred tools through `ALL_TOOLS`; the issue supports degraded discovery and fallback behavior, not complete loss by itself.

## Source-level contradiction worth testing

The planner intentionally defers runtimes and builds a discovery executor when searchable metadata exists. Code Mode intentionally skips `ToolSpec::ToolSearch`, while separately promising that deferred runtimes remain in `ALL_TOOLS`. Responses Lite intentionally places client tools in input history, and WebSocket reuse may later omit that history from the wire delta.

Each individual rule is coherent. The untested composition is whether the final generated turn still has the same effective route after:

1. model/tool-mode transformation;
2. Responses Lite serialization;
3. prewarm and incremental reuse;
4. resume or compaction reconstruction;
5. catalogue and thread-binding refresh.

## Executable contract probe

`rust-probe/` models the composition without copying Codex internals. Its integration cases assert:

1. Direct-mode `tool_search` keeps deferred MCP reachable.
2. Code Mode `ALL_TOOLS` is valid without nested `tool_search`.
3. Code Mode missing `ALL_TOOLS` rejects the deferred runtime.
4. A directly sent Responses Lite `additional_tools` manifest is valid.
5. WebSocket omission requires a matching inherited-manifest receipt.
6. Missing search metadata promotes only the affected runtime to direct exposure.
7. Search-disabled mode promotes deferred runtimes while leaving existing direct tools alone.
8. Stale catalogue state warns separately from route existence.

Run:

```sh
cd campaigns/0002-tool-surface-continuity/lanes/L05-deferred-discovery-invariant/rust-probe
cargo test --all-targets --locked
```

## Repair shape

The repair must preserve the intended architecture:

- Do not make all MCP tools direct.
- Do not require nested `tool_search` in Code Mode when `ALL_TOOLS` is complete and executable.
- Do not reject `additional_tools` merely because top-level `tools` is absent.
- Do not disable WebSocket incremental reuse globally.

Apply the smallest repair at the first divergent boundary:

1. **Logical planner gap:** promote only unloadable deferred runtimes to `Direct`, or return a typed planner error.
2. **Code Mode runtime gap:** rebuild or reject when `exec` lacks the matching `ALL_TOOLS` runtime entry.
3. **Transport gap:** send the full manifest when inherited identity cannot be verified.
4. **Stale catalogue:** rebuild the binding/search index and publish a new generation.
5. **Stale saved declarations:** use explicit preserve/clear/replace lifecycle semantics.

## What remains unproven

The public evidence does not yet identify whether fresh Sol failures are owned by Codex serialization, service-side interpretation of `additional_tools`, originator-specific model metadata, or model-visible handling after delivery. The resume report does not yet distinguish lost service inheritance from incorrect client chain reconstruction.

The defensible claim is narrower:

> Codex intentionally defers and incrementally carries tools, but controlled reports show effective generated turns where internally discovered tools have no usable model-executable route. The missing cross-layer invariant is directly testable and repairable without exposing hidden schemas or undoing deferred discovery.
