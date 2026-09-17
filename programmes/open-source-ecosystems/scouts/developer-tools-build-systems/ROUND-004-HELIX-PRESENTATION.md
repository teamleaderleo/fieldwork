# Helix final-view replay loops — review brief

Date: 2026-08-08  
Programme: #207  
Scout lane: #210  
Upstream contact authorized: `false`

## What Helix is

Helix is a terminal-based modal text editor written in Rust. It occupies roughly the same product category as Vim, Neovim, and Kakoune: keyboard-driven editing, modes, configurable keymaps, macros, multiple editor views, language-server integration, and terminal UI behavior.

The code involved here is not syntax highlighting or language support. It is the command-dispatch layer that turns keymaps and replayed input into editor commands.

## Existing upstream repair

Upstream issue:

- https://github.com/helix-editor/helix/issues/16111

Upstream repair:

- https://github.com/helix-editor/helix/pull/16136
- head: `85e9b90b66e614e10ace01f50e03d5abc0908b1d`
- current state at recheck: open and mergeable
- comments/reviews at recheck: none

The upstream repair handles one lifecycle path: `KeymapResult::MatchedSequence`.

A keymap such as:

```toml
[keys.insert]
C-q = ["wclose", "normal_mode"]
```

used to execute `normal_mode` after `wclose` removed the final editor view. `normal_mode` then dereferenced the now-empty view tree and panicked. The upstream PR changes matched-sequence execution so each completed command lifecycle returns `Editor::should_close()` and the sequence stops when the editor has no views left.

That repair is correctly placed after command execution and post-command/mode-switch dispatch.

## What the owned review found beyond that repair

Helix has three other synthetic replay loops that are independent of `KeymapResult::MatchedSequence`.

### 1. Configured keymap macros

`MappableCommand::Macro` stores a sequence of key events and later dispatches them through the compositor:

```rust
for key in keys.into_iter() {
    compositor.handle_event(&compositor::Event::Key(key), cx);
}
cx.editor.macro_replaying.pop();
```

If an early key closes the final view, a later key is still dispatched against the empty editor.

### 2. Recorded-register macro replay

`replay_macro` has nested count/key loops:

```rust
for _ in 0..count {
    for &key in keys.iter() {
        compositor.handle_event(&compositor::Event::Key(key), cx);
    }
}
cx.editor.macro_replaying.pop();
```

The same terminal transition can happen inside either loop. Cleanup still needs to run after stopping.

### 3. Counted dot-repeat

`EditorView::command_mode` replays the recorded insert operation inside an outer count loop and an inner `last_insert` event loop.

If the first replay closes the final view, another synthetic insert-mode operation can begin against the empty view tree.

## Executed proof

Owned review PR:

- https://github.com/teamleaderleo/helix/pull/3

On exact test head `4b750d6db183c199f648ff1079b7cf1eac59e57c`, Build run `30981560017` compiled successfully, passed workspace tests, and ran the integration suite:

```text
183 passed; 3 failed
```

The three failures were:

1. `macro_stops_after_final_window_close`;
2. `recorded_macro_stops_after_final_window_close`;
3. `counted_repeat_stops_after_replayed_final_window_close`.

Each failed with the same terminal condition:

```text
helix-view/src/tree.rs:327:18
internal error: entered unreachable code
```

Later exact-head runs reproduced the three crashes while formatting, clippy, docs, grammar checks, MSRV checks, and workspace tests remained clean.

## Controls

The owned matrix also checks that stopping is limited to the real terminal transition.

Passing controls include:

- ordinary matched sequences still complete;
- closing one of multiple views continues against the remaining view;
- a refused final close continues;
- configured macros continue while another view remains;
- recorded macros continue while another view remains;
- macro replay state is empty after normal continuation;
- counted dot-repeat clears `editor.count` when the editor remains open.

One experimental cleanup test incorrectly required an error status from a configured macro route. CI disproved that extra expectation, and it was removed. It did not affect the three crash reproductions.

## Proposed repair

The repair stays inside the three replay loops and reuses the same terminal predicate as upstream PR #16136.

### Configured macro

```rust
for key in keys.into_iter() {
    compositor.handle_event(&compositor::Event::Key(key), cx);
    if cx.editor.should_close() {
        break;
    }
}
cx.editor.macro_replaying.pop();
```

### Recorded macro

```rust
'replay: for _ in 0..count {
    for &key in keys.iter() {
        compositor.handle_event(&compositor::Event::Key(key), cx);
        if cx.editor.should_close() {
            break 'replay;
        }
    }
}
cx.editor.macro_replaying.pop();
```

### Counted dot-repeat

Use a labeled repeat loop and test `Editor::should_close()` after synthetic replay operations so the outer repeat stops immediately after terminal close. Leave the existing final cleanup in place:

```rust
cxt.editor.count = None;
```

## Why this is a good patch

The candidate does not add missing-view guards throughout editing commands. It enforces the lifecycle invariant at the dispatch/replay owners: once the editor reaches its terminal state, code that is manufacturing additional user input stops manufacturing it.

That gives one consistent rule across:

- matched keymap sequences;
- configured keymap macros;
- recorded macros;
- counted repeat.

The patch should touch only:

- `helix-term/src/commands.rs`;
- `helix-term/src/ui/editor.rs`.

The regression tests remain in the owned review overlay until a clean source-and-test branch is produced.

## Current candidate state

Owned clean candidate:

- https://github.com/teamleaderleo/helix/pull/7
- branch: `fix/final-view-replay-loops-clean`
- base: corrected control head `6e34c90b877167679d4f7d753ea6816059869699`
- runner commit: `aa068dddb9111f304c0246b836095e6827261396`
- current diff: one temporary workflow only
- production source commit: not yet present

The ordinary PR Build matrix is queued on the rebased candidate. The branch-local runner is prepared to apply and test the bounded source repair, then remove itself and commit only the two production files if all gates pass.

## Recommendation

Continue on Helix now.

This lane has:

- reproducible runtime failures;
- three stack traces pointing to the same lifecycle mistake;
- passing negative controls;
- a narrow two-file repair;
- an upstream PR that establishes the same terminal predicate for the neighboring command-sequence path.

The next acceptance bar is straightforward: produce the ordinary two-file source commit on the owned fork, run the focused command-sequence suite plus the normal Helix Build matrix, and require all terminal reproductions and continuation/cleanup controls to pass before considering any upstream interaction.
