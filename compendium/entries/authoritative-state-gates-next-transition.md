# Authoritative state gates the next transition

## Metadata

```json
{
  "schema": 1,
  "id": "authoritative-state-gates-next-transition",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["lifecycle", "testing", "controllers"],
    "concerns": ["state-consistency", "ordering", "truthfulness"],
    "mechanisms": ["observation", "state-transition"],
    "triggers": ["asynchrony", "replacement", "reuse"]
  },
  "aliases": ["observe-authoritative-completion-before-reuse"],
  "relations": [],
  "cases": [
    "teamleaderleo/linux-fieldwork#423",
    "teamleaderleo/fieldwork#528"
  ]
}
```

## In simple words

When the next action is legal only after a lifecycle transition completes, gate that action on the state or event owned by the component that performs the transition. A correlated symptom is weaker evidence.

```text
request shutdown
      ↓
SSH disappears        ← correlated symptom
      ↓
VMM shutdown event    ← authoritative completion
      ↓
reuse VM/disk/state
```

## Useful review questions

- Which component owns the transition?
- What exact event or state does it publish when the transition is complete?
- Is the test/controller waiting on that event, or on a side effect that usually happens nearby?
- Can the proxy symptom happen before cleanup or durable state transition finishes?
- Can the authoritative event be delayed while the proxy already changed?

## Limits

A proxy can be a valid contract when the system explicitly defines it as the authoritative boundary. The problem is not indirect observation by itself; it is using evidence whose ordering relative to the required transition is weaker than the caller assumes.
