# Unit 02 — uv BusyBox `realpath` compatibility

## Current disposition

`REPAIR IN PROGRESS — complete owner/test boundary and migration coverage under validation`

Do not review or submit the previously published source head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`.

Its delimiter-removal behavior and recorded platform results remain useful, but deeper review found three omissions:

1. `copy_entrypoint` recognized corrected and historical `/'python'` launchers but not the `/'python3'` forms that existing relocatable environments can generate;
2. the earlier platform matrix executed launchers but did not execute sourced activation fragments using `SCRIPT_PATH`;
3. `crates/uv/tests/python/venv.rs::verify_pyvenv_cfg_relocatable` contains the target's existing exact POSIX and fish activation expectations and must change with the generator.

## Why `python3` is part of the migration contract

A production-path trace established:

1. Unix environment discovery prefers `bin/python3` over `bin/python`;
2. discovery intentionally preserves the invoked executable spelling in `sys.executable`;
3. interpreter layout forwards that value to wheel installation;
4. a relocatable install embeds the relative executable in the generated launcher;
5. project-run later uses an exact shebang recognizer when copying entrypoints into an overlay environment.

The active source therefore recognizes four exact forms: corrected and historical launchers for both `python` and `python3`. The direct `copy_entrypoint` regression test executes all four forms and verifies rewritten content, body preservation, and executable-mode preservation.

## Exact active identity

- Routing issue: `teamleaderleo/fieldwork#435`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Target repository: `astral-sh/uv`
- Fork repository: `teamleaderleo/uv`
- Clean source branch to be republished: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Public source base and current public main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Superseded clean source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Active execution carrier head: `f1210594a77cfd3e8dc2a2e1d68b228514e862dd`
- Active execution PR: `teamleaderleo/uv#7` — execution machinery only
- Public upstream contact authorized: `no`

## Source boundary under validation

The clean proposal now correctly includes four files:

| File | Responsibility |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate delimiter-free relocatable wheel launchers and update the exact shebang assertion |
| `crates/uv-virtualenv/src/virtualenv.rs` | Generate delimiter-free POSIX and fish relocatable activation paths |
| `crates/uv/src/commands/project/run.rs` | Recognize current/historical × python/python3 relocatable shebangs and test all four forms |
| `crates/uv/tests/python/venv.rs` | Update the existing target-native assertions for generated POSIX and fish activation text |

No workflow, packet, publisher, or harness file belongs in the clean source commit.

## Active gates

- exact execution-carrier ancestry and six-file execution-only fence;
- exact four-source/test-file candidate and publication fences;
- generated source replacement count: five `realpath --` and seven `dirname --` calls;
- integration expectation replacement count: two `realpath --` and four `dirname --` calls;
- two historical `realpath --` and `dirname --` forms retained only in project-run compatibility constants;
- `git diff --check`;
- `cargo fmt --all --check`;
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
- `cargo test -p uv-install-wheel test_shebang`;
- four-form `copy_entrypoint` unit test;
- existing `venv::verify_pyvenv_cfg_relocatable` integration test;
- GNU and Alpine 3.22 BusyBox launcher matrices;
- GNU and Alpine 3.22 BusyBox sourced-Bash activation matrices;
- macOS 15 launcher and sourced-Bash activation matrices;
- Linux and macOS direct-shebang `$0` probes;
- one source-only commit directly on the exact public base.

The activation matrix covers absolute, relative, Bash PATH lookup, spaces, `./-activate`, and external-symlink sourcing. Bash rejects a bare `-activate` operand before script execution, so supported leading-hyphen sourcing supplies a path-like `SCRIPT_PATH`.

## Superseded receipt retained

Run `30690034279` remains valid evidence for delimiter-free launcher behavior:

- Linux/source job `91342987834` passed formatting, affected-crate compilation, wheel shebang testing, the earlier two-form recognizer test, GNU and BusyBox launcher matrices, and direct-shebang probes;
- macOS job `91342987814` passed the six-case launcher matrix and direct-shebang probes;
- publication job `91343684491` created source head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059` and tree `fdcbe687e0afaaf499e5098b3308525e03000526`;
- artifacts `8815417615`, `8815330073`, and `8815424130` retain the exact receipts.

That head is superseded because its migration recognizer and changed-file fence were incomplete, not because its executed delimiter-free launcher behavior failed.

## Packet contents

- `DEEP_DIVE.md` — ownership, failure model, compatibility reasoning, and claim limits
- `APPROACHES.md` — selected correction, alternatives, and decision history
- `TESTS.md` — exact commands, revisions, failures, and retained receipts
- `UPSTREAM_ISSUE.md` — existing-issue assessment
- `UPSTREAM_PR.md` — internal PR inputs; not public-ready text
- `REVIEW.md` — review guide and disposition record

The remaining packet files still contain the prior green receipt and will be advanced only after the active workflow reaches a terminal result.

## Continuation order

1. Finish the active focused workflow.
2. On green, record the exact new source commit, tree, four-file diff, job IDs, and artifact digests.
3. Update every packet document and the canonical #435 handoff to the new exact head.
4. Close execution PR #7 without merge.
5. Return to `READY FOR LAST-MILE LOOK` only after the republished branch is one source-only commit over the current public base.

No public upstream issue comment, reaction, assignment, branch, or pull request was created.
