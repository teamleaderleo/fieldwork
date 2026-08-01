# Upstream pull-request draft — fix: make relocatable launchers compatible with BusyBox realpath

Draft status: `source-ready; human rewrite, review, and authorization required`  
Proposed head: `teamleaderleo/uv:upstream/02-busybox-realpath` at `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`  
Proposed base: `astral-sh/uv:main` from reviewed base `79bbface771210df216b738e9bdc7df95e5a9e6b`  
Public interaction authorized: `no`

---

## Summary

- Make relocatable wheel and virtualenv launchers quiet under BusyBox `realpath`.
- Keep project-run's generated-shebang recognizer synchronized with the corrected launcher text.
- Preserve tested GNU behavior, symlink resolution, quoting, and sibling-interpreter selection.

## Problem

Relocatable launchers currently call `realpath -- "$0"`. BusyBox `realpath` treats `--` as a pathname, emits `realpath: --: No such file or directory`, then resolves the real launcher operand. The command succeeds while successful Alpine invocations gain a misleading stderr line.

The same text is owned by wheel entry-point generation, virtualenv activation generation, and project-run recognition. A partial change would leave generated and recognized forms inconsistent.

## Change

Remove `--` from the nested `realpath` and `dirname` calls in all three current owners. Preserve the existing `realpath`-before-`dirname` order introduced to support symlinked relocatable launchers. Update the wheel shebang assertion and the project-run recognizer with the generated text.

Exact source commit: [`c43b126`](https://github.com/teamleaderleo/uv/commit/c43b1262be71d9fc0b60ca613700ef7ae60bf69d)

Exact compare: [`79bbface...c43b126`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c43b1262be71d9fc0b60ca613700ef7ae60bf69d)

Exact source files:

- `crates/uv-install-wheel/src/wheel.rs` — +2/-2;
- `crates/uv-virtualenv/src/virtualenv.rs` — +4/-4, including rustfmt's braced match arm;
- `crates/uv/src/commands/project/run.rs` — +1/-1.

Exact replacement fence: five `realpath --` and seven `dirname --` occurrences.

## Tests

Final execution-only carrier: `9c1465a8beff5e44053756523a053dbc64abc047`  
Workflow/job: [`30676914631`](https://github.com/teamleaderleo/uv/actions/runs/30676914631) / `91305994591`  
Artifact: `8810846105`  
Artifact digest: `sha256:88af531d65679b1a756541d598c8c8fc85d250dd03ee32b58ede2d8a883ad45c`

Passed:

- exact carrier and source changed-path fences;
- exact replacement-count fence;
- `git diff --check`;
- `cargo fmt --all --check`;
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
- `cargo test -p uv-install-wheel test_shebang`;
- GNU current/candidate matrix: absolute, relative, PATH, spaces, `./-tool`, external symlink;
- Alpine 3.22 BusyBox current/candidate matrix with the same six cases;
- clean one-commit source publication from exact public base.

## Compatibility

- public API: unchanged;
- existing behavior retained: symlink-first canonicalization, sibling interpreter, argument delivery, quoting, and status;
- generated text: delimiter-free shebang and activation fragments; project-run recognition changes with them;
- platform evidence: GNU and Alpine BusyBox executed;
- platform limits: macOS/BSD remain unexecuted;
- performance and allocation: same utility invocations and nesting;
- migration: existing generated scripts retain their current text until regenerated;
- rollback: reverting source commit `c43b126` restores prior generation.

## Alternatives considered

- BusyBox runtime detection adds shell branching to every generated launcher.
- stderr redirection hides genuine resolution failures.
- `readlink -f` changes the portability and symlink contract.
- explicit bare-leading-hyphen normalization lacks a reproduced supported invocation and widens generated text.
- accepting both historical and corrected forms in project-run remains a maintainer judgment.
- a shared launcher helper is a separate maintainability refactor.

## Limits

- A bare option-like `$0` is unmeasured; the executed leading-hyphen case reaches the script as `./-tool`.
- Native macOS and BSD utility behavior has not been executed in this packet.
- The complete project suite and clippy were outside the focused run.
- This draft was prepared by an autonomous assistant and cannot be submitted as-is under Astral's AI policy. A human must understand the source, independently review it, and author the public description in their own words.

## Related work

- [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209)
- [`astral-sh/uv#8058`](https://github.com/astral-sh/uv/issues/8058)
- [`astral-sh/uv#8079`](https://github.com/astral-sh/uv/pull/8079)

---

## Submission checklist

- [x] Branch exact source head matches packet `README.md`.
- [x] Branch is one source-only commit directly on reviewed public base.
- [x] Diff contains exactly the three source files above.
- [x] Temporary workflows, publishers, receipts, and Fieldwork files are absent.
- [x] Focused baseline/candidate relation verified.
- [x] Current-head formatting, compile, native test, and matrices are green.
- [x] Current duplicate and overlap search completed on 2026-08-01.
- [x] Existing issue #16209 selected; duplicate issue rejected.
- [x] Contribution and AI policies checked.
- [ ] Every changed line independently reviewed by a human.
- [ ] macOS/BSD risk accepted or tested.
- [ ] Old/new project-run recognition decision accepted.
- [ ] Human rewrites title and body in their own words and confirms policy compliance.
- [ ] Exact user authorization to open the public pull request recorded.

No public issue comment, reaction, assignment, branch, or pull request was created in `astral-sh/uv`.
