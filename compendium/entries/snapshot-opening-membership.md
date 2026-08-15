# Snapshot opening membership before fanout

## Metadata

```json
{
  "schema": 1,
  "id": "snapshot-opening-membership",
  "kind": "repair-pattern",
  "maturity": "supported",
  "facets": {
    "domains": ["async-runtime", "sdk", "controllers"],
    "concerns": ["completeness", "lifecycle", "concurrency"],
    "mechanisms": ["fanout", "collection-snapshot"],
    "triggers": ["mutation-during-iteration", "reentry"]
  },
  "aliases": ["stable-opening-fanout-set"],
  "relations": [
    {"type": "related-to", "target": "fanout-iterates-live-membership"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#194"
  ]
}
```

## In simple words

When an operation promises to attempt every child present at the start, copy the opening membership before invoking any child. Mutations made by callbacks then affect future operations without rewriting the current operation's participant set.

```text
live children
    ↓ snapshot
opening set [A, B, C]
    ↓ fanout
A / B / C all get current operation

callback mutation
    ↓
changes membership for next operation
```

## Use it when

- callbacks can unregister/register children;
- the contract is opening-set completeness;
- fanout must continue after synchronous child failure;
- current concurrency semantics should remain intact.

## What it does not solve

- self-dependency through lifecycle reentry;
- whether to aggregate or fail fast on child errors;
- whether child settlement should be sequential or concurrent;
- stale child objects whose own lifetime ended before invocation.

Those are separate ownership and error-policy questions.

## Regression shape

Have the first child remove a later child while the operation is running. The later child should still receive the current operation but be absent from a second invocation. Add a control where a child throws synchronously and later children still begin.
