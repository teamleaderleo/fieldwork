# Arrow C Data null field names

Date: 2026-08-06

Status: `SPEC-CONFORMANCE CHARACTERIZATION CANDIDATE`

Public upstream contact remains unauthorized. This is a private Fieldwork note only.

## Specification contract

`ArrowSchema.name` is optional. A producer may omit it by setting the pointer to `NULL` or by providing an empty string. Consumers may ignore field names.

## DuckDB source pin

Inspected at public main `7a91c3658f9411ab17556e55f9df34b3b2140f6e`.

Relevant paths:

- `src/function/table/arrow.cpp`
- `src/function/table/arrow/arrow_duck_schema.cpp`
- `src/main/capi/arrow-c.cpp`

## Current top-level behavior

`ArrowTableFunction::PopulateArrowTableSchema` uses:

```cpp
auto name = string(schema.name);
if (name.empty()) {
    name = string("v") + to_string(col_idx);
}
```

The fallback handles an empty string but the `string` constructor is reached first. A null name can therefore throw a standard-library exception before DuckDB synthesizes `vN`.

The C API wrapper catches `std::exception`, so `duckdb_schema_from_arrow` is expected to return an error rather than crash. That is still a rejection of a conforming Arrow schema and may expose implementation-specific error text.

## Nested behavior

Struct and sparse-union schema parsing currently passes child `name` pointers directly into DuckDB member-name construction. Arrow permits those names to be null too.

DuckDB needs deterministic synthetic member names because its STRUCT and UNION logical types require addressable members. Candidate policy:

- top-level unnamed fields: `v0`, `v1`, ...;
- nested unnamed members: `v0`, `v1`, ... within each parent;
- deduplicate synthetic and supplied names through the same case-insensitive policy used for top-level columns;
- preserve supplied nonempty names;
- treat an empty string and null pointer identically.

## Characterization matrix

### Top-level scalar field

- one INT32 child with `name = nullptr`;
- schema conversion must succeed;
- array conversion must preserve values;
- resulting name should be `v0` where a name-inspection API is available.

### Top-level empty-string control

Same fixture with `name = ""`; current fallback should pass.

### Struct member

- top-level field named `s`;
- `+s` child with one INT32 member whose name is null;
- schema and array conversion must succeed;
- resulting member name must be deterministic.

### Sparse-union member

- valid sparse union type IDs;
- one or more null member names;
- conversion must preserve mapped values and synthesize unique member names.

### Collisions

- supplied `v0` next to unnamed member zero;
- names differing only by case;
- several unnamed members;
- empty and null names mixed.

### Error controls

A null mandatory `format` remains invalid and should produce an ordinary invalid-input error. Null optional `name` must not be conflated with null `format`.

## Repair direction

Introduce one helper such as:

```cpp
string ArrowFieldName(const char *name, idx_t index) {
    if (!name || name[0] == '\0') {
        return "v" + to_string(index);
    }
    return name;
}
```

Use it consistently for top-level columns and nested member construction, followed by the existing deduplication rules.

## Scope recommendation

This is a small schema-import conformance unit. Keep it separate from general child-pointer validation, metadata parsing, and union type-ID mapping.
