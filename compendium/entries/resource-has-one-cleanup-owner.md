# Every live resource has one cleanup owner

## Metadata

```json
{
  "schema": 1,
  "id": "resource-has-one-cleanup-owner",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["process-lifecycle", "async-runtime", "systems"],
    "concerns": ["resource-ownership", "lifecycle", "recovery"],
    "mechanisms": ["cleanup", "ownership-transfer"],
    "triggers": ["backgrounding", "partial-initialization", "cancellation"]
  },
  "aliases": ["exactly-one-cleanup-owner"],
  "relations": [],
  "cases": [
    "teamleaderleo/fieldwork#319",
    "teamleaderleo/fieldwork#171"
  ]
}
```

## In simple words

A resource that remains live after one lifecycle phase must have a component that still owns its eventual cleanup. When responsibility moves, the transfer should be explicit and failure before transfer should leave cleanup with the old owner.

```text
creator owns resource
      ↓ successful transfer
lifecycle owner owns resource
      ↓ terminal observation
cleanup exactly once
```

The dangerous middle is:

```text
creator stops cleaning
+ successor never accepted cleanup ownership
```

## Useful review questions

- Who created the resource?
- Until what event does the creator need it?
- Which component observes the event that makes cleanup legal?
- Where does ownership transfer?
- If transfer fails, who still cleans up?
- Can two owners both clean it, or can both believe the other owns it?
- Is cleanup idempotent when terminal paths race?

## Limits

Shared resources can intentionally have reference-counted or collective lifetime. In that case the invariant becomes “the ownership protocol has one authoritative rule for deciding when cleanup is legal,” rather than requiring one literal object owner.
