# Tests and receipts — Unit 02

## Final public source

- Final head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`
- Changed files: four
- Diff: 207 additions, 16 deletions
- Public pull request: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)
- Final canonical CI: run `31059965759` — success

This is the runtime-capability-probe generation, not the earlier unconditional delimiter-removal candidate.

## Final behavior under test

Generated POSIX launchers selected between:

```sh
realpath -- "$0"
```

and:

```sh
realpath "$0"
```

using a runtime probe that required `realpath -- /` to succeed and return only `/`.

Equivalent capability logic was added to POSIX and Fish activation generation. `uv run` recognized current and historical relocatable launchers in both `python` and `python3` forms.

## Added target-native tests

### `uv-install-wheel`

Two Unix tests created fake `realpath` executables and put them first in `PATH`:

- `relocatable_realpath_uses_delimiter_when_supported`
- `relocatable_realpath_falls_back_for_busybox`

Together they verified:

- the compliant branch probes with `realpath -- /`;
- the compliant branch keeps `--` for the actual launcher operand;
- the BusyBox-style branch falls back without `--`;
- a bare `$0 = -foo` remains covered;
- a literal file named `--` does not create a false compatible result;
- stderr remains clean.

The macOS expectation canonicalized the temporary path to account for platform path aliases such as `/var` resolving through `/private/var`.

### `uv`

`copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs` covered the four accepted exact forms:

- current `python`;
- current `python3`;
- historical `python`;
- historical `python3`.

The runtime-probe constant import was gated with `#[cfg(unix)]` so Windows Clippy did not report an unused import.

## Final CI receipt

The final workflow run completed successfully after the macOS expectation and Windows Clippy repairs.

Visible successful coverage included:

- Rust formatting and lint;
- Linux full tests;
- Windows full tests and Clippy;
- macOS tests;
- supported build and generated-file checks;
- documentation, lockfile, release, and publish checks expected by the repository workflow.

No visible final job failed. Expected platform or configuration skips remained skips.

## Focused local evidence

Focused execution covered the affected `uv-install-wheel`, `uv-virtualenv`, and `uv` surfaces. Resolver behavior was also exercised with GNU-style and BusyBox-style `realpath` implementations.

The additional probe measured about `0.4 ms` per relocatable launcher execution in the local benchmark.

## Superseded evidence

Earlier packet receipts for head `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8` validated the unconditional delimiter-removal candidate across GNU, Alpine/BusyBox, macOS, Bash, and Fish.

Those runs remain useful characterization evidence but are not the final submitted source. Maintainer review exposed the missing bare leading-hyphen guarantee, which led to the runtime-probe revision.

## Outcome boundary

The final candidate was not rejected because of a failing test or unresolved CI job. It was retired because uv maintainers did not accept the runtime and maintenance tradeoff of probing in every affected generated launcher.

The preferred repair moved to [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26).
