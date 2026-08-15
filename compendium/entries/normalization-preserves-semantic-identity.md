# Normalization preserves semantic identity

## Metadata

```json
{
  "schema": 1,
  "id": "normalization-preserves-semantic-identity",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["filesystems", "parsing", "caching"],
    "concerns": ["identity", "compatibility", "state-consistency"],
    "mechanisms": ["normalization", "canonicalization", "cache-key"],
    "triggers": ["representation-conversion", "edge-case-input"]
  },
  "aliases": ["normalize-only-defined-equivalences"],
  "relations": [],
  "cases": [
    "teamleaderleo/fieldwork#225",
    "teamleaderleo/linux-fieldwork#28"
  ]
}
```

## In simple words

A normalizer may change representation only across equivalences the governing contract actually defines. It must not erase distinctions that later validation, matching, cache identity, or user-visible naming depends on.

```text
representation A == representation B by contract
      → normalization may unify them

representation A != representation B by contract
      → normalization must preserve the distinction
```

## Useful review questions

- What exact equivalence is normalization supposed to implement?
- Is the helper performing prefix removal, character stripping, path canonicalization, case folding, decoding, or something broader?
- Does validation need to see tokens that normalization erases?
- Can two distinct inputs collapse to one cache key or matcher identity?
- Does a later layer need the original literal spelling for references or round-tripping?

## Limits

Some protocols deliberately define broad canonical forms. In those cases byte differences are not semantic differences. The invariant is contract-relative: preserve distinctions that remain meaningful after the specified normalization, not every original byte.
