# Arrow C Stream error contracts

Date: 2026-08-06

Status: `SOURCE-SUPPORTED HARDENING CANDIDATE`

Public upstream contact remains unauthorized. This is a private Fieldwork research note only.

## Source pin

DuckDB source inspected at `58c019320e250a7b369efd756f84c6dfd68bedcb`.

Relevant code:

- `src/common/arrow/arrow_wrapper.cpp`
- `src/include/duckdb/common/arrow/arrow_wrapper.hpp`

## Contract mismatch

The Arrow C Stream interface requires a `get_last_error` callback, but explicitly allows that callback to return `NULL` when no detailed error description is available.

DuckDB currently uses:

```cpp
const char *ArrowArrayStreamWrapper::GetError() {
    return arrow_array_stream.get_last_error(&arrow_array_stream);
}
```

and then constructs a `string` directly from the result in the `get_schema` and `get_next` failure paths.

A conforming producer can therefore return an error code and `NULL` detail. Depending on the standard-library implementation, constructing a string from that null pointer can throw an unrelated library exception or otherwise fail before DuckDB reports the original stream error.

## Narrow repair direction

Preserve both the errno-compatible return code and optional detail:

1. capture the integer return code from `get_schema` or `get_next`;
2. call `get_last_error` only after a nonzero return;
3. treat a null detail as absent rather than as a C string;
4. use a stable fallback such as the errno description or `Arrow stream operation failed with code N`;
5. copy a non-null detail immediately because Arrow guarantees it only until the next callback.

The wrapper should also reject null mandatory callbacks and a released stream with an ordinary `InvalidInputException` rather than dereferencing a null function pointer.

## Characterization matrix

### `get_schema`

- returns `EINVAL`, detail `"bad schema"`;
- returns `EINVAL`, detail `NULL`;
- null `get_schema` callback;
- stream release already null;
- failed call partially initializes `out`, whose release callback must still be handled according to the producer contract.

### `get_next`

- returns `EIO`, detail `"read failed"`;
- returns `EIO`, detail `NULL`;
- null `get_next` callback;
- failed call leaves `out.release` non-null;
- failed call leaves `out.release` null.

### Ownership controls

Every case should count:

- stream release calls;
- partially returned schema/array release calls;
- last-error calls;
- whether any callback is invoked after stream release.

## Expected behavior

Errors should retain their Arrow operation and numeric code. A missing detail must not replace the real failure with `basic_string: construction from null is not valid`, a segmentation fault, or another implementation-specific message.

## Scope recommendation

This is a small wrapper-level hardening unit. It does not require Arrow conversion changes, schema parser changes, or provider-specific code.
