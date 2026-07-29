# High-leverage open-source systems and creative infrastructure

Programme: #114

Portfolio pull request: #115

Primary strategy: `portfolio.md`

## In simple words

This programme dispatches serious architecture, behavior, and integration research across visible and technically respected open-source systems. The lanes are not a good-first-issue queue. Each lane is expected to produce source maps, controlled probes, negative controls, and a useful decision even when no upstream contribution follows.

## Dispatched lanes

| Wave | Issue | Target | Primary question | Candidate owned backdrop |
|---|---:|---|---|---|
| 1 | #116 | wgpu | Backend portability, validation, diagnostics, device/surface loss, and GPU-resource lifecycle | Botany Sim, Make Good TV, Renderprove |
| 1 | #117 | Wasmtime | Capability sandboxing, WASI authority, interruption, resource limits, and terminal truth | Smolrunner, Stensibly |
| 1 | #118 | Tauri | IPC, permissions, plugins, packaging, updater, webview, process, and cross-platform lifecycle | Rollodoro, Relirium, Ourchival |
| 1 | #120 | Tantivy | Index commits, reader reload, searcher visibility, deletes, merges, crash recovery, and rebuildability | Baxtori, Ourchival, Relirium, Proofwake |
| 2 | #121 | Automerge and Yjs | Local-first identity, convergence versus product conflict, snapshots, migration, corruption, and offline recovery | Days Upon, Relirium |
| 2 | #122 | Apache DataFusion and Polars | Reproducible plans, streaming, cancellation, schema drift, resource limits, and truthful output publication | Quarry |
| 2 | #123 | Godot | Web export, engine/editor automation, scene/resource identity, rendering/input lifecycle, and externally authoritative state | Botany Sim, Make Good TV |
| 3 | #124 | Bevy | ECS identity, deferred commands, schedules, assets, fixed timestep, rendering extraction, and replay | Botany Sim, Make Good TV |
| 3 | #125 | FFmpeg | Probe/demux/decode/filter/encode/mux interruption, trailer finalization, partial media, metadata, and provenance | Make Good TV, Ourchival, Renderprove |

## Dispatch order

### Wave 1

Start with wgpu, Wasmtime, Tauri, and Tantivy. They combine strong specialist or public visibility, realistic owned-project seams, and contributor processes where a focused outside contribution is plausible.

### Wave 2

Run the comparative Automerge/Yjs and DataFusion/Polars lanes with shared fixtures. Start the Godot lane with source mapping, then use the already-open owned R&D leads only after exact engine contracts are clear.

### Wave 3

Use Bevy as an architecture-learning and possible contribution lane. Keep FFmpeg as deliberate hard mode: proceed to an upstream-shaped result only with exact development-tree reproduction and regression-quality evidence.

## Claim protocol

A worker claiming a lane should comment with:

- worker identity;
- exact target source revision and released version where applicable;
- owned path and branch;
- first source subsystems;
- first executable probe;
- expected negative control;
- stop condition;
- upstream contact authorization state.

Do not claim several lanes when one deep lane is still unbounded.

## Target hubs and labels

These lanes begin as portfolio reconnaissance. Create a stable `target:*` label and target hub when the target is mapped and likely to receive recurring Fieldwork work. Do not create `testbed:*` labels until a real owned integration trial starts.

## Evidence standard

Each lane should distinguish:

- source-confirmed behavior;
- released reproduction;
- exact-tree reproduction;
- owned integration evidence;
- cross-platform or cross-backend reproduction;
- upstream-ready evidence.

A prestigious target does not lower the evidence threshold.

## Upstream boundary

Quiet source research and local public probes are authorized. Upstream issues, comments, discussions, pull requests, mailing-list messages, or Forgejo submissions are not authorized until a specific packet is reviewed.
