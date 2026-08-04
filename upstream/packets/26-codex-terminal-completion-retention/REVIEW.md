# Review record

## Disposition

`ACCEPT ISSUE-FIRST SOURCE / REFRESH DIRECT PARENT BEFORE DELIVERY`

Reviewed source:

- PR: `teamleaderleo/codex#144`
- base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- head: `b2a704c708748462d7893fe82cf8971f00ca751e`
- review: `4856710273`
- shape: one commit, four files, 294 additions, 57 deletions

No blocking code finding was identified inside the stated normal-close scope.

## Authority review

The old flow lets a broadcast subscriber assemble the final transcript. That subscriber can attach late or receive `Lagged`, so successful live delivery is not a complete record of what the producer received.

The selected source separates the owners:

- local and exec-server producer paths write each chunk to a bounded completion buffer first;
- live broadcast remains best effort;
- the completion watcher reconciles the observer transcript from producer-owned state before signaling output drained;
- a nonempty synchronous fallback remains authoritative for the synchronous command path.

This is the smallest repair that prevents observer loss from erasing final command bytes.

## File review

### `process.rs`

- Adds a separate bounded completion buffer.
- Records chunks into both the ordinary read buffer and completion buffer before broadcast.
- Removes the local intermediate combined broadcast receiver and consumes the stdout/stderr `mpsc` receivers directly, eliminating a second lag point before retention.
- Preserves stdout/stderr selection semantics: the removed helper also merged the two receivers with `tokio::select!`.
- Preserves output-close notification through `OutputTaskGuard`.

### `async_watcher.rs`

- Live deltas remain best effort and retain existing UTF-8/event limits.
- Subscriber lag no longer affects authoritative completion state.
- On normal output completion, the watcher drains any remaining broadcast events and then replaces the partial transcript with the producer-owned bounded transcript.
- Existing cancellation grace remains unchanged.

### Tests

The tests exercise output sent before subscription, a deliberately lagged receiver, invalid UTF-8, bounded producer retention, transcript replacement, local and remote producer paths, and close/drain behavior.

## Risk review

### Accepted

- **Memory:** a second head/tail buffer exists per process, but it is bounded by the existing buffer type rather than unbounded output.
- **Live/final divergence:** intentional. Live deltas are observational; the final transcript is authoritative.
- **Drain ownership:** `reconcile_transcript()` drains the completion buffer once into the final transcript after the existing close/grace decision.
- **Repeated patterns:** replacement uses the producer transcript directly, avoiding heuristic overlap matching.

### Explicit limits

- Bytes that arrive only after the existing hard-termination grace boundary are not newly guaranteed.
- This does not solve process-tree cleanup, reattachment, remote settlement, conversation persistence, or unbounded transcripts.
- A final direct-parent restack and rerun are required before an authorized PR.

## Current-public comparison

All four base files remain byte-identical on public `7325f348a2ff9e1a7dd931ed9ad65f365d064146`. The implementation therefore has no file-level conflict with intervening public work.

This comparison supports issue readiness but does not replace a final current-head execution.

## Test evidence

Corrected paired run `30699322569`:

- baseline library `2,129/2,129`;
- source focused controls `12/12`;
- source library `2,133/2,133`;
- integration compilation passed;
- exact source fence and formatting passed.

## Issue suitability

This is the strongest first Codex issue because it is:

- a direct information-loss mechanism;
- user-visible in the completed command result;
- bounded to one producer/observer authority error;
- supported by a complete implementation and paired execution;
- not duplicated in the current public issue search;
- independent of the broader receipt architecture.

The issue should ask whether bounded producer-owned retention is the intended final-output authority and link only to the clean source PR #144 as implementation evidence.

No public upstream interaction occurred.