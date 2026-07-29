# Agent and CLI Execution

## In simple words

Map deterministic tool, process, permission, session, terminal, interruption, and recovery behavior in agentic CLIs. Scouts should separate product differences and model output from concrete execution or state failures.

- Programme hub: #14
- State: `ready`
- Coordinator: unclaimed
- Upstream contact: unauthorized

## Ready scouts

- #22 — Gemini CLI tool execution and session recovery
- #23 — Codex tool, process, and terminal lifecycle
- #24 — cross-agent process and terminal semantics

## Current decision

Run target-specific scouts independently. Use the comparison scout to produce shared case packs and target-specific branch candidates, not a superficial feature comparison.
