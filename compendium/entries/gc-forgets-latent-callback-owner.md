# Garbage collection forgets a latent callback owner

## Metadata

```json
{
  "schema": 1,
  "id": "gc-forgets-latent-callback-owner",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["controllers", "async-runtime"],
    "concerns": ["lifecycle", "identity", "authority"],
    "mechanisms": ["garbage-collection", "callback", "reclamation"],
    "triggers": ["supersession", "late-result", "replacement"]
  },
  "aliases": ["collect-authority-while-callback-can-return", "latent-callback-after-gc"],
  "relations": [
    {"type": "violates", "target": "collection-must-account-for-latent-callback-references"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/systemd#28"
  ]
}
```

## In simple words

The GC predicate looks only at current authoritative fields and misses an older retained object that can still deliver a callback. The authority/generation record is collected while a path back into it remains live.

## Typical signatures

- superseded links remain in a table while current-ID fields move on;
- callback closures retain an old owner or generation;
- collection logic inspects active/pending IDs but not every retained link;
- a late callback after GC causes missing-state lookup, stale authority reuse, or ABA collision;
- tests reclaim records only after all callbacks have already settled.

## Repair shape

Define liveness from future callback capability. Either retire/cancel all callback-capable objects before collecting the record or include every such reference in the GC predicate.

## Regression shape

Supersede an owner, retain one old callback-producing object, remove the newest owner so GC becomes tempting, run collection, then deliver the old callback. The system must still have enough identity/authority state to classify it safely.

## Limits

Do not retain records forever because some object is merely memory-reachable. The relevant question is whether the object can still invoke a state transition or publish a result.
