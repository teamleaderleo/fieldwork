# Codex GitHub Actions prerequisite map and retained harness failures

Owner: Fieldwork #239 lane J/O  
Canonical finding: `findings/F239-codex-upstream-convergence/finding.md`  
Exact public source inspected: `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Evidence class: `source-read` plus named carrier execution receipts  
Upstream contact authorized: `no`

## In simple words

Running Codex's real repository commands requires more than installing Rust.

The repository-owned `setup-ci` action installs shared build-path configuration, DotSlash, and `just`. It does not install `uv` or `cargo-nextest`. Full `just fmt` and `just fmt-check` run Python formatters through `uv`, while `just test` runs `cargo nextest`.

A carrier that omits one of those tools can reconstruct the candidate correctly and still fail before any Codex test begins. That failure describes the carrier environment, not the product behavior.

## Current upstream setup contract

At `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`:

| Source | Current behavior | Consequence for owned carriers |
| --- | --- | --- |
| `.github/actions/setup-ci/action.yml` | configures CI build paths; installs DotSlash and `just@1.51.0` | use it when repository entrypoints require `just` or DotSlash; do not treat it as the complete toolchain |
| `.github/workflows/repo-checks.yml` | installs `uv` separately with `astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b`, version `0.11.3`, before `just fmt-check` | install the same pinned runner before full repository formatting |
| root `justfile` | `fmt` and `fmt-check` call `scripts/format.py`; `test` calls `cargo nextest` with the repository stack/profile settings | install `cargo-nextest` when selected setup does not supply it |
| `scripts/format.py` | runs Just, Rust, Bazel/Starlark, Python SDK, and Python script formatter groups; both Python groups invoke `uv run` | missing `uv` can fail formatting even when the changed source is Rust-only |

The exact upstream revision is part of this contract. A later change to these files requires a setup refresh rather than copying this pin indefinitely.

## Retained failure sequence

### Missing `just`

Owned Codex PR #53 run `30579942527`:

- source reconstruction passed;
- exact four-file source fence passed;
- formatting stopped with exit `127` because `just` was absent;
- no terminal behavior test ran.

Repair: invoke repository-owned `./.github/actions/setup-ci`.

Evidence class: `carrier-executed`; zero target behavior evidence.

### Missing `uv`

Owned Codex PR #53 run `30582012412`, job `91004310038`:

- current source reconstruction passed;
- the carrier reached repository-wide formatting;
- Python SDK and Python scripts formatter groups failed with `No such file or directory: 'uv'`;
- every terminal test and source publication step was skipped.

Repair: install current upstream's pinned `astral-sh/setup-uv` action and `uv` version before `just fmt`.

Evidence class: `carrier-executed`; zero target behavior evidence.

### Missing `cargo-nextest` risk

The reviewed terminal carrier explicitly installs `cargo-nextest` because `setup-ci` does not. The root `just test` recipe invokes `cargo nextest`; an environment that omits it cannot supply an exact repository-entrypoint test result.

### Generator drift after prerequisites pass

Owned Codex PR #79 run `30584093534`, job `91011250342`:

- checkout and Rust setup passed;
- candidate generation stopped because `let turn_context = &step_context.turn;` had two current-source matches;
- formatting and tests never ran.

Repair head: `40ad25450b9b1296906b66126b710ea877dc7e82`, anchoring the edit to the `handle_mcp_tool_call` argument-parse boundary.

This is separate from tool installation but follows the same evidence rule: a source generator or harness failure is not product evidence.

## Successful controls after environment repair

### Terminal retention

Fieldwork PR #268 run `30587866332` passed on exact carrier head `58c0d027e2acf80fb9e16d89d0daba65de0dc563`:

- current source reconstruction and repository formatting;
- exact four-file source fence;
- nine unique terminal/deque controls;
- full `codex-core` library execution;
- compile-only integration-target coverage;
- retained source artifacts for source-only materialization.

This is target execution for the bounded terminal claim. Fieldwork integrity remained a separate queued repository gate at the retrieval snapshot.

### Append acknowledgement

Owned Codex PR #80 run `30583967538` passed at exact carrier head `401c2e5e6a37730aae3e8da95591cc6f56655cfc`. The candidate still requires source-only successor review and current-head drift comparison before promotion.

### MCP publication

Owned Codex PR #77 run `30584055792` passed at exact carrier head `0fb2e6b09a6ff03bcfcbd665b187cadb64d36b4b`. The current source candidate and publication semantics remain separately reviewable.

## Required carrier checklist

Before a Codex GitHub Actions carrier runs a repository entrypoint:

1. pin the exact public Codex source revision;
2. inspect that revision's workflow and entrypoint files;
3. use `./.github/actions/setup-ci` when the carrier needs repository CI build paths, DotSlash, or `just`;
4. install the exact current `uv` action/version before `just fmt` or `just fmt-check`;
5. install `cargo-nextest` before `just test` when it is not otherwise present;
6. install the declared Rust toolchain and required components;
7. install Node/pnpm or other tools only when the selected repository command requires them;
8. run exact source-head and changed-file-fence checks before behavior tests;
9. resolve exact test names and require nonzero unique matches;
10. classify every setup, generation, formatting, fetch, or dependency failure as carrier evidence only;
11. preserve the failure receipt and repair the harness before changing product semantics or weakening the gate.

## Current public drift

Public Codex moved from the canonical finding's prior pin `3016671bb077c43448b8fa88f3edfa9772e17058` to `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa` through one commit.

That commit changes:

- `codex-rs/protocol/src/permissions.rs`;
- `codex-rs/sandboxing/src/policy_transforms.rs`;
- `codex-rs/sandboxing/src/policy_transforms_tests.rs`.

It does not overlap the active append, terminal, MCP runtime/call, deferred-tool, Responses Lite, receipt-wire, replay, or typed-identity source fences. Existing candidate classifications carry forward for those declared fences. Permission and sandbox findings require their own review.

## Recommendation

Treat the target map as the first durable reminder and this file as the exact evidence record. Do not duplicate a fixed `uv` version across generic Fieldwork templates. The target's current workflows remain the authority; Fieldwork records the rule to inspect and mirror them.