# Upstream pull-request draft — fix: make relocatable launchers compatible with BusyBox realpath

Draft status: `not ready — current-head receipt and human review required`  
Proposed head: `teamleaderleo/uv:upstream/02-busybox-realpath`  
Proposed base: `astral-sh/uv:main` at packet-recorded exact base  
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

Exact expected source files:

- `crates/uv-install-wheel/src/wheel.rs`;
- `crates/uv-virtualenv/src/virtualenv.rs`;
- `crates/uv/src/commands/project/run.rs`.

Exact replacement fence: five `realpath --` and seven `dirname --` occurrences.

## Tests

- `cargo fmt --all --check`
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`
- `cargo test -p uv-install-wheel test_shebang`
- GNU current/candidate matrix: absolute, relative, PATH, spaces, `./-tool`, external symlink
- Alpine 3.22 BusyBox current/candidate matrix with the same six cases
- exact changed-path and replacement-count fences

Final exact workflow, job, source head, and artifact are recorded in `TESTS.md` and packet `README.md`.

## Compatibility

- public API: unchanged;
- existing behavior retained: symlink-first canonicalization, sibling interpreter, argument delivery, quoting, and status;
- platform notes: GNU and Alpine BusyBox executed; macOS/BSD remain the largest gap;
- performance and allocation: same utility invocations and nesting;
- migration or rollback: existing generated scripts retain their current text until regenerated; source revert restores generation.

## Alternatives considered

- BusyBox runtime detection adds shell branching to every generated launcher.
- stderr redirection hides genuine resolution failures.
- `readlink -f` changes the portability and symlink contract.
- explicit bare-leading-hyphen normalization lacks a reproduced supported invocation and widens generated text.
- a shared launcher helper is a separate maintainability refactor.

## Limits

- A bare option-like `$0` is unmeasured; the executed leading-hyphen case reaches the script as `./-tool`.
- Native macOS and BSD utility behavior has not been executed in this packet.
- This draft was prepared by an autonomous assistant and cannot be submitted as-is under Astral's AI policy. A human must understand the source, independently review it, author the public description in their own words, and obtain explicit authorization.

## Related work

- [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209)
- [`astral-sh/uv#8058`](https://github.com/astral-sh/uv/issues/8058)
- [`astral-sh/uv#8079`](https://github.com/astral-sh/uv/pull/8079)

---

## Submission checklist

- [ ] Branch exact source head matches packet `README.md`.
- [ ] Branch is one source-only commit directly on the recorded public base.
- [ ] Diff contains exactly the three source files above.
- [ ] Temporary workflows, publishers, receipts, and Fieldwork files are absent.
- [ ] Every changed file reviewed by a human at the exact head.
- [ ] Focused baseline/candidate relation verified.
- [ ] Current-head formatting, compile, native test, and matrix are green.
- [ ] macOS/BSD risk accepted or tested.
- [x] Current duplicate and overlap search completed on 2026-08-01.
- [x] Existing issue #16209 selected; duplicate issue rejected.
- [x] Contribution and AI policies checked.
- [ ] Human rewrites title/body in their own words and confirms policy compliance.
- [ ] Exact user authorization to open the public pull request recorded.
