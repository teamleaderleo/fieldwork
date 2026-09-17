# Compendium entry schema

## In simple words

Each compendium entry is ordinary Markdown with one machine-readable JSON metadata block near the top. The prose explains the idea; the metadata makes cross-cutting retrieval and relationship checks possible.

This is an experimental schema. Prefer repairing it after real extraction pressure rather than preserving a field merely because version 1 happened to contain it.

## Required shape

````markdown
# Human title

## Metadata

```json
{
  "schema": 1,
  "id": "stable-kebab-case-id",
  "kind": "bug-species",
  "maturity": "candidate",
  "facets": {
    "domains": ["distributed-systems"],
    "concerns": ["durability", "recovery"],
    "mechanisms": ["acknowledgement"],
    "triggers": ["interruption"]
  },
  "aliases": [],
  "relations": [
    {"type": "related-to", "target": "another-local-entry"}
  ],
  "cases": [
    "teamleaderleo/fieldwork#384"
  ]
}
```

## In simple words
...
````

The filename must be `<id>.md`.

## Core fields

### `schema`

Integer schema generation. Version 1 is the initial experiment.

### `id`

Stable lowercase kebab-case identifier. IDs are conceptual identities, not prose titles. Rename only when the concept itself was misidentified; prefer aliases for wording changes.

### `kind`

Current allowed values:

```text
bug-species
invariant
hunting-technique
repair-pattern
regression-pattern
concept
anti-pattern
executable-graduation
```

The set may grow when real material does not fit cleanly.

### `maturity`

Current allowed values:

```text
candidate
supported
mature
```

This describes confidence in the reusable abstraction.

### `facets`

A map from normalized facet family to an array of normalized values. Version 1 recognizes these families without requiring every entry to populate each one:

```text
domains
concerns
mechanisms
triggers
techniques
```

Facet values are kebab-case. Entries may participate in several values simultaneously.

`domains` is deliberately only one facet. Do not use it as a canonical parent.

### `aliases`

Search terms or prior names that should resolve conceptually to this entry. An alias does not create another identity.

### `relations`

Typed links between local compendium entries.

Initial relation vocabulary:

```text
violates
illustrates
related-to
detected-by
repaired-by
protected-by
clarifies
counterexample-to
specializes
generalizes
graduated-to
```

The validator checks local relationship targets when they look like local IDs. External/owned case references belong in `cases`, not in `relations`.

### `cases`

Pointers to concrete evidence carriers. Version 1 accepts ordinary strings because the repositories already have several useful evidence shapes: owned issue references, paths, findings, investigations, experiments, and exact source records.

Prefer stable owned references such as:

```text
teamleaderleo/fieldwork#626
teamleaderleo/linux-fieldwork#609
findings/F83-codex-append-acknowledgement/finding.md
```

The case itself owns source revision, execution receipts, caveats, and history.

## Recommended human sections

The exact prose shape can vary, but a bug species is usually useful when a reader can recover:

```text
In simple words
Execution shape
Typical signatures
Invariant violated
Hunting questions
Repair shape
Regression shape
Limits and counterexamples
Cases
Related entries
```

A concept or technique should use the sections that fit the subject rather than imitating a bug template mechanically.

## Important modeling rules

### Keep similar-looking bugs separate until the owner matches

Two failures that share vocabulary can have different state owners or different legality rules. Prefer two related candidate entries over one falsely universal species.

### Record limits early

A mature entry needs examples where it does *not* apply. A counterexample is useful corpus material, not a failure of the taxonomy.

### Separate invariant from repair

`Owned(x) before Published(x)` is an invariant. `prepare → own → publish → retire` is one repair/state-machine pattern that can enforce it. Keeping them separate makes alternate correct implementations representable.

### Separate terminal selection from cleanup liveness

For example, “cleanup must not replace the selected error” and “cleanup must not indefinitely block publication of an already-selected error” are related but not identical bugs. Do not collapse them solely because both mention cleanup.

### Unknown is information

When an external effect may have occurred, uncertainty should remain explicit. An ambiguous outcome is not equivalent to failure, absence, cancellation, or success.

## Validation boundary

The version-1 helper checks structural consistency only:

- one metadata block per entry;
- valid JSON;
- schema, ID, kind, and maturity;
- filename/ID agreement;
- known facet families and array values;
- duplicate IDs;
- relation shape and local-target existence.

It cannot prove that a generalization is technically sound. Case-backed review remains responsible for meaning.
