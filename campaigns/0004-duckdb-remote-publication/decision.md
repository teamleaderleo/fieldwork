# Campaign 0004 Decision

State: `claimed`

## Established decision

The S3-compatible baseline supports an actual correctness issue:

> `COPY TO S3` can return `InterruptException` while completing a multipart upload at the requested final key.

CSV may be a valid-looking deterministic prefix. Parquet may be a completed but unreadable object.

A transparent request trace established that DuckDB checks the absent final key after interruption, then uploads buffered parts and completes the multipart upload before the query thread returns its interruption result. No delete or abort request occurs.

## Action

- Keep the held upstream issue draft.
- Continue repair lane #103.
- Require a source-level failing regression before drafting a code PR.
- Prefer explicit successful close plus multipart abort on uncommitted destruction, subject to an implicit-close audit.
- Retain core cleanup reordering as a containment option rather than the preferred semantic repair.
- Keep a generic file-handle abort contract as a last resort.

## Contact boundary

Upstream contact remains unauthorized. No upstream issue or PR has been opened.
