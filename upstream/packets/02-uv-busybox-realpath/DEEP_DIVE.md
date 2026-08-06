# Deep dive — Unit 02

## Technical conclusion

The compatibility defect is specific to BusyBox `realpath`, not BusyBox `dirname`.

BusyBox `realpath` treats `--` as another pathname. A generated launcher can therefore resolve its real operand and continue while also emitting:

```text
realpath: --: No such file or directory
```

Normal POSIX-style implementations consume `--` as the end-of-options delimiter. Removing it unconditionally weakens protection for a bare operand beginning with `-`.

## Final downstream design

The final submitted uv patch used a runtime behavior probe:

```sh
if _uv_realpath_probe=$(realpath -- / 2>/dev/null) &&
    [ "$_uv_realpath_probe" = / ]; then
    realpath -- "$0"
else
    realpath "$0"
fi
```

### Why probe `/`

`/` is an existing operand with a known canonical result. The probe does not depend on the current directory, temporary files, symlinks, permissions, or user configuration.

### Why check status and output

On an ordinary implementation:

- `--` is consumed as a delimiter;
- `/` is the only operand;
- output is `/`;
- status is successful.

On BusyBox, `--` is treated as a pathname. When no such file exists, the probe may still print `/` for the second operand but returns failure. If a literal file named `--` exists, BusyBox can return success after resolving both operands, but the captured output is not equal to the single value `/`.

Both conditions are therefore required.

## Runtime rather than generation-time selection

A relocatable environment may be generated in one environment and executed under another `PATH`. The launcher uses whichever `realpath` the execution environment resolves.

Generation-time detection can inspect a different implementation from the one that later executes the artifact. Runtime probing observes the actual dependency.

## Historical constraint

`realpath` itself must remain. uv uses canonicalization so an externally symlinked launcher still locates the interpreter beside the original launcher rather than beside the alias.

The patch therefore selected the argument form without replacing the resolution algorithm.

## Ownership and migration

Wheel generation and virtualenv activation generation own emitted text. Project-run owns an exact recognizer used when copying entrypoints.

Persisted launchers create a two-by-two compatibility matrix:

1. current runtime-probe launcher + `python`;
2. current runtime-probe launcher + `python3`;
3. historical `realpath --` launcher + `python`;
4. historical `realpath --` launcher + `python3`.

Four explicit prefixes keep migration authority narrow. A general shell parser would accept more than the known producer formats.

## Failure modes of the alternatives

### Unconditional delimiter removal

A bare `-foo` operand may be reinterpreted as an option on implementations with normal option parsing.

### Retry after a protected call fails

BusyBox can resolve `$0`, fail on the separate `--` pathname, and then execute the fallback. Command substitution can capture the resolved path twice.

### Prefix relative `$0` with `./`

A launcher found through `PATH` may live outside the current directory. Rewriting a bare `$0` as `./$0` can select a different file.

### `command -v`

Useful for executable commands found through `PATH`, but not a common solution for sourced activation scripts.

### BusyBox fingerprinting

Executable names, help text, versions, and symlink layouts describe packaging rather than the required behavior and can vary independently.

## Exact final source

- Final public head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`
- Diff: four files, 207 additions, 16 deletions
- Final canonical CI: run `31059965759` — success
- Public PR: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)

## Evidence

The final candidate covered:

- compliant and BusyBox-style fake `realpath` implementations;
- probe and final-call argument recording;
- a bare `-foo` operand;
- a literal file named `--`;
- clean stderr;
- current and historical `python` / `python3` launcher forms;
- POSIX and Fish activation generation;
- Linux, macOS, and Windows ordinary CI.

The measured local cost of the extra probe was about `0.4 ms` per relocatable launcher execution.

## Project decision

The runtime probe solved the demonstrated compatibility problem while preserving option safety, but uv maintainers did not accept the added invocation and generated-shell complexity as a downstream tradeoff.

They preferred to make BusyBox `realpath` support the POSIX delimiter directly. That repair is tracked at [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26).

The final disposition is therefore `RETIRE`, not because the candidate failed its evidence, but because the target project selected a different ownership boundary.
