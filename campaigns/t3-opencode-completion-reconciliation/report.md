# Campaign: T3 and OpenCode lifecycle ownership

State: `claimed`

Last reconciled: `2026-07-30`

## Current status

Campaign #71 no longer treats the legacy OpenCode adapter as the assumed production landing target.

The legacy investigation remains valid executable evidence, but later source movement in the open Orchestration V2 stack materially changes the ownership architecture. Review issue #234 now decides whether to:

- transfer the accepted lifecycle contracts to V2 and hold legacy production work;
- retain a narrowly justified legacy compatibility slice; or
- repair missing V2 controls before either path proceeds.

No production T3 source is committed. No upstream contact is authorized.

## Read these records

- Current V2 source comparison and required controls: [`artifacts/orchestration-v2-reexamination.md`](artifacts/orchestration-v2-reexamination.md)
- Full legacy investigation preserved verbatim: [`report-legacy-2026-07-30.md`](report-legacy-2026-07-30.md)
- Exact contract matrix: [`artifacts/test-matrix.json`](artifacts/test-matrix.json)
- Landing-target review: Fieldwork issue #234
- Prior A/B/C/D disposition: Fieldwork issue #178
- Canonical dossier: Fieldwork PR #75
- Owned T3 test-only carrier: `teamleaderleo/t3code#1`

## Current evidence

### Legacy exact controls

Owned T3 test-only head:

`cae5d869f3ca441b4117197e34796a7d8b9466af`

The unpatched exact controls execute and fail on the intended current boundaries, including:

- resumed-session recovery without exact active-run ownership;
- successful abort without canonical persisted settlement;
- stale and duplicate interruption races;
- caller cancellation and teardown overlap;
- provider-session generation replacement;
- pending request expiry and late-response rejection;
- legacy reaper check-then-stop ordering.

The first A, B, and composed candidate matrix did not test candidate behavior because malformed stored patch hunk metadata stopped `git apply`. Those failures are carrier defects, not product results.

The carriers were repaired at Fieldwork commits:

- A: `8e2cc0053aaf653b069a08349557c3268c795d08`;
- B: `8df686d9616281083d276af50f9ae72277a73070`;
- A+B overlay: `03ad4d94c8ed13d9b1d16673affc5863853452f2`.

Fieldwork integrity now validates candidate unified-diff hunk metadata and runs negative controls. Repaired A and B workflows passed their filter stages and have real focused, existing-suite, ingestion, and typecheck jobs queued. No green candidate claim exists.

### Orchestration V2 source movement

Pinned open upstream inputs:

- [`pingdotgg/t3code#2829`](https://redirect.github.com/pingdotgg/t3code/pull/2829) at `1c24c650c74c813d07209a25f1384890d22e315d`;
- [`pingdotgg/t3code#4759`](https://redirect.github.com/pingdotgg/t3code/pull/4759) at `1e994fdcbe155999574a5f3c4ae964a2c8118e39`;
- [`pingdotgg/t3code#4786`](https://redirect.github.com/pingdotgg/t3code/pull/4786) at `a3b3a5d5af53850f74ef7d6741f6ef07b368cfdc`.

These are open source inputs, not merged or released behavior.

Source review confirms V2 introduces:

- durable app runs and attempts;
- exact provider session, thread, and turn identity;
- typed runtime request states (`pending`, `resolved`, `expired`, `cancelled`);
- a durable per-thread serialized effect outbox for provider interruption and other external effects;
- fail-closed process recovery that cancels nonterminal provider work and expires pending requests;
- live-session idle release guarded by busy count, idle generation, runtime identity, and atomic entry removal.

This architecture strongly supersedes the legacy shape for pending-request cleanup and reaper safety. It also changes restart handling from uncertain outcome reconstruction to explicit cancel-on-restart. The remaining review question is whether V2's durable outbox is the correct sole owner for interruption and whether post-crash `cancelled` is acceptable when an abort may have reached OpenCode without a durable receipt.

## Active disposition

### A — interruption ownership

Prior review accepted the contract only with exact generation/session/turn fencing and canonical interrupted settlement.

V2 appears to supply that ownership primarily in the durable outbox and provider-turn control service rather than inside the OpenCode adapter. Review #234 must approve or repair that layer choice.

### B — pending interactive requests

V2's typed request states and exact provider-turn affinity materially match the truthful-expiry contract. Require exact ordering and late-response controls before transfer.

### C — restart and delayed-event correlation

Legacy status/history reconstruction remains held. Review #234 decides whether V2's explicit cancel-on-restart policy is the supported replacement.

### D — external idle-release ordering

Legacy reaper production work remains held. V2's generation-checked live-session manager supplies the missing atomic ownership boundary, subject to exact adversarial execution.

## Required next gates

1. Let the repaired legacy A/B jobs execute and classify only exact-head results.
2. Do not create a legacy production branch while #234 is open.
3. Execute V2 controls for duplicate interruption, caller cancellation after command commit, process loss after abort acceptance, replacement-session fencing, request cleanup ordering, and stale idle-release generation.
4. Do not treat open upstream PRs as merged behavior.
5. Restack Fieldwork PR #75 onto current `main` before promotion or merge; the pre-restack head is preserved at `archive/campaign-71-pre-adaptive-restack`.
6. Keep upstream contact unauthorized.

## Stop conditions

Hold promotion if:

- an old effect can target or settle a replacement provider generation;
- process recovery can leave any run, request, node, provider turn, or effect falsely active;
- request cleanup can be represented as user-authored input;
- external session release can proceed from a stale idle observation;
- exact V2 controls are missing or fail;
- the landing architecture remains dependent on unmerged source without a pinned executable carrier.
