# Deep dive — Unit 02: uv BusyBox `realpath` compatibility

## Technical conclusion

`TECHNICALLY GREEN — CLEAN SOURCE PUBLICATION PENDING`

uv should remove the unsupported option delimiter from generated `realpath` calls while preserving `realpath` itself, all `dirname --` delimiters, symlink canonicalization, and recognition of persisted launchers generated before the change.

The four-file candidate is coherent and has passed the declared Linux source, test, lint, GNU, and BusyBox gates. The canonical clean branch still points at a superseded three-file candidate and is not a valid review subject.

## Governing invariant

Anything uv generates as a relocatable launcher or activation path must:

1. resolve the real generated file when reached through an external symlink;
2. locate the sibling interpreter or environment from that canonical file;
3. succeed without false stderr on GNU and BusyBox utility implementations;
4. preserve exact migration recognition for uv-generated files that persist across upgrade;
5. keep generated owners and their native assertions synchronized.

## Root cause

The current generated launcher contains:

```sh
"$(dirname -- "$(realpath -- "$0")")"/python
```

BusyBox `realpath` does not treat `--` as an option delimiter. It treats it as an extra pathname, reports that the pathname does not exist, then continues to resolve the real operand. The launcher therefore succeeds while writing an error-looking diagnostic to stderr.

The correction is:

```sh
"$(dirname -- "$(realpath "$0")")"/python
```

Only the unsupported `realpath` delimiter is removed.

## Why `realpath` remains

Historical upstream PR #8079 changed relocatable launchers from a directory-change calculation to `realpath`-based canonicalization. That repair made an entrypoint reached through an external symlink select the interpreter beside the real launcher rather than beside the symlink.

Replacing or removing `realpath` would reopen that behavior. The external-symlink matrix passes on the candidate and is a required negative control.

## Why `dirname --` remains

The concrete failure is isolated to BusyBox `realpath`. The candidate retains all existing `dirname --` calls and executes them successfully in GNU and Alpine 3.22 BusyBox matrices. Removing more syntax than the failing utility requires would enlarge generated-text churn and migration surface without evidence.

Exact count fence:

```text
source realpath delimiters removed: 5
native expectation delimiters changed: 2
legacy realpath delimiters retained in run.rs: 2
dirname delimiters retained: wheel 2, virtualenv 4, run 4, venv test 4
```

## Migration ownership

`uv run` copies entrypoints into an overlay environment only when their shebang matches one of its accepted generated forms. Existing files survive uv upgrades, so changing future generation without recognizing old generation would silently skip prior uv-created relocatable entrypoints.

The candidate names and recognizes four exact forms:

- corrected `python`;
- corrected `python3`;
- historical delimiter-bearing `python`;
- historical delimiter-bearing `python3`.

A direct unit test runs all four through `copy_entrypoint` and verifies interpreter replacement, body preservation, and executable-mode preservation.

The boundary is intentionally exact. Although Python discovery supports arbitrary executable requests, no observed producer in this path emits versioned or alternate-interpreter basenames into this fixed generated shebang contract. Adding guessed `python3.12`, PyPy, or arbitrary-pattern recognition would broaden the migration parser without a failing producer. Reopen that boundary only with an exact generated example.

## Why not detect BusyBox at generation time

A public issue comment proposed conditioning generated text on the shell or utility implementation present during generation. That is the wrong authority for a relocatable artifact:

- the generated file can be moved to another host or container;
- generation-time `/bin/sh` need not match execution-time utilities;
- the common delimiter-free `realpath` form already passes GNU, BusyBox, and the historical macOS matrix;
- runtime branching would complicate every generated launcher and the exact migration recognizer.

The selected source emits one portable form instead.

## Leading-hyphen analysis

GNU `realpath "$0"` can parse a synthetic bare `$0=-tool` as an option. The relevant question is whether a directly executed generated shebang can receive that value.

The exact Linux probe requested process `argv[0]` values `-tool`, `--help`, and `plain-name`. In every case `/bin/sh` exposed the actual script pathname as `$0`. The ordinary `./-tool` matrix case also passed on GNU and BusyBox.

The synthetic control remains documented, but no product branch is selected for a condition the operating-system shebang path did not deliver.

## Exact candidate identity

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Validated carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Run/job: `30753911776` / `91512671857`
- Artifact: `8835628919`
- Artifact ZIP SHA-256: `1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- Candidate patch: 175 lines, four files, 89 additions, 15 deletions

Candidate blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  run.rs
f68dc858066242be1888b922262d53e22975856a  venv.rs
```

## Complete-diff review

The diff contains only:

- five narrow generated-source delimiter removals;
- two corresponding native expectation changes;
- four exact migration constants;
- replacement of one inline exact matcher with four named exact matchers;
- one private-function migration regression.

No public API, command-line behavior, dependency, lockfile, workflow, generated documentation, or unrelated source path changes.

## Overlap result

Current searches by upstream issue number, BusyBox, relocatable launcher, and `realpath` found no active equivalent pull request. Merged PR #8079 is historical semantic precedent, not an overlapping implementation.

## Evidence and limitations

Strong evidence:

- exact patch and blob identities retained;
- formatting, affected-crate compilation, three focused/native tests, and full declared clippy passed;
- GNU and BusyBox launcher plus Bash activation matrices passed;
- baseline BusyBox false diagnostic reproduced deterministically;
- direct shebang `$0` behavior bounded.

Still optional or pending:

- one-commit publication of the exact four-file tree;
- supplemental executable Fish matrix;
- macOS execution on this exact carrier;
- FreeBSD or another BSD family;
- full repository test suite.

The publication step is mechanical. Fish and macOS remain useful confidence, but the target-native fish assertion and historical macOS form already support the selected source shape.

## Stop and reopen conditions

Stop duplicate implementation if an equivalent upstream change appears. Reopen technical design if:

- a supported utility rejects delimiter-free `realpath`;
- a direct supported entry path supplies a bare option-like shell `$0`;
- an exact uv producer emits another relocatable interpreter basename;
- the queued Fish execution reverses the native expectation result;
- current upstream changes one of the four owners before authorization.

No public upstream contact occurred.