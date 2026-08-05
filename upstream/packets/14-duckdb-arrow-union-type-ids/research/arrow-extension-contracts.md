# DuckDB Arrow extension-type contracts

Date: 2026-08-05

## Status

Research only. No public contact, implementation branch, or numbered-unit claim is authorized by this note.

Source observations were pinned to DuckDB public source `043e1894425b49984c5010f253589e5d9c5fdde4`.

## Core finding

An Arrow extension type has at least four distinct contracts:

1. **identity** — extension name and optional vendor/type metadata;
2. **physical storage** — Arrow format, buffers, and children;
3. **DuckDB logical meaning** — registered alias or extension logical type;
4. **conversion context** — callbacks, options, catalog state, and lifetime.

Correct interoperability requires all four to agree. Current behavior is intentionally permissive for unknown extensions but highly callback-dependent for registered ones. The degradation and failure policies are not yet expressed as one explicit contract.

## Current import path

DuckDB currently:

1. parses the physical Arrow format into an `ArrowType`;
2. parses extension metadata;
3. checks whether a matching extension is registered;
4. if registered, invokes its `GetType` callback and attaches conversion data;
5. if unknown, retains the physical storage type.

This unknown-extension fallback is important for compatibility. A consumer should still be able to read storage bytes when it does not understand higher-level semantics.

However, callers cannot easily distinguish:

- no extension metadata;
- unknown extension degraded to storage;
- known extension accepted losslessly;
- known extension whose metadata was malformed but ignored;
- registered extension whose callback selected a different physical interpretation.

## Registered-extension fallback concern

`ArrowTypeExtension::GetType` supports a custom callback. When no callback exists, the default returns the configured DuckDB type directly, with a source comment indicating this fallback is undesirable.

That can be safe for one-format scalar extensions, but it risks bypassing schema-specific verification:

- physical format differs from the registered expected format;
- nested storage shape differs;
- required metadata is absent;
- output version uses a view/large layout the converter does not support;
- storage child names/nullability differ from the canonical extension definition.

A registered extension should either provide a validator/type resolver or use a default resolver that checks its declared physical format and structural schema.

## Canonical versus noncanonical identity

Canonical extensions use `ARROW:extension:name`. Noncanonical DuckDB types are represented through `arrow.opaque` plus JSON metadata containing vendor and type names.

Useful invariants:

- canonical extension identity should not depend on unordered metadata map iteration;
- `arrow.opaque` requires valid vendor and type names;
- reserved metadata keys should have deterministic duplicate rules;
- empty names should be rejected or treated as no extension;
- a known extension with unknown format should fail, not silently degrade;
- an unknown extension with valid storage may degrade, but the loss of semantic identity should be observable.

## Schema/data layout agreement

Extension schema population selects among normal, large-offset, and view formats based on client options such as:

- Arrow output version;
- string-view production;
- large-buffer mode;
- lossless conversion.

The appender must use the same physical layout. Prior nested-extension and output-version bugs show that schema and bytes can diverge while DuckDB-only tests remain self-consistent or incomplete.

Every registered extension should have one source of truth for:

```text
(options, logical type) -> physical schema + physical appender type + conversion callbacks
```

Separate schema and appender branching should be mechanically cross-checked.

## Consumer compatibility policy

Not every downstream consumer supports every extension or Arrow format. Existing clients sometimes disable metadata or advanced layouts, such as Polars output suppressing extension metadata.

A clearer output policy could distinguish:

- **lossless extension output** — extension metadata and canonical storage;
- **storage-compatible output** — physical Arrow type without extension identity;
- **consumer-compatible fallback** — cast or alternative layout;
- **unsupported** — controlled error rather than misleading schema.

This policy should be selected explicitly by client surface rather than hidden in scattered booleans.

## Context and registration lifetime

Extension callbacks receive a `ClientContext`. Lazy schema or array production may happen after the original connection is closed. This intersects with the lifetime dossier:

- extension registration lives in `DBConfig`/catalog state;
- callback code may parse logical types or inspect settings;
- lazy result consumers may call `get_schema` later;
- extension loading/unloading or transaction state may change.

Potential designs:

1. eagerly resolve extension schema and conversion data into an immutable snapshot;
2. retain a minimal conversion context independent of an active transaction;
3. retain the full context through result lifetime;
4. prohibit context-dependent lazy callbacks and require eager preparation.

The extension API should state which design it promises.

## Import decision taxonomy

A useful internal result could carry:

```text
ExtensionResolution {
  status: NONE | LOSSLESS | UNKNOWN_DEGRADED | KNOWN_UNSUPPORTED | MALFORMED;
  physical_type;
  logical_type;
  extension_identity;
  conversion_data;
}
```

This would support diagnostics, testing, and future strict modes without changing default compatibility immediately.

## Discriminating import matrix

1. known canonical extension with expected primitive storage;
2. known canonical extension with wrong primitive format;
3. known nested extension with missing child;
4. known extension with wrong child nullability;
5. unknown canonical extension over primitive storage;
6. unknown canonical extension over nested storage;
7. valid `arrow.opaque` vendor/type pair;
8. malformed `arrow.opaque` JSON;
9. duplicate reserved extension keys;
10. empty extension name;
11. extension metadata on dictionary storage;
12. extension metadata on run-end encoded storage;
13. extension loaded before bind and unavailable before execution;
14. connection closed before lazy schema callback;
15. callback throws a controlled invalid-input error;
16. callback returns a logical type incompatible with storage conversion.

## Discriminating export matrix

For every extension/layout combination:

- produce schema and array;
- validate with a reference implementation;
- inspect extension metadata exactly;
- verify buffer count and child shape;
- consume values externally;
- re-import through DuckDB where supported.

Settings matrix:

1. lossless off/on;
2. Arrow output versions before and after view support;
3. normal/large offsets;
4. string/binary view off/on;
5. metadata enabled/disabled for consumer compatibility;
6. top-level and nested extension values;
7. sliced/dictionary/constant DuckDB vectors;
8. values exceeding `STANDARD_VECTOR_SIZE`.

## Candidate future units

### Unit A — default registered-extension format verification

Replace the unchecked default `GetType` fallback with validation against declared format and structural storage.

### Unit B — unknown-extension degradation observability

Retain compatibility while recording or exposing that semantic identity was lost.

### Unit C — extension schema/appender parity test framework

For every registered extension, assert declared schema layout matches finalized array buffers recursively.

### Unit D — immutable extension conversion snapshot

Remove active-transaction dependence from lazy Arrow callbacks.

### Unit E — consumer compatibility profile

Replace scattered client booleans with explicit lossless/storage/fallback output profiles.

## Relationship to other research lanes

- metadata framing defines safe extension identity parsing;
- lifetime research defines callback/context validity;
- reference-consumer interop proves schema/data agreement;
- pushdown capabilities must account for extension physical types;
- encoded-layout invariants apply when extension storage is nested, dictionary encoded, or run-end encoded.

## Links

- https://github.com/duckdb/duckdb/pull/15285
- https://github.com/duckdb/duckdb/pull/13986
- https://github.com/duckdb/duckdb/pull/22011
- https://github.com/duckdb/duckdb/pull/22508
- https://github.com/duckdb/duckdb/pull/23190
- https://github.com/duckdb/duckdb/pull/24157
