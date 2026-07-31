# Campaign 0004 Evidence Map

## Established

| Evidence | Result | Durable location |
|---|---|---|
| Natural CSV/Parquet S3 completion | exact count and checksum | L01 report and compact summary |
| Hard process death after uploaded part | no final key; incomplete multipart upload retained | L01 report and broad artifact |
| Same-key retry | exact new object; older multipart upload remains | L01 report and broad artifact |
| Remote `USE_TMP_FILE true` | accepted; no staging object; direct multipart | L01 report |
| Manual interrupt after uploaded part | `InterruptException` plus completed final object | L01 focused matrix |
| CSV consumer result | readable deterministic prefix | L01 report |
| Parquet consumer result | completed key; missing footer/magic bytes | L01 report |
| Request order | `HEAD` 404 after interrupt, more parts, multipart completion, then query error | L02 trace artifact |
| Delete/abort requests | none during failed-query teardown | L02 trace artifact |

## Established source mechanism for the pinned fixture

The request trace and source map align:

1. core cleanup checks the final key while multipart upload is incomplete;
2. the key is absent;
3. member destruction releases the S3 file handle;
4. S3 destructor-driven close uploads remaining buffers and completes multipart;
5. the partial final object appears before the caller receives `InterruptException`.

## Open

- exact source-level regression seam in httpfs tests;
- whether implicit S3 destructor completion is relied upon by other writers;
- narrowest safe repair ownership between core and httpfs;
- behavior on AWS S3 and other providers;
- partitioned, rotated, per-thread, and concurrent remote output.

## Held interaction

A complete upstream issue draft is stored in L02. Upstream contact remains unauthorized.
