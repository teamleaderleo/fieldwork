# Reconciliation

## Metadata

```json
{
  "schema": 1,
  "id": "reconciliation",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["distributed-systems", "controllers", "persistence"],
    "concerns": ["recovery", "state-consistency", "idempotency"],
    "mechanisms": ["observation", "retry", "reconciliation"],
    "triggers": ["restart", "timeout", "ambiguous-outcome"]
  },
  "aliases": ["observe-and-repair-state"],
  "relations": [
    {"type": "clarifies", "target": "unknown-outcome-requires-reconciliation-before-retry"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#83",
    "teamleaderleo/fieldwork#384"
  ]
}
```

## In simple words

Reconciliation compares current authoritative observations with intended/durable local state and decides the next safe transition without pretending the interrupted operation either definitely succeeded or definitely failed.

```text
persisted intent / attempt identity
        +
current external observation
        ↓
classify what is known
        ↓
continue / retry / clean up / hold unknown
```

## Why it matters

Rollback is often impossible after external effects. Reconciliation lets the controller recover by observing what now exists instead of reconstructing history from a missing acknowledgement.

## Useful questions

- Which observations are authoritative?
- Which attempt/generation are they about?
- Can the state be `Unknown` rather than forced into success/failure?
- Which transitions are idempotent?
- What evidence makes retry safe?
- Can stale observations accidentally authorize destructive cleanup or reuse?
