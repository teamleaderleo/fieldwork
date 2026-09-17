# Authoritative state

## Metadata

```json
{
  "schema": 1,
  "id": "authoritative-state",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "lifecycle", "distributed-systems"],
    "concerns": ["state-consistency", "truthfulness"],
    "mechanisms": ["observation", "state-transition"],
    "triggers": ["asynchrony", "replacement"]
  },
  "aliases": ["source-of-truth-state", "owner-issued-state"],
  "relations": [
    {"type": "clarifies", "target": "authoritative-state-gates-next-transition"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#423",
    "teamleaderleo/fieldwork#528"
  ]
}
```

## In simple words

Authoritative state is the state whose owner is entitled to decide whether a transition has happened, a resource is live, an operation is terminal, or a later action is legal.

A symptom can correlate with authoritative state without being authoritative itself.

```text
SSH disappeared          observation
VMM emitted shutdown     authoritative lifecycle event
```

The same distinction appears in controllers, durable records, generation owners, protocol commit points, and reconciliation systems.

## Domain-qualified notes

- **Lifecycle:** the component performing the transition usually owns the terminal event/state.
- **Persistence:** an on-disk record may become authoritative only after its required durability boundary.
- **Distributed systems:** local state may be non-authoritative when the external side can commit independently.
- **Testing:** assertions should prefer authoritative evidence when later reuse/destruction depends on exact completion.

## Common mistake

Treating the easiest observable signal as proof of the strongest state needed by the caller.
