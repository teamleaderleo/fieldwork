# Deep dive — Unit 02: make relocatable launchers compatible with BusyBox `realpath`

## In simple words

uv writes relocatable shell launchers that locate themselves with `realpath`, take the containing directory with `dirname`, and execute the sibling Python interpreter. GNU coreutils accepts `--` as an option delimiter for both commands. BusyBox `realpath` treats `--` as another pathname, prints `realpath: --: No such file or directory`, then continues with the actual launcher path. The command succeeds while emitting a false-looking error.

The selected correction removes `--` from the `realpath` and `dirname` calls in every current owner of this launcher text: wheel entry-point generation, POSIX and fish activation generation, and the project-run recognizer. The candidate preserves the symlink-first canonicalization introduced by upstream PR #8079.

## Governing invariant

> A relocatable launcher must resolve the launcher target before selecting its sibling interpreter, execute successfully across supported invocation forms, and keep stderr clean on a successful invocation.

## Current behavior

- entrypoint: generated relocatable wheel shebang, relocatable activation script, or project-run copied entrypoint;
- state owner: the generator text in `uv-install-wheel` and `uv-virtualenv`, plus the recognizer in `uv::commands::project::run`;
- caller-visible result: status 0 and the intended sibling Python, with an extra BusyBox diagnostic on stderr;
- side effects: generated script content on disk;
- cleanup owner: the invoking shell and uv's ordinary file lifecycle;
- persistence or publication boundary: generated launcher and activation files survive after the uv command exits;
- failure ordering: BusyBox reports the unsupported delimiter before resolving the real operand, then the nested command substitution proceeds.

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| Wheel launcher | [`crates/uv-install-wheel/src/wheel.rs` at public base `79bbface`](https://github.com/astral-sh/uv/blob/79bbface771210df216b738e9bdc7df95e5a9e6b/crates/uv-install-wheel/src/wheel.rs#L110-L145), `format_shebang` | Generates relocatable wheel entry-point shell text and owns its unit snapshot | [`test_shebang`](https://github.com/astral-sh/uv/blob/79bbface771210df216b738e9bdc7df95e5a9e6b/crates/uv-install-wheel/src/wheel.rs#L1390-L1435) |
| Activation generation | [`crates/uv-virtualenv/src/virtualenv.rs` at public base `79bbface`](https://github.com/astral-sh/uv/blob/79bbface771210df216b738e9bdc7df95e5a9e6b/crates/uv-virtualenv/src/virtualenv.rs#L475-L505) | Generates relocatable POSIX and fish activation paths | [`crates/uv/tests/python/venv.rs`](https://github.com/astral-sh/uv/blob/79bbface771210df216b738e9bdc7df95e5a9e6b/crates/uv/tests/python/venv.rs) |
| Project-run recognizer | [`crates/uv/src/commands/project/run.rs` at public base `79bbface`](https://github.com/astral-sh/uv/blob/79bbface771210df216b738e9bdc7df95e5a9e6b/crates/uv/src/commands/project/run.rs#L2020-L2100), `copy_entrypoint` | Recognizes generated relocatable shebang text before rewriting an entrypoint | project-run integration tests under [`crates/uv/tests/project/run.rs`](https://github.com/astral-sh/uv/blob/79bbface771210df216b738e9bdc7df95e5a9e6b/crates/uv/tests/project/run.rs) |

## Reproduction or characterization

### Setup

- original executed base: `1da26a68629be6ae5fd7f924a7d49ff54763a7df`;
- current reconciled public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`;
- environments: Ubuntu 24.04 GNU coreutils and Alpine 3.22 BusyBox 1.37.0;
- fixture: generated shell launcher beside a fake `python` executable;
- invocation forms: absolute, relative, PATH lookup, spaces, `./-tool`, and external symlink;
- retained prior carrier: [`teamleaderleo/uv#3@0aad1cc`](https://github.com/teamleaderleo/uv/tree/0aad1cc1fc9aa03fc5705da44112671101e20624);
- current carrier: [`teamleaderleo/uv#5`](https://github.com/teamleaderleo/uv/pull/5).

### Baseline result

The prior focused matrix executed 24 cases. GNU remained clean. BusyBox baseline cases all completed successfully and emitted the expected `realpath: --` diagnostic.

### Candidate result

The prior candidate completed all 24 cases with status 0, the sibling fake-Python selection, argument delivery, and clean stderr. Current-head execution is recorded in `TESTS.md` and must be read as the authoritative current result once complete.

## Failure model

1. uv emits `realpath -- "$0"` into a persistent launcher.
2. BusyBox `realpath` interprets `--` as a pathname operand.
3. BusyBox reports that the `--` pathname does not exist, then resolves `$0`.
4. `dirname` receives the resolved path and the launcher successfully executes the sibling Python.
5. The caller sees success plus a diagnostic that resembles a product failure.

Steps 1–4 are directly observed in the retained matrices and public reproduction. The downstream degree of log confusion is documented by the public report and remains qualitative.

## Consequence and claim boundary

### Established

- BusyBox 1.37.0 emits the diagnostic for the current fragment.
- Removing the delimiters makes the tested BusyBox cases quiet.
- GNU behavior remains unchanged in the tested matrix.
- All three current source owners still contain the delimiter form at public base `79bbface`.
- The synchronized candidate removes five `realpath --` and seven `dirname --` occurrences.

### Inferred

- Updating only wheel generation would leave activation and project-run behavior textually inconsistent.
- Keeping generator and recognizer text synchronized avoids silently failing to recognize launchers generated by the corrected code.

### Unknown or unmeasured

- bare option-like `$0` values created through hostile or unusual process construction;
- newline-containing launcher paths;
- every BSD and macOS utility implementation;
- prevalence across production workloads;
- complete repository-wide test coverage at the current candidate head until the current CI record finishes.

## Selected implementation

The generator owners retain their existing path-resolution responsibility. The patch removes unsupported delimiters while preserving nesting, quoting, symlink resolution, executable selection, and generated text layout. The project-run recognizer changes in the same commit so it accepts the corrected generated shebang.

The change deliberately avoids introducing BusyBox detection, stderr suppression, or a new shared abstraction. Those directions widen runtime behavior and review scope without improving the executed compatibility result.

## Compatibility analysis

- public API: unchanged;
- source compatibility: internal string literals only;
- binary or wire compatibility: not applicable;
- persistence or format compatibility: generated shebang text changes; project-run recognition changes with it;
- platform behavior: tested on GNU coreutils and Alpine BusyBox; BSD/macOS remain an explicit gap;
- performance and allocation: same command count and nesting; no meaningful change expected;
- cancellation, retry, and recovery: not applicable to the generated command fragment;
- generated output: wheel shebang snapshot and activation text require synchronized expectations;
- migration or rollback: existing generated scripts retain their old text until regenerated; reverting the source commit restores prior generation.

## Adversarial and edge controls

- re-entry: immediate rerun included in the disposable matrix process model;
- concurrency: each matrix case uses an isolated temporary directory;
- interruption: trap removes temporary files on exit, HUP, INT, and TERM;
- failure before ownership transfer: status and stderr are captured before assertions;
- failure after partial effect: generated files remain confined to the temporary directory;
- cleanup failure: unmeasured beyond shell trap execution;
- same-resource collision: unique `mktemp` root;
- unrelated-resource isolation: exact changed-path fences in both prior and current carriers;
- platform boundary: GNU and BusyBox only.

## Review risks

1. **Option-like `$0`** — the executed leading-hyphen case reaches the launcher as `./-tool`; a bare `-tool` process argument remains outside the evidence.
2. **Recognizer drift** — controlled by changing `run.rs` with the two generators.
3. **Symlink regression** — controlled by the external-symlink matrix case and preserved `realpath`-before-`dirname` order.
4. **Platform regression** — GNU control passed; macOS/BSD execution remains the strongest missing platform control.
5. **Overbroad replacement** — exact per-file counts and exact changed-file fences stop unreviewed replacements.

## Reversing evidence

Reopen the conclusion if:

- a supported invocation produces a bare option-like `$0` and the candidate misparses it;
- macOS or BSD `realpath`/`dirname` behavior fails with the corrected fragment;
- current upstream replaces these generators or publishes an equivalent correction;
- project-run recognizes a broader contract that requires accepting both old and new shebang forms indefinitely.

## Adjacent work excluded

- centralizing all launcher fragments;
- replacing `realpath` with `readlink -f` or shell-only canonicalization;
- general shell-wrapper redesign;
- changing non-relocatable shebang handling;
- adding runtime BusyBox detection;
- rewriting already-generated launchers in place.
