# Deep dive — Unit 02

## Technical conclusion

The compatibility defect is specific to BusyBox `realpath`, not BusyBox `dirname`.

BusyBox `realpath` treats `--` as another pathname. A generated launcher therefore succeeds but emits `realpath: --: No such file or directory`. BusyBox `dirname` removes an optional `--` before validating its single operand.

The selected generated form is:

```sh
"$(dirname -- "$(realpath "$0")")"
```

For POSIX and Fish activation, the same rule applies: remove `--` only from `realpath`; preserve nested `dirname --` calls.

## Why unconditional generation is correct

A maintainer-side suggestion on the public issue proposed detecting BusyBox and post-processing the launcher as an edge case. That approach binds generated text to the generation host.

Relocatable artifacts can move between hosts. A virtual environment generated under GNU userland may later execute under BusyBox, or the reverse. The selected fragment is accepted by GNU, BusyBox, and macOS, so unconditional portable generation avoids a host-flavour branch and produces one stable artifact format.

## Historical constraint

`realpath` itself must remain. Upstream added canonicalization to preserve externally symlinked relocatable entrypoints. Removing `realpath`, replacing it casually with another utility, or deriving the interpreter from the symlink location would reintroduce that class of bug.

The patch therefore changes the unsupported delimiter, not the resolution algorithm.

## Ownership and migration

Wheel generation and virtualenv activation generation own emitted text. Project-run owns an exact recognizer used when copying an entrypoint into an overlay environment.

Unix environment discovery may preserve `python` or `python3` as the executable spelling. Persisted relocatable launchers can therefore contain either basename.

The recognizer accepts exactly four forms:

1. corrected `python`;
2. corrected `python3`;
3. historical `realpath --` + `python`;
4. historical `realpath --` + `python3`.

The absolute-shebang fallback is unchanged. The narrow four-form grammar protects migrations without turning the recognizer into a general shell parser.

## Invariants retained

- Resolve the real launcher before selecting its sibling interpreter.
- Preserve external-symlink behavior.
- Preserve quoting, spaces, arguments, relative/PATH invocation, and executable mode.
- Keep success stderr clean on BusyBox.
- Keep old generated launchers copyable after uv upgrades.
- Preserve every supported `dirname --` delimiter.
- Generate one portable artifact independent of the generation host.

## Exact source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Diff: four files, 89 insertions, 15 deletions

The source diff contains five generated-source `realpath --` removals, two matching native expectation changes, four exact migration constants, replacement of one inline matcher with four named exact matchers, and one private-function regression test.

## Evidence

The exact source passed:

- formatting and affected-crate compilation;
- three focused/native Rust tests;
- full locked workspace/all-target/all-feature clippy;
- GNU and Alpine/BusyBox launcher matrices;
- GNU, Alpine/BusyBox, and macOS Bash activation probes;
- GNU, Alpine/BusyBox, and macOS Fish activation probes;
- Linux direct-shebang `$0` discrimination;
- exact one-commit publication fences.

The BusyBox baseline reproduced the false diagnostic. The candidate selected the same canonical interpreter/environment and kept stderr empty. GNU and macOS remained clean.

## Review result

A fresh exact-diff review found no remaining source defect. The principal review choice is stylistic and architectural: whether four explicit migration strings are preferable to a broader helper. The current shape is transparent, allocation-free, bounded to observed producers, and covered by one table-style regression loop.

## Evidence limits

- The entire repository test suite was not run.
- The source remains pinned to the reviewed public base and requires current-main reconciliation before submission.
- No public upstream contact occurred.