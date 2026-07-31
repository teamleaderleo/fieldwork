# Current-main receipt coverage blocker

Date: 2026-07-31  
Canonical campaign: Fieldwork #83  
Owned Codex base: `f7265553ea1510304f3091833dcbce65ef21f10c`  
Owned source PR: `teamleaderleo/codex#120`  
Exact source head: `a7f1d4c3bb7681037c0231a3b8156c70b9fb99bf`

## Accepted bounded seam

PR #120 is one commit and exactly five product files over the stated base:

- `codex-rs/tools/src/tool_operation.rs`
- `codex-rs/tools/src/tool_operation_tests.rs`
- `codex-rs/core/src/state/tool_operation_receipts.rs`
- `codex-rs/core/src/state/tool_operation_receipts_tests.rs`
- `codex-rs/core/src/session/tool_operation.rs`

It removes compaction decision authority from the public serializable receipt DTO, keeps unsupported versions visible, moves reconciliation into a private version-aware core predicate, and exposes a lock-compatible validator for raw call/output identity plus live receipt certainty.

Compaction behavior remains unchanged.

## Exact execution

Publisher PR #114 at `848995dd15f5548fb0e8b32824fb185d9aab8a18` completed run `30628245506`, job `91148367702`.

Passed:

- exact two-file publisher fence;
- exact five-file generated source fence;
- pinned Rust formatting;
- five uniquely resolved DTO controls with full-name `--exact` execution;
- four uniquely resolved core controls with full-name `--exact` execution;
- complete `codex-tools` package;
- `cargo check -p codex-core --lib --locked`;
- clean source-only publication.

At the stable source head:

- V8 run `30637133629`: success;
- `fieldwork-codex-tools` run `30637133597`: success;
- repository and Rust formatting in blocking-CI run `30637133885`: success.

Independent complete-diff review `4829206168` accepted the bounded decision seam.

## Blocking-CI classification

Blocking-CI run `30637133885` failed before Bazel could build or execute the receipt source. The first deterministic package-loading error was:

```text
codex-rs/windows-sandbox-rs/BUILD.bazel: codex_rust_crate()
got unexpected keyword argument: binary_test_target_compatible_with
```

The traceback terminates in `defs.bzl`. Neither path is in PR #120's five-file source fence. The same package-loading mismatch propagated across Bazel test, clippy, release-build, and argument-comment-lint jobs on multiple platforms.

This is baseline/worktree Bazel macro drift, not receipt behavior evidence.

## Coverage blocker

`SessionState` currently initializes `ToolOperationReceipts::default()`. Resumed or replaced history is installed separately. An empty receipt owner therefore does not prove complete coverage.

An empty map can mean:

1. no relevant operation exists in the covered history;
2. receipt state was never restored for existing history.

The current validator cannot safely distinguish these cases.

## Required next controls

Before any compaction caller uses the validator:

- fresh empty history must explicitly establish complete live coverage;
- resumed history containing call/output items without restored receipt state must fail closed;
- structurally valid call/output pairs without a corresponding receipt must fail closed;
- replaced and forked history with absent or partial receipt coverage must fail closed;
- a durable coverage epoch or checkpoint must identify the exact history interval represented by the owner;
- unsupported versions and coverage loss must remain fail-closed after restoration;
- validation and replacement must occur under the same session-state lock;
- rollback reconstruction must remove only receipt evidence owned by the removed segment.

## Sequence correction

The next implementation order is:

1. define explicit coverage state and fresh-history activation;
2. persist versioned receipt updates and bounded coverage checkpoints;
3. restore coverage through resume, fork, rollback, and compaction;
4. migrate Code Mode to source-qualified logical identity;
5. enable all six compaction request/install gates;
6. apply the same certainty contract to continuation and retry.

No merge, deployment, credentials, production mutation, or public upstream interaction is authorized.
