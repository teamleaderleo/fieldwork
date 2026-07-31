# Terminal retention current-source restack

Date: 2026-07-31  
Portfolio: Fieldwork #239  
Technical owner: Fieldwork #23 / F23  
Public upstream interaction: none

## Current-source package

The verified normal-close terminal-retention candidate has been restacked directly onto the latest inspected public Codex source.

- current public/source base: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`;
- current source PR: `teamleaderleo/codex#93`;
- exact current source head: `7f15307fd2c157d8a139310d2e8243f3f2b391a4`;
- predecessor source PR: `teamleaderleo/codex#91@5216ca53ef949c285508e2a2b71d02462a87f6ec`;
- historical behavior run/job: `30587866332` / `91023382172`;
- predecessor independent review: `4824480012`.

The six public commits from `97576b1794872e342450ebd577123e052ab57626` through `4642370542739d5dd080b0c87a9de06a6435d3db` change zero files in the terminal candidate's four-file fence. The current-source commit reuses the four byte-verified predecessor blobs and preserves every other path from the latest public tree.

Exact source fence:

- `codex-rs/core/src/unified_exec/async_watcher.rs`;
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`;
- `codex-rs/core/src/unified_exec/process.rs`;
- `codex-rs/core/src/unified_exec/process_tests.rs`.

## Exact current-source execution gate

A disposable one-file carrier is open as `teamleaderleo/codex#94`.

- carrier head: `f3d34f36e87d19f87a3b3739fa7c01e5e2bc4fc9`;
- workflow run: `30597355839`;
- state at this receipt: queued;
- source checked by the workflow: exact #93 head `7f15307fd2c157d8a139310d2e8243f3f2b391a4`.

The gate requires:

1. direct parent equals `4642370542739d5dd080b0c87a9de06a6435d3db`;
2. exact four-file fence and clean repository formatting;
3. nine uniquely resolved terminal/deque controls through the repository `just test` entrypoint;
4. focused `codex-core` package gate.

Required markers:

- `FIELDWORK_TERMINAL_CURRENT_SOURCE_FENCE=4/4`;
- `FIELDWORK_TERMINAL_CURRENT_EXACT=9/9`;
- `FIELDWORK_TERMINAL_CURRENT_CORE=PASS`.

## Current disposition

The artifact-materialization blocker is closed. The candidate now sits at a current-source execution and complete-diff gate.

A successful #94 receipt will move F23 from `delivery-gate-ready` with current-source execution pending to current-source target-executed, after which the disposable carrier can retire and #93 can receive final complete-diff review.

Hard termination, Windows process-tree containment, remote executor reattachment, durable result persistence, and unbounded retention remain separate findings.
