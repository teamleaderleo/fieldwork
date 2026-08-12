# uv #21058 diagnostic thunderdome

Target source: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream-owned reproduction: https://redirect.github.com/astral-sh/uv/pull/21059

Status: internal design experiment. None of these candidates is selected for upstream submission.

Owned-fork carriers, all based on the same upstream commit:

- A: `teamleaderleo/uv#90` — command-local hint via `uv tool dir`
- B: `teamleaderleo/uv#91` — shared exact-path lower-level hint
- C: `teamleaderleo/uv#92` — command-local hint with the resolved tool-root path
- D: patch-only — shared exact-path top-level hint without a new `uv-tool` dependency

The upstream-owned regression snapshot is intentionally unchanged in the first carrier commit for A/B/C. A focused test failure is useful evidence here because it exposes the exact diagnostic output produced by the candidate.

## Shared behavior

Every contender retains the original behavior repair in the `uv tool upgrade --all` path: stop converting `InstalledTools::tools()` failure to an empty inventory.

Required controls:

- invalid tool-directory package name fails instead of reporting `Nothing to upgrade`;
- empty tool directory continues to report `Nothing to upgrade` and exit 0;
- missing and malformed receipts remain per-tool values after successful enumeration;
- unrelated top-level I/O failures do not receive an invalid-name recovery hint;
- preserve the current propagated-error exit classification unless a separate decision changes it.

## Recovery wording boundary

Generic rename advice is rejected for now.

The directory name is parsed separately and used as the enumerated tool identity. The receipt retains the original requested requirements, and receipt parsing does not validate those requirements against the directory name. Renaming an invalid directory to an arbitrary valid package name could therefore replace an obvious invalid-directory state with a directory/receipt/environment identity mismatch.

Preferred recovery family:

- move the unexpected directory outside the uv tool directory; or
- remove it if it is unwanted.

The first A/B/C carrier strings still contain `rename`; those strings are superseded R&D output and should be changed before any candidate is treated as selected.

## A — command-local diagnostic

Sketch: `A-command-local.patch`

Carrier: `teamleaderleo/uv#90`

`tool upgrade` catches `InstalledTools::tools()` errors, adds `Failed to enumerate installed tools` context, supplies a recovery hint only for `uv_tool::Error::ToolName`, renders the diagnostic, and returns `ExitStatus::Error`.

Preferred invalid-name hint family after wording refinement:

```text
hint: Run `uv tool dir` to locate the tool directory, then move the invalid directory outside it or remove it
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

Preferred output family:

```text
error: Failed to enumerate installed tools
  Caused by: Invalid tool directory at `.../tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Move the invalid tool directory at `.../tool backup` outside the uv tool directory, or remove it
```

Advantages:

- exact offending child path;
- common recovery semantics can reach `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all`;
- follows uv's lower-level `Hint` pattern.

Costs:

- four source files plus one `Cargo.lock` dependency-list edit: five files total;
- adds explicit `uv-tool -> uv-errors` dependency metadata;
- changes `uv-tool` error API;
- broadens user-visible behavior across sibling commands and therefore needs sibling controls.

`uv-errors` is already present transitively in this part of the dependency graph, so B does not add a new third-party package. The lockfile cost is an extra `"uv-errors"` entry under the existing `uv-tool` package.

Current source has exactly one `PackageName::from_str` call in `uv-tool`, at the tool-directory enumeration site, and no explicit `uv_tool::Error::ToolName` consumer. That makes the path-aware invalid-name case narrower than initially feared.

## C — command-local root-path hint

Sketch: `C-path-aware-local-hint.patch`

Carrier: `teamleaderleo/uv#92`

C asks whether most of B's recovery value can be obtained without touching `uv-tool` at all. It keeps A's command-local boundary but inserts the already-known `InstalledTools::root()` path directly into the hint.

Preferred invalid-name hint family:

```text
hint: Inspect the uv tool directory at `/actual/tool/root`; move the invalid directory outside it or remove it
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

## D — exact path with shared top-level hint

Sketch: `D-shared-path-top-level-hint.patch`

D keeps B's `InvalidToolDirectory { path, source }` data in `uv-tool`, but does not implement `uv_errors::Hint` there. The top-level diagnostic walker recognizes that concrete error variant and pushes the recovery hint itself.

Advantages:

- exact offending child path;
- shared recovery across sibling tool commands;
- no `uv-tool -> uv-errors` or `Cargo.lock` edit;
- three source files instead of B's five-file footprint.

Weaknesses:

- the top-level diagnostic layer knows a concrete `uv_tool::Error` variant;
- recovery policy lives away from the lower-level error definition;
- still broadens sibling command output and needs sibling controls.

D is currently patch-only because A/B/C already provide enough queued carriers to compare the main behavior/UX axes. Materialize D if B's exact-path behavior proves valuable and its dependency placement is the main objection.

## Scorecard

| Question | A | B | C | D |
| --- | --- | --- | --- | --- |
| Expected files | 1 | 5 | 1 | 3 |
| Exact offending child path | no | yes | no | yes |
| Tool-root path shown directly | no | yes | yes | yes |
| Shared recovery across tool commands | no | yes | no | yes |
| New direct crate dependency | no | yes | no | no |
| Explicitly preserves exit 2 in command | yes | normal propagation | yes | normal propagation |
| Central shared hint handling | no | yes via `Hint` | no | yes via concrete match |
| User must run `uv tool dir` | yes | no | no | no |

## Execution matrix

For each selected contender, exercise the same cases:

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
