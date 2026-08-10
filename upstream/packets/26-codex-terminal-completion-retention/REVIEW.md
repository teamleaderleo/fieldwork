# Review record

## Disposition

`ISSUE OPEN / IMPLEMENTATION PROOF ACCEPTABLE / RESTACK BEFORE PUBLIC PR`

Upstream issue: `openai/codex#37207`  
Owned proof: `teamleaderleo/codex#144`

## Current source

- base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- current proof head: `d4ff73f50e30e96b6db4a08205c9d3600e15488e`
- shape: four Rust files

The current proof uses one shared output state:

```rust
struct OutputState {
    output: HeadTailBuffer,
    completion: HeadTailBuffer,
}
```

Each accepted producer chunk advances both retained views under one mutex before the live broadcast. Completion drains the completion view and replaces the partial listener transcript.

This is an improvement over the earlier two-mutex proof because it removes the window where one retained view could advance without the other and reduces producer-side locking.

## Authority review

The public flow still lets scheduled broadcast consumers influence retained output:

- the local collector can receive `Lagged` before adding missed chunks to its ordinary output buffer;
- the completion watcher can receive `Lagged` while building the transcript used at command completion;
- a completion watcher created after output was broadcast cannot receive earlier chunks.

Merged upstream PR `openai/codex#4992` gives useful intent for the first behavior. It changed unified exec to continue after `Lagged` so a slow receiver would skip missed messages but stay alive for later output. That is a reasonable live-stream resilience rule. It does not establish that missed live messages should also disappear from the completed command record.

The proof separates those roles: live observation may lose updates, while completion comes from bounded output retained before live delivery.

## Current static review

No blocking logic issue was found in the single-mutex adaptation during the latest review.

### `process.rs`

- Polling and completion views share one `Arc<Mutex<OutputState>>`.
- `record_output_chunk()` acquires that state once, pushes the completion copy and polling copy, then returns before broadcast.
- The local path consumes split stdout/stderr `mpsc` receivers directly rather than inserting the earlier combined broadcast before retention.
- Exec-server chunks follow the same retain-before-broadcast ordering.

### `async_watcher.rs`

- Live delta handling remains separate from completion retention.
- The listener may still skip `Lagged` for live observation.
- Before `output_drained`, completion replaces the listener-owned transcript with the retained completion view.
- Existing cancellation grace is unchanged.

### Tests

The proof still covers:

- output emitted before completion subscription;
- a deliberately lagged receiver;
- invalid UTF-8 through that lag case;
- partial transcript replacement;
- local and exec-server producer ordering;
- existing close/drain, capped-output, and synchronous-fallback behavior.

## Remaining review questions before a public PR

### Sustained output / backpressure

Retention now sits closer to the stdout/stderr readers. The critical operation is bounded and uses one mutex, but a current-main restack should add a sustained simultaneous stdout/stderr test while another task polls/drains output. That checks that preserving bytes does not create an unexpected stall under heavy output.

### Cancellation boundary

The patch intentionally preserves the existing trailing-output grace. A timing test should place output immediately before, around, and after that boundary so the completion guarantee is explicit.

### Live prompts

This repair improves the completed result. A live listener can still miss an interactive prompt while the command is running. Reliable live replay or lag signaling belongs to a separate change.

## Public drift

Latest public head checked: `b3278e96cb6df4b77b8dd93cf6c65d74990a033d`.

Two production files in the proof have changed upstream since the implementation base. Merged `openai/codex#37083` consolidated output state into `OutputHandles`. The public code still retains both relevant `Lagged(_) => continue` paths, so issue #37207 remains present, but the proof branch is no longer mechanically current-main-ready.

Any public PR should be a semantic restack onto current `OutputHandles` rather than a direct replay.

## Execution evidence

### Earlier paired receipt

Corrected paired run `30699322569` validated the previous two-mutex source head `b2a704c708748462d7893fe82cf8971f00ca751e`:

- baseline library `2,129/2,129`;
- source focused controls `12/12`;
- source library `2,133/2,133`;
- integration compilation passed;
- exact source fence and formatting passed.

### Current single-mutex head

- V8 canary `31072774070`: passed.
- Blocking CI `31072774224`: failed.
- Formatting, Rust benchmark smoke, cargo-shear, blob-size policy, cargo-deny, and codespell passed.
- The first deterministic failure is an owned-repository manifest check complaining about a stale `code-mode/Cargo.toml` feature-exception entry, outside this four-file proof.

The current single-mutex head still needs a fresh paired source-vs-baseline receipt before a public PR.

## Upstream state

`openai/codex#37207` is open with `bug`, `CLI`, and `tool-calls` labels. No maintainer comments were present at the latest check, and no public PR for this issue was found.

No follow-up public interaction is authorized without another owner decision.