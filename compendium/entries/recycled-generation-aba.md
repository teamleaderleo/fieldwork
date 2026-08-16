# Recycled generation creates an ABA collision

## Metadata

```json
{
  "schema": 1,
  "id": "recycled-generation-aba",
  "kind": "bug-species",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "async-runtime", "distributed-systems"],
    "concerns": ["identity", "ordering", "authority"],
    "mechanisms": ["generation", "garbage-collection", "reclamation"],
    "triggers": ["replacement", "recreation", "late-result"]
  },
  "aliases": ["generation-aba-collision", "recreated-key-reuses-old-generation"],
  "relations": [
    {"type": "violates", "target": "generation-identity-must-not-be-reused-while-stale-work-can-return"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/gemini-cli#24",
    "teamleaderleo/systemd#26",
    "teamleaderleo/systemd#27"
  ]
}
```

## In simple words

A record is reclaimed, its local generation counter disappears, the same external identity is recreated, and the counter starts over. A stale callback from the old lifetime can then carry the same apparent generation as the new owner.

```text
old: K / gen 1  ---- stale callback ----┐
                                      │
delete K                              │
recreate K / gen 1                    │
                                      ▼
                              stale looks current
```

## Typical signatures

- per-key generation counters are stored inside garbage-collected records;
- external identities can be reused;
- superseded callbacks, timers, RPC replies, or confirmations can outlive record reclamation;
- equality checks compare only key + local generation;
- tests cover replacement but not delete/recreate plus stale completion.

## Repair shape

Use an identity that cannot collide while stale work remains relevant. A process-global monotonic generation is often the simplest bounded-memory choice. Another valid design can use a durable/non-reused incarnation token.

## Regression shape

Create generation A, leave stale work pending, finalize/reclaim A, recreate the same external key, then release the stale work. The stale completion must be rejected even if the user-visible key is identical.

## Limits

A global counter is a mechanism, not the invariant. Systems with provable quiescence before identity reuse or stronger incarnation IDs do not need it.
