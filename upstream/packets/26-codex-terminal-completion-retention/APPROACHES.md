# Approaches considered

## 1. Keep final output subscriber-owned

Rejected. Broadcast delivery is intentionally best effort. Pre-subscription output and `Lagged` events make subscriber timing part of the final result.

## 2. Increase broadcast capacity

Rejected. A larger ring changes probability, not authority. It cannot recover bytes emitted before subscription and can still be overrun.

## 3. Attach another subscriber earlier

Rejected. This creates another scheduled observer and still makes final correctness depend on broadcast/task lifecycle.

## 4. Retain unbounded producer output

Rejected. It repairs loss by introducing unbounded per-process memory growth.

## 5. Retain one bounded producer transcript

Selected in principle. Final output must come from bytes retained by the process owner before live delivery.

## 6. Use a standalone deque and overlap streamed/retained views

Implemented in earlier prototypes, then superseded.

Overlap inference is more complex than necessary and creates repeated-pattern and truncation questions. The current process already uses `HeadTailBuffer`; using the same bounded representation for producer completion state permits direct replacement rather than heuristic suffix/prefix reconciliation.

## 7. Add a bounded completion buffer beside the ordinary output buffer

Selected implementation.

- write every accepted local or exec-server chunk to completion state before broadcast;
- retain existing ordinary output-buffer behavior;
- preserve live best-effort events;
- replace the final partial observer transcript from the producer-owned bounded buffer on normal close.

This cleanly separates live observation from terminal authority.

## 8. Keep the local intermediate combined broadcast

Rejected in the selected source.

The old local path converted stdout/stderr `mpsc` receivers into an intermediate broadcast receiver before Codex retained output. That added another lossy channel. The source consumes the two `mpsc` receivers directly with `tokio::select!`, preserving merge behavior while retaining before the one live broadcast.

## 9. Patch only the completion consumer

Rejected. A consumer cannot reconstruct bytes that no subscriber received. The owning producer must preserve them.

## 10. Introduce a general receipt framework first

Rejected for this issue. The concrete final-output authority bug is independently repairable. A broad receipt abstraction would enlarge the review surface and delay a user-visible correctness fix.

## 11. File one umbrella issue about lost information

Rejected. Terminal bytes, persistence acknowledgement, prewarm lineage, and cleanup certainty have different owners and failure contracts. File bounded issues in sequence and explain the common authority principle only as context.

## 12. First issue: append acknowledgement

Deferred to sequence item 2.

Append acknowledgement is a useful visibility seam, but every current caller discards it. Terminal retention demonstrates actual user-visible information loss and has a stronger first-contact narrative.

## 13. First issue: terminal completion retention

Selected.

Reasons:

- direct missing output in a completed command;
- exact producer/observer ownership error;
- no current public duplicate found;
- four-file clean source and complete review;
- 12/12 focused tests plus paired complete library execution;
- all source-base files unchanged on current public main.

## 14. Submit a public PR immediately

Deferred. Start with a bounded issue asking whether producer-owned retention is the intended boundary. Link to the clean owned implementation as evidence after explicit authorization. Restack and rerun only after the issue direction is accepted.

## 15. Treat old setup failures as source evidence

Rejected. Missing tools, shallow history, guard mismatches, and the superseded wrong broad gate remain carrier diagnostics. The authoritative execution is corrected paired run `30699322569`.

No public upstream interaction occurred.