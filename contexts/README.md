# Contexts

This directory holds reusable integration-context dossiers and patterns.

A context is not a target map and not an experiment. It explains how a tested mechanism participates in a larger workflow, which actors and boundaries are involved, what consequences propagate outward, and which claims are documented versus inferred.

A context is selected after a target investigation identifies a mechanism needing wider interpretation. It is not a menu of default hypotheses.

## Layout

```text
contexts/
├── README.md
├── registry.yml
├── patterns/
│   └── <cross-project-pattern>.md
└── systems/
    └── <specific-system-or-workflow>.md
```

`registry.yml` holds cheap pattern leads and relationships to retained experiments or case packs when those relationships actually exist. A candidate entry is not an assignment.

Use `patterns/` for cross-project situations that have emerged from concrete research and may be reusable across targets.

Use `systems/` only when Fieldwork has enough evidence to describe a particular application or integration without guessing.

## No canonical pattern

- No context pattern is Fieldwork's default lens.
- Do not apply a pattern to a target merely because the pattern is familiar or already documented.
- Promote or create a pattern only when a concrete investigation needs wider interpretation.
- When the target's architecture differs from an existing pattern, preserve the difference instead of forcing a fit.
- Retained patterns may provide vocabulary, source leads, or experimental techniques, but they do not choose the research question.

## Rules

- Link a retained experiment to its relevant context dossier when making wider claims.
- Keep documented adoption separate from illustrative use.
- Record exact standards, versions, retrieval dates, supported claims, and source limitations.
- Prefer compact diagrams and concrete scenarios over generic claims that something is production-relevant.
- Update a context when its underlying standard, project contract, or deployment assumption changes.
- Do not turn a broad context into automatic permission to investigate or contact every project that might fit it.
- Promote candidate contexts only when a concrete investigation needs the wider interpretation.

See `INTEGRATION_CONTEXT.md` and `templates/integration-context.md`.
