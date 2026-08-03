# Jujutsu AppleDouble table-head experiment

State: `confirmed — bounded repair direction retained`

Parent scout: `#561`  
Exact target: `jj-vcs/jj@3a650c3a68aadfa693b193ffb3176fd09b824c86`  
Exact `lib/src/stacked_table.rs` blob: `47dd3e95d1caedf638b7b74422e0dd8d13214fd1`  
Public upstream issue: `jj-vcs/jj#9775`  
Executed Fieldwork head: `34160846db75a2ed45ce59db70580042e409b56f`  
Workflow run: `30795127911` — success  
Job: `91626849442` — success  
Artifact: `8848625279`, 550 bytes  
Artifact SHA-256: `44ec0144ffd6ff6198861fd9ecd54535a5945b758040c22c15e8d4d2c1b85ac0`  
Upstream contact authorized: `false`

## In simple words

Jujutsu's table store scans every filename in its `heads` directory and currently tries to load each one as a real content-addressed table segment. A macOS AppleDouble `._*` sidecar can therefore become false metadata authority and break ordinary table-store loading.

The retained comparison accepts only exact 128-character lowercase hexadecimal segment identities as table-head names. It ignores platform-generated and otherwise invalid filenames while still reporting corruption when a valid-looking segment file cannot be loaded.

## Exact target-native result

### Current source characterization

The fixture:

1. created a valid table store and head;
2. added `._<valid-head-name>` under `heads/`;
3. reloaded the store;
4. required the current loader to return an error naming that sidecar.

Result:

```text
test stacked_table::tests::stacked_table_appledouble_head_is_treated_as_segment ... ok
test result: ok. 1 passed; 0 failed; 1246 filtered out
```

This confirms that the current loader attempts to load the AppleDouble sidecar as a table segment.

### Bounded candidate comparison

The comparison filtered head-directory entries to exact lowercase hexadecimal segment identities and proved:

1. the AppleDouble sidecar is ignored;
2. a same-length non-hex filename is ignored;
3. the original valid head still loads;
4. a truncated file with a valid-looking lowercase hexadecimal segment name still raises a load error.

Result:

```text
test stacked_table::tests::stacked_table_ignores_non_segment_heads_but_preserves_corruption ... ok
test result: ok. 1 passed; 0 failed; 1246 filtered out
RESULT current-sidecar=load-error candidate-sidecar=ignored candidate-nonhex=ignored candidate-valid-name-corruption=error
```

## Retained setup negatives

Two pre-product runs remain useful harness evidence:

- `30794870299`: a relative target path broke after the probe changed directories, and missing pipeline `pipefail` let `tee` create a false green before compilation;
- `30794996907`: after fixing path and pipeline handling, the run correctly failed because the initial insertion anchor matched three test matrices.

The final generation canonicalized the target path, enabled pipeline `pipefail`, and used the unique `stacked_table_empty` test header as its insertion anchor.

## Selected direction

Retain exact segment-name validation in `TableStore::get_head_tables()` as the smallest demonstrated direction.

Why it currently wins:

- filenames that cannot be valid content-addressed segment identities receive no table-head authority;
- AppleDouble and same-length non-hex noise no longer break the store;
- a valid-looking corrupt segment remains visible as corruption rather than being silently skipped;
- the change belongs at the directory-entry trust boundary before `load_table()`;
- the same module already validates segment naming during garbage collection.

## Evidence boundary

Evidence class: `target-native-unit-fixture`.

This experiment exercises the internal `TableStore` directly. It does not reproduce a complete archived Jujutsu repository, inspect every internal metadata directory, or claim all AppleDouble placements are harmless. A submission-shaped source candidate must run the repository's normal formatting, clippy, and workspace tests and comply with the project's CLA and commit-review requirements.

## Disposition

`PROMOTE — one bounded source-and-test candidate is justified.`

No public issue, pull request, comment, review, reaction, branch, or message was created or modified in the target repository.
