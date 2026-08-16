# Retryability

## Metadata

```json
{
  "schema": 1,
  "id": "retryability",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["distributed-systems", "storage", "controllers"],
    "concerns": ["recovery", "idempotency", "truthfulness"],
    "mechanisms": ["retry", "reconciliation", "ownership-transfer"],
    "triggers": ["partial-failure", "timeout", "interruption"]
  },
  "aliases": ["safe-retry-authority"],
  "relations": [
    {"type": "clarifies", "target": "unknown-outcome-requires-reconciliation-before-retry"},
    {"type": "related-to", "target": "remote-effect-certainty"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#83",
    "teamleaderleo/linux-fieldwork#645"
  ]
}
```

## In simple words

Retryability is not merely "the last attempt returned an error." It is the property that another attempt can be made without duplicating a completed effect, destroying surviving state, or violating the operation's ownership/identity contract.

Different domains establish retryability differently:

- a remote mutation may need a stable idempotency key or reconciliation proof;
- dirty metadata may remain retryable only while the original dirty copy is retained;
- a controller may retry only within the same durable attempt identity or after proving the prior attempt absent;
- a cleanup action may be retryable only while an owner and exact resource identity remain available.

## Useful questions

- What evidence says the prior effect is absent, incomplete, or safe to replay?
- Does retry preserve the same logical operation identity?
- Is the operation intrinsically idempotent?
- Which state must survive the failed attempt for retry to remain possible?
- Can a retry race a late completion from the first attempt?

## Common mistake

```text
error returned
→ assume nothing happened
→ retry
```

Errors describe the observer's result path. Retry authority depends on the underlying effect and surviving ownership state.
