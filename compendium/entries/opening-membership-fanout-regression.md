# Opening-membership fanout regression

## Metadata

```json
{
  "schema": 1,
  "id": "opening-membership-fanout-regression",
  "kind": "executable-graduation",
  "maturity": "mature",
  "facets": {
    "domains": ["testing", "sdk", "async-runtime"],
    "concerns": ["completeness", "concurrency", "lifecycle"],
    "mechanisms": ["regression-testing", "collection-snapshot", "fanout"],
    "triggers": ["mutation-during-iteration", "synchronous-throw"]
  },
  "aliases": ["opentelemetry-fanout-l5"],
  "relations": [
    {"type": "related-to", "target": "fanout-iterates-live-membership"},
    {"type": "related-to", "target": "snapshot-opening-membership"},
    {"type": "graduated-to", "target": "success-implies-complete-selected-work"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#194",
    "teamleaderleo/opentelemetry-js#6"
  ]
}
```

## In simple words

The “attempt every child present when the lifecycle operation begins” lesson reached executable target-native enforcement in the retained OpenTelemetry JS candidate.

The implementation/test contract is no longer only prose:

```text
snapshot opening membership
→ invoke every opening child even if an earlier child removes a later one
→ synchronous child throws become rejected work rather than aborting invocation fanout
→ preserve eager Promise.all concurrency
→ mutations remain visible to future lifecycle operations
```

## Evidence fence

Fieldwork #194 records the exact accepted owned-fork implementation head `db7a0b3a2179f43bf1e0145c8352ff0367bdce79`, pinned base, target workflows, and independent complete-diff review.

The exact head passed unit, lint, E2E, bundler, W3C integration, peer-dependency, CodeQL, and Zizmor gates. The case remains internal/owned-fork evidence; no public upstream authority follows from this record.

## Why this is an L5-style graduation

The compendium can now retrieve not only:

```text
bug species: live membership fanout
repair: snapshot opening membership
```

but also a concrete executable example demonstrating the invariant in a real target and preserving negative controls around synchronous throw, concurrency, and future membership mutation.

## Limit

This does not make `snapshot opening membership` a universal collection rule. The executable contract belongs to APIs whose lifecycle operation promises attempt-all behavior over opening membership.
