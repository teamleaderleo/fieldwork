# One owner controls retry budget and classification

## Metadata

```json
{
  "schema": 1,
  "id": "one-owner-controls-retry-budget",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["networking", "controllers", "caching"],
    "concerns": ["recovery", "lifecycle", "resource-ownership"],
    "mechanisms": ["retry", "backoff", "classification"],
    "triggers": ["transient-failure", "nested-retry"]
  },
  "aliases": ["single-retry-authority", "do-not-stack-retry-loops"],
  "relations": [
    {"type": "related-to", "target": "retryability"},
    {"type": "related-to", "target": "operation-owner"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

A logical operation should have one bounded owner for retry classification, attempt count, backoff, and terminal failure. A failure class that escapes the existing retry loop should usually be routed into that owner rather than wrapped in a second independent loop.

```text
classify failure
→ existing retry owner
→ consume one shared attempt budget
→ backoff/policy
→ terminal result
```

## Useful review questions

- Which layer already owns retry count/backoff?
- Does a new wrapper multiply attempts with an inner loop?
- Can permanent failures become accidentally retryable?
- Are timers/cancellation owned by the same operation generation?
- Does one failure class bypass classification merely because it originates at a different layer?

## Limits

Nested retries can be correct when they represent genuinely independent operations with separate budgets, such as a short transport connection retry inside a much longer job-level retry. The invariant applies to one logical effect whose attempt budget would otherwise be multiplied or fragmented.
