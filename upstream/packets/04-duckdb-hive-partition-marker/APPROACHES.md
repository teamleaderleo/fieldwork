# Approaches — Unit 04: preserve the literal Hive default-partition marker

## In simple words

The selected direction reserves the raw Hive marker for SQL NULL and URL-escapes only the exact colliding literal. It repairs the path before information is lost, uses DuckDB's existing decoder, and changes no API. Reader-only fixes lose because one directory may already contain overwritten or semantically merged data. UUID filenames are a useful control, yet they preserve files without preserving partition identity.

## Decision criteria

1. SQL NULL and the exact literal marker produce distinct directory identities.
2. Existing raw-marker directories continue to read as SQL NULL.
3. Ordinary partition values keep their current path encoding.
4. The change stays local, reviewable, and free of a new public option.
5. The result survives fixed filenames, UUID filenames, and nested multi-column partitions.

## Selected approach

### Escape one underscore of the exact reserved literal in the writer

- Design: after ordinary Hive escaping, compare the result with `__HIVE_DEFAULT_PARTITION__`; on equality, emit `%5F_HIVE_DEFAULT_PARTITION__`.
- Owning boundary: `PartitionFileRequestBuilder::BuildDirectory`.
- Evidence: historical applied-patch native pass; current-head regression matrix; source-confirmed existing URL decode.
- Advantages: preserves the raw marker for SQL NULL, round trips through existing decode, no reader special case, no public API.
- Costs and risks: external readers must follow Hive URL-decoding conventions to recover the literal; executed semantics are Parquet-specific.
- Remaining controls: ordinary current-head CI, human-authored replacement under DuckDB's contribution policy, optional external-reader matrix.

## Viable alternatives

### Reject the literal reserved value

- Design: throw when a non-NULL partition value equals the marker.
- Why it remains plausible: it prevents silent collision with a small writer-side check.
- What it would improve: deterministic failure instead of data loss or semantic collapse.
- What it would widen or complicate: turns a representable string into an API restriction and breaks workloads that can safely use URL encoding.
- Exact discriminator: maintainer policy declaring the raw marker an unrepresentable user value.
- Reopening trigger: upstream rejects encoded literal directories.

### Add a configurable NULL marker

- Design: expose an option selecting the output token and teach readers/writers the configured contract.
- Why it remains plausible: prior discussion on DuckDB PR #8540 mentioned a future option.
- What it would improve: supports ecosystem-specific marker conventions.
- What it would widen or complicate: API, persistence compatibility, auto-detection, defaults, cross-reader behavior, and option plumbing.
- Exact discriminator: concrete user demand for marker customization beyond this collision.
- Reopening trigger: an accepted upstream design for configurable Hive NULL markers.

### Encode every underscore or every partition value more aggressively

- Design: change the generic escape rules.
- Why it remains plausible: a broader codec can reserve more names consistently.
- What it would improve: potential future reserved-token safety.
- What it would widen or complicate: directory churn for ordinary values, compatibility review, and larger regression scope.
- Exact discriminator: another demonstrated collision under current `Escape` behavior.
- Reopening trigger: a systematic path-codec defect rather than this one exact reserved token.

## Executed losing approaches

### Reader-only interpretation

- Exact source: current `HivePartitioning::GetValue` on `63094a6f725af5045113dda74e291c7d604f6a88`.
- What ran: baseline native SQLLogic test with both values written to one partition root.
- Result: one row remained under fixed filenames; the reader observed only SQL NULL.
- Why it lost: the writer had already collapsed path identity and overwritten data.
- Useful evidence retained: baseline run `30599146006` and its exact one-row failure.

### UUID filenames as the repair

- Exact test: current unit 04 UUID control.
- What it tests: both values use distinct file names while sharing the colliding directory under an unpatched writer.
- Result model: both files can survive, while Hive parsing still maps the shared path token to SQL NULL.
- Why it lost: file uniqueness solves overwrite only; logical partition identity remains collapsed.
- Useful evidence retained: UUID is an adversarial control in the selected regression matrix.

### Output-path collision guard

- Exact prior record: Fieldwork issue #223 discussion.
- Design: detect that two logical values resolve to one directory and abort.
- Why it lost: defensive detection improves failure behavior but leaves the literal value unrepresentable and does not repair semantic collapse with unique filenames.
- Useful evidence retained: a guard could remain defense-in-depth for future codec collisions.

## Rejected easy answers

### Change the reader to treat encoded and raw marker forms identically

- Temptation: add another null alias.
- Why it is incomplete: `%5F_HIVE_DEFAULT_PARTITION__` must decode to the literal string; treating it as NULL recreates the collision.
- Negative control: current `Unescape` already recovers the literal underscore.

### Rename the Hive NULL marker

- Temptation: choose a less likely token.
- Why it is incomplete: breaks the established Hive-compatible raw marker and merely moves the reserved-name collision.
- Source fact: merged PR #20512 deliberately adopted `__HIVE_DEFAULT_PARTITION__` for compatibility.

### Rely on users to avoid the string

- Temptation: document the token as reserved.
- Why it is incomplete: current behavior can silently lose or misclassify data; the writer has a compact reversible encoding path.
- Negative control: public issue #24308 provides an executable two-row reproduction.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [issue #24308](https://github.com/duckdb/duckdb/issues/24308) | reports the exact literal-marker/NULL collision | open | direct problem record; no public interaction from Fieldwork |
| [PR #20512](https://github.com/duckdb/duckdb/pull/20512) | writes raw Hive marker for SQL NULL and reads it as NULL | merged | creates the correct NULL contract whose reserved-literal collision this unit repairs |
| [PR #21731](https://github.com/duckdb/duckdb/pull/21731) | ignores NULL markers during Hive type detection | merged | complementary type-inference work |
| [issue #24309](https://github.com/duckdb/duckdb/issues/24309) | literal string `NULL` read as SQL NULL | closed | adjacent literal-token ambiguity |
| [PR #24318](https://github.com/duckdb/duckdb/pull/24318) | preserves literal string `NULL` for VARCHAR partitions | merged | complementary; current base includes it; exact reserved marker still collides |
| [PR #8540](https://github.com/duckdb/duckdb/pull/8540) | initial NULL Hive typing test and discussion of marker choice | merged | historical context and possible future configurable-marker idea |
| [owned PR #7](https://github.com/teamleaderleo/duckdb/pull/7) | applied-patch execution carrier | open draft | accepted mechanism evidence; superseded for source cleanliness by the unit 04 branch |
| [owned PR #18](https://github.com/teamleaderleo/duckdb/pull/18) | current-head materialization and execution carrier | open draft | becomes the clean owned candidate after temporary files are erased from branch history |

## Deferred adjacent work

- configurable marker option — separate API and compatibility design;
- JSON and other copy-format execution — generic source caller, separate target-native matrices;
- external Spark/Arrow/Polars reader verification — ecosystem compatibility study;
- generalized reserved-path collision detection — defense-in-depth beyond the exact defect;
- literal `NULL` semantics — already handled by current upstream prior art.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | DuckDB `de477da`, Fieldwork issue #223 | characterize | exact path collision reproduced | source disproves shared path |
| 2026-07-31 | owned PR #7 head `85a2cf96a2e6fe67157ca0d8d8b7dc1494a8e058`, runs `30599145476` and `30599146006` | select writer escape | candidate passed; unpatched ordinary control failed at intended assertion | current main equivalent fix |
| 2026-08-01 | DuckDB public `63094a6`, merged PR #24318, current policy | refresh and hold submission | defect remains; test matrix widened; AI-generated PR policy blocks public filing | independently human-authored replacement and fresh full review |
