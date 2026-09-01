## In simple words

Two owned Tantivy execution carriers were already queued when a source-level harness audit found the same bookkeeping problem in both: each created a new file and then expected `git diff --name-only` to list it. Git does not list untracked files in that command, so both carriers would have stopped before Rust compilation even though the candidate/test content was unchanged.

The fix is evidence-only. Each workflow now marks the generated file as intent-to-add before the diff fence. The PR-2999 carrier also marks its generated `Cargo.lock` the same way before final hygiene. No production candidate code changed.

The decisive experiment remains the exact terminal-settlement discriminator against public Tantivy PR 2999. Until that run executes, the overlap conclusion stays `source-read + target-test-prepared`.

## Exact carrier generations

### PR-2999 terminal-settlement discriminator

Owned repository: `teamleaderleo/tantivy`

Owned PR: `#6`

Exact carrier head after preflight repair:

```text
0f298695dd70ee5b0e158f17a807b12992788824
```

Exact public proposal under test:

```text
quickwit-oss/tantivy PR 2999
039e02e00af3befe4a17e679af6fedfcfdee3d44
```

Replacement workflow run:

```text
31560902881
```

State at receipt creation: `queued`.

Harness change:

```text
git add -N src/indexer/index_writer/fieldwork_prepare_failure_barrier.rs
git add -N Cargo.lock
```

These calls expose generated files to `git diff` without staging their content for publication.

Candidate/test semantics are unchanged from carrier head `88f71abbb71ef2a66752c0e1d338368d04525eb5`.

### Old-architecture source materializer

Owned repository: `teamleaderleo/tantivy`

Owned PR: `#5`

Exact carrier head after the second harness repair:

```text
14fb48e59676b5e73ba18e062180c3839f8c8579
```

Pinned historical target base:

```text
667132fa7ab4a30e0c1870d791f23902ebfc6152
```

Replacement materializer run:

```text
31560922556
```

Ordinary Unit Tests run:

```text
31560922593
```

State at receipt creation: queued/pending.

Earlier harness failure `31205834330` stopped because the workflow wrote the new regression file before creating its destination directory. The first repair created that directory. Preflight review then found the independent untracked-file fence problem before the replacement runner started.

The second repair adds:

```text
git add -N src/indexer/index_writer/prepare_commit_generation_fence.rs
```

The reviewed production patch blob and regression blob remain the same as the already target-executed carrier:

```text
candidate.patch blob: 23290f4dc852471c7f58014ce81db37f6678b5bc
regression blob:      3b44c47386431b85d514cfc952357a12315a167a
```

## Why this is harness evidence, not target evidence

Neither preflight repair changes Tantivy production behavior. They only make the intended generated files visible to the workflows' own file-fence assertions.

Therefore this receipt does not upgrade any claim to `target-executed`.

The previous old-architecture candidate retains its historical `target-executed` evidence on its exact executed head. The PR-2999 overlap remains `target-test-prepared` until run `31560902881` reaches and executes the discriminator.

## Decision

1. Treat `31560902881` as the active overlap gate.
2. If it reproduces late old-epoch publication after returned failure, compare the collect-all-flushes repair on the persistent-worker architecture.
3. If it falsifies the source model, retire the old generation-fence candidate as architecturally superseded unless another current invariant survives.
4. A successful PR #5 materialization is archival/current-history maintenance only while PR 2999 remains live.

Automated upstream contact: prohibited.

Human-performed upstream interaction recorded: none.
