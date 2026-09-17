# uv #21058 diagnostic thunderdome

## In simple words

The original bug is a false-success problem: `uv tool upgrade --all` can turn a failed inventory read into `Nothing to upgrade`. The behavior repair is small. The remaining experiment compares where richer diagnostic context should live, which commands should share it, and what recovery wording stays safe when the tool directory itself may be damaged or misconfigured.

Target source: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream-owned reproduction: https://redirect.github.com/astral-sh/uv/pull/21059

Status: internal design experiment. None of these candidates is selected for upstream submission.

Companion material:

- `RESULTS.md` — executed behavior from the implementation contenders;
- `RANKING.md` — current B2 versus E engineering decision;
- `CONTENT_PROTOTYPES.md` — rendered diagnostic and hint alternatives across nearby tool failure families;
- `HINT_BOUNDARIES.md` — rules for when recovery advice is justified, executable, and safe.

Owned-fork carriers, all based on the same upstream commit:

- A: `teamleaderleo/uv#90` — command-local hint via `uv tool dir`
- B2: `teamleaderleo/uv#91` — shared exact-path lower-level hint plus inventory context
- C: `teamleaderleo/uv#92` — command-local hint with the resolved tool-root path
- B1: `teamleaderleo/uv#93` — shared exact-path lower-level hint without outer inventory context
- E: `teamleaderleo/uv#94` — scoped typed wrapper with central hint rendering
- D/E2: patch-only comparison material

The upstream-owned regression snapshot is intentionally unchanged in the first carrier commits for A/B1/B2/C. A focused test failure is useful evidence there because it exposes the exact diagnostic output produced by each candidate before wording is selected.

## Shared behavior

Every contender retains the original behavior repair in the `uv tool upgrade --all` path: stop converting `InstalledTools::tools()` failure to an empty inventory.

Required controls:

- invalid tool-directory package name fails instead of reporting `Nothing to upgrade`;
- empty tool directory continues to report `Nothing to upgrade` and exit 0;
- missing and malformed receipts remain per-tool values after successful enumeration;
- unrelated top-level I/O failures do not receive an invalid-name recovery hint;
- preserve the current propagated-error exit classification unless a separate decision changes it.

## Recovery wording boundary

Generic rename advice is rejected.

The directory name is parsed separately and used as the enumerated tool identity. The receipt retains the original requested requirements, and receipt parsing does not validate those requirements against the directory name. Renaming an invalid directory to an arbitrary valid package name could therefore replace an obvious invalid-directory state with a directory/receipt/environment identity mismatch.

Preferred recovery family:

- move the unexpected directory outside the uv tool directory; or
- remove it if it is unwanted.

`UV_TOOL_DIR` adds another boundary: the configured root itself can be wrong. `CONTENT_PROTOTYPES.md` includes copy that keeps destructive advice conditional when uv may be looking at unrelated contents.

The first A/B/C carrier strings still contain `rename`; those strings are superseded R&D output.

## A — command-local diagnostic

Sketch: `A-command-local.patch`

Carrier: `teamleaderleo/uv#90`

`tool upgrade` catches `InstalledTools::tools()` errors, adds operation context, supplies a recovery hint only for `uv_tool::Error::ToolName`, renders the diagnostic, and returns `ExitStatus::Error`.

Preferred invalid-name hint family after wording refinement:

```text
hint: Run `uv tool dir` to locate the tool directory, then move the invalid directory outside it or remove it if it is unwanted
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

## B2 — path-aware shared `uv_tool` hint + inventory context

Sketch: `B-shared-path-hint.patch`

Carrier: `teamleaderleo/uv#91`

`InstalledTools::tools()` creates a dedicated path-aware invalid-directory-name error carrying the exact directory path and original `InvalidNameError`. `uv_tool::Error` implements `uv_errors::Hint`; the central diagnostic collector learns `uv_tool::Error`; `tool upgrade` adds operation context and propagates normally.

Preferred output family:

```text
error: Failed to inspect installed tools
  Caused by: Invalid tool directory name: `.../tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

Advantages:

- exact offending child path;
- common recovery semantics reach `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all` in executed probes;
- follows uv's lower-level `Hint` pattern;
- operation context also improves unrelated top-level inventory I/O in `upgrade --all`.

Costs:

- complete review footprint is six files including `Cargo.lock` and the existing upstream regression;
- adds explicit `uv-tool -> uv-errors` dependency metadata;
- changes `uv-tool` error API;
- broadens user-visible behavior across sibling commands and therefore needs sibling coverage.

`uv-errors` is already present transitively in this part of the dependency graph, so B2 does not add a new third-party package. The lockfile cost is an extra `"uv-errors"` entry under the existing `uv-tool` package.

Current source has exactly one `PackageName::from_str` call in `uv-tool`, at the tool-directory enumeration site, and no explicit `uv_tool::Error::ToolName` consumer. That makes the path-aware invalid-name case narrower than initially feared.

## C — command-local root-path hint

Sketch: `C-path-aware-local-hint.patch`

Carrier: `teamleaderleo/uv#92`

C asks whether most of B2's recovery value can be obtained without touching `uv-tool` at all. It keeps A's command-local boundary but inserts the already-known `InstalledTools::root()` path directly into the hint.

Preferred invalid-name hint family:

```text
hint: Inspect the uv tool directory at `/actual/tool/root`; move the invalid directory outside it or remove it if it is unwanted
```

Advantages:

- one production file, like A;
- no new dependency or lower-level error variant;
- no extra `uv tool dir` lookup for the user;
- explicit exit 2;
- unrelated I/O remains hint-free.

Weaknesses:

- identifies the root while the parser message identifies the bad name; it does not combine them into one exact offending path;
- sibling commands remain unchanged;
- command code still owns rendering.

E now provides a cleaner scoped form of this idea through normal propagation and central hint rendering.

## B1 — path-aware shared hint without outer context

Carrier: `teamleaderleo/uv#93`.

B1 keeps the production repair literally `installed_tools.tools()?` and lets the lower-level path-aware error carry the invalid-name context. It has the same sibling-command payoff as B2 and a shorter invalid-name chain.

Its cost is visible on unrelated top-level inventory I/O: `upgrade --all` returns the raw I/O error without `Failed to inspect installed tools`. B2 is preferred if the repair should explain the entire failure set currently swallowed by `unwrap_or_default()`.

## D — exact path with shared top-level hint

Sketch: `D-shared-path-top-level-hint.patch`

D keeps B's path-aware data in `uv-tool` but teaches the top-level diagnostic walker to match the concrete error variant directly instead of implementing `Hint` in `uv-tool`.

It avoids the direct crate dependency, but the central diagnostic file explicitly consolidates hints through the generic `Hint` trait. D is therefore retained as a cost experiment and demoted behind B2.

## E — scoped typed wrapper + central hint

Sketch: `E-scoped-central-hint.patch`

Carrier: `teamleaderleo/uv#94@f7ce7e1e854bf70415b3aecfd8612ffafbfafa20`.

Focused run `31570915333` / job `94032523828`: success.

E keeps the behavior and user-visible change inside `tool upgrade --all`, wraps top-level `InstalledTools::tools()` failures in `Failed to inspect installed tools`, and uses the central `Hint` collector for variant-aware recovery.

Executed invalid-name family:

```text
error: Failed to inspect installed tools
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Inspect the uv tool directory at `/actual/tool/root`; move the invalid directory outside it, or remove it
exit: 2
```

Executed receipt-read I/O family:

```text
error: Failed to inspect installed tools
  Caused by: failed to read from file `.../ruff/uv-receipt.toml`: Is a directory (os error 21)
exit: 2
```

Sibling commands intentionally remain unchanged. Complete review footprint is three files including the existing upstream regression.

`E2-scoped-command-owned-hint.patch` keeps identical user-visible semantics while moving the wrapper type beside the command that owns it.

## Scorecard

| Question | A | B2 | C | B1 | E |
| --- | --- | --- | --- | --- | --- |
| Complete review files | 2 | 6 | 2 | 6 | 3 |
| Exact offending child path | no | yes | no | yes | no |
| Tool-root path shown directly | no | yes | yes | yes | yes |
| Shared recovery across tool commands | no | yes | no | yes | no |
| New direct crate dependency | no | yes | no | yes | no |
| Central shared hint handling | no | yes via `Hint` | no | yes via `Hint` | yes via scoped `Hint` |
| Operation context for unrelated upgrade inventory I/O | yes | yes | yes | no | yes |
| User must run `uv tool dir` | yes | no | no | no | no |
| Executed | yes | yes | yes | yes | yes |

## Execution matrix

The completed focused probes cover:

```sh
# invalid package-directory name
tmp="$(mktemp -d)"
export UV_TOOL_DIR="$tmp"
mkdir "$UV_TOOL_DIR/tool backup"
uv tool list
uv tool upgrade --all
uv tool uninstall --all
uv --preview tool audit --all

# empty control
tmp="$(mktemp -d)"
export UV_TOOL_DIR="$tmp"
uv tool upgrade --all

# deterministic non-name top-level receipt I/O
tmp="$(mktemp -d)"
export UV_TOOL_DIR="$tmp"
mkdir -p "$UV_TOOL_DIR/ruff/uv-receipt.toml"
uv tool upgrade --all
```

Next content-focused controls are recorded in `CONTENT_PROTOTYPES.md`: wrong `UV_TOOL_DIR`, Windows path display, and executing the recovery action to prove convergence.

## Relevant precedent

- `uv_virtualenv::Error` implements `uv_errors::Hint` only for variants with known recovery actions.
- `uv tool list` and `uv tool audit` already give command-oriented recovery guidance for malformed receipts and missing environments.
- `uv tool dir` is the native command for locating the tool root and was proven usable under the invalid-name state.
- https://redirect.github.com/astral-sh/uv/issues/19630 shows a recovery hint can be unusable when it points to a command that reads the same corrupt state.
- https://redirect.github.com/astral-sh/uv/issues/4867 and https://redirect.github.com/astral-sh/uv/pull/4868 show unexpected tool-root children can originate from uv itself; the historical repair fixed the producer.
- https://redirect.github.com/astral-sh/uv/pull/5520 is a useful path-aware diagnostic precedent for damaged installed metadata.

See Fieldwork #627 for the full failure taxonomy and interaction state.
