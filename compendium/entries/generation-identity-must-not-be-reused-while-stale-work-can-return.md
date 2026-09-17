# Generation identity must not be reused while stale work can return

## Metadata

```json
{
  "schema": 1,
  "id": "generation-identity-must-not-be-reused-while-stale-work-can-return",
  "kind": "invariant",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "async-runtime", "distributed-systems"],
    "concerns": ["identity", "ordering", "authority"],
    "mechanisms": ["generation", "garbage-collection", "reclamation"],
    "triggers": ["replacement", "recreation", "late-result"]
  },
  "aliases": ["generation-aba", "do-not-recycle-epochs-with-stale-work"],
  "relations": [
    {"type": "related-to", "target": "generation"},
    {"type": "related-to", "target": "only-current-generation-may-publish"}
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

If old asynchronous work can finish after a record is deleted and recreated, a generation identifier reused for the new lifetime can make stale work look current.

```text
key K generation 1
→ old callback remains in flight
→ record deleted
→ K recreated
→ per-key counter restarts at 1
→ old callback tagged 1 arrives
→ stale work appears current
```

## Useful review questions

- Can an external key be deleted and recreated?
- Can callbacks from the prior lifetime still arrive?
- Does generation state disappear with the record?
- Can the same generation value be assigned again within the process/durable observation horizon?
- Is a globally monotonic epoch cheaper and clearer than retaining per-key tombstones forever?

## Limits

Generation reuse is safe when the system can prove no observer or stale work from the old lifetime remains, or when the identity includes another non-reused component. The invariant is about collision with surviving authority evidence, not a universal ban on bounded counters.
