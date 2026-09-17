# Terminal state revokes producer authority

## Metadata

```json
{
  "schema": 1,
  "id": "terminal-state-revokes-producer-authority",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "streaming", "controllers"],
    "concerns": ["lifecycle", "state-consistency", "resource-ownership"],
    "mechanisms": ["terminal-state", "producer-lifecycle"],
    "triggers": ["cancellation", "late-result", "replacement"]
  },
  "aliases": ["late-producers-cannot-mutate-terminal-state"],
  "relations": [],
  "cases": [
    "teamleaderleo/fieldwork#714",
    "teamleaderleo/fieldwork#127"
  ]
}
```

## In simple words

Once an operation enters its authoritative terminal state, producers owned only by that operation must no longer be able to mutate the published result, schedule more work, or continue acting as if the operation were live.

```text
Running
  ↓
Terminal
  ↓
late producer callback → ignored / retired
```

## Useful review questions

- What single state says the operation is terminal?
- Is that state selected before resolve/reject/publication?
- Which callbacks can still arrive afterward?
- Can a pending read, iterator result, provider result, retry timer, or lazy promise append to terminal state?
- Which owned producers have cancellation/return/retirement primitives?
- Can stale callbacks schedule another generation of work after terminal selection?

## Limits

Some operations intentionally expose a live object whose contents continue evolving after an initial readiness result. In that design the initial result is not the terminal boundary; model the true owner/lifetime instead of applying this invariant too early.
