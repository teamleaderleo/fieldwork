# Ambiguous external outcome

## Metadata

```json
{
  "schema": 1,
  "id": "ambiguous-external-outcome",
  "kind": "bug-species",
  "maturity": "mature",
  "facets": {
    "domains": ["distributed-systems", "agent-runtime", "remote-api"],
    "concerns": ["idempotency", "durability", "recovery"],
    "mechanisms": ["retry", "acknowledgement", "reconciliation"],
    "triggers": ["timeout", "interruption", "acknowledgement-loss"]
  },
  "aliases": ["unknown-remote-outcome", "commit-then-ack-loss"],
  "relations": [
    {"type": "violates", "target": "unknown-outcome-requires-reconciliation-before-retry"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#83",
    "teamleaderleo/fieldwork#134",
    "teamleaderleo/fieldwork#384"
  ]
}
```

## In simple words

The caller stops receiving evidence after an external operation may already have taken effect. Local code wants a binary answer, but the truthful state is neither success nor failure: the outcome is unknown.

```text
send mutation
    ↓
remote side may act
    ↓
response / acknowledgement lost
    ↓
local timeout or interruption
    ↓
???
```

The dangerous follow-up is to translate `???` into `failed` and retry automatically.

## Typical signatures

- a timeout occurs after request dispatch;
- cancellation is requested locally but remote cancellation is not confirmed;
- a write can commit before the acknowledgement path fails;
- caller/session interruption loses the tool result while the remote service continues;
- one layer reports failure while a later reconciliation read finds the effect present;
- retry can duplicate a mutation.

## Hunting questions

- Can failure occur after dispatch but before acknowledgement?
- Does the remote operation have a stable identity or idempotency key?
- Is cancellation request distinct from cancellation delivery and remote settlement?
- Which result states distinguish `Absent`, `Persisted`, and `Ambiguous`?
- Can external state be queried before retry?
- Which mutations are intrinsically safe to replay?

## Repair shape

Represent uncertainty rather than erasing it:

```text
pre-dispatch failure → known absent
acknowledged result  → known terminal evidence
lost post-dispatch result → ambiguous
```

Then require stable identity, a documented idempotency contract, or reconciliation before retrying consequential mutations.

## Regression shape

Inject at least three windows:

```text
fail before dispatch
commit then lose acknowledgement
normal commit + acknowledgement
```

The test should prove that the middle case is not classified as ordinary failure and does not gain blind retry authority.

## Limits and counterexamples

For a pure read or an operation with strong server-side idempotency, ambiguity may be operationally cheap. The state is still epistemically ambiguous; the difference is that replay is known safe.
