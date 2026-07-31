# Receipt DTO decision-boundary review repair

Date: 2026-07-31  
Canonical campaign: Fieldwork #83  
Related Codex sources: #104, #106, #109  
Public upstream interaction: none

## Review result

Independent complete-diff review of Codex source #104 at `8b31601977ccedce8a1c79c81b1b055d733402a9` accepted the privacy-safe wire vocabulary and identified one decision-boundary blocker.

`ToolOperationReceipt` is a permissive public Serde DTO. Its `is_compaction_ready()` method treated every deserialized field combination as if version, epoch, sequence, identity, coverage, and legal transitions had already been validated. A caller could decode a combination such as `ReadOnly + Pending + Pending` and receive compaction authorization directly from wire state.

Review disposition:

- `ACCEPT vocabulary`;
- `REPAIR decision boundary`;
- hold #104 from compaction authority.

Source #104 remains target-executed from carrier #105 run `30623383624`, exact `5/5`, complete `codex-protocol` package. It was returned to draft after the review.

## Accepted repair

Publisher #109 at `2bc4e75d19743b87f14eac4bd2584a899dfc8ad1` is stacked on tool-effect source #106 at `b76d46832f8426cb8acb4031b00f41069c7d7014`.

The repair:

1. removes `ToolOperationReceipt::is_compaction_ready()` from the wire DTO;
2. preserves receipt fields and transition mutators for information-preserving wire state;
3. changes protocol controls to assert state transitions without making compaction decisions;
4. adds an inconsistent-wire-state control proving permissive decoding remains visible for later validation;
5. publishes one clean product file after six exact protocol controls and the complete package.

Publisher run: `30624296447`, queued at record creation.  
Output branch: `fieldwork/83-receipt-domain-boundary-464237`.

## Replacement ownership

- Protocol DTOs preserve and serialize observations.
- The live core ledger owns a private predicate for ledger-constructed local state.
- Durable replay validates version, epoch, sequence, identity, duplicate state, bounds, and coverage into a domain ledger before installation.
- Compaction consumes validated ledger state only.

The pre-review live-ledger publisher #108 was closed before execution. Its run `30623693696` remained queued and supplied zero source or target-test evidence. The ledger will be republished on the repaired protocol head with the predicate moved into core.

## Boundary

This repair does not enable compaction, replay, retry, dispatch, result persistence, or retirement. It removes premature decision authority and preserves those later gates as separate reviewed changes.

No merge, deployment, credentials, production mutation, or public upstream interaction occurred.
