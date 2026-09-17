# Ownership

## Metadata

```json
{
  "schema": 1,
  "id": "ownership",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["systems", "storage", "controllers"],
    "concerns": ["resource-ownership", "authority", "lifecycle"],
    "mechanisms": ["ownership-transfer", "cleanup", "allocation"],
    "triggers": ["partial-failure", "replacement"]
  },
  "aliases": ["lifecycle-ownership", "resource-ownership"],
  "relations": [
    {"type": "clarifies", "target": "ownership-before-publication"},
    {"type": "clarifies", "target": "resource-has-one-cleanup-owner"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#609",
    "teamleaderleo/fieldwork#319"
  ]
}
```

## In simple words

Ownership is the rule that decides which actor is currently responsible for a resource or state and which actions that responsibility authorizes: publish, mutate, reuse, clean up, retry, or transfer.

The word is deliberately domain-qualified.

- **Allocator/storage ownership:** the object is excluded from free/reuse state.
- **Cleanup ownership:** one lifecycle actor remains responsible for eventual release.
- **Controller ownership:** an attempt/generation/lease has authority to publish or mutate shared state.
- **Rust value ownership:** the language's move/drop/borrow rules govern memory/resource lifetime; this is related structurally but is not identical to the higher-level protocols above.

## Useful questions

- What state proves ownership?
- What actions does ownership authorize?
- Can ownership move?
- What proves the successor accepted the transfer?
- What happens if transfer fails halfway?
- Can two actors both believe they own the resource, or can neither own it?

## Why the distinction matters

A system can have memory-safe Rust ownership while still having incorrect allocator, lifecycle, or distributed ownership. The compendium should connect the shared reasoning vocabulary without flattening these into one mechanism.
