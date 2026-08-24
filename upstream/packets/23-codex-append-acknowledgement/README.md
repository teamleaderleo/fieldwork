# Unit 23 — Codex append acknowledgement

## Current disposition

`IMPLEMENTATION PROOF COMPLETE / CURRENT-MAIN REFRESH REQUIRED / PROPOSAL SEQUENCE: SECOND`

The discovery remains present on public Codex main inspected at `7325f348a2ff9e1a7dd931ed9ad65f365d064146`: `record_conversation_items()` and its persistence helpers still discard the live-thread append result before raw-response delivery continues.

The retained implementation proof is `teamleaderleo/codex#140@babc761faeb1bf618aa4a9495236336f6d63f006`, based on `2b5bdcf67547860f2e5c5a605009a70026796b2b`. It is one reviewed commit touching exactly:

- `codex-rs/core/src/session/mod.rs`
- `codex-rs/core/src/session/turn_tests.rs`
- `codex-rs/thread-store/src/in_memory.rs`

Public main advanced 66 commits after that base and changed `session/mod.rs`, so #140 is evidence and design proof, not a current-main delivery head. Refresh and rerun only when this issue is authorized and reaches its turn in the proposal sequence.

## Finding

The session boundary currently combines three actions:

1. update in-memory conversation history;
2. attempt authoritative rollout persistence;
3. deliver raw response items to observers.

The persistence outcome is logged and lost. Observer delivery therefore cannot establish that authoritative history acknowledged the item.

The implementation proof returns a boolean acknowledgement:

| case | acknowledgement | durable item |
| --- | --- | --- |
| no live thread | `true` | persistence not required for the ephemeral session |
| successful live append | `true` | present |
| pre-write failure | `false` | absent |
| commit-then-error | `false` | may already be present |

`false` means only “not acknowledged.” It proves neither absence nor retry safety.

## Result-shape decision

Fieldwork #503 is complete. Retain `bool` for this first seam because every reviewed production caller discards the value. Widen to typed certainty or a reconciliation receipt only when a concrete caller needs to distinguish confirmed absence from unknown commit outcome.

## Proposal sequence

1. **Terminal output retention first.** Best-effort broadcast can erase bytes from the final command transcript. The four-file source fence remains byte-identical on current public main and its implementation has a complete execution receipt.
2. **Append acknowledgement second.** Surface the authoritative history append acknowledgement, link to a refreshed #140 implementation, and keep retry/caller policy out of scope.
3. **Responses Lite lineage third.** Prevent non-generating prewarm state from becoming the predecessor of the first generated request.
4. **Cleanup and remote outcome uncertainty later.** Coordinate with existing public liveness issues rather than filing a duplicate umbrella report.

Recent public Codex commit `17df7545a34ac533eedf5b628f49f2f1ad60e44e` reinforces the governing principle: unresolved state must not be mislabeled as cancellation, and late terminal results should remain reportable.

## Validation retained

Current-source predecessor materialization run `30754015720` passed formatting, four exact append-outcome controls, the complete `codex-thread-store` package, and the exact three-file gate. Review `4842611857` found no code issue inside the unit fence.

Historical exact receipts and superseded sources remain indexed in this packet. PR #136 is closed as superseded; execution carriers are retired.

## Public boundary

No public upstream interaction occurred. Before eventual discussion:

- refresh semantically onto the then-current public head;
- rerun exact and ordinary gates;
- repeat duplicate and overlap search;
- link only to the clean implementation proof, not Fieldwork machinery;
- obtain explicit public-contact authorization.