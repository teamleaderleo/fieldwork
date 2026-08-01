# Upstream pull-request inputs — fix: make relocatable launchers compatible with BusyBox realpath

Status: `READY FOR HUMAN LAST-MILE REVIEW AND REWRITE`  
Proposed head: `teamleaderleo/uv:upstream/02-busybox-realpath` at `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`  
Proposed base: `astral-sh/uv:main` at reviewed current head `79bbface771210df216b738e9bdc7df95e5a9e6b`  
Public interaction authorized: `no`

This file supplies verified facts and a draft outline. Astral's policy requires a human to understand the code and write the public submission in their own words.

---

## Suggested title input

`fix: make relocatable launchers compatible with BusyBox realpath`

## Verified summary inputs

- Remove unsupported `--` delimiters from relocatable wheel and virtualenv launcher utility calls.
- Preserve `realpath`-before-`dirname` symlink resolution and sibling-interpreter selection.
- Keep `copy_entrypoint` compatible with both corrected and previously generated relocatable shebangs.
- Add direct regression coverage for both recognized shebang forms.

## Problem

Relocatable launchers currently call `realpath -- "$0"`. BusyBox `realpath` treats `--` as a pathname, emits `realpath: --: No such file or directory`, then resolves the real launcher operand. Successful Alpine invocations therefore gain a misleading stderr line.

The generated text is owned by wheel entry-point generation and virtualenv activation generation. Project-run also recognizes the generated wheel shebang before rewriting its interpreter. Existing launcher files can survive uv upgrades, so the recognizer needs to accept the historical form as well as the corrected form.

## Change

1. Generate delimiter-free nested `realpath` and `dirname` calls in wheel and virtualenv owners.
2. Update the wheel exact shebang assertion.
3. Define current and historical relocatable shebang constants in project-run.
4. Match the current form first and the historical form second.
5. Test that both exact forms rewrite to the new interpreter while preserving body and executable mode.

Exact source commit: [`c42973e`](https://github.com/teamleaderleo/uv/commit/c42973ef0490c75df1c7e7f4e9a54d46c6bca059)

Exact compare: [`79bbface...c42973e`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c42973ef0490c75df1c7e7f4e9a54d46c6bca059)

Exact source files:

- `crates/uv-install-wheel/src/wheel.rs` — +2/-2;
- `crates/uv-virtualenv/src/virtualenv.rs` — +4/-4;
- `crates/uv/src/commands/project/run.rs` — +59/-7, including constants and a direct test.

The clean branch is one commit ahead and zero behind current public main. It contains no execution workflow, harness, packet, or receipt file.

## Verified tests

Final carrier: `6fbdf4d7fb0ff577f5be24972b1a5bba73111793`  
Closed execution PR: [`teamleaderleo/uv#7`](https://github.com/teamleaderleo/uv/pull/7)  
Workflow: [`30690034279`](https://github.com/teamleaderleo/uv/actions/runs/30690034279)

Passed:

```text
cargo fmt --all --check
cargo check -p uv-install-wheel -p uv-virtualenv -p uv
cargo test -p uv-install-wheel test_shebang
cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs
```

Platform matrices:

- Ubuntu GNU: 12/12;
- Alpine 3.22 BusyBox: 12/12;
- macOS 15: 12/12.

Each matrix covers current and corrected forms across absolute, relative, PATH, spaces, `./-tool`, and external-symlink invocation.

Direct shebang probes on Linux and macOS forced caller argv0 values `-tool`, `--help`, and `plain-name`. Shell `$0` was the script path in every case, closing the option-like `$0` concern for direct launcher execution.

Artifacts:

- Linux/source: `8815417615`, `sha256:6a2f205d91e2a70021cc16c8d6b4a30ee2f983a90344a88f5e9d9206d1d9dd8d`;
- macOS: `8815330073`, `sha256:9f9a50fe67a2df015a17f79303f340512a35da28a0841e9ba6e9377ff0dc8b8c`;
- publication: `8815424130`, `sha256:f33ce4b084c7a37dcb7cc6bacc4b2f00f8e82200294afda491d77cac2327f3d8`.

## Compatibility inputs

- Public API: unchanged.
- Symlink behavior: preserved and executed.
- Spaces, relative paths, PATH lookup, and `./-tool`: executed.
- Newly generated launcher text: delimiter-free.
- Persisted earlier launcher text: still recognized by project-run copying.
- Performance: same runtime utility nesting and command count.
- Migration: regeneration is unnecessary for project-run recognition.
- Rollback: revert `c42973e`.

## Alternatives considered

- BusyBox runtime detection adds shell branching with no executed benefit.
- stderr redirection hides genuine resolution failures.
- `readlink -f` changes the chosen utility and portability contract.
- shell normalization for bare option-like `$0` targets a synthetic condition absent from direct shebang execution on Linux and macOS.
- cross-crate launcher centralization is a broader follow-up.
- an integration test may replace or supplement the direct unit test if maintainers prefer.

## Related work

- [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209)
- [`astral-sh/uv#8058`](https://github.com/astral-sh/uv/issues/8058)
- [`astral-sh/uv#8079`](https://github.com/astral-sh/uv/pull/8079)

## Human last-mile checklist

- [x] Exact source branch and commit recorded.
- [x] One commit directly on current public main.
- [x] Exactly three source files.
- [x] Historical and corrected recognizer test passes.
- [x] GNU, BusyBox, and macOS platform evidence passes.
- [x] Direct shebang `$0` question tested on Linux and macOS.
- [x] Existing issue selected; duplicate issue avoided.
- [x] Public upstream remained untouched.
- [ ] Human independently reviews every changed line.
- [ ] Human decides whether the direct test placement is acceptable.
- [ ] Human decides whether full clippy or complete suite is desired.
- [ ] Human rewrites title/body in their own voice.
- [ ] Explicit authorization to contact public upstream is recorded.

No public issue comment, reaction, assignment, branch, or pull request was created in `astral-sh/uv`.
