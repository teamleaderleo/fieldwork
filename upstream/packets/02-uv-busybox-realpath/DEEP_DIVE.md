# Deep dive — Unit 02: make relocatable launchers compatible with BusyBox `realpath`

## In simple words

uv writes relocatable shell launchers that locate themselves with `realpath`, take the containing directory with `dirname`, and execute the sibling Python interpreter. GNU coreutils accepts `--` as an option delimiter for both commands. BusyBox `realpath` treats `--` as another pathname, prints `realpath: --: No such file or directory`, then continues with the actual launcher path. The launcher succeeds while emitting a misleading diagnostic.

The selected correction removes `--` from the `realpath` and `dirname` calls in every current owner of this launcher text: wheel entry-point generation, POSIX and fish activation generation, and the project-run recognizer. The source preserves the symlink-first canonicalization introduced by upstream PR #8079.

## Governing invariant

> A relocatable launcher must resolve the launcher target before selecting its sibling interpreter, execute successfully across supported invocation forms, and keep stderr clean on a successful invocation.

## Exact source identity

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source head: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`
- Clean source tree: `63c644c8bba5a5cb3376401f64bd1ce561aa674e`
- Complete compare: [`79bbface...c43b126`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c43b1262be71d9fc0b60ca613700ef7ae60bf69d)
- Relationship: one commit ahead, zero behind
- Exact file fence: wheel.rs, virtualenv.rs, project/run.rs
- Exact replacement fence: five `realpath --`, seven `dirname --`

## Current behavior

- entrypoint: generated relocatable wheel shebang, relocatable activation script, or project-run copied entrypoint;
- state owner: generator text in `uv-install-wheel` and `uv-virtualenv`, plus the recognizer in `uv::commands::project::run`;
- caller-visible result before the fix: status 0 and the intended sibling Python, with an extra BusyBox diagnostic on stderr;
- side effects: generated script content on disk;
- cleanup owner: the invoking shell and uv's ordinary file lifecycle;
- persistence boundary: generated launcher and activation files survive after the uv command exits;
- failure ordering: BusyBox reports the unsupported delimiter before resolving the real operand, then the nested command substitution proceeds.

## Source map

| Area | Exact corrected source | Responsibility | Relevant test |
| --- | --- | --- | --- |
| Wheel launcher | [`wheel.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv-install-wheel/src/wheel.rs) | Generates relocatable wheel entry-point shell text and owns its exact assertion | `test_shebang` in the same file |
| Activation generation | [`virtualenv.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv-virtualenv/src/virtualenv.rs) | Generates relocatable POSIX and fish activation paths | focused compile plus external behavior matrix |
| Project-run recognizer | [`run.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv/src/commands/project/run.rs) | Recognizes corrected relocatable shebang text before rewriting an entrypoint | focused compile and exact source fence |

## Reproduction and final characterization

### Environments

- Ubuntu 24.04 GNU coreutils;
- Alpine 3.22 BusyBox 1.37.0;
- generated shell launcher beside a fake `python` executable;
- invocation forms: absolute, relative, PATH lookup, spaces, `./-tool`, and external symlink.

### Baseline result

The current fragment completed every controlled invocation. GNU remained quiet. BusyBox completed every invocation while emitting `realpath: --`.

### Candidate result

The corrected fragment completed every controlled invocation on GNU and BusyBox with:

- status 0;
- sibling fake-Python selection;
- argument delivery;
- clean stderr;
- preserved external-symlink behavior.

The final current-head workflow executed 24 matrix cases total: 12 GNU and 12 Alpine BusyBox.

## Final execution identity

- Execution-only base: `d2ebfd92457b0047a4b02e3ccb8431769e12b145`
- Execution carrier: `9c1465a8beff5e44053756523a053dbc64abc047`
- Closed carrier PR: [`teamleaderleo/uv#6`](https://github.com/teamleaderleo/uv/pull/6)
- Workflow/job: [`30676914631`](https://github.com/teamleaderleo/uv/actions/runs/30676914631) / `91305994591`
- Artifact: `8810846105`
- Artifact digest: `sha256:88af531d65679b1a756541d598c8c8fc85d250dd03ee32b58ede2d8a883ad45c`

The run passed exact carrier and source fences, `git diff --check`, rustfmt, affected-crate compilation, the native shebang test, both matrices, result-marker checks, alternate-index source construction, and exact source publication.

## Failure model

1. uv emits `realpath -- "$0"` into a persistent launcher.
2. BusyBox `realpath` interprets `--` as a pathname operand.
3. BusyBox reports that the `--` pathname does not exist, then resolves `$0`.
4. `dirname` receives the resolved path and the launcher executes the sibling Python.
5. The caller sees success plus a diagnostic that resembles a product failure.

Steps 1–4 are directly observed in the retained matrices and public reproduction. The downstream degree of log confusion remains qualitative.

## Consequence and claim boundary

### Established

- BusyBox 1.37.0 emits the diagnostic for the public-base fragment.
- Removing the delimiters makes the tested BusyBox cases quiet.
- GNU behavior remains unchanged in the tested matrix.
- All three source owners were synchronized in one commit.
- The final source changes exactly three files.
- Rustfmt requires the corrected virtualenv match arm to use a braced form.
- The affected crates compile and the native shebang assertion passes.

### Inferred

- Updating only wheel generation would leave activation and project-run behavior textually inconsistent.
- Keeping generator and recognizer text synchronized avoids silently failing to recognize launchers generated by the corrected code.
- Runtime BusyBox detection adds complexity without improving the executed result.

### Unknown or unmeasured

- bare option-like `$0` values created through unusual process construction;
- newline-containing launcher paths;
- native BSD and macOS utility implementations;
- prevalence across production workloads;
- complete repository-wide test coverage;
- whether project-run should permanently recognize both historical and corrected forms.

## Selected implementation

The existing owners retain path-resolution responsibility. The patch removes unsupported delimiters while preserving nesting, quoting, symlink resolution, executable selection, and generated text intent. The project-run recognizer changes in the same commit so it accepts the corrected generated shebang.

The virtualenv source uses rustfmt's braced match arm. This is the only line-layout expansion beyond direct delimiter removal.

The change avoids BusyBox detection, stderr suppression, utility replacement, and a new shared abstraction. Those directions widen runtime behavior and review scope.

## Compatibility analysis

- public API: unchanged;
- source compatibility: internal string literals only;
- binary or wire compatibility: none;
- persistence or format compatibility: generated shebang and activation text changes; project-run recognition changes with it;
- platform behavior: GNU and Alpine BusyBox executed; BSD/macOS remain an explicit gap;
- performance and allocation: same command count and nesting;
- cancellation, retry, and recovery: outside this generated command fragment;
- generated output: wheel shebang assertion and activation text are synchronized;
- migration: existing generated scripts retain old text until regenerated;
- rollback: reverting `c43b126` restores prior generation.

## Adversarial and edge controls

- re-entry: repeated prior and current focused runs;
- concurrency: each matrix execution uses an isolated temporary directory;
- interruption: trap removes temporary files on EXIT, HUP, INT, and TERM;
- failure before assertions: status, stdout, and stderr are captured first;
- partial effects: generated fixtures remain confined to the temporary directory;
- same-resource collision: unique `mktemp` root;
- unrelated-resource isolation: exact changed-path fences and alternate-index source publication;
- platform boundary: GNU and BusyBox only.

## Review risks

1. **Option-like `$0`** — the executed leading-hyphen case reaches the launcher as `./-tool`; a bare `-tool` process argument remains outside the evidence.
2. **Recognizer compatibility** — a human should decide whether project-run must accept historical and corrected forms.
3. **Symlink regression** — controlled by the external-symlink matrix and preserved `realpath`-before-`dirname` order.
4. **Platform regression** — GNU passed; macOS/BSD execution remains the strongest missing platform control.
5. **Overbroad replacement** — exact per-file counts, changed-file fences, and one source-only commit control this risk.
6. **Policy ownership** — Astral requires independent human understanding and human-authored public communication.

## Reversing evidence

Reopen the conclusion if:

- a supported invocation produces a bare option-like `$0` and the candidate misparses it;
- macOS or BSD `realpath`/`dirname` fails with the corrected fragment;
- current upstream replaces these generators or lands an equivalent correction;
- project-run has a compatibility contract requiring both forms;
- human review finds a source ownership or test error.

## Adjacent work excluded

- centralizing all launcher fragments;
- replacing `realpath` with `readlink -f` or shell-only canonicalization;
- general shell-wrapper redesign;
- changing non-relocatable shebang handling;
- adding runtime BusyBox detection;
- rewriting already-generated launchers in place;
- complete project suite expansion without reviewer direction.
