# Contexts

This directory holds reusable integration-context dossiers and patterns.

A context is not a target map and not an experiment. It explains how a tested mechanism participates in a larger workflow, which actors and boundaries are involved, what failures propagate outward, and which claims are documented versus inferred.

## Layout

```text
contexts/
├── README.md
├── registry.yml
├── patterns/
│   ├── retry-idempotency.md
│   └── ...
└── systems/
    └── <specific-system-or-workflow>.md
```

`registry.yml` holds cheap pattern leads and the relationship between worked contexts, experiments, and canonical case packs. A candidate entry is not an assignment.

Use `patterns/` for cross-project situations such as retries, streaming, cancellation, correlation, caching, migration, and recovery.

Use `systems/` only when Fieldwork has enough evidence to describe a particular application or integration without guessing.

## Worked example

`patterns/retry-idempotency.md` is paired with:

- `playgrounds/examples/retry-idempotency/`
- `playgrounds/cases/retry-idempotency.json`

The experiment validates a small state-and-retry model. The dossier cites standards and official guidance, explains representative workflows, and lists the production boundaries the model does not cover.

## Rules

- Link a retained experiment to its relevant context dossier when making wider claims.
- Keep documented adoption separate from illustrative use.
- Record exact standards, versions, retrieval dates, supported claims, and source limitations.
- Prefer compact diagrams and concrete scenarios over generic claims that something is production-relevant.
- Update a context when its underlying standard, project contract, or deployment assumption changes.
- Do not turn a broad context into automatic permission to investigate or contact every project that might fit it.
- Promote candidate contexts only when a concrete investigation needs the wider interpretation.

See `INTEGRATION_CONTEXT.md` and `templates/integration-context.md`.