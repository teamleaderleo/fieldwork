## In simple words

Codex separates the command result from the event transcript shown to clients. The command-result path drains an authoritative output buffer. The event path subscribes to a separate 64-chunk broadcast and skips lag notifications. A busy or paused event consumer can therefore receive a shorter transcript than the command actually produced. The retained probe makes that split deterministic: a 128-chunk subprocess produced 128 authoritative chunks while the modeled event transcript retained only chunks 64 through 127.

The rest of the lifecycle has several deliberate protections: live sessions are stored before the initial yield, terminal reads and writes are serialized, the terminal end event waits for output draining and active interaction, turn interruption has a bounded cleanup phase, and the TUI restores terminal modes on panic, external-program handoff, suspend, and exit. The campaign list below concentrates on the remaining deterministic seams.

## Assignment

- Fieldwork issue: `#23`
- Programme: `agent-cli-execution` (`#14`)
- Target hub: Codex (`#8`)
- Worker: `chatgpt:gpt-5.6-thinking`
- Fieldwork base: `09fe47ac92ec9c0c333b4979011f6321795deff2`
- Target revision: [`openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Retrieval date: `2026-07-29`
- Claim scope: mechanism and interface; operational consequences remain provisional
- Upstream contact: unauthorized and unused

## Contribution boundary

At claim time, Codex documents external code contributions as invitation-only and says unsolicited pull requests are closed without review. This scout therefore stops at source mapping, retained evidence, campaign candidates, and maintainer-direction questions. No upstream issue, pull request, discussion, comment, or other contact was created.

Evidence label: **Normative**.

## Code and test map

### Tool admission, approval, sandboxing, and retry

- `codex-rs/core/src/tools/handlers/unified_exec/exec_command.rs`
  - Parses the tool call, resolves environment and working directory, allocates the process id, handles apply-patch interception, and calls the unified-exec manager.
- `codex-rs/core/src/tools/orchestrator.rs`
  - Owns approval, permission materialization, sandbox selection, first attempt, sandbox-denial classification, retry approval, and the optional second attempt.
  - Uses a distinct retry run id derived from the call id.

Evidence label: **Documented** and **Observed**.

### Process and terminal state

- `codex-rs/core/src/unified_exec/mod.rs`
  - Owns `ProcessStore`, reserved ids, process entries, limits, yield bounds, output bounds, and deterministic test ids.
- `codex-rs/core/src/unified_exec/process_manager.rs`
  - Starts and stores sessions, collects command-response output, serializes per-terminal interaction, refreshes/removes exited sessions, prunes at the process cap, lists sessions, and terminates one or all sessions.
- `codex-rs/core/src/unified_exec/process.rs`
  - Wraps local PTY and exec-server processes, output tasks, state watches, cancellation, interruption, termination, and sandbox-denial checks.
- `codex-rs/utils/pty/src/process.rs`
  - Owns local child termination, reader/writer/wait tasks, PTY handles, resize, interrupt support, and stdout/stderr fan-in.

Evidence label: **Documented** and **Observed**.

### Event ordering and transcript assembly

- `codex-rs/core/src/unified_exec/async_watcher.rs`
  - Builds the event transcript from a broadcast subscriber, emits output deltas, waits for exit, output drain, late network-denial classification, and the interaction lock, then emits one terminal item.
- `codex-rs/core/src/tools/events.rs`
  - Emits command begin/end items and apply-patch file-change plus turn-diff events.
- `codex-rs/core/src/tools/parallel.rs`
  - Gates parallel-capable and exclusive tools, owns cancellation race handling, and emits the aborted-tool outcome.

Evidence label: **Observed**.

### Interruption, cleanup, and recovery

- `codex-rs/core/src/tasks/mod.rs`
  - Cancels the running task, allows a 100 ms graceful interval, aborts the task handle, invokes task cleanup, records and flushes the interrupted-turn marker, then emits and flushes `TurnAborted`.
  - Background terminals have separate list, terminate, and close-all operations.
- `codex-rs/core/src/session/handlers.rs`
  - Routes interrupt and explicit background-terminal cleanup independently.
- `codex-rs/tui/src/tui.rs`
  - Restores terminal modes on panic and exit, pauses input while handing the terminal to an external process, flushes buffered input, and re-enables modes afterward.
- `codex-rs/tui/src/tui/job_control.rs`
  - Restores modes before `SIGTSTP`, reapplies them after resume, probes cursor position, flushes input, and restores the inline or alternate-screen viewport.

Evidence label: **Observed**.

### Repository-state reporting

- `codex-rs/core/src/turn_diff_tracker.rs`
  - Tracks exact committed apply-patch deltas from captured content without rereading the workspace.
- `codex-rs/core/src/tools/events.rs`
  - Updates or invalidates the tracker only through apply-patch event completion.
- `codex-rs/core/src/unified_exec/process_manager.rs`
  - Creates unified-exec event contexts without a turn-diff tracker.

Evidence label: **Observed**.

### Relevant tests

- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
  - Covers late output, output-close ordering, grace fallback, late network denial, and UTF-8 chunk splitting.
- `codex-rs/core/src/unified_exec/process_tests.rs`
  - Covers remote write failure state and confirmed remote termination state.
- `codex-rs/core/src/unified_exec/process_manager_tests.rs`
  - Covers deterministic environment setup, bounded producer-buffer collection, omission propagation, network denial, and pruning policy.
- `codex-rs/core/tests/suite/unified_exec.rs`
  - Holds broader unified-exec integration coverage.

No test found in this revision forces the event subscriber to lag beyond the 64-chunk process broadcast and then compares the final event transcript with the authoritative producer buffer.

Evidence label: **Observed** with a source-search limitation.

## Lifecycle map

1. The handler allocates a process id and prepares a unified-exec request.
2. The orchestrator resolves approval and sandbox policy and opens the process.
3. The manager emits command begin, starts the event subscriber, and stores a live process before the initial yield.
4. The producer task writes every received output chunk to its retained `HeadTailBuffer`, then sends the chunk to a 64-entry broadcast.
5. The initial tool response independently drains the retained producer buffer.
6. The event subscriber consumes the broadcast, appends chunks to a second transcript, and emits deltas.
7. On process exit, cancellation starts a trailing-output phase. The terminal watcher waits for transcript drain, late denial classification, and the interaction lock before emitting the terminal item.
8. Polls and writes share the interaction lock. A terminal interaction event therefore completes before the terminal end event can acquire the same lock.
9. Turn interruption cancels the task and flushes the abort marker and event. Background processes remain under the unified-exec manager until natural exit or explicit cleanup.

## Retained probe

Artifact: `artifacts/unified_exec_broadcast_lag_probe.py`

Command:

```bash
python3 artifacts/unified_exec_broadcast_lag_probe.py --chunks 128 --capacity 64
```

Retained result: `artifacts/probe-result.json`

Observed model result:

- subprocess exit code: `0`
- authoritative chunks: `128`
- event transcript chunks: `64`
- skipped chunks: `64`
- first authoritative chunk: `chunk-0000`
- first event chunk: `chunk-0064`
- terminal transcript matched authoritative output: `false`

The model preserves the consequential mechanism: one authoritative producer capture, one bounded event broadcast, a delayed subscriber, lag ignored, and a terminal event derived from the subscriber transcript. It omits Tokio scheduling, PTY behavior, protocol serialization, and the Codex binary. This result demonstrates mechanism feasibility and supplies a direct unit-test design; it does not establish real-world frequency.

Evidence label: **Illustrative**, anchored by **Observed** source behavior.

## Ranked campaign candidates

### 1. Make unified-exec terminal transcripts loss-aware and reconcilable

**Current behavior.** Local process output is retained in the producer buffer, then copied through a 64-chunk broadcast. The event subscriber handles `Lagged` by continuing. The final terminal item is assembled from the subscriber transcript.

**Consequence.** Under subscriber delay or bursty output, the command response and terminal event can disagree. A resumed session, app-server consumer, TUI history, or audit consumer may retain a shorter middle-truncated transcript without an omission marker.

**Owning boundary.** `unified_exec/process.rs` and `unified_exec/async_watcher.rs`.

**Campaign evidence.** Add a deterministic test that sends more than 64 distinct chunks before allowing the subscriber to run, then asserts one of these explicit contracts:

- replay missed chunks from the authoritative producer buffer;
- build the final item directly from an authoritative sequence-aware transcript; or
- emit a counted omission marker and preserve a machine-readable loss signal.

Compare local and exec-server paths: the exec-server path already uses sequence numbers and replay reads when events lag or sequences jump.

**Disposition.** Open a focused correctness campaign. Implementation waits for maintainer direction.

**Evidence labels.** **Observed**, **Illustrative**, operational impact **Inferred**.

### 2. Define confirmed termination as a close-and-drain protocol

**Current behavior.** Confirmed termination requests process termination, marks the wrapper exited, cancels the process token, and aborts the output task. The local lower layer kills the child and aborts reader, writer, and wait tasks. The terminal watcher can then complete with the last state available, commonly using `-1` when no exit code was observed.

**Consequence.** Final child output, a real signal-derived exit status, or a backend failure may disappear during explicit termination. The event can report a generic failure while the caller believes termination was confirmed.

**Owning boundary.** `unified_exec/process.rs`, `utils/pty/src/process.rs`, and `unified_exec/process_manager.rs`.

**Campaign evidence.** Run a child with a signal/termination handler that writes a unique final marker and exits with a known code. Terminate through both local and exec-server paths. Assert event ordering, final marker presence, state, and exit-code contract. Include a backend that acknowledges termination before publishing `Closed`.

**Disposition.** Run a lifecycle campaign before proposing a change. Candidate improvements include a bounded close wait, separate `termination_requested` and `closed` states, and an explicit termination reason.

**Evidence labels.** Source behavior **Observed**; output-loss consequence **Inferred**.

### 3. Make background-terminal capacity eviction explicit

**Current behavior.** The process store has a soft cap of 64. At capacity, pruning prefers an old exited entry, then falls back to the least-recently-used live entry outside the eight most recent. A pruned live process is terminated after removal. Its process state carries no dedicated capacity-eviction reason.

**Consequence.** Opening another terminal can end an older live job. The final command item may show a generic `-1` failure without identifying resource pressure or which request caused eviction. Recovery becomes guesswork for long-running build, watch, or server commands.

**Owning boundary.** `unified_exec/process_manager.rs`.

**Campaign evidence.** Open 65 deterministic long-lived sessions, record list order and terminal events, and assert the exact eviction contract. Compare these policies: reject the new session, terminate an old session with an explicit reason, or expose capacity and eviction telemetry to clients.

**Disposition.** Open a bounded resource-lifecycle campaign after the transcript campaign. No architecture replacement needed.

**Evidence labels.** Policy and termination **Observed**; user consequence **Inferred**.

### 4. Reconcile repository mutations performed through commands

**Current behavior.** Turn-diff reporting tracks exact apply-patch deltas from captured content and intentionally avoids rereading the filesystem. Unified-exec command events carry no tracker. A command that changes files or Git state can therefore leave the turn-diff view unchanged while the repository changed.

**Consequence.** Clients that use turn-diff events as the current-turn change record can miss command-driven edits, generated files, renames, resets, checkouts, or cleanup. Resume and review flows then have two state views: the workspace and the retained turn diff.

**Owning boundary.** `turn_diff_tracker.rs`, `tools/events.rs`, unified-exec completion, and the session's repository snapshot contract.

**Campaign evidence.** Define the product contract first. Then run a temporary Git repository through commands that edit, rename, delete, reset, and switch branches. Compare workspace state, Git status, command items, turn-diff events, and resumed-session state. Candidate contracts include explicit invalidation, scoped post-command reconciliation, or clear API naming that limits turn diff to apply-patch mutations.

**Disposition.** Start with interface research and maintainer direction. This crosses repository-state and performance boundaries.

**Evidence labels.** Mechanism **Observed**; client dependence and severity **Unknown**.

### 5. Specify stdout/stderr chronology for local execution

**Current behavior.** Local stdout and stderr arrive on separate channels and are merged with an unbiased select and no shared sequence. Unified-exec then labels output deltas as stdout and builds one aggregate transcript.

**Consequence.** Cross-stream chronology can vary from the child's write order, and stream identity disappears in the unified transcript. This complicates deterministic log parsing and failure reconstruction.

**Owning boundary.** `utils/pty/src/process.rs` and `unified_exec/async_watcher.rs`.

**Campaign evidence.** First establish the intended contract for TTY and non-TTY modes. Use a child that alternates numbered stdout/stderr writes under controlled flushing. Repeat across local PTY, local pipes, exec server, Unix, and Windows. Preserve source stream and sequence where the backend can supply them; document aggregate-only semantics where it cannot.

**Disposition.** Retain as a lower-priority compatibility campaign pending contract evidence.

**Evidence labels.** Merge behavior **Observed**; chronology consequence **Inferred**.

## Negative results and existing protections

- Live background sessions are stored before the initial yield, protecting them from accidental drop when the active turn is interrupted.
- Per-terminal polls and writes share an interaction lock. The terminal end watcher takes the same lock after output drain, giving terminal interaction publication a clear ordering boundary.
- The event watcher waits for late network-denial classification before finalizing the terminal item.
- Exec-server output carries sequence numbers and has a replay path for lag and gaps.
- Turn abort records and flushes its history marker before emitting `TurnAborted`, then flushes the terminal event.
- TUI startup installs a panic hook that restores terminal state. Exit restoration resets keyboard reporting, raw mode, focus, paste, cursor, console mode, and stderr handling.
- Suspend/resume and external-program handoff explicitly pause event input, restore modes, flush input, and reapply TUI modes.
- Production process ids are random but checked against reserved ids; deterministic tests use monotonically increasing ids. No collision defect was identified.

These protections make broad lifecycle replacement a poor campaign. The candidates above are narrow ownership-boundary problems.

Evidence labels: **Observed** and **Negative result**.

## Competing hypotheses

1. **Broadcast lag is practically unreachable.** The event subscriber usually runs concurrently and processes chunks quickly.
   - Distinguishing evidence: an in-repository stress test with forced scheduler delay, large rapid chunks, and protocol serialization enabled.
2. **The final item only promises best-effort streaming history.** The tool response remains authoritative.
   - Distinguishing evidence: a documented protocol contract and client code showing how final command items are consumed and persisted.
3. **Dropping output on termination is acceptable.** Explicit termination prioritizes immediacy over drain.
   - Distinguishing evidence: documented semantics plus tests asserting the chosen exit code, output boundary, and completion event.
4. **Turn diff intentionally covers apply-patch only.** Command-driven mutations are outside that surface.
   - Distinguishing evidence: API naming/documentation and consumers that independently query repository state before review or resume.

## Recommendation

Promote candidate 1 into the next campaign. It has a compact owning boundary, a deterministic adversarial test, a direct local-versus-exec-server comparison, and a clear correctness contract.

Queue candidates 2 and 3 as lifecycle probes. Keep candidate 4 in interface research until client expectations and repository-state costs are explicit. Keep candidate 5 as compatibility research.

## Limitations

- Source review used the pinned GitHub revision through repository APIs.
- The execution container could not resolve GitHub, so the Codex workspace and binary were not cloned or built.
- The retained probe is a mechanism model with a real subprocess, not a Codex end-to-end test.
- No testbed was selected.
- No claims about model output quality are included.
- No upstream contact occurred.
