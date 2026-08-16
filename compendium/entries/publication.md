# Publication

## Metadata

```json
{
  "schema": 1,
  "id": "publication",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["storage", "filesystems", "distributed-systems"],
    "concerns": ["state-consistency", "visibility", "durability"],
    "mechanisms": ["publication", "state-transition"],
    "triggers": ["partial-failure", "concurrency"]
  },
  "aliases": ["make-visible", "make-authoritative"],
  "relations": [
    {"type": "clarifies", "target": "ownership-before-publication"},
    {"type": "clarifies", "target": "publication-before-ownership"}
  ],
  "cases": [
    "teamleaderleo/linux-fieldwork#609"
  ]
}
```

## In simple words

Publication is the transition that makes a prepared object or state visible enough that another component may rely on it, reference it, discover it, or treat it as authoritative.

Publication is domain-specific:

- writing a pointer into a parent metadata table;
- atomically renaming a completed file to its final name;
- exposing a generation as current;
- acknowledging a result so another actor stops replaying work;
- installing an index/cache pointer consumed by readers.

Publication does **not** automatically imply durability, integrity, or ownership. Those relationships must come from the governing contract.

## Useful questions

- What exact operation changes visibility?
- Who can act differently once publication occurs?
- Which prerequisites must already be true?
- Which cleanup/reuse actions become legal afterward?
- Can publication be observed before the state it depends on is durable or owned?
