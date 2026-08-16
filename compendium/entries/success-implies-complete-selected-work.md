# Success implies complete selected work

## Metadata

```json
{
  "schema": 1,
  "id": "success-implies-complete-selected-work",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["developer-tools", "storage", "lifecycle"],
    "concerns": ["completeness", "truthfulness", "recovery"],
    "mechanisms": ["aggregation", "status-publication"],
    "triggers": ["partial-failure", "skipped-work"]
  },
  "aliases": ["success-means-complete-coverage"],
  "relations": [],
  "cases": [
    "teamleaderleo/fieldwork#626",
    "teamleaderleo/linux-fieldwork#611"
  ]
}
```

## In simple words

A success result is meaningful only if it covers the work the operation claims to have selected, or if partial coverage is explicitly represented as part of the contract.

```text
selected set
    ↓
process every required member
    ↓
success
```

A system may legitimately support partial success. In that case the result must make the missing or failed members machine-visible rather than silently shrinking the selected set after errors occur.

## Useful review questions

- What did the caller ask the operation to cover?
- Which items were actually attempted?
- Which items were skipped because their prerequisites could not be read or validated?
- Does exit status or the durable marker distinguish complete from partial work?
- Can an empty result mean both “there was nothing to do” and “everything was skipped”?
- Does a later consumer treat the success marker as permission to trust or reuse state?

## Limits

Best-effort discovery commands can intentionally skip inaccessible objects. The invariant applies only when their success contract implies complete selected coverage or when downstream consumers rely on that implication.
