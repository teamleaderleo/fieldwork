# Operation owner

## Metadata

```json
{
  "schema": 1,
  "id": "operation-owner",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["systems", "controllers", "async-runtime"],
    "concerns": ["resource-ownership", "lifecycle", "authority"],
    "mechanisms": ["state-transition", "cleanup", "reconciliation"],
    "triggers": ["partial-failure", "replacement"]
  },
  "aliases": ["state-machine-owner", "transition-owner"],
  "relations": [
    {"type": "clarifies", "target": "resource-has-one-cleanup-owner"},
    {"type": "clarifies", "target": "authoritative-state-gates-next-transition"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#319",
    "teamleaderleo/linux-fieldwork#423"
  ]
}
```

## In simple words

The operation owner is the component whose state machine decides whether a specific operation is pending, committed, terminal, retryable, or eligible for cleanup.

It is not necessarily the component that initiated the operation or the one that presents the UI.

## Why it matters

Many cross-layer bugs appear when one layer assumes another layer already owns a fact:

```text
caller thinks worker owns cleanup
worker thinks caller owns cleanup
→ nobody owns cleanup
```

or:

```text
test sees proxy symptom
→ assumes transition complete
→ actual transition owner still running
```

## Useful questions

- Which component can authoritatively say this operation is done?
- Which component owns retry identity?
- Who can make cleanup legal?
- Who publishes the terminal state?
- Can ownership move, and what proves the transfer completed?
