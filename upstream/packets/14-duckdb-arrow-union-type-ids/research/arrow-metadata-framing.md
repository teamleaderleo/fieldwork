# DuckDB Arrow metadata framing and parsing

Date: 2026-08-05

## Status

Research only. This note creates no public contact, source branch, or numbered-unit claim.

Source observations were pinned to DuckDB public source `043e1894425b49984c5010f253589e5d9c5fdde4` and must be refreshed before implementation.

## Core finding

Arrow C Data schema metadata is a serialized key/value sequence exposed through a raw `const char *`. DuckDB's parser currently has no accompanying byte length. It reads counts and lengths directly, advances the pointer, and constructs strings without validating negative values, cumulative arithmetic, or available bytes.

The absence of a total byte length is an API-level limitation: complete memory bounds validation cannot be reconstructed from the pointer alone. That does not mean the parser must accept every malformed integer or perform unchecked arithmetic.

## Current parser behavior

`ArrowSchemaMetadata::ArrowSchemaMetadata(const char *metadata)` currently:

1. reads `num_pairs` as `int32_t`;
2. loops from zero to `num_pairs`;
3. reads `key_length` as `int32_t`;
4. casts it to `idx_t` for `std::string` construction;
5. advances the raw pointer by `key_length`;
6. repeats this for `value_length`;
7. assigns into an unordered map;
8. accesses required metadata entries with `operator[]`, default-inserting missing keys;
9. parses extension JSON, using stricter errors only for `arrow.opaque`.

Consequences include:

- a negative key/value length becoming a huge unsigned allocation/read length;
- unchecked pointer arithmetic;
- attacker-controlled pair counts and cumulative work;
- duplicate keys silently overwriting earlier values;
- missing keys becoming indistinguishable from present empty values;
- no deterministic upper bound on metadata parsing work;
- malformed extension metadata being ignored for many canonical/unknown extensions.

## What can be fixed without a byte length

A narrow parser-hardening contribution can still reject structurally impossible or unreasonable inputs before dereferencing payload bytes:

- reject negative pair counts;
- cap pair count;
- reject negative key/value lengths;
- cap individual key/value lengths;
- use checked cumulative-size arithmetic;
- reject cumulative metadata above a configured hard ceiling;
- avoid `operator[]` for required-key lookup;
- define duplicate-key behavior explicitly;
- validate extension-name and metadata-key pairing;
- preserve a controlled physical-type fallback when an extension is unknown.

These checks reduce obvious integer-conversion and denial-of-service risks, but they cannot prove that the producer allocated enough bytes.

## Stronger API direction

Newer or internal conversion APIs could accept a bounded metadata view:

```text
MetadataView {
  const char *data;
  idx_t size;
}
```

The parser could then validate:

- every 4-byte prefix fits;
- every key/value payload fits;
- cumulative offset never exceeds `size`;
- no trailing bytes, or trailing bytes according to an explicit policy;
- a configurable size limit below `idx_t` maximum.

The Arrow C Data ABI itself still provides only a pointer, so generic consumers may need to copy through a producer-specific bounded API or accept that the raw ABI remains trusted-memory input.

## Unknown extension behavior

DuckDB first derives the physical storage type from `schema.format`. It only replaces that type when extension metadata identifies a registered extension. Unknown extensions therefore degrade to their physical storage type rather than calling an absent extension callback.

That is a useful compatibility behavior and should be retained, but the degradation should be observable:

- registered and accepted extension;
- unknown extension preserved as physical storage;
- known extension with unsupported physical format;
- malformed extension metadata;
- strict noncanonical `arrow.opaque` metadata failure.

Silently treating all malformed metadata as ordinary storage can hide producer corruption or type-fidelity loss.

## Duplicate-key policy

The Arrow metadata encoding permits a sequence of key/value pairs, but consumers need a deterministic policy. Options:

1. first value wins;
2. last value wins;
3. reject duplicates;
4. reject duplicates only for reserved `ARROW:*` keys.

For extension identity and payload, rejecting duplicate reserved keys is the safest narrow rule. Nonreserved application metadata could retain last-wins compatibility if needed.

## Proposed error taxonomy

- `InvalidInputException`: negative count/length, over-limit count/length, malformed required extension metadata;
- `NotImplementedException`: valid extension format not supported by DuckDB;
- controlled physical fallback: unknown extension over a valid physical format;
- internal error only for impossible DuckDB-owned serialized metadata.

## Discriminating malformed matrix

1. negative pair count;
2. extremely large pair count with no entries;
3. negative key length;
4. negative value length;
5. individual length above cap;
6. cumulative-size overflow;
7. duplicate `ARROW:extension:name`;
8. duplicate `ARROW:extension:metadata`;
9. extension name present without metadata key;
10. metadata key present without extension name;
11. malformed JSON for `arrow.opaque`;
12. malformed JSON for a canonical extension;
13. unknown canonical extension over primitive storage;
14. unknown extension over nested storage;
15. registered extension with mismatching physical format;
16. empty extension name;
17. embedded NUL bytes in key and value;
18. valid zero-pair metadata;
19. metadata at exact configured size cap;
20. bounded parser with truncated 4-byte prefix, key, and value payloads.

Each test should verify controlled errors and release behavior, not merely process survival.

## Suggested unit decomposition

### Unit A — signed length/count validation

Smallest possible source change. Reject negatives and unreasonable caps with native malformed fixtures.

### Unit B — reserved-key duplicate and presence rules

Defines extension metadata identity behavior without changing general application metadata.

### Unit C — bounded internal metadata view

Adds a size-aware parser for APIs that can supply length, while retaining a documented raw-pointer compatibility path.

### Unit D — extension-fidelity observability

Expose or retain a flag indicating that an unknown extension was degraded to physical storage.

## Relationship to public issue #21849

This is one concrete slice of the broader Arrow C Data validation umbrella. It should remain separate from child-pointer, buffer-count, union, list, or run-end validation so the correctness and compatibility policy can be reviewed independently.

## Relevant source

- `src/common/arrow/schema_metadata.cpp`
- `src/include/duckdb/common/arrow/schema_metadata.hpp`
- `src/function/table/arrow/arrow_duck_schema.cpp`
- `src/common/arrow/arrow_type_extension.cpp`

## Links

- https://github.com/duckdb/duckdb/issues/21849
- https://github.com/duckdb/duckdb/pull/15285
- https://github.com/duckdb/duckdb/pull/22011
