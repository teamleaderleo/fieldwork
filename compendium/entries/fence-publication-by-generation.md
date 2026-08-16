# Fence publication by generation

## Metadata

```json
{
  "schema": 1,
  "id": "fence-publication-by-generation",
  "kind": "repair-pattern",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "storage", "agent-runtime"],
    "concerns": ["state-consistency", "authority", "ordering"],
    "mechanisms": ["generation", "publication", "ticket"],
    "triggers": ["overlap", "late-result", "replacement"]
  },
  "aliases": ["accepted-current-ticket", "generation-fence"],
  "relations": [
    {"type": "related-to", "target": "stale-generation-publication"},
    {"type": "related-to", "target": "only-current-generation-may-publish"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#180",
    "teamleaderleo/fieldwork#84"
  ]
}
```

## In simple words

Give replaceable work a monotonic generation/ticket and require a current-generation check at the publication boundary.

```text
start generation A (ticket 10)
start generation B (ticket 11)
accept B as current
B publishes
A finishes late
A ticket 10 != current 11
→ retain/discard A locally as appropriate
→ reject A global publication
```

This lets older in-flight work finish when necessary without regaining authority over future work.

## Use it when

- overlapping refresh/rebuild/relist work is useful or unavoidable;
- completion order can differ from start/supersession order;
- future requests should use exactly one accepted current generation;
- old in-flight operations may still need captured old authority.

## Alternative repair

When overlap provides no value and old workers must fully quiesce before replacement, a simpler state machine can settle all predecessors before publishing/starting the successor. Do not add generation machinery merely because it is fashionable.

## Regression shape

Force reverse completion order and assert stale publication is rejected. Add a failed-replacement control and an in-flight old-operation control to prove the fence is neither too weak nor too broad.
