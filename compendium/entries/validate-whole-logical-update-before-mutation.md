# Validate the whole logical update before mutation

## Metadata

```json
{
  "schema": 1,
  "id": "validate-whole-logical-update-before-mutation",
  "kind": "invariant",
  "maturity": "supported",
  "facets": {
    "domains": ["controllers", "protocols", "configuration"],
    "concerns": ["atomicity", "authority", "state-consistency"],
    "mechanisms": ["validation", "authorization", "transaction"],
    "triggers": ["multi-item-request", "partial-failure"]
  },
  "aliases": ["whole-message-before-mutation", "validate-authorize-build-then-publish"],
  "relations": [
    {"type": "related-to", "target": "publication"},
    {"type": "related-to", "target": "commit-point"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657",
    "teamleaderleo/systemd#24",
    "teamleaderleo/systemd#29",
    "teamleaderleo/systemd#31"
  ]
}
```

## In simple words

When one request/message claims to perform one logical update, validation and authorization should cover the complete update before any element mutates authoritative state.

```text
decode whole request
→ validate every element
→ authorize every element
→ resolve defaults/references
→ build owned candidate state
→ publish once
```

A loop over request elements is not automatically the transaction boundary.

## Useful review questions

- Does the public request promise all-or-nothing behavior?
- Can an early element mutate state before a later element fails validation?
- Are defaults/references resolved before publication?
- Does authorization happen for each element before any side effect?
- Can a malformed or unauthorized final item leave a believable partial update?

## Regression shape

Use a request whose early elements are valid and whose final element is malformed or unauthorized. After rejection, authoritative state must match the pre-request state exactly.

## Limits

Streaming protocols and explicitly incremental APIs may intentionally commit item-by-item. In those contracts, forcing whole-message atomicity would be wrong. The invariant follows the logical update boundary promised by the interface.
