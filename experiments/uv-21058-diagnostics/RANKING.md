# uv #21058 diagnostic ranking

Source generation: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream regression: https://redirect.github.com/astral-sh/uv/pull/21059

This ranking follows focused runs `31569454399` and `31570073281`.

## Finalists

### 1. B2 — shared path-aware error + inventory context

Why it is alive:

- exact offending child path;
- same actionable recovery appears automatically in `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all`;
- unrelated top-level `upgrade --all` inventory I/O receives operation context and no invalid-name hint;
- follows uv's documented `Hint` architecture;
- real sibling-command execution proved the cross-command payoff.

Why it may be too large:

- complete repair footprint is six files including existing regression and `Cargo.lock`;
- changes a lower-level error API and adds direct `uv-tool -> uv-errors` dependency metadata;
- expands #21058 into a shared tool-inventory diagnostic improvement.

Polish before treating it as a candidate:

- rename lower-level variant to `InvalidToolDirectoryName`;
- display `Invalid tool directory name: <path>`;
- remove generic rename recovery;
- prefer `Failed to inspect installed tools` if retaining the outer header;
- remove obsolete transparent `ToolName` variant if no producer remains;
- add `Cargo.lock` direct-dependency entry;
- update upstream-owned `tool_upgrade.rs` snapshot;
- decide whether sibling snapshot coverage belongs in the same repair.

### 2. E — scoped typed wrapper + central hint

Why it is alive:

- keeps user-visible change scoped to `tool upgrade --all`;
- expected complete footprint is three files including existing regression;
- normal propagation preserves exit 2;
- central `Hint` rendering follows uv's diagnostics convention;
- gives every top-level inventory failure operation context;
- invalid-name recovery can show the configured tool root without touching `uv-tool`.

Tradeoff:

- no exact offending child path; user combines bad basename from parser cause with root path in hint;
- command-specific wrapper type lives in diagnostics layer;
- sibling commands remain on the current bare invalid-name error.

E is being materialized on the owned fork for execution after the first ranking pass.

## Proven fallbacks

### A — one-file production fix with `uv tool dir` hint

A is the smallest executed option and fully works. `uv tool dir` was explicitly proven to succeed under the broken inventory state. If review scope needs to stay extremely narrow, A is a solid fallback.

Complete upstream-quality footprint: two files including existing regression.

### C — one-file production fix with root path in hint

C is also fully executed. It saves the extra `uv tool dir` command but still owns local rendering and gains no exact-child or sibling-command benefit. E is likely a cleaner version of the same scoped idea if E executes successfully.

## Demoted

### B1

Excellent concise invalid-name output and same sibling payoff as B2. Demoted because unrelated top-level inventory I/O remains bare. B2 gives better coverage for the full top-level failure set that `unwrap_or_default()` currently hides.

### D

Avoids the direct `uv-tool -> uv-errors` dependency but requires one-off concrete variant policy inside the central diagnostic walker. That file explicitly documents `Hint` implementations as the consolidation mechanism, so B is cleaner if shared behavior is selected.

## Current decision question

The remaining choice is mostly scope, not correctness:

- **B2** if invalid tool-directory-name state should become a first-class shared tool-inventory diagnostic.
- **E** if #21058 should improve `tool upgrade --all` only while still using uv's central error/hint machinery.

Both preserve the original behavior insight: `unwrap_or_default()` should stop converting inventory failure into an empty successful result.
