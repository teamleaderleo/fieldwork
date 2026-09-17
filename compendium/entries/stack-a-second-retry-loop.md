# Stack a second retry loop around the first

## Metadata

```json
{
  "schema": 1,
  "id": "stack-a-second-retry-loop",
  "kind": "anti-pattern",
  "maturity": "supported",
  "facets": {
    "domains": ["networking", "controllers", "caching"],
    "concerns": ["recovery", "lifecycle", "resource-ownership"],
    "mechanisms": ["retry", "backoff", "classification"],
    "triggers": ["transient-failure", "nested-retry"]
  },
  "aliases": ["retry-the-retry-loop", "independent-wrapper-retry"],
  "relations": [
    {"type": "violates", "target": "one-owner-controls-retry-budget"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

One failure class slips past an existing bounded retry mechanism, so the repair wraps the entire operation in another retry loop instead of teaching the existing owner how to classify that failure.

```text
outer retry N
  └── inner retry M

possible attempts = N × M
```

## Why it is dangerous

- attempt budgets multiply silently;
- backoff ownership becomes unclear;
- permanent failures can become retryable;
- cancellation/timers span two owners;
- metrics and logs disagree about what counts as an attempt;
- the same logical effect can be repeated far more often than policy intended.

## Better move

Find the existing retry authority and classify the escaped transient failure there when it belongs to the same logical operation. Preserve one attempt identity, budget, backoff policy, and terminal decision.

## Limits

Independent nested operations can legitimately retry independently. The anti-pattern applies when the wrapper and inner loop both retry the same logical effect or share one intended attempt budget.
