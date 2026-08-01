# Approaches — Unit 04: preserve the literal Hive default-partition marker

## In simple words

The selected direction reserves the raw Hive marker for SQL NULL and URL-escapes only the exact colliding literal. It repairs the path before information is lost, uses DuckDB's existing decoder, and changes no API. Reader-only fixes lose because one directory may already contain overwritten or semantically merged data. UUID filenames preserve files while leaving partition identity collapsed.

## Current exact inputs

- public source base: `duckdb/duckdb@81fcce7fa76a320dc65be54cb0825e5315ac6f5b`;
- clean owned source: `teamleaderleo/duckdb@1c931ed41822f0e27d66afb636be2730695dcf8d`;
- source PR: [`teamleaderleo/duckdb#18`](https://github.com/teamleaderleo/duckdb/pull/18);
- exact-head execution carrier: [`teamleaderleo/duckdb#19`](https://github.com/teamleaderleo/duckdb/pull/19);
- exact-head execution run: [`30696673877`](https://github.com/teamleaderleo/duckdb/actions/runs/30696673877), job `91360634513`;
- archived prior clean generation: `866c8ee8e479789000dbd3acc1fd5a0444af41c2`.

## Decision criteria

1. SQL NULL and the exact literal marker produce distinct directory identities.
2. Existing raw-marker directories continue to read as SQL NULL.
3. Ordinary partition values keep their current path encoding.
4. The change stays local, reviewable, and free of a new public option.
5. The result survives fixed filenames, UUID filenames, filter pruning, encoded-token aliasing, and nested multi-column partitions.
6. The clean branch remains one commit over the exact public base with product source and target-native test only.

## Selected approach

### Escape one underscore of the exact reserved literal in the writer

- Design: after ordinary Hive escaping, compare the result with `__HIVE_DEFAULT_PARTITION__`; on equality, emit `%5F_HIVE_DEFAULT_PARTITION__`.
- Owning boundary: `PartitionFileRequestBuilder::BuildDirectory`.
- Evidence: historical applied-patch native pass; current source review; existing URL decode; exact-head execution run tracked above.
- Advantages: preserves the raw marker for SQL NULL, round trips through existing decoding, adds no reader special case, and changes no public API.
- Costs and risks: external readers must follow Hive URL-decoding conventions to recover the literal; executed semantics remain Parquet-focused until the current run completes.

### Injectivity control added during owner review

A second literal, `%5F_HIVE_DEFAULT_PARTITION__`, now appears in the target test. Ordinary URL encoding turns its percent sign into `%25`, producing `%255F_HIVE_DEFAULT_PARTITION__`. The three logical values therefore map to three paths:

| Logical value | Directory value |
| --- | --- |
| SQL NULL | `__HIVE_DEFAULT_PARTITION__` |
| literal marker | `%5F_HIVE_DEFAULT_PARTITION__` |
| literal spelling of encoded token | `%255F_HIVE_DEFAULT_PARTITION__` |

This control checks that the repair does not create a second alias.

### Filter-pruning control added during owner review

The target test now queries both `p = '__HIVE_DEFAULT_PARTITION__'` and `p IS NULL`. DuckDB resolves Hive partition constants before file open for pruning, so the same identity rule must hold outside complete scans.

## Viable alternatives

### Reject the literal reserved value

- Design: throw when a non-NULL partition value equals the marker.
- Benefit: deterministic failure instead of silent collision.
- Cost: makes an otherwise representable string unavailable despite an existing reversible codec.
- Reopening trigger: maintainers declare the raw marker intentionally unrepresentable as a user value.

### Add a configurable NULL marker

- Design: expose an option selecting the output token and teach readers and writers the configured contract.
- Benefit: supports ecosystem-specific marker conventions.
- Cost: widens API, persistence, auto-detection, defaulting, and cross-reader compatibility work.
- Reopening trigger: accepted upstream design or concrete demand for marker customization.

### Encode every underscore or every partition value more aggressively

- Design: broaden the generic escape rules.
- Benefit: reserves more path names systematically.
- Cost: directory churn for ordinary values and a much larger compatibility review.
- Reopening trigger: another demonstrated collision under current `Escape` behavior.

## Executed losing approaches

### Reader-only interpretation

- Exact historical source: `duckdb/duckdb@de477da7606fc2d857f81117f0140d0550a5c42c`.
- Run: `30599146006`, job `91065692552`.
- Result: one row remained under fixed filenames; the reader observed SQL NULL.
- Why it lost: the writer had already collapsed path identity and overwritten data.

### UUID filenames as the repair

- Model: both values receive unique file names while sharing the colliding directory.
- Result: both payloads can survive while both inherit SQL NULL partition semantics.
- Why it lost: file uniqueness leaves logical partition identity collapsed.

### Output-path collision guard

- Prior record: Fieldwork issue #223.
- Benefit: converts silent data loss into a deterministic error.
- Why it lost: leaves the literal value unrepresentable and does not repair semantic collapse with unique filenames.
- Retained value: possible defense-in-depth for future codec collisions.

## Rejected easy answers

### Treat encoded and raw marker forms as NULL

`%5F_HIVE_DEFAULT_PARTITION__` must decode to the literal string. Mapping it to SQL NULL recreates the same collision.

### Rename the Hive NULL marker

The raw marker is an established compatibility contract. Renaming moves the reserved-name collision and breaks existing paths.

### Tell users to avoid the string

The current writer can silently overwrite or misclassify data. A compact reversible writer-side correction exists.

## Prior upstream work

| Link | Approach | Status | Relationship |
| --- | --- | --- | --- |
| [issue #24308](https://github.com/duckdb/duckdb/issues/24308) | exact literal-marker/NULL collision | open | direct public problem record |
| [PR #20512](https://github.com/duckdb/duckdb/pull/20512) | raw marker for SQL NULL | merged | establishes the NULL contract |
| [PR #21731](https://github.com/duckdb/duckdb/pull/21731) | type detection around NULL markers | merged | complementary inference work |
| [issue #24309](https://github.com/duckdb/duckdb/issues/24309) | literal string `NULL` ambiguity | closed | adjacent token issue |
| [PR #24318](https://github.com/duckdb/duckdb/pull/24318) | preserve literal `NULL` for VARCHAR | merged | complementary and present in current base |
| [PR #8540](https://github.com/duckdb/duckdb/pull/8540) | historical marker discussion | merged | context for a future configurable marker |
| [owned PR #7](https://github.com/teamleaderleo/duckdb/pull/7) | historical execution carrier | open draft | retained baseline and patch evidence |
| [owned PR #18](https://github.com/teamleaderleo/duckdb/pull/18) | clean source candidate | open, ready for owner review | current unit source record |
| [owned PR #19](https://github.com/teamleaderleo/duckdb/pull/19) | workflow-only execution carrier | open | checks out and executes exact source SHA |

## Additional addressable DuckDB areas found during context review

These stay outside unit 04's source diff.

### A. Escaped Hive partition keys remain encoded — issue-first candidate

Current evidence:

- `HivePartitioning::GetValue` URL-decodes partition values;
- parsed partition keys remain raw path text;
- existing [`hive_partition_escape.test`](https://github.com/duckdb/duckdb/blob/81fcce7fa76a320dc65be54cb0825e5315ac6f5b/test/sql/copy/partitioned/hive_partition_escape.test) writes a partition column name containing reserved characters and expects automatic Hive binding to fail with a binder error.

Addressable question: define a reversible key codec and decode keys consistently during parse/bind, with collision handling for two encoded spellings that decode to one identifier.

Required next evidence: minimal writer/readback test for names containing `=`, slash, percent, space, and backslash; duplicate decoded-key behavior; explicit-type binding behavior.

### B. Query-fragment slash can re-enable Hive parsing — source-inferred candidate

`HivePartitioning::Parse` disables partition candidacy at `?`, then sets `candidate_partition=true` after each later slash. A query value with a path-like suffix such as `?redirect=/p=value/file` can therefore expose `p=value` as a phantom partition after the first query slash.

Required next evidence: direct parser or reader test using an HTTP-style path with query parameters containing slash and equals signs. The candidate should advance only after a runnable reproduction.

### C. Repeated external partition keys collapse through map insertion — lower priority

An external path such as `a=1/a=2/file.parquet` produces duplicate logical keys. The parser stores partitions in a map and retains one insertion. Writer-generated paths cannot contain duplicate table column names, so this is primarily an external-path ambiguity.

Required next evidence: define intended behavior—reject, first-wins, or last-wins—and add a direct parser/read test before any source proposal.

## Deferred broader work

- configurable marker option;
- JSON and other copy-format execution;
- Spark, Arrow, and Polars reader verification;
- generalized reserved-path collision detection;
- remote and object-store execution;
- literal `NULL` semantics already handled by current upstream work.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | DuckDB `de477da`, Fieldwork #223 | characterize | exact path collision reproduced | source disproves shared path |
| 2026-07-31 | PR #7 head `85a2cf96...`, runs `30599145476` and `30599146006` | select writer escape | patched run passed and unpatched run failed at the intended assertion | current main equivalent fix |
| 2026-08-01 | public `63094a6`, clean `866c8ee` | materialize | expanded matrix passed and clean two-file source branch was published | exact-head review expires |
| 2026-08-01 | public `81fcce7`, clean `1c931ed`, PRs #18/#19 | accept implementation for owner inspection; execute exact-head gates | source remains localized; alias and pruning controls added; exact-head run queued | current run failure or source movement |
