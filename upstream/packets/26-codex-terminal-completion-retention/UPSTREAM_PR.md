# Upstream pull request preparation

## Status

**Do not submit without a maintainer invitation and a separate owner decision.**

Upstream issue: `openai/codex#37207`

Proposed title:

> fix(core): retain completed command output before live broadcast

## Current direction

Unified exec should preserve the existing live-stream resilience behavior while preventing listener timing from defining the completed command result.

The current proof stores the polling and completion buffers together:

```rust
struct OutputState {
    output: HeadTailBuffer,
    completion: HeadTailBuffer,
}
```

Each accepted local or exec-server chunk advances both bounded views under one mutex before the live broadcast. When output closes, the completion watcher replaces its partial listener transcript with the retained completion view.

This preserves:

- the existing bounded head/tail output policy;
- the omission marker;
- model-facing truncation downstream;
- live `Lagged` recovery;
- UTF-8 delta handling;
- cancellation/trailing-output grace;
- synchronous fallback behavior.

## Why this direction

Merged `openai/codex#4992` introduced explicit `Lagged(_) => continue` handling so a receiver that falls behind can skip missed messages and continue streaming later output. That resilience behavior should remain.

The issue is that the same lossy delivery path can also control the completed transcript. The repair moves completion authority to bounded output retained before live delivery rather than turning `Lagged` into a fatal error.

## Current public source

Latest public head checked: `b3278e96cb6df4b77b8dd93cf6c65d74990a033d`.

Public main has structurally changed since the owned proof was based. Merged `openai/codex#37083` now stores the existing output buffer, notification state, close state, and cancellation token together in `OutputHandles`.

That refactor does not fix `openai/codex#37207`:

- the completion watcher still continues after `RecvError::Lagged(_)` while building its transcript;
- the local collector still continues after `RecvError::Lagged(_)` before missed chunks can be added to its retained output buffer.

A public implementation therefore needs a semantic restack onto current `OutputHandles`. Do not mechanically replay the owned branch.

## Owned proof

`teamleaderleo/codex#144`

- base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- current head: `d4ff73f50e30e96b6db4a08205c9d3600e15488e`
- four Rust files
- current shape: one shared `OutputState` mutex

The proof demonstrates the ownership change and retains the existing regression coverage. It is review evidence, not a current-main delivery candidate.

## Tests already present in the proof

- output emitted before the completion listener subscribes;
- a deliberately lagged live receiver while the completion view retains the bytes;
- invalid UTF-8 through the same lag path;
- replacement of a partial streamed transcript with the retained completion transcript;
- local and exec-server producer ordering;
- normal close, cancellation grace, capped output, and synchronous fallback behavior.

## Additional tests before a public PR

1. Sustained simultaneous stdout and stderr while another task polls and drains the polling buffer.
2. Output arriving immediately before, around, and after the trailing-output grace boundary.
3. Repeated polling followed by completion, confirming the final item retains the intended capped whole-process history.
4. App-server live/final reconciliation if the current public surface makes that useful during review.

## Execution status

### Earlier paired receipt

Run `30699322569` validated the earlier two-mutex source:

- baseline library: `2,129/2,129`;
- source focused controls: `12/12`;
- source library: `2,133/2,133`;
- integration targets compiled;
- formatting and exact four-file fence passed.

### Current single-mutex proof

- V8 canary `31072774070`: passed.
- Blocking CI `31072774224`: failed.
- Formatting, Rust benchmark smoke, cargo-shear, blob-size policy, cargo-deny, and codespell passed.
- The first deterministic blocking failure is an owned-fork manifest check on a stale `code-mode/Cargo.toml` exception, outside the proof files.

The current proof still needs a fresh paired baseline/source receipt before it could become delivery evidence.

## Reviewer checklist for a later authorized PR

- [ ] Direct parent is current public main.
- [ ] Patch is adapted to the current `OutputHandles` ownership shape.
- [ ] Completion state is retained before live broadcast.
- [ ] Polling and completion views advance under one coherent state update.
- [ ] Live `Lagged` recovery remains non-fatal.
- [ ] Existing head/tail and model-facing truncation policies remain intact.
- [ ] Sustained-output/polling stress coverage passes.
- [ ] Cancellation-boundary coverage passes.
- [ ] Fresh paired baseline/source receipt passes or shared failures are explicitly classified.
- [ ] Public PR links issue `openai/codex#37207` only after authorization.

## Public interaction boundary

The issue is filed and open. No public pull request, follow-up comment, reaction, review, or other upstream interaction is authorized without another owner decision.