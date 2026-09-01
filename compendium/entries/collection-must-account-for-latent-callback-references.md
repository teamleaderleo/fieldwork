# Collection must account for latent callback-facing references

## Metadata

```json
{
  "schema": 1,
  "id": "collection-must-account-for-latent-callback-references",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["controllers", "async-runtime"],
    "concerns": ["lifecycle", "identity", "authority"],
    "mechanisms": ["garbage-collection", "callback", "reclamation"],
    "triggers": ["supersession", "late-result", "replacement"]
  },
  "aliases": ["latent-references-block-gc", "future-callbacks-count-as-live"],
  "relations": [
    {"type": "related-to", "target": "terminal-state-revokes-producer-authority"},
    {"type": "related-to", "target": "generation"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/systemd#28"
  ]
}
```

## In simple words

A record is not safely reclaimable merely because no current authoritative pointer references it. Any retained object capable of delivering a future callback can still carry old identity/authority back into the system.

```text
current owner moved on
→ old link/object still retained somewhere
→ authority record garbage-collected
→ old callback arrives
→ callback refers to state whose owner record vanished/recycled
```

## Useful review questions

- Which objects can still produce callbacks, completions, retries, or finalizers?
- Are superseded links still stored even if they are no longer authoritative?
- Does the GC predicate inspect every callback-capable reference, not only current IDs?
- Can a late callback recreate or accidentally match a reclaimed generation?
- Can the retained object be cancelled/retired before collection instead?

## Limits

A callback-capable object that has been synchronously cancelled with a contract proving no later delivery need not keep the authority record live. The key is future reachability into the state machine, not memory reachability by itself.
