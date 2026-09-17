# Callback order used as authority

## Metadata

```json
{
  "schema": 1,
  "id": "callback-order-used-as-authority",
  "kind": "anti-pattern",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "auth", "controllers"],
    "concerns": ["authority", "ordering", "state-consistency"],
    "mechanisms": ["callback", "generation", "commit-point"],
    "triggers": ["overlap", "late-result"]
  },
  "aliases": ["registration-order-means-owner", "call-stack-means-current"],
  "relations": [
    {"type": "violates", "target": "committed-state-outranks-callback-ancestry"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

The implementation treats callback registration order, call-stack ancestry, or start order as proof that one callback owns the current state even though a stronger committed generation/version exists.

## Typical temptation

- "the callback registered most recently must be current";
- "this callback was triggered from the refresh that started first";
- "the active call stack tells us which session owns this event";
- "the last callback to finish should win."

These timing facts can correlate with authority without defining it.

## Better move

Bind callbacks to the committed generation/receipt/epoch they report, then compare that identity with current authoritative state before publishing or notifying.

## Limits

Do not replace an API whose documented semantics really are callback order with a generation protocol. The anti-pattern requires a mismatch between timing ancestry and the stronger owner contract.
