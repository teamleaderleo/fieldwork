# Duplicate CRDT writer identity makes arrival order authoritative

Finding ID: `F121-crdt-duplicate-writer-identity`  
State: `target-executed / application-ownership-ready`  
Owning issue: #121  
Fieldwork carrier: PR #263  
Automerge: `@automerge/automerge@3.3.2`, source `b4a1bbe9fc17d26c4d3f1819f9ee3b318de3a516`  
Yjs: `yjs@13.6.31`, source `271330889b13eae102873bb417d6747a0ddd8b4a`  
Execution: `30582556167` on Node 22 and Node 24  
Upstream contact authorized: `false`

## In simple words

Two independent offline writers must not reuse one CRDT writer identity.

When the corpus intentionally reused an Automerge actor ID, the first writer was accepted and the second produced a duplicate-sequence error. When it reused a Yjs client ID, the first delivered writer was kept and the other writer's independent value disappeared without an exception.

In both engines, delivery order became the recovery decision.

## Exact Automerge result

Two independent documents used actor ID:

`00000000000000000000000000000001`

Each produced its first change at sequence 1.

```text
left then right:
  retained value: { left: true }
  second change: duplicate seq 1 error

right then left:
  retained value: { right: true }
  second change: duplicate seq 1 error
```

Automerge detects the collision but only after the first writer has established history. Recovery still needs application knowledge to decide whether the first writer was authoritative, whether both must be reconstructed under fresh identities, or whether the document must be quarantined.

## Exact Yjs result

Two independent documents used client ID `424242` and each created its first map item.

```text
left then right: { left: true }
right then left: { right: true }
```

No error was thrown. The second writer's item occupied an already-used client-clock identity and did not become a second independent operation.

## Governing invariant

> A writer identity belongs to one sequential operation history, not to an account, device class, provider, restored backup label, or reusable installation name.

Applications must retain:

- a fresh writer identity for every independent history;
- durable binding between writer identity and accepted local history;
- backup and clone rules that prevent two resumed copies from continuing under one identity;
- collision detection or reconciliation receipts at import and recovery boundaries;
- application-level entity and provider IDs separate from CRDT writer IDs.

## Recovery rule

When duplicate writer identity is suspected:

1. stop accepting more updates into the authoritative document;
2. preserve every source history and arrival order;
3. reconstruct independent writers with fresh identities where the engine permits it;
4. merge or replay through application-owned identity and conflict policy;
5. record which operations were retained, rejected, or recreated;
6. never resolve the incident by silently choosing the first network arrival.

## Main criticism

Both libraries document writer/client identity as an internal operation namespace. Deliberately overriding those identities is already outside normal use, and Automerge's clone API creates fresh actors by default.

The finding therefore targets application backup, restore, cloning, and device-identity design. It does not establish a library defect.

## Edge cases still open

- incremental restore from a stale snapshot;
- copied browser storage or virtual-machine images;
- server-assigned client IDs;
- sync providers that reconnect after identity collision;
- detecting Yjs collisions before lost operations are accepted;
- migration between CRDT engines;
- long-lived actor/client identifier exhaustion or reuse.

## Decision

**ACCEPT writer identity as a single-history authority boundary. Require fresh identities for independent histories and explicit recovery for collisions.**

No public upstream interaction occurred.
