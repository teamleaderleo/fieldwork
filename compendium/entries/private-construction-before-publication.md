# Construct privately before public publication

## Metadata

```json
{
  "schema": 1,
  "id": "private-construction-before-publication",
  "kind": "repair-pattern",
  "maturity": "mature",
  "facets": {
    "domains": ["filesystems", "installation", "storage"],
    "concerns": ["atomicity", "recovery", "publication"],
    "mechanisms": ["private-staging", "publication", "rollback"],
    "triggers": ["partial-failure", "retry"]
  },
  "aliases": ["stage-then-publish", "private-setup-before-publication"],
  "relations": [
    {"type": "related-to", "target": "publication"},
    {"type": "related-to", "target": "ownership-before-publication"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#657"
  ]
}
```

## In simple words

Build a new generation in a private location that readers do not treat as authoritative. Publish only after the generation is complete enough to satisfy the public contract.

```text
private setup
→ validate / finish required work
→ publish public name/reference
```

Failure before publication owns cleanup or isolation of the private generation. Failure after publication has a different recovery contract because other actors may already rely on it.

## Use it when

- fresh installs/builds/caches have several fallible setup steps;
- a public name or pointer would make an incomplete generation look usable;
- retry must distinguish failed private setup from an existing valid published generation.

## Important distinction

Do not let cleanup authority for a failed **fresh unpublished** generation delete or roll back a previously published generation. Publication changes both visibility and rollback authority.

## Limits

Private staging is not enough when readers can discover the staging path anyway, or when the public contract requires streaming incremental visibility. The publication boundary must match what consumers actually observe.
