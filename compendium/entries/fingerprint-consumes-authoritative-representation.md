# Fingerprints consume the authoritative representation

## Metadata

```json
{
  "schema": 1,
  "id": "fingerprint-consumes-authoritative-representation",
  "kind": "invariant",
  "maturity": "mature",
  "facets": {
    "domains": ["storage", "caching", "integrity"],
    "concerns": ["identity", "data-integrity", "compatibility"],
    "mechanisms": ["checksum", "fingerprint", "serialization"],
    "triggers": ["representation-conversion", "normalization"]
  },
  "aliases": ["hash-what-equality-means", "checksum-exact-representation"],
  "relations": [
    {"type": "related-to", "target": "equivalence-matches-observation-surface"},
    {"type": "related-to", "target": "normalization-preserves-semantic-identity"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/tantivy#3"
  ]
}
```

## In simple words

A checksum, fingerprint, signature, or cache identity must consume the representation whose equality it claims to certify.

If the contract is byte identity, line decoding, newline removal, path normalization, or another preprocessing step can make different objects feed the same fingerprint input.

```text
file A bytes: "ab\nc"
file B bytes: "a\nbc"

lossy line join:
A → "abc"
B → "abc"

raw-byte identity was lost before hashing
```

## Useful review questions

- What exact equality does the fingerprint claim: bytes, decoded text, normalized structure, logical records?
- Does preprocessing erase boundaries or metadata relevant to that equality?
- Could two distinct authoritative representations feed the same pre-hash input?
- Is normalization itself part of the public identity contract?

## Limits

Canonicalized fingerprints are legitimate when the contract explicitly defines canonical equivalence. The invariant is to hash/sign the *authoritative equality representation*, not necessarily raw bytes in every system.
