# Equivalence must match the observation surface

## Metadata

```json
{
  "schema": 1,
  "id": "equivalence-matches-observation-surface",
  "kind": "invariant",
  "maturity": "mature",
  "facets": {
    "domains": ["api", "parsing", "caching"],
    "concerns": ["identity", "compatibility", "truthfulness"],
    "mechanisms": ["equivalence", "normalization", "observation"],
    "triggers": ["representation-conversion", "optimization"]
  },
  "aliases": ["observable-equivalence", "do-not-normalize-away-observable-differences"],
  "relations": [
    {"type": "related-to", "target": "normalization-preserves-semantic-identity"},
    {"type": "related-to", "target": "semantic-identity"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/react#2"
  ]
}
```

## In simple words

Two states are equivalent only with respect to the observation surface the contract protects.

A more abstract model can call two representations equivalent while users, selectors, serializers, diagnostics, or downstream tools can still observe the difference.

```text
semantic shortcut says:
A == B

public observer says:
observe(A) != observe(B)

therefore the shortcut is not valid for that contract
```

## Useful review questions

- Which exact observers can inspect the representation?
- Is equality token-based, byte-based, ordered, normalized, or literal?
- Does the proposed optimization suppress a difference visible through another API?
- Which representation-sensitive negative control would make the equivalence claim lose?
- Is the consumer comparing the same notion of equality the producer claims?

## Limits

Not every byte difference is observable or meaningful. The invariant says to derive equivalence from the governing observation contract rather than from either raw bytes by default or an overly abstract semantic model by default.
