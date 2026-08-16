# Unknown external outcome requires reconciliation before retry

## Metadata

```json
{
  "schema": 1,
  "id": "unknown-outcome-requires-reconciliation-before-retry",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["distributed-systems", "agent-runtime", "remote-api"],
    "concerns": ["durability", "idempotency", "recovery"],
    "mechanisms": ["retry", "acknowledgement", "reconciliation"],
    "triggers": ["timeout", "interruption", "acknowledgement-loss"]
  },
  "aliases": ["reconcile-before-retrying-ambiguous-effects"],
  "relations": [],
  "cases": [
    "teamleaderleo/fieldwork#83",
    "teamleaderleo/fieldwork#134",
    "teamleaderleo/fieldwork#384"
  ]
}
```

## In simple words

After a mutation is dispatched, losing the response does not prove that the mutation failed. When the external effect may have happened, retry authority depends on stronger evidence: an idempotency contract, a stable operation identity, or a reconciliation read.

```text
mutation dispatched
      ↓
caller loses result
      ↓
Absent?  Committed?  Still running?
      ↓
UNKNOWN
      ↓
reconcile / use idempotency contract
      ↓
retry only when safe
```

## Useful review questions

- Was the request dispatched before the timeout or interruption?
- What exact evidence distinguishes pre-dispatch failure from acknowledgement loss?
- Is there a stable operation or idempotency key?
- Can current external state be read back and matched to the attempted mutation?
- Does local cancellation prove anything about remote settlement?
- Can a retry duplicate an already-committed effect?

## Limits

Pure reads and operations with a documented idempotent replay contract may be safe to retry without a reconciliation round trip. The invariant matters most when duplicate external effects are consequential and the transport cannot prove absence.
