# Premature equivalence collapse

## Metadata

```json
{
  "schema": 1,
  "id": "premature-equivalence-collapse",
  "kind": "anti-pattern",
  "maturity": "supported",
  "facets": {
    "domains": ["api", "parsing", "caching"],
    "concerns": ["identity", "compatibility", "truthfulness"],
    "mechanisms": ["equivalence", "normalization", "optimization"],
    "triggers": ["representation-conversion", "optimization"]
  },
  "aliases": ["normalize-because-semantically-same", "abstract-equivalence-before-observer-audit"],
  "relations": [
    {"type": "violates", "target": "equivalence-matches-observation-surface"},
    {"type": "related-to", "target": "normalization-erases-semantic-distinction"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/react#2"
  ]
}
```

## In simple words

A repair or optimization decides that two representations are “the same” using one convenient semantic model before enumerating the public observers that can still distinguish them.

```text
choose abstract equivalence
→ normalize/suppress difference
→ later observer sees changed literal representation
```

## Typical temptation

- token sets look equivalent, so reorder/deduplicate literal text;
- decoded values match, so exact source bytes are discarded;
- normalized paths compare equal, so original spelling no longer matters;
- two status shapes mean the same thing to one consumer, so the distinction is removed globally.

## Better move

List the protected observation surfaces first. Add at least one reversing control that is sensitive to representation. Only collapse the states when every contract-relevant observer agrees on the equivalence or the API explicitly authorizes normalization.

## Limits

This anti-pattern does not argue against canonicalization. It argues against choosing canonicalization semantics from an abstraction that is weaker than the public observation contract.
