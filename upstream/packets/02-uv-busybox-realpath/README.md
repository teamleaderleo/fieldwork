# Unit 02 — uv BusyBox `realpath` compatibility

## Current disposition

`REPAIR IN PROGRESS — python3 relocatable-shebang recognition gap found during last-mile examination`

Do not review or submit the previously published source head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`. Its delimiter-removal behavior and recorded platform results remain valid, but its project-run recognizer covers corrected and historical `/'python'` launchers only.

A production-path trace established that an existing relocatable environment can generate the corresponding `/'python3'` form:

1. Unix environment discovery prefers `bin/python3` over `bin/python`;
2. environment discovery intentionally preserves the invoked executable spelling in `sys.executable`;
3. interpreter layout forwards that value to wheel installation;
4. a relocatable install embeds the relative executable in the generated launcher;
5. project-run later uses an exact shebang recognizer when copying entrypoints into an overlay environment.

The active repair recognizes four exact forms: corrected and historical launchers for both `python` and `python3`. The direct `copy_entrypoint` regression test executes all four forms and verifies rewritten content and executable-mode preservation.

## Active identity

- Routing issue: `teamleaderleo/fieldwork#435`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Target repository: `astral-sh/uv`
- Fork repository: `teamleaderleo/uv`
- Clean source branch to be republished: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Public source base and current public main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Superseded clean source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Active execution carrier head: `de209ed2adfb20ffdd49884a202b876406a71ee7`
- Active execution PR: `teamleaderleo/uv#7` — execution machinery only
- Active workflow: `30691495703`
- Public upstream contact authorized: `no`

## Source boundary under validation

The clean source remains bounded to exactly three files:

| File | Responsibility |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate delimiter-free relocatable wheel launchers and update the exact shebang assertion |
| `crates/uv-virtualenv/src/virtualenv.rs` | Generate delimiter-free POSIX and fish relocatable activation paths |
| `crates/uv/src/commands/project/run.rs` | Recognize current/historical × python/python3 relocatable shebangs and test all four forms |

No workflow, packet, publisher, or harness file belongs in the clean source commit.

## Gates being rerun

- exact execution-carrier ancestry and path fence;
- exact three-source-file candidate and publication fences;
- `git diff --check`;
- `cargo fmt --all --check`;
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
- `cargo test -p uv-install-wheel test_shebang`;
- `cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs` with all four exact forms;
- GNU launcher matrix;
- Alpine 3.22 BusyBox launcher matrix;
- macOS 15 launcher matrix;
- Linux and macOS direct-shebang `$0` probes;
- one source-only commit directly on the exact public base.

## Superseded receipt retained

The previous run `30690034279` remains useful evidence for the delimiter-free launcher behavior itself:

- Linux/source job `91342987834` passed formatting, affected-crate compilation, wheel shebang test, the earlier two-form recognizer test, GNU and BusyBox matrices, and direct-shebang probes;
- macOS job `91342987814` passed the six-case current/candidate launcher matrix and direct-shebang probes;
- publication job `91343684491` created source head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059` and tree `fdcbe687e0afaaf499e5098b3308525e03000526`;
- artifacts `8815417615`, `8815330073`, and `8815424130` retain the exact receipts.

That source head is superseded only because the recognizer migration set was incomplete for `python3`; it should not be reviewed as the final proposal.

## Packet contents

- `DEEP_DIVE.md` — ownership, failure model, compatibility reasoning, and claim limits
- `APPROACHES.md` — selected correction, alternatives, and decision history
- `TESTS.md` — exact commands, revisions, failures, and retained receipts
- `UPSTREAM_ISSUE.md` — existing-issue assessment
- `UPSTREAM_PR.md` — internal PR inputs; not public-ready text
- `REVIEW.md` — review guide and disposition record

These files still contain the prior green receipt and will be advanced to the new exact source head only after workflow `30691495703` reaches a terminal result.

## Continuation order

1. Wait for the active focused workflow to finish.
2. On green, record the exact new source commit, tree, diff, job IDs, and artifact digests.
3. Update every packet document and the canonical #435 handoff to the new exact head.
4. Close execution PR #7 without merge.
5. Return to `READY FOR LAST-MILE LOOK` only after the republished branch is one source-only commit over the current public base.

No public upstream issue comment, reaction, assignment, branch, or pull request was created.
