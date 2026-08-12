# uv #21058 diagnostic thunderdome

Target source: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://github.com/astral-sh/uv/issues/21058

Upstream-owned reproduction: https://github.com/astral-sh/uv/pull/21059

Status: internal design experiment. None of these patches is selected for upstream submission.

## Shared behavior

Every contender retains the original behavior repair in the `uv tool upgrade --all` path: stop converting `InstalledTools::tools()` failure to an empty inventory.

The required controls are:

- invalid tool-directory package name must fail instead of reporting `Nothing to upgrade`;
- an empty tool directory must continue to report `Nothing to upgrade` and exit 0;
- missing and malformed receipts remain per-tool values after successful enumeration;
- unrelated top-level I/O failures must not receive an invalid-name recovery hint;
- preserve the current propagated-error exit classification unless a separate decision changes it.

## Contenders

### A — command-local diagnostic

Patch: `A-command-local.patch`

`tool upgrade` catches `InstalledTools::tools()` errors, adds `Failed to enumerate installed tools` context, supplies a recovery hint only for `uv_tool::Error::ToolName`, renders the diagnostic, and returns `ExitStatus::Error`.

Expected advantages:

- smallest source scope;
- no new lower-level dependency;
- explicit control over exit 2;
- unrelated I/O gets context without an invalid-name hint.

Expected weaknesses:

- sibling commands keep their current bare invalid-name diagnostic;
- the hint can identify the bad name only through the underlying parser message, not a retained path;
- command code owns diagnostic rendering.

### B — path-aware shared `uv_tool` hint

Patch: `B-shared-path-hint.patch`

`InstalledTools::tools()` creates a dedicated `InvalidToolDirectory` error carrying the directory path and the original `InvalidNameError`. `uv_tool::Error` implements `uv_errors::Hint`; the central diagnostic collector learns `uv_tool::Error`; `tool upgrade` adds operation context and propagates normally.

Expected advantages:

- direct path in the error and recovery hint;
- consistent hint across `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all` when the same invalid directory blocks enumeration;
- follows uv's existing lower-level `Hint` pattern.

Expected weaknesses:

- adds `uv-errors` to `uv-tool`;
- broadens user-visible behavior across commands;
- requires sibling-command snapshots/controls before selection.

### C — path-aware error, local hint

Patch: `C-path-aware-local-hint.patch`

`uv_tool` retains the offending directory path in a dedicated error variant, but does not depend on `uv-errors`. `tool upgrade` matches that variant and renders the path-specific recovery hint locally; other top-level errors receive context only.

Expected advantages:

- precise recovery for the reported command;
- avoids adding `uv-errors` to `uv-tool`;
- lower-level error retains useful path data for future consumers.

Expected weaknesses:

- diagnostic policy is split between `uv-tool` data and `uv` command rendering;
- sibling commands gain a better error string but no recovery hint;
- more code than A without the cross-command payoff of B.

## Thunderdome scorecard

| Question | A | B | C |
| --- | --- | --- | --- |
| Smallest change | best | largest | middle |
| Precise offending path | no | yes | yes |
| Shared recovery across tool commands | no | yes | no |
| New crate dependency | no | `uv-tool -> uv-errors` | no |
| Preserves exit 2 explicitly | yes | via normal propagation | yes |
| Keeps rendering centralized | no | yes | no |
| Best initial probe | yes | after A | after A |

## Experiments to run when materialized in the owned fork

For each contender, use the same current-main base and run:

```sh
# invalid package-directory name
tmp="$(mktemp -d)"
export UV_TOOL_DIR="$tmp"
mkdir "$UV_TOOL_DIR/tool backup"
uv tool list; echo "list: $?"
uv tool upgrade --all; echo "upgrade: $?"
uv tool uninstall --all; echo "uninstall: $?"
uv tool audit --all --preview; echo "audit: $?"

# empty control
tmp="$(mktemp -d)"
export UV_TOOL_DIR="$tmp"
uv tool upgrade --all; echo "empty-upgrade: $?"
```

Then add reachable I/O controls:

1. tool-root `read_dir` failure;
2. non-`NotFound` `uv-receipt.toml` read failure.

The selection criterion is not merely which patch is shortest. Prefer the smallest design that gives correct context and recovery advice for the actual failure type without misleading sibling commands.

## Relevant precedent

- `uv_virtualenv::Error` implements `uv_errors::Hint` only for variants with known recovery actions.
- `uv tool list` and `uv tool audit` already give command-oriented recovery guidance for malformed receipts and missing environments.
- `uv tool dir` is the native command for locating the tool root.
- Historical uv PR #5520 handled known dangling package-directory residue by identifying the path and giving a targeted user-facing response instead of surfacing a generic invalid-name error.

See Fieldwork #627 for the full failure taxonomy and upstream interaction state.
