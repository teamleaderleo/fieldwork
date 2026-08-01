# Deep dive — Unit 02: make relocatable launchers compatible with BusyBox `realpath`

## Final technical conclusion

`READY FOR LAST-MILE LOOK`

uv's relocatable launchers should call delimiter-free `realpath` and `dirname`. BusyBox treats `--` as a pathname and emits `realpath: --: No such file or directory`, even while resolving the real launcher and completing successfully.

The final source also preserves recognition of the historical delimiter-bearing shebang in `copy_entrypoint`. Existing generated launchers can persist after a uv upgrade; accepting both forms prevents a migration regression.

## Governing invariant

A relocatable launcher must resolve the launcher target before selecting its sibling interpreter, execute successfully across supported invocation forms, keep stderr clean on success, and remain recognizable across the generation transition introduced by this fix.

## Exact source identity

- Public base/current main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Clean source tree: `fdcbe687e0afaaf499e5098b3308525e03000526`
- Complete compare: [`79bbface...c42973e`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c42973ef0490c75df1c7e7f4e9a54d46c6bca059)
- Relationship: one commit ahead, zero behind
- Exact file fence: wheel.rs, virtualenv.rs, project/run.rs

## Source ownership

| Area | Exact source | Responsibility |
| --- | --- | --- |
| Wheel launcher | [`wheel.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv-install-wheel/src/wheel.rs) | Generates relocatable wheel shebang and owns exact assertion |
| Activation generation | [`virtualenv.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv-virtualenv/src/virtualenv.rs) | Generates POSIX and fish relocatable activation paths |
| Project-run recognition | [`run.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv/src/commands/project/run.rs) | Accepts corrected and historical relocatable shebangs, rewrites interpreter, tests both forms |

## Failure model

1. Earlier uv emits `realpath -- "$0"` into a persistent shell launcher.
2. BusyBox `realpath` interprets `--` as a pathname.
3. BusyBox reports the nonexistent `--` pathname, then resolves `$0`.
4. Nested `dirname` selects the launcher directory.
5. The launcher executes the sibling Python with status 0 and a misleading stderr line.

The corrected generated form removes the unsupported delimiter while retaining command order, quoting, symlink canonicalization, interpreter selection, and arguments.

## Persistence and migration

Generated launchers and activation files survive after the uv process exits. Updating uv changes future generated text while older files retain the historical form.

`copy_entrypoint` previously matched one exact relocatable shebang. The final source defines:

- `RELOCATABLE_SHEBANG` for corrected generation;
- `LEGACY_RELOCATABLE_SHEBANG` for persisted earlier generation.

Both feed the same rewrite path. The direct unit test verifies both forms produce the new interpreter shebang, retain the body, and preserve mode.

## Platform characterization

Final workflow `30690034279` executed the same six invocation forms for current and corrected launchers:

- absolute;
- relative;
- PATH;
- spaces;
- `./-tool`;
- external symlink.

Results:

- GNU: current 6/6 clean, corrected 6/6 clean;
- Alpine 3.22 BusyBox: current 6/6 success with expected diagnostic, corrected 6/6 clean;
- macOS 15: current 6/6 successful, corrected 6/6 clean.

The external-symlink case confirms preservation of the symlink-first behavior introduced by upstream PR #8079.

## Option-like `$0` analysis

A synthetic shell command can set `$0=-tool`; delimiter-free GNU `realpath "$0"` then parses an option and fails. The generated launcher enters through an operating-system shebang, so the relevant question is whether direct script execution exposes that synthetic value.

Linux and macOS probes forced process argv0 to `-tool`, `--help`, and `plain-name`. Shell `$0` was the actual script pathname in every case. The supported `./-tool` invocation also passed across all three matrix environments.

Conclusion: no shell normalization branch is needed for the supported direct launcher path. Reopen only with a supported invocation that delivers a bare option-like shell `$0`.

## macOS path identity finding

macOS canonicalizes temporary paths from `/var/...` to `/private/var/...`. The first assertion compared lexical and canonical paths and failed after successful candidate execution. The harness changed its expected fake-Python path to the `realpath` result; the complete matrix then passed.

This finding belongs to the test harness, not product source.

## Compatibility analysis

- Public API: unchanged.
- Generated format: corrected shebang and activation text for newly generated files.
- Migration: historical relocatable shebang remains accepted by project-run copying.
- Symlink behavior: retained.
- Quoting and spaces: executed.
- Leading-hyphen pathname: executed as `./-tool`.
- Performance: same runtime utility nesting and command count in generated launchers.
- Rollback: revert `c42973e` to restore earlier generation and single-form recognition.

## Evidence limits

Optional future coverage:

- FreeBSD or another BSD-family runtime;
- complete repository suite;
- full clippy;
- integration-level placement of the `copy_entrypoint` regression.

These are reviewer choices. GNU, BusyBox, and macOS cover the concrete compatibility question that drove the unit.

## Reversing evidence

Reopen technical work if:

- a supported platform rejects the corrected launcher;
- a supported direct entry path supplies option-like shell `$0`;
- human review rejects historical-form recognition;
- upstream changes the three owners before submission;
- broader target tests expose a related failure.

## Excluded adjacent work

- rewriting already-generated launchers in place;
- cross-crate launcher-text centralization;
- replacing `realpath` with another utility;
- runtime BusyBox detection;
- general shell-wrapper redesign;
- non-relocatable shebang changes.

## Final execution identity

- Closed carrier PR: [`teamleaderleo/uv#7`](https://github.com/teamleaderleo/uv/pull/7)
- Carrier head: `6fbdf4d7fb0ff577f5be24972b1a5bba73111793`
- Workflow: [`30690034279`](https://github.com/teamleaderleo/uv/actions/runs/30690034279)
- Linux/source job: `91342987834`
- macOS job: `91342987814`
- publication job: `91343684491`

The run passed exact fences, formatting, affected-crate compilation, two focused Rust tests, all three platform matrices, direct shebang probes, and clean publication.
