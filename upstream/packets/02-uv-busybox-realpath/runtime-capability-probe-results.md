# Runtime `realpath` capability probe

Candidate base: `teamleaderleo/uv@ec33f13043de5e3a3221cdacc4bca650e1d65a09`

## Design

Generated relocatable launchers and activation scripts probe whether the installed `realpath` accepts the POSIX `--` delimiter:

```sh
if _uv_realpath_probe=$(realpath -- / 2>/dev/null) \
    && [ "$_uv_realpath_probe" = / ]; then
    realpath -- "$0"
else
    realpath "$0"
fi
```

The exact-output check prevents a BusyBox false positive even if the current directory contains a real file named `--`.

The Fish form also checks that the probe produced exactly one output item before selecting the delimiter form.

## Local execution results

Passed with GNU `realpath` and BusyBox `realpath`:

- absolute launcher path;
- relative launcher path;
- PATH lookup;
- leading-hyphen launcher invoked as `./-tool`;
- direct bare `$0` value `-foo`;
- directory containing both `-foo` and a literal file named `--`;
- relocatable POSIX activation path;
- empty stderr in every case.

Deterministic fake implementations also verified:

- a compliant implementation receives `realpath -- /` and then `realpath -- -foo`;
- a BusyBox-like implementation receives the probe and then falls back to `realpath -foo`;
- a status-only probe would fail the literal-`--` regression, while the exact-output probe passes it.

## Cost

The measured difference on this host was approximately `0.4 ms` per uv-generated relocatable launcher execution. It does not affect ordinary `uv` CLI invocations. Activation scripts pay the probe once when sourced.

## Remaining validation

- Run Rust formatting, focused tests, compilation, and Clippy after applying the patch to the PR branch.
- Exercise the revised Fish expression with a Fish binary in CI.
- Re-run the existing GNU/Linux, Alpine/BusyBox, and macOS launcher and activation matrix.
