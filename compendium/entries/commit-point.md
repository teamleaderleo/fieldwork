# Commit point

## Metadata

```json
{
  "schema": 1,
  "id": "commit-point",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["distributed-systems", "storage", "migration"],
    "concerns": ["recovery", "state-consistency", "authority"],
    "mechanisms": ["commit-point", "acknowledgement", "publication"],
    "triggers": ["partial-failure", "late-cleanup-failure"]
  },
  "aliases": ["point-of-no-ordinary-rollback", "protocol-commit-boundary"],
  "relations": [
    {"type": "related-to", "target": "remote-effect-certainty"},
    {"type": "related-to", "target": "publication"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#606",
    "teamleaderleo/fieldwork#83"
  ]
}
```

## In simple words

A commit point is the event after which the system's legal recovery options change because a new state or effect is now authoritative enough that ordinary rollback to the prior state would lie or create conflicting owners.

```text
before commit:
rollback may restore old state

commit point crossed:
new state/effect authoritative

after commit:
cleanup/repair/compensation may remain
ordinary rollback may be illegal
```

The exact commit point can be an on-disk durability boundary, a remote protocol acknowledgement, a published generation, or another owner-defined event.

## Useful questions

- Which event makes the new state authoritative?
- Does the code remember whether an error happened before or after that event?
- Which recovery actions remain legal after commit?
- Can a late local failure accidentally route through pre-commit rollback?
- Is a lost acknowledgement proof that commit did not happen? Usually not without stronger protocol evidence.

## Limits

Some systems support explicit compensating operations after commit. Compensation is a new operation with its own commit and failure semantics, not erasure of the original commit.
