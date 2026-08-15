# Generation

## Metadata

```json
{
  "schema": 1,
  "id": "generation",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["controllers", "storage", "agent-runtime"],
    "concerns": ["identity", "ordering", "authority"],
    "mechanisms": ["generation", "replacement"],
    "triggers": ["overlap", "replacement"]
  },
  "aliases": ["epoch", "revision-generation", "replacement-generation"],
  "relations": [
    {"type": "clarifies", "target": "only-current-generation-may-publish"},
    {"type": "clarifies", "target": "stale-generation-publication"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#180",
    "teamleaderleo/fieldwork#84"
  ]
}
```

## In simple words

A generation is an identity for one version of replaceable live state or work. It lets the system distinguish "this callback belongs to the current owner" from "this callback is valid work from an older owner that may no longer publish globally."

Examples include:

- worker sets before/after an index-writer replacement;
- MCP catalogue refresh tickets;
- cached read versions;
- approval attempts;
- runner/controller attempt generations.

A generation is useful when chronological completion order and logical replacement order can differ.

## Useful questions

- What event increments or replaces the generation?
- Is generation identity durable when restart matters?
- Which actions require current-generation authority?
- Which old-generation operations may still finish under captured authority?
- Can a generation identifier wrap, be reused, or suffer ABA-like ambiguity?
