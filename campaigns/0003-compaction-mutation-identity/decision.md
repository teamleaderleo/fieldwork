# Initial implementation decision

Decision date: 2026-07-30

Campaign: #83

## Decision

Do not add a compaction-only tool-name heuristic.

Implement the repair in two reviewable source stages before wiring all replacement paths:

1. operation-effect and terminal-receipt ownership at dispatch and result persistence;
2. pre-compaction validation plus compacted checkpoint preservation.

## Stage 1 acceptance

The first owned Codex change should:

- introduce a typed operation-effect enum;
- default unclassified client-executed runtimes to `PotentialMutation`;
- let explicitly safe runtimes opt into `ReadOnly`;
- create a bounded operation receipt when a call item becomes durable;
- update terminal and result-persistence state without retaining arguments or output bodies;
- add focused tests for default classification and receipt state transitions;
- leave compaction behavior unchanged until the receipt owner is established.

This stage prevents the validator from guessing and keeps the first code review below the campaign’s complexity limit.

## Stage 2 acceptance

The second owned Codex change should:

- validate complete, missing, duplicate, reordered, orphan, and late identities before prompt normalization;
- reject compaction for incomplete `PotentialMutation` operations with a typed recoverable error;
- permit complete and reconciled identities;
- integrate local, remote v1, and remote v2;
- preserve the minimal operation receipt through replacement history and rollout reconstruction;
- prove that resume, fork, inline continuation, and retry do not replay ambiguous mutations.

## Compatibility policy

Older rollout checkpoints without receipts hydrate as `unknown`. A pending or unknown potentially mutating operation requires reconciliation before new compaction. A checkpoint with no active call/result evidence remains compatible.

## Privacy policy

Persist only bounded typed state and stable operation identity. Exclude tool arguments, output bodies, credentials, provider payloads, resource names, and private content. Product diagnostics may use a keyed digest rather than a raw call ID.

## Testing order

1. receipt unit tests;
2. raw-history validator unit tests;
3. local compaction integration tests;
4. remote v1 tests;
5. remote v2 tests;
6. resume and fork reconstruction;
7. late-result and automatic retry controls.

## Stop rule

No source PR is accepted as the campaign repair until compiled tests prove fail-closed behavior for every ambiguous mutation class and normal continuation for complete identities.
