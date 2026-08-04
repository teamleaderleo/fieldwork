# Upstream pull request draft — use only after issue agreement

> Recreate the source as a direct child of current public main and rerun all gates before use.

## Title

fix(core): retain terminal completion output before best-effort broadcast

## Summary

- retain bounded stdout/stderr at the unified-exec producer before broadcasting live deltas;
- keep broadcast best effort for live observers;
- reconcile the final command transcript from producer-owned state on normal close;
- preserve existing output bounds, UTF-8 delta handling, cancellation grace, and synchronous fallback behavior;
- add regressions for pre-subscription output and lagged observers.

## Problem

The producer can receive output before the streaming subscriber attaches or while the subscriber is lagged. Because the subscriber currently owns the accumulated completion transcript, those bytes can be missing from the final completed item.

## Files

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

## Prepared evidence

Owned implementation proof: `teamleaderleo/codex#144@b2a704c708748462d7893fe82cf8971f00ca751e`.

Corrected paired execution run `30699322569`:

- baseline library: `2,129/2,129`;
- source focused controls: `12/12`;
- source library: `2,133/2,133`;
- integration targets compiled;
- formatting and exact four-file fence passed.

All four source-base files were still byte-identical on public head `7325f348a2ff9e1a7dd931ed9ad65f365d064146` when the packet was refreshed.

## Test plan

- output emitted before subscription appears in the completed item;
- lagged live receivers do not affect producer retention;
- invalid UTF-8 remains in the authoritative bounded transcript;
- partial streamed state is replaced by the full bounded producer transcript;
- local and exec-server producers follow the same authority ordering;
- normal close and synchronous command behavior remain unchanged;
- complete `codex-core` library and relevant integration compilation pass.

## Non-goals

- unbounded terminal history;
- hard-kill output beyond the existing grace boundary;
- process-tree cleanup or remote reattachment;
- conversation-history persistence;
- general operation receipts.

No public upstream interaction has occurred.