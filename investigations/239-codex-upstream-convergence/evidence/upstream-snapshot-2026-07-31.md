# Codex upstream snapshot receipt — 2026-07-31

Owner: lane J, Fieldwork #239  
Retrieval date: 2026-07-31  
Read-only upstream head: `a01a2d91461a57809e944de7758477b92617ab01`  
Previous workspace analysis pin: `745603a5a1eb48b6f343633d622eeb72dd549d7b`  
Upstream contact authorized: `false`

## In simple words

One new Codex commit landed after the workspace analysis was drafted. It preserves executor paths in read-command actions and updates app-server protocol representations. Its changed files do not enter the active source fences for deferred-loader authority, MCP reconnect/publication, append acknowledgement, or terminal producer-owned retention.

The candidate classifications recorded at `745603a5a1eb48b6f343633d622eeb72dd549d7b` therefore carry forward to `a01a2d91461a57809e944de7758477b92617ab01` for those declared fences. The new command-action behavior deserves future adjacent execution-path review and creates no absorption or conflict for the current bounded candidates.

## Exact delta

Commit:

```text
a01a2d91461a57809e944de7758477b92617ab01
Preserve executor paths in read command actions (#36223)
```

Compare boundary:

```text
745603a5a1eb48b6f343633d622eeb72dd549d7b
...
a01a2d91461a57809e944de7758477b92617ab01
```

Changed areas:

- app-server protocol schemas and TypeScript command action representation;
- app-server protocol item builders and focused tests;
- selected-environment app-server tests;
- path-URI utilities and tests;
- one analytics test expectation.

## Declared active source fences checked

### Append acknowledgement

- `codex-rs/core/src/session/mod.rs`;
- `codex-rs/core/src/session/turn_tests.rs`;
- `codex-rs/thread-store/src/in_memory.rs`.

Delta overlap: `none`.

### Terminal producer-owned retention

- `codex-rs/core/src/unified_exec/process.rs`;
- `codex-rs/core/src/unified_exec/process_tests.rs`;
- `codex-rs/core/src/unified_exec/async_watcher.rs`;
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`.

Delta overlap: `none`.

### MCP reconnect and publication

Current candidate ownership centers on MCP runtime and host refresh paths. The delta contains no MCP runtime or client file.

Delta overlap: `none` within the current candidate fences.

### Deferred executable authority and Responses Lite

Current candidate ownership centers on request construction, tool exposure, and the standalone Code Mode host. The delta contains no request client, tool registry, Code Mode host, or Responses Lite source file.

Delta overlap: `none` within the current candidate fences.

## Adjacent relevance

The commit preserves executor paths in public command-action records. That reinforces a broader Fieldwork principle: model-visible or client-visible execution records should retain the authority and environment path that produced the action.

This is adjacent prior art for future operation-lineage and execution-provenance analysis. It does not establish remote-effect settlement, result persistence, runtime-generation binding, or terminal transcript retention.

## Classification carry-forward

| Candidate | Classification at `745603...` | Classification at `a01a2d...` |
| --- | --- | --- |
| Deferred executable loader | architectural conflict; semantic residue | unchanged |
| Host MCP reconnect | complementary; current-source review pending | unchanged |
| MCP generation publication | complementary; current-source review pending | unchanged |
| Terminal producer-owned retention | mechanically conflicting with earlier deque work; semantically complementary | unchanged |
| Append acknowledgement | semantic residue; exact execution pending | unchanged |
| Responses Lite first-generated capability prefix | policy plausible; production source held | unchanged |
| MCP timeout outcome separation | complementary operation-lifecycle work | unchanged |

## Expiry

This receipt supports current-source language through `a01a2d91461a57809e944de7758477b92617ab01` for the declared fences. A later upstream head requires a new delta review before `current`, `portable`, `conflict-free`, or `proposal-ready` language is reused.