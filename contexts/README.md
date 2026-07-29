# Contexts

This directory holds reusable integration-context dossiers and patterns.

A context is not a target map and not an experiment. It explains how a tested mechanism participates in a larger workflow, which actors and boundaries are involved, what failures propagate outward, and which claims are documented versus inferred.

## Layout

```text
contexts/
├── README.md
├── patterns/
│   ├── retry-idempotency.md
│   └── ...
└── systems/
    └── <specific-system-or-workflow>.md
```

Use `patterns/` for cross-project situations such as retries, streaming, cancellation, correlation, caching, migration, and recovery.

Use `systems/` only when Fieldwork has enough evidence to describe a particular application or integration without guessing.

## Rules

- Link a retained experiment to its relevant context dossier when making wider claims.
- Keep documented adoption separate from illustrative use.
- Record exact standards, versions, and retrieval dates.
- Prefer compact diagrams and concrete scenarios over generic claims that something is production-relevant.
- Update a context when its underlying standard, project contract, or deployment assumption changes.
- Do not turn a broad context into automatic permission to investigate or contact every project that might fit it.

See `INTEGRATION_CONTEXT.md` and `templates/integration-context.md`.