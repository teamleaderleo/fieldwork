# Held Upstream Issue History Addendum

Status: `held`  
Upstream contact authorized: `false`

## Prior reports and fixes

This issue is a cancellation-specific continuation of an earlier S3 teardown problem.

- DuckDB PR #9758 added destructor-driven S3 `Close()` because successful `EXPORT DATABASE` metadata file handles were discarded without explicit close, leaving `schema.sql` and `load.sql` unpublished.
- DuckDB issue #12038 reported failed queries publishing incomplete CSV/JSON and footerless Parquet to S3.
- DuckDB PR #12031 changed the S3 destructor to skip `Close()` only while a C++ exception is actively unwinding.

The current interrupt reproduction shows the remaining gap: by writer-member destruction time, the interruption is stored in query error state rather than represented by an actively unwinding exception. The destructor therefore still calls `Close()` and completes multipart upload.

## Suggested addition to a future report

> This appears to be a cancellation path not covered by the active-exception guard added for #12038/#12031. The earlier fix correctly avoids destructor completion during C++ stack unwinding, while manual interruption reaches failed teardown after the error has been captured by the query engine.

## Repair caution

The destructor close cannot simply be removed without replacing successful implicit-close users. Current core `EXPORT DATABASE` metadata writing still writes through a generic `FileHandle` and releases it without explicit `Close()`.

A future upstream report should present this history because it explains both:

1. why current behavior exists; and
2. why the repair likely needs explicit commit/abort state or an audited migration to explicit successful close.

No upstream contact occurred.
