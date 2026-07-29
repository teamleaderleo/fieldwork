# Campaign 0004 Status

State: `claimed`

Campaign issue: #96  
Programme: #16  
Target hub: #11  
Upstream contact authorized: `false`

## Current result

L01 is complete. DuckDB Python 1.5.5 with the bundled `httpfs` extension can return `InterruptException` while completing an S3 multipart upload at the requested final key.

- CSV can be a readable deterministic prefix of the requested export.
- Parquet can be a completed object that rejects reads because terminal metadata is absent.
- Hard process death leaves an incomplete multipart upload rather than a final object.
- Same-key retry does not remove the older incomplete upload.
- Remote `USE_TMP_FILE true` does not create local-style staging.

## Active lane

- #103 — source-level regression and repair ownership for interrupted S3 publication.

## Durable evidence

- L01 report and compact result summary
- L02 request-order trace and compact trace result
- held upstream issue draft
- owned DuckDB research branch and workflow artifacts

## Decision gate

Issue-level reporting is supported and held for human approval.

A code PR draft waits for:

1. a source-level failing regression;
2. an audit of destructor-driven successful S3 close;
3. a decision between multipart abort, explicit close semantics, cleanup reordering, or a broader abort contract.

No upstream contact occurred.
