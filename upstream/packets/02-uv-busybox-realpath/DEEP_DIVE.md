# Deep dive — Unit 02

## Technical conclusion

The compatibility defect is specific to BusyBox `realpath`, not BusyBox `dirname`.

BusyBox `realpath` treats `--` as another pathname. A generated launcher therefore succeeds but emits `realpath: --: No such file or directory`. BusyBox `dirname` uses `single_argv`, whose implementation removes an optional `--` before validating its one operand.

The selected generated form is:

```sh
"$(dirname -- "$(realpath "$0")")"
```

For activation, the same rule applies: remove `--` only from `realpath`; preserve nested `dirname --` calls.

## Ownership and migration

Wheel generation and virtualenv activation generation own the emitted text. Project-run owns an exact recognizer used when copying an entrypoint into an overlay environment.

Unix environment discovery prefers `bin/python3` and preserves the invoked executable spelling in `sys.executable`. Wheel installation receives that path, so persisted relocatable launchers may use either `python` or `python3`.

The recognizer accepts exactly four forms:

1. corrected `python`;
2. corrected `python3`;
3. historical `realpath --` + `python`;
4. historical `realpath --` + `python3`.

The absolute-shebang fallback is unchanged.

## Invariants retained

- Resolve the launcher before selecting its sibling interpreter.
- Preserve symlink-first behavior.
- Preserve quoting, spaces, arguments, relative/PATH invocation, and executable mode.
- Keep success stderr clean on BusyBox.
- Keep old generated launchers copyable after uv upgrades.
- Preserve every supported `dirname --` delimiter.

## Exact source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Diff: four files, 89 insertions, 15 deletions

The diff contains only five generated-source `realpath --` removals, two matching native expectation changes, four exact migration constants, replacement of one inline matcher with four named exact matchers, and one private-function regression test.

## Evidence

The exact source passed formatting, affected-crate compilation, three focused/native tests, the full declared workspace clippy gate, GNU launcher and Bash activation matrices, Alpine 3.22 BusyBox launcher and Bash activation matrices, and the Linux direct-shebang `$0` discriminator.

The BusyBox baseline reproduced the false diagnostic in every matrix case. The candidate selected the correct canonical interpreter/environment and kept stderr empty.

## Evidence limits

The exact final source was not rerun on macOS because the hosted macOS job remained queued and was canceled when publication advanced. Earlier macOS 15 evidence passed the broader delimiter-removal form; the final source restores supported `dirname --`, but that is not described as an exact final-carrier result.

Executable Fish validation remains supplemental. uv's existing Fish generated-text integration assertion passed on the exact final source.

No public upstream contact occurred.