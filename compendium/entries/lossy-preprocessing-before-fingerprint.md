# Lossy preprocessing before a fingerprint

## Metadata

```json
{
  "schema": 1,
  "id": "lossy-preprocessing-before-fingerprint",
  "kind": "anti-pattern",
  "maturity": "supported",
  "facets": {
    "domains": ["storage", "caching", "integrity"],
    "concerns": ["identity", "data-integrity", "compatibility"],
    "mechanisms": ["checksum", "normalization", "serialization"],
    "triggers": ["representation-conversion", "normalization"]
  },
  "aliases": ["normalize-before-hash-without-contract", "hash-lossy-view"],
  "relations": [
    {"type": "violates", "target": "fingerprint-consumes-authoritative-representation"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/tantivy#3"
  ]
}
```

## In simple words

The implementation transforms data into a convenient representation before hashing or signing it, but the transformation is not injective with respect to the identity the fingerprint is supposed to protect.

## Typical temptation

- iterate decoded lines and concatenate them;
- normalize paths or whitespace before a byte-identity checksum;
- stringify structured values through a non-canonical serializer;
- discard separators/metadata that seem irrelevant to the local consumer.

## Better move

Name the equality contract first. Feed the fingerprint exactly the bytes/canonical structure that represent that equality. Add a collision-style regression where two distinct authoritative inputs become identical only after the suspect preprocessing.

## Limits

Canonical fingerprints intentionally preprocess input. The anti-pattern is **lossy preprocessing without an explicit equivalence contract**, not preprocessing itself.
