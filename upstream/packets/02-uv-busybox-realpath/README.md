# Unit 02 — uv BusyBox `realpath` compatibility

## Disposition

`RETIRED — PUBLIC PR CLOSED UNMERGED — UPSTREAM BUSYBOX FIX PREFERRED`

Public issue: [astral-sh/uv#16209](https://redirect.github.com/astral-sh/uv/issues/16209)  
Public pull request: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)  
Preferred upstream repair: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26)  
Final public head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`  
Final canonical CI: run `31059965759` — success

The downstream uv candidate is no longer a landing proposal. uv maintainers rejected runtime capability probing because the extra command and generated-shell complexity did not fit the project's preferred tradeoff. They chose to pursue POSIX-compatible `--` handling in BusyBox `realpath` instead.

This was a project-level design decision, not a test failure. The final uv candidate was fully green.

## What the submitted PR became

The first candidate removed `--` only from generated `realpath` calls. Maintainer review identified that a bare option-like entrypoint such as `-foo` could then be interpreted as an option on implementations that support normal option parsing.

The revised candidate preserved `--` where supported and used the compatibility form only when the runtime implementation failed a capability probe:

```sh
if _uv_realpath_probe=$(realpath -- / 2>/dev/null) &&
    [ "$_uv_realpath_probe" = / ]; then
    realpath -- "$0"
else
    realpath "$0"
fi
```

The probe checked both status and output. That also handled the edge case where a literal file named `--` existed and BusyBox resolved both operands.

The same decision was applied to POSIX and Fish activation generation. `uv run` continued to recognize current and historical `python` and `python3` relocatable launcher forms.

## Final source boundary

| File | Change |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate a relocatable launcher with the runtime `realpath` capability probe and add branch-specific fake-utility tests. |
| `crates/uv-virtualenv/src/virtualenv.rs` | Apply equivalent runtime selection to POSIX and Fish activation generation. |
| `crates/uv/src/commands/project/run.rs` | Recognize current and historical `python` / `python3` launcher text. |
| `crates/uv/tests/python/venv.rs` | Update relocatable activation expectations. |

Final public diff: four files, 207 additions, 16 deletions.

## Durable findings

The investigation established why the obvious downstream alternatives were incomplete:

- Unconditionally removing `--` weakens operand protection for bare names beginning with `-`.
- Retrying `realpath -- "$0"` without the delimiter can capture the resolved path twice on BusyBox because BusyBox processes both operands before returning failure.
- Prefixing relative `$0` with `./` can resolve the wrong file when the launcher was found through `PATH`.
- `command -v` does not provide the same answer for sourced activation scripts.
- Generation-time detection can inspect a different `realpath` from the executable later selected through runtime `PATH`.
- Identifying BusyBox by executable name, help text, or symlink layout is brittle.
- Runtime capability probing works technically, but uv does not want its per-launcher runtime and maintenance cost.

The final project choice was therefore to repair BusyBox rather than carry a downstream uv compatibility branch.

## Evidence retained

The final candidate covered:

- implementations that accept `realpath --`;
- BusyBox-style implementations that treat `--` as a pathname;
- a bare `-foo` operand;
- a literal file named `--`;
- current and historical `python` / `python3` launcher recognition;
- POSIX and Fish activation generation;
- Linux, macOS, and Windows ordinary CI.

The final upstream CI run completed successfully. The measured local overhead of the additional probe was about `0.4 ms` per relocatable launcher execution.

## Closeout rule

Do not reopen, rework, or resubmit the downstream uv candidate unless uv maintainers explicitly request another downstream direction.

Keep this packet as:

- a negative-result record;
- a shell-portability case study;
- evidence for the upstream BusyBox repair;
- a reminder to check an ambiguous architectural direction before expanding a full implementation.

## Packet guide

- `PRESENTATION.md` — executive decision brief.
- `CODE_WALKTHROUGH.md` — explanation of uv, Rust, shell generation, and every changed file.
- `DEEP_DIVE.md` — technical invariants and historical constraints.
- `APPROACHES.md` — selected, rejected, and project-preferred designs.
- `TESTS.md` — execution receipts.
- `UPSTREAM_ISSUE.md` — issue history and upstream handoff.
- `UPSTREAM_PR.md` — submitted PR history and closeout.
- `REVIEW.md` — diff-review guide.
- `HANDOFF.md` — terminal disposition and continuation boundary.
