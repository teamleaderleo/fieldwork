# Ownership before publication

## Metadata

```json
{
  "schema": 1,
  "id": "ownership-before-publication",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["storage", "resource-management", "distributed-systems"],
    "concerns": ["resource-ownership", "state-consistency", "recovery"],
    "mechanisms": ["publication", "allocation", "reachability"],
    "triggers": ["partial-failure", "resource-exhaustion", "restart"]
  },
  "aliases": ["owned-before-reachable"],
  "relations": [],
  "cases": [
    "teamleaderleo/linux-fieldwork#609"
  ]
}
```

## In simple words

If publication makes an object live, the state that prevents another owner from reclaiming or reusing that object must already be established when publication occurs.

```text
prepare
→ establish ownership
→ publish
→ retire predecessor
```

The exact representation of ownership varies: reference count, lease, reservation, generation, durable intent, allocator bit, or another exclusion mechanism. The invariant is about the relationship between reachability and reuse authority.

## Useful review questions

- What operation makes this object reachable or externally authoritative?
- What state prevents another actor from treating it as free or unowned?
- Can publication happen first?
- What if execution stops immediately after publication?
- Can restart/reconciliation reconstruct a state in which the live object appears reusable?

## Limits

Some systems establish ownership implicitly through the same atomic operation that publishes the object. In that case there is no separate ordering edge to enforce. Do not invent a two-step protocol where the underlying primitive already provides one indivisible transition.
