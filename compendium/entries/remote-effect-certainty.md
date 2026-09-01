# Remote-effect certainty

## Metadata

```json
{
  "schema": 1,
  "id": "remote-effect-certainty",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["distributed-systems", "remote-api", "agent-runtime"],
    "concerns": ["idempotency", "recovery", "truthfulness"],
    "mechanisms": ["acknowledgement", "reconciliation", "retry"],
    "triggers": ["timeout", "interruption", "cancellation"]
  },
  "aliases": ["external-outcome-certainty", "mutation-settlement-certainty"],
  "relations": [
    {"type": "clarifies", "target": "ambiguous-external-outcome"},
    {"type": "clarifies", "target": "unknown-outcome-requires-reconciliation-before-retry"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#83",
    "teamleaderleo/fieldwork#134",
    "teamleaderleo/fieldwork#384"
  ]
}
```

## In simple words

Remote-effect certainty describes what the local system actually knows about a consequential external operation after dispatch.

A useful minimum vocabulary is:

```text
Absent     — strong evidence the effect did not occur
Persisted  — strong evidence the effect occurred
Ambiguous  — it may have occurred; local evidence cannot decide
```

Cancellation request, timeout, transport error, caller interruption, and lost acknowledgement are observations about the communication/control path. None automatically proves the remote effect is absent.

## Why it matters

Retry authority depends on this distinction. Treating `Ambiguous` as `Absent` can duplicate mutations; treating it as `Persisted` can skip required work.

## Useful questions

- Was dispatch attempted or confirmed?
- Can the service expose the operation by stable identity?
- Is replay idempotent?
- Can a read/reconciliation distinguish absence from commit?
- Does cancellation have a confirmed delivered/settled state?
