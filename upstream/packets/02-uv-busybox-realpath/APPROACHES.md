# Approaches — Unit 02

## Final downstream candidate

Preserve the `--` operand delimiter when the runtime `realpath` implementation supports it and fall back to the BusyBox-compatible form only when a capability probe fails.

```sh
if _uv_realpath_probe=$(realpath -- / 2>/dev/null) &&
    [ "$_uv_realpath_probe" = / ]; then
    realpath -- "$0"
else
    realpath "$0"
fi
```

Equivalent logic was generated for POSIX and Fish activation scripts. `uv run` recognized current and historical relocatable launcher text in both `python` and `python3` forms.

## Why this candidate was technically selected

- It preserved operand protection on normal POSIX-style implementations.
- It avoided the BusyBox false diagnostic.
- It selected behavior using the exact runtime utility reached through `PATH`.
- The `/` probe had a stable existing operand and known output.
- Checking both status and output avoided a false positive when a literal file named `--` existed.
- It retained quoting, `dirname --`, and `realpath`-based symlink resolution.
- It covered generated launchers and sourced activation scripts with the same capability decision.

## Alternatives reviewed

### Remove `--` from every generated `realpath` call

This was the first submitted approach. Maintainer review rejected it because a bare operand such as `-foo` can be reinterpreted as an option on implementations that support option parsing.

### Retry without `--` after failure

```sh
realpath -- "$0" 2>/dev/null || realpath "$0"
```

BusyBox processes both operands. It can resolve `$0`, fail on the `--` pathname, and then run the fallback. Command substitution can therefore receive the resolved path twice.

### Prefix a relative `$0` with `./`

```sh
case "$0" in
    /*) realpath "$0" ;;
    *)  realpath "./$0" ;;
esac
```

This makes an option-like name safe, but it can change the target. A launcher found as `-foo` through `PATH` may actually live at `/opt/venv/bin/-foo`; `./$0` instead points into the current directory.

### Use `command -v`

This can recover an executable launcher found through `PATH`, but it does not provide the same solution for sourced activation scripts, which need not be executable commands.

### Detect BusyBox when generating the artifact

Rejected because a relocatable environment may execute with a different `PATH` and `realpath` implementation from the generation environment.

### Identify BusyBox by name, help text, version output, or symlink layout

Rejected as brittle. The required distinction is behavior, not branding or installation shape.

### Redirect `realpath` stderr

Rejected because it hides genuine resolution errors together with the false BusyBox diagnostic.

### Replace or remove `realpath`

Rejected because it changes the portability and symlink-canonicalization contract that the launcher already relies on.

### Broaden launcher recognition into a parser

Rejected. The known generated formats are a fixed compatibility matrix: current and historical forms, each using `python` or `python3`. Exact prefixes keep the accepted grammar narrow.

## Project-preferred approach

uv maintainers ultimately rejected runtime capability probing as a downstream tradeoff. Although the candidate was fully green, they did not want the additional command invocation and generated-shell complexity in every affected launcher.

The project-preferred solution is to add normal `--` handling to BusyBox `realpath` itself. The upstream handoff is tracked at [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26).

## Final outcome

- Public uv PR: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)
- State: closed without merge
- Final uv head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`
- Final canonical CI: run `31059965759` — success
- Disposition: `RETIRE` downstream candidate; retain as negative-result evidence

Public upstream interaction occurred and is complete. No further uv comment or replacement PR is planned unless maintainers request a new downstream direction.
