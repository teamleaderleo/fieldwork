# Semantic identity

## Metadata

```json
{
  "schema": 1,
  "id": "semantic-identity",
  "kind": "concept",
  "maturity": "mature",
  "facets": {
    "domains": ["filesystems", "auth", "parsing"],
    "concerns": ["identity", "authority", "compatibility"],
    "mechanisms": ["normalization", "validation", "caching"],
    "triggers": ["representation-conversion", "replacement"]
  },
  "aliases": ["logical-object-identity"],
  "relations": [
    {"type": "clarifies", "target": "normalization-preserves-semantic-identity"},
    {"type": "clarifies", "target": "validated-identity-must-match-used-identity"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#406",
    "teamleaderleo/fieldwork#471",
    "teamleaderleo/linux-fieldwork#28"
  ]
}
```

## In simple words

Semantic identity is the property that makes two representations refer to the same object for the decision being made.

The relevant identity depends on the domain:

- a filesystem pathname may resolve to one inode/object under a particular namespace state;
- an account ID is usable only under the credential/authority context that validates it;
- two archive member spellings may or may not be equivalent under the archive/filter contract;
- two cache keys may be distinct even when a convenience path normalizer collapses them.

## Useful questions

- Which differences are syntax and which differences name another object?
- Which authority context participates in identity?
- Can the representation be rebound between check and use?
- Does normalization erase distinctions the policy still cares about?
- Is the durable/cached token sufficient to recover the same logical object later?

## Why it belongs in the compendium

Many bug species use the word “identity” while meaning different things. A concept entry lets views connect the shared question without pretending path identity, credential authority, attempt identity, and object lifetime are interchangeable mechanisms.
