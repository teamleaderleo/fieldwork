# Publication before ownership

## Metadata

```json
{
  "schema": 1,
  "id": "publication-before-ownership",
  "kind": "bug-species",
  "maturity": "supported",
  "facets": {
    "domains": ["storage", "resource-management", "distributed-systems"],
    "concerns": ["resource-ownership", "state-consistency", "recovery"],
    "mechanisms": ["publication", "allocation", "reachability"],
    "triggers": ["partial-failure", "resource-exhaustion", "restart"]
  },
  "aliases": ["reachable-before-owned"],
  "relations": [
    {"type": "violates", "target": "ownership-before-publication"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#609"
  ]
}
```

## In simple words

An object becomes reachable or authoritative before the state that prevents another actor from treating it as free or unowned has been established.

```text
allocate
→ publish
→ establish ownership later
```

If execution stops in the middle, the live object can look reusable.

## Typical signatures

- corruption appears only after reopen/restart;
- resource exhaustion or fault injection is needed to expose the ordering window;
- the success path looks correct because the deferred ownership update normally runs;
- a live object appears on a free/reusable list after reconstruction;
- the implementation carries an out-parameter, deferred vector, callback, or later fixup representing ownership work that should have been local to publication.

## Hunting questions

- What exact operation makes the object reachable?
- What tells other actors or the allocator that the object is owned?
- Can those two facts be separated by fallible work?
- What survives if execution stops immediately after publication?
- Does restart/reopen rebuild reuse state from ownership metadata?

## Repair shape

A common safe shape is:

```text
prepare
→ own
→ publish
→ retire predecessor
```

When rollback is unavailable, prefer conservative residual state such as an unreachable object remaining owned over a live object becoming reusable.

## Regression shape

Fail in the publication window, reopen/reconcile from durable state, and prove that every still-live object remains excluded from reuse. Pair that failure regression with a successful lifecycle control showing that dead predecessors eventually become reusable.

## Limits and counterexamples

Not every publication requires a separate ownership phase. If the publish primitive atomically establishes reachability and exclusion, splitting it into conceptual steps would make the model worse rather than better.
