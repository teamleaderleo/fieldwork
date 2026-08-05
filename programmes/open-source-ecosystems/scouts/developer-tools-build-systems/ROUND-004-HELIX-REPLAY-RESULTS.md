# Developer tools scout round 004 — Helix replay results

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `executed failing characterizations; owned-fork production candidate authorized`  
Upstream contact authorized: `false`

## In simple words

The active upstream Helix repair correctly stops ordinary mapped command sequences after the final view closes. The same terminal transition remains unsafe in three adjacent replay engines:

1. configured keymap macros;
2. recorded-register macro replay;
3. counted dot-repeat of the last insert.

All three owned tests compiled and failed during the repository's target-native integration suite with the same empty-view tree panic. The surrounding controls passed.

## Exact identity

- repository: https://github.com/teamleaderleo/helix
- owned pull request: https://github.com/teamleaderleo/helix/pull/3
- upstream repair base: `85e9b90b66e614e10ace01f50e03d5abc0908b1d`
- executed owned head: `4b750d6db183c199f648ff1079b7cf1eac59e57c`
- pull-request merge test revision: `5431c1f0393acc1c5795862ea2e502cd3963f690`
- workflow: `Build`
- run: `30981560017`
- failing job: `92226916213`
- platform: `windows-11-arm`

## Command evidence

The repository workflow ran:

```text
cargo test --workspace
cargo integration-test
```

`cargo test --workspace` completed successfully.

The integration suite compiled successfully, ran 186 tests, and reported:

```text
183 passed; 3 failed
```

## Failing characterizations

### Configured keymap macro

Test:

```text
test::command_sequences::macro_stops_after_final_window_close
```

Binding concept:

```toml
[keys.normal]
C-x = "wclose"
C-q = "@<C-x>l"
```

The macro dispatches `wclose`, closes the only view, then dispatches movement against the empty editor.

Result:

```text
helix-view/src/tree.rs:327:18
internal error: entered unreachable code
```

### Recorded-register macro

Test:

```text
test::command_sequences::recorded_macro_stops_after_final_window_close
```

The target-native key sequence records a macro while two views exist, then replays it when one view remains. The first recorded key closes the final view and a later recorded movement key still runs.

Result:

```text
helix-view/src/tree.rs:327:18
internal error: entered unreachable code
```

### Counted dot-repeat

Test:

```text
test::command_sequences::counted_repeat_stops_after_replayed_final_window_close
```

The fixture records an insert-mode close while another view remains, then requests two repeats when one view remains. The first repeat closes the editor and the second iteration starts against the empty editor.

Result:

```text
helix-view/src/tree.rs:327:18
internal error: entered unreachable code
```

## Passing controls on the same run

The following controls passed:

- `single_command_final_window_close_exits_cleanly`;
- `normal_mode_sequence_after_final_window_close_exits_cleanly`;
- `ordinary_command_sequence_runs_to_completion`;
- `command_sequence_continues_when_another_window_remains`;
- `refused_final_window_close_keeps_sequence_context_alive`;
- `macro_continues_when_another_window_remains`;
- upstream `test_keymap_sequence_stops_after_closing_last_view`.

These controls establish that the guard must follow editor terminal state rather than command identity. Replays continue when another view remains and stop only after the final view is actually gone.

## Source ownership

### Configured keymap macros

`MappableCommand::Macro` queues a compositor callback that loops over parsed keys:

```rust
for key in keys {
    compositor.handle_event(&Event::Key(key), cx);
}
```

It does not check `cx.editor.should_close()` between keys.

### Recorded-register macros

`replay_macro` loops over the requested count and register keys:

```rust
for _ in 0..count {
    for &key in keys.iter() {
        compositor.handle_event(&Event::Key(key), cx);
    }
}
```

It does not stop either loop after terminal close.

### Counted dot-repeat

`EditorView::command_mode` executes the saved insert command and replays saved insert events inside a count loop. It does not stop the current replay or later count iterations when the editor closes.

## Candidate repair boundary

The narrow candidate is to apply the existing editor terminal predicate inside each synthetic-input loop:

1. configured macro — break after a dispatched key makes `should_close()` true;
2. recorded macro — break the key loop and stop later count iterations, while still clearing `macro_replaying`;
3. dot-repeat — stop saved insert events and later repeat iterations, while still clearing `editor.count`.

The candidate must preserve the passing two-view controls and normal replay behavior.

## Current disposition

`EXECUTED DEFECT / THREE ADJACENT REPLAY LOOPS`

A production candidate is justified in the owned fork. The next evidence must include:

- the three formerly failing tests passing;
- the two-view macro control still passing;
- the upstream command-sequence regression still passing;
- ordinary workspace and integration gates.

No public upstream interaction was performed.
