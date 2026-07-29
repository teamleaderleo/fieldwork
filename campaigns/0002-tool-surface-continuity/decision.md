# Final Decision Record

## In simple words

All eight research lanes are complete and accepted. The campaign now moves from investigation to bounded implementation. The first implementation protects mutations across compaction. The second adds explicit host and MCP refresh contracts. Request exposure and fallback authority follow as separate work.

Decision date: 2026-07-30

Campaign: #31

Decision owner: GPT-5.6 Thinking coordinator takeover

## Accepted evidence

- #61 / L01 lifecycle provenance
- #58 / L02 transport and prewarm
- #64 / L03 compaction and result identity
- #62 / L04 MCP and app catalogue convergence
- #59 / L05 deferred discovery
- #81 / L06 effective-surface diagnostics
- #60 / L07 fallback authority
- #57 / L08 ChatGPT coexistence field trial

Every accepted lane retains exact revisions, bounded commands or integration receipts, evidence labels, negative findings, and upstream-contact status.

## Decision

### Close Campaign #31 research after PR #51 is updated and merged

The campaign question has been answered at interface scope: several independent lifecycle boundaries can reduce or misreport the effective tool surface, and receipt v1 identifies the earliest observable boundary in every retained case.

### Promote implementation campaign 1 — mutation identity and compaction checkpoint

Current behavior:

- missing output becomes a synthetic prompt result;
- duplicate and reordered outputs pass through;
- late output can become orphaned after replacement;
- compacted replacement loses raw call/result identity.

Required candidate:

- mutation-aware raw-history validator before local, remote v1, and remote v2 compaction;
- durable privacy-safe operation receipts carried into checkpoints;
- late-result reconciliation and duplicate/causal-order rejection;
- automatic retry contract based on idempotency and reconciliation;
- receipt-v1 instrumentation for completion, persistence, and delivery.

Stop condition: compiled owned-fork tests distinguish complete, missing, duplicate, reordered, and late mutation results and prove the candidate fails closed without replay.

### Promote implementation campaign 2 — host lifecycle and MCP refresh contract

Current behavior:

- saved host declarations can silently win cold reconstruction;
- ordinary MCP refresh can reuse a client whose remote identity and catalogue changed.

Required candidate:

- preserve, replace, clear, and reject host lifecycle policies;
- saved/current/effective provenance receipt;
- generic MCP hard refresh or live relist with remote identity and catalogue digest validation;
- revision increment for every accepted catalogue replacement;
- old captured steps retain authority while new steps receive the new binding.

Stop condition: compiled owned-fork tests cover resume/fork host mismatch and stable-endpoint stub-to-real convergence.

### Queue implementation campaign 3 — request exposure invariants

- send a complete manifest on the first generated Responses Lite request unless inheritance is directly validated;
- compare logical and wire digests;
- direct-expose or reject every deferred runtime without an executable loader.

### Queue implementation campaign 4 — authority-aware fallback

- compare credential, account, scope, approval, actor, visibility, logical identity, audit, and recovery;
- allow equivalent routes;
- require named approval for changed authority;
- fail closed for ambiguous or weakened mutation paths.

## Human gates retained

Human approval remains required for:

- any external upstream interaction;
- paid services, live accounts, production resources, or consequential external mutations;
- changing owned defaults after experimental validation;
- publishing a defect claim beyond the widest supported evidence scope.

## Conditional fieldwork

Run ChatGPT disconnect/reconnect and application-restart continuation only when the host exposes those actions or the incident recurs. Use benign reads before mutation and unique operation identities with read-after-write reconciliation.

## Final stop rule

New research requires one of:

- a focused implementation test that fails;
- a new typed receipt state;
- a private host control becoming available;
- an incident recurrence with a first-failing receipt.
