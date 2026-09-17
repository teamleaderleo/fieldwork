# Terminal authority leak

## Metadata

```json
{
  "schema": 1,
  "id": "terminal-authority-leak",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "streaming", "controllers"],
    "concerns": ["lifecycle", "state-consistency", "resource-ownership"],
    "mechanisms": ["terminal-state", "producer-lifecycle"],
    "triggers": ["cancellation", "late-result", "replacement"]
  },
  "aliases": ["late-producer-after-terminal-state"],
  "relations": [
    {"type": "violates", "target": "terminal-state-revokes-producer-authority"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#714",
    "teamleaderleo/fieldwork#127"
  ]
}
```

## In simple words

The public operation is already terminal, but work that belonged to the old operation still has authority to mutate state, consume inputs, reconnect, append output, or schedule successors.

```text
operation terminal
      ↓
old producer still live
      ↓
late mutation / read / reconnect / callback
```

## Typical signatures

- a returned body changes after the Promise that produced it has resolved;
- a stream or iterator continues reading after a sibling failure makes the result undeliverable;
- a request timeout returns to the caller but reconnect/replay traffic continues;
- late callbacks decrement counters or schedule more reads after abort;
- stale generation finalizers clear or mutate newer state.

## Hunting questions

- Where is terminal state selected?
- Does terminal selection happen before cleanup and outward resolve/reject?
- Which async callbacks can already be in flight at that point?
- Do those callbacks check terminal/generation state before mutating anything?
- Which resources can be actively cancelled, returned, or retired?
- Is producer cleanup best-effort without giving late callbacks authority again?

## Repair shape

Use one shared terminal owner. Select terminal state first, then retire owned producers. Every late continuation checks the terminal/generation token before publishing or scheduling more work.

## Regression shape

Force one producer to become terminal while another producer has an already-pending continuation. Release the pending continuation afterward and assert that it cannot mutate result state, issue another read/request, or replace the selected outcome.

## Limits and counterexamples

A background operation may intentionally outlive the caller-facing request. In that case it needs a distinct durable owner and result identity; it is not an authority leak merely because the original caller stopped waiting.
