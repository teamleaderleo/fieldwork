# uv #21058 diagnostic thunderdome

Target source: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream-owned reproduction: https://redirect.github.com/astral-sh/uv/pull/21059

Status: internal design experiment. None of these candidates is selected for upstream submission.

Owned-fork carriers, all based on the same upstream commit:

- A: `teamleaderleo/uv#90` — command-local hint via `uv tool dir`
- B: `teamleaderleo/uv#91` — shared exact-path lower-level hint
- C: `teamleaderleo/uv#92` — command-local hint with the resolved tool-root path

The upstream-owned regression snapshot is intentionally unchanged in the first carrier commit for each contender. A focused test failure is useful evidence here because it exposes the exact diagnostic output produced by the candidate.

## Shared behavior

Every contender retains the original behavior repair in the `uv tool upgrade --all` path: stop converting `InstalledTools::tools()` failure to an empty inventory.

Required controls:

- invalid tool-directory package name fails instead of reporting `Nothing to upgrade`;
- empty tool directory continues to report `Nothing to upgrade` and exit 0;
- missing and malformed receipts remain per-tool values after successful enumeration;
- unrelated top-level I/O failures do not receive an invalid-name recovery hint;
- preserve the current propagated-error exit classification unless a separate decision changes it.

## A — command-local diagnostic

Sketch: `A-command-local.patch`

Carrier: `teamleaderleo/uv#90`

`tool upgrade` catches `InstalledTools::tools()` errors, adds `Failed to enumerate installed tools` context, supplies a recovery hint only for `uv_tool::Error::ToolName`, renders the diagnostic, and returns `ExitStatus::Error`.

Invalid-name hint family:

```text
hint: Run `uv tool dir` to locate the tool directory, then move, rename, or remove the invalid directory
```

Advantages:

- one production file;
- no lower-level API or dependency change;
- explicit exit 2;
- unrelated I/O gets context without invalid-name recovery advice.

Weaknesses:

- requires the user to run another command to locate the directory;
- sibling commands keep their current bare invalid-name diagnostic;
- command code owns diagnostic rendering.

## B — path-aware shared `uv_tool` hint

Sketch: `B-shared-path-hint.patch`

Carrier: `teamleaderleo/uv#91`

`InstalledTools::tools()` creates a dedicated `InvalidToolDirectory` error carrying the exact directory path and original `InvalidNameError`. `uv_tool::Error` implements `uv_errors::Hint`; the central diagnostic collector learns `uv_tool::Error`; `tool upgrade` adds operation context and propagates normally.

Expected output family:

```text
error: Failed to enumerate installed tools
  Caused by: Invalid tool directory at `.../tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Move, rename, or remove the invalid tool directory at `.../tool backup`
```

Advantages:

- exact offending child path;
- common recovery semantics can reach `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all`;
- follows uv's lower-level `Hint` pattern.

Costs:

- four source files before any `Cargo.lock` refresh;
- adds `uv-tool -> uv-errors`;
- changes `uv-tool` error API;
- broadens user-visible behavior across sibling commands and therefore needs sibling controls.

The first carrier intentionally leaves `Cargo.lock` untouched so CI can tell us whether the dependency itself adds lockfile churn.

## C — command-local root-path hint

Carrier: `teamleaderleo/uv#92`

C asks whether most of B's recovery value can be obtained without touching `uv-tool` at all. It keeps A's command-local boundary but inserts the already-known `InstalledTools::root()` path directly into the hint.

Invalid-name hint family:

```text
hint: Inspect the uv tool directory at `/actual/tool/root`; move, rename, or remove the invalid directory
```

Advantages:

- one production file, like A;
- no new dependency or lower-level error variant;
- no extra `uv tool dir` lookup for the user;
- explicit exit 2;
- unrelated I/O remains hint-free.

Weaknesses:

- identifies the root, while the underlying parser message identifies the bad name; it does not combine them into one exact offending path;
- sibling commands remain unchanged;
- command code still owns rendering.

## Scorecard

| Question | A | B | C |
| --- | --- | --- | --- |
| Production files in first carrier | 1 | 4 | 1 |
| Exact offending child path | no | yes | no |
| Tool-root path shown directly | no | yes | yes |
| Shared recovery across tool commands | no | yes | no |
| New crate dependency | no | `uv-tool -> uv-errors` | no |
| Explicitly preserves exit 2 | yes | normal propagation | yes |
| Central hint collection | no | yes | no |
| User must run `uv tool dir` | yes | no | no |

## Execution matrix

For each contender, exercise the same cases:

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

Then add reachable top-level I/O controls:

1. tool-root `read_dir` failure;
2. non-`NotFound` `uv-receipt.toml` read failure.

Selection criterion: prefer the smallest design that gives correct operation context and actionable recovery advice for the actual failure type without misleading sibling commands.

## Relevant precedent

- `uv_virtualenv::Error` implements `uv_errors::Hint` only for variants with known recovery actions.
- `uv tool list` and `uv tool audit` already give command-oriented recovery guidance for malformed receipts and missing environments.
- `uv tool dir` is the native command for locating the tool root.
- Historical uv PR https://redirect.github.com/astral-sh/uv/pull/5520 handled known dangling package-directory residue by identifying the path and giving a targeted user-facing response instead of surfacing only the generic invalid-name failure.

See Fieldwork #627 for the full failure taxonomy and interaction state.
