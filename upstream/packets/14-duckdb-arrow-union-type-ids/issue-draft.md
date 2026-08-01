# Private upstream issue draft

> Draft only. Public upstream contact requires explicit authorization.

## Title

Arrow sparse unions interpret logical type IDs as child indexes

## Body

DuckDB's Arrow sparse-union conversion appears to use each value in the union type-ID buffer as a positional child index. Arrow schemas can assign sparse logical IDs, for example `+us:3,7`, where IDs `3` and `7` identify children zero and one.

A focused characterization using sparse IDs `{3,7}` reproduces the problem. The same case also exercises parent-array offsets so sliced input reads the correct type-ID and child value.

A candidate fix parses the schema's type-code list, stores a logical-ID to child-index map, and resolves each row's type ID through that map before reading the child and constructing the DuckDB union value.

Questions for maintainers:

1. Should malformed union input validation live in the schema conversion path, the row conversion path, or both?
2. Should duplicate logical type IDs be rejected while parsing the schema?
3. Which Arrow type-ID storage variants should DuckDB accept for sparse unions?

Private evidence before any authorized publication:

- characterization: `teamleaderleo/duckdb#12` at `ed05ac593498fb4f95546ec591824ee23429088d`;
- passing minimal candidate: `teamleaderleo/duckdb#14` at `c962ece64c1356015aef15a37c0cc636f63b376b`;
- hardening experiment: `teamleaderleo/duckdb#16` at `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`;
- public defect reference: `duckdb/duckdb#21842`.

Current blocker: the hardening child passes the ordinary `Main` workflow but fails its targeted positive mapping test after a successful debug build. The available job-log API response omits the assertion body.