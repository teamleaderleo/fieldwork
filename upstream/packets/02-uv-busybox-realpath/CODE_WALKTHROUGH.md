# Code walkthrough — uv BusyBox `realpath` compatibility

## What uv is doing

uv can generate executable wrappers for Python commands and activation scripts for relocatable virtual environments. Those files cannot hard-code the environment's original absolute path, so they find their own location at runtime and select the neighboring Python interpreter or environment directory.

Rust owns the code that generates this shell text and, in one path, recognizes previously generated launcher text later.

## The final generated decision

The final submitted patch used this POSIX shell fragment:

```sh
if _uv_realpath_probe=$(realpath -- / 2>/dev/null) &&
    [ "$_uv_realpath_probe" = / ]; then
    realpath -- "$0"
else
    realpath "$0"
fi
```

Read it in order:

1. Run `realpath -- /` and capture stdout.
2. Suppress the expected BusyBox diagnostic from the probe.
3. Require a successful exit status.
4. Require the captured output to equal `/`.
5. If both checks pass, resolve the launcher with the protected `realpath -- "$0"` form.
6. Otherwise use the BusyBox-compatible `realpath "$0"` form.

Checking both status and output handles the edge case where a file named `--` exists. BusyBox may then resolve both `--` and `/` successfully, but the captured output contains more than `/` and fails the capability check.

The surrounding launcher still uses `dirname --`, quoting, and `realpath` canonicalization.

## File 1: `crates/uv-install-wheel/src/wheel.rs`

This crate installs wheels and writes console-script entrypoints.

The patch introduced a Rust constant containing the shell capability decision:

```rust
const RELOCATABLE_REALPATH: &str =
    r#"if _uv_realpath_probe=$(realpath -- / 2>/dev/null) && [ "$_uv_realpath_probe" = / ]; then realpath -- "$0"; else realpath "$0"; fi"#;
```

`format_shebang` inserts that fragment into the existing shell/Python launcher wrapper:

```rust
format!(r#""$(dirname -- "$({RELOCATABLE_REALPATH})")"/"#)
```

The compressed Rust string is the same multiline shell logic shown above. It is a constant because the generator and tests need one exact artifact fragment.

### Tests in this file

Two Unix tests create fake `realpath` executables and place them first in `PATH`:

- `relocatable_realpath_uses_delimiter_when_supported`
- `relocatable_realpath_falls_back_for_busybox`

The fake utilities record their arguments, letting the tests verify the probe and final call rather than merely checking the final pathname.

The tests cover:

- a compliant implementation using `--` for the probe and operand;
- a BusyBox-style implementation falling back without `--`;
- a bare launcher operand named `-foo`;
- a literal file named `--`;
- clean stderr.

macOS temporary paths were canonicalized in the expectation because paths such as `/var` may resolve through `/private/var`.

## File 2: `crates/uv-virtualenv/src/virtualenv.rs`

This crate renders activation scripts.

The existing `match` selects generated text for each activation format. The final patch inserted equivalent capability decisions into:

- POSIX `activate`, using `$SCRIPT_PATH`;
- Fish `activate.fish`, using `(status -f)`.

They need separate syntax because POSIX shell and Fish are different languages.

Windows batch and Nushell branches retain their existing relocation mechanisms. `activate.csh` remains unavailable for relocatable environments because csh cannot determine its own sourced script location reliably.

## File 3: `crates/uv/src/commands/project/run.rs`

`uv run` may copy an installed entrypoint into another environment and replace its Python executable. Before doing so, it checks whether the file starts with launcher text uv knows how to interpret.

The patch recognizes a fixed two-by-two compatibility matrix:

| Generated form | Interpreter |
| --- | --- |
| current runtime-probe launcher | `python` |
| current runtime-probe launcher | `python3` |
| historical `realpath --` launcher | `python` |
| historical `realpath --` launcher | `python3` |

That appears as four exact constants:

```rust
RELOCATABLE_SHEBANG
RELOCATABLE_PYTHON3_SHEBANG
LEGACY_RELOCATABLE_SHEBANG
LEGACY_RELOCATABLE_PYTHON3_SHEBANG
```

The recognizer chains `strip_prefix` calls. It accepts only launcher formats uv is known to have generated rather than using a loose shell parser or regular expression.

The test feeds all four forms through the real private `copy_entrypoint` function and checks that:

- the output points to the new Python executable;
- the Python body remains intact;
- executable permissions remain intact.

The Unix-only constant import in the test module is guarded with `#[cfg(unix)]`, preventing a Windows Clippy unused-import failure.

## File 4: `crates/uv/tests/python/venv.rs`

This existing integration surface checks generated relocatable activation text. Its expected POSIX and Fish forms were updated to include the capability decision.

## Why the patch became large

The production behavior is a small shell branch. Most additions are:

- fake-utility test harness code;
- edge-case controls;
- exact current and historical launcher signatures;
- platform-specific test corrections.

The repetition in `run.rs` is a fixed set of compatibility signatures. A helper could generate them programmatically, but the explicit constants make the accepted historical file formats visible and auditable.

## Alternatives and their failure modes

- Removing `--` globally loses option protection for a bare `-foo` operand.
- Retrying after failure can capture the resolved path twice on BusyBox.
- Prefixing `$0` with `./` can point into the current directory instead of the location found through `PATH`.
- `command -v` does not cover sourced activation scripts.
- Generation-time detection can inspect a different utility from the one selected at execution time.
- BusyBox name, help, or symlink detection is brittle.

`APPROACHES.md` preserves the detailed comparison.

## Final source and outcome

- Public PR: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)
- Final head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`
- Final diff: four files, 207 additions, 16 deletions
- Final canonical CI: run `31059965759` — success
- State: closed without merge

The code worked as tested. uv maintainers declined the runtime and maintenance cost and chose an upstream BusyBox repair instead: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26).
