# uv #21058 thunderdome results

## In simple words

Every implementation contender now has execution evidence for the core invalid-name, empty-root, and unrelated receipt-I/O controls. Shared B behavior also has sibling-command execution, while scoped E has its own focused run proving central hint rendering without changing sibling commands.

The code experiment has therefore moved from "does this compile and preserve exit status?" to a product choice about diagnostic scope, exact object identity, and recovery copy.

Source generation: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream reproduction: https://redirect.github.com/astral-sh/uv/pull/21059

Execution:

- shared contender run `31569454399` — success, A/C/B2/B1 jobs passed;
- sibling-command run `31570073281` — success, shared B payoff established;
- scoped E run `31570915333` / job `94032523828` — success.

See `CONTENT_PROTOTYPES.md` for copy variants and `HINT_BOUNDARIES.md` for recovery rules.

## Shared controls

Every executed contender passed the applicable controls:

- invalid directory name -> exit 2, invalid-package-name cause, no `Nothing to upgrade`;
- empty tool directory -> `Nothing to upgrade`, exit 0;
- `ruff/uv-receipt.toml` created as a directory -> exit 2, no invalid-name recovery hint.

The receipt-path-as-directory fixture is a deterministic non-name top-level `InstalledTools::tools()` failure.

Sibling jobs also confirmed `uv tool dir` remains usable when the tool root contains `tool backup`; it prints the configured root and exits 0.

## A — command-local + `uv tool dir`

Owned carrier: `teamleaderleo/uv#90`

```text
error: Failed to enumerate installed tools
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Run `uv tool dir` to locate the tool directory, then move, rename, or remove the invalid directory
exit: 2
```

Receipt-read I/O:

```text
error: Failed to enumerate installed tools
  Caused by: failed to read from file `/tmp/.../ruff/uv-receipt.toml`: Is a directory (os error 21)
exit: 2
```

Sibling commands under the same invalid directory remain unchanged and report only the generic invalid package-name error.

Notes:

- one production file;
- explicit exit 2 after local rendering;
- variant-specific hint boundary works;
- `uv tool dir` recovery lookup is proven usable in the broken state;
- `rename` is superseded wording;
- `enumerate` is superseded as preferred copy; compare `inspect`.

## C — command-local + tool-root path

Owned carrier: `teamleaderleo/uv#92`

```text
error: Failed to enumerate installed tools
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Inspect the uv tool directory at `/tmp/...`; move, rename, or remove the invalid directory
exit: 2
```

Receipt-read I/O has the same operation context as A and no hint.

Sibling commands remain unchanged.

Notes:

- one production file;
- saves the extra `uv tool dir` lookup;
- user combines the bad basename from the cause with the root path from the hint;
- polished path output should use `user_display()`;
- `rename` is superseded;
- E now provides cleaner scoped diagnostic plumbing for the same user-visible axis.

## B2 — exact child path + shared hint + outer context

Owned carrier: `teamleaderleo/uv#91`

```text
error: Failed to enumerate installed tools
  Caused by: Invalid tool directory at `/tmp/.../tool backup`
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Move, rename, or remove the invalid tool directory at `/tmp/.../tool backup`
exit: 2
```

Receipt-read I/O:

```text
error: Failed to enumerate installed tools
  Caused by: failed to read from file `/tmp/.../ruff/uv-receipt.toml`: Is a directory (os error 21)
exit: 2
```

Sibling commands gain the shared exact-path diagnostic. `uv tool list`, `uv tool uninstall --all`, and `uv --preview tool audit --all` each report the path-aware invalid-name cause and the same recovery hint, exit 2.

Notes:

- exact offending child path;
- shared `Hint` implementation compiles and improves all three sibling inventory commands consistently;
- unrelated I/O receives operation context but no hint in `upgrade --all`;
- complete review footprint is six files including the existing regression and `Cargo.lock`;
- prefer `Invalid tool directory name` over the first-pass `Invalid tool directory`;
- `rename` is superseded;
- prefer `Failed to inspect installed tools` over `enumerate`.

## B1 — exact child path + shared hint, no outer context

Owned carrier: `teamleaderleo/uv#93`

```text
error: Invalid tool directory at `/tmp/.../tool backup`
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Move, rename, or remove the invalid tool directory at `/tmp/.../tool backup`
exit: 2
```

Receipt-read I/O:

```text
error: failed to read from file `/tmp/.../ruff/uv-receipt.toml`: Is a directory (os error 21)
exit: 2
```

Sibling command output is the same shared exact-path diagnostic as B2 because that behavior comes from the lower-level `uv_tool::Error` + central `Hint`, not the upgrade command's outer context.

Notes:

- shortest exact-path invalid-name diagnostic;
- upgrade production change remains literally `installed_tools.tools()?`;
- unrelated top-level inventory I/O remains bare;
- complete shared-hint footprint remains six files once the regression and lock metadata are counted;
- prefer `Invalid tool directory name` and move-out/remove recovery.

## E — scoped typed wrapper + central hint

Owned carrier: `teamleaderleo/uv#94@f7ce7e1e854bf70415b3aecfd8612ffafbfafa20`

Focused run `31570915333` / job `94032523828`: **success**.

Invalid-name output:

```text
error: Failed to inspect installed tools
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Inspect the uv tool directory at `/tmp/...`; move the invalid directory outside it, or remove it
exit: 2
```

Empty control:

```text
Nothing to upgrade
exit: 0
```

Receipt-read I/O:

```text
error: Failed to inspect installed tools
  Caused by: failed to read from file `/tmp/.../ruff/uv-receipt.toml`: Is a directory (os error 21)
exit: 2
```

Sibling-command scope control:

```text
uv tool list
uv tool uninstall --all
uv --preview tool audit --all
```

all remain on the current bare invalid-package-name error and exit 2, with no `hint:` line.

Notes:

- central hint rendering works with a command-scoped wrapper;
- normal error propagation preserves exit 2;
- every top-level `upgrade --all` inventory failure gains `Failed to inspect installed tools` context;
- the invalid-name hint stays variant-specific;
- complete review footprint is three files including the upstream regression;
- no `uv-tool` API or dependency change;
- exact child path remains unavailable without lower-level data.

`E2-scoped-command-owned-hint.patch` carries the same semantics with the wrapper type colocated with `tool upgrade` instead of the generic diagnostics module.

## Recovery wording conclusion

Do not recommend arbitrary renaming.

The directory basename is used as the enumerated package identity, while the tool receipt separately retains the original requested requirement. Receipt deserialization does not validate the directory basename against that target. Renaming an invalid child to an arbitrary valid package name can therefore create a subtler identity mismatch.

Current preferred recovery:

```text
Move the invalid directory outside the uv tool directory, or remove it if it is unwanted.
```

For a custom-root-aware variant:

```text
If the configured tool directory is unexpected, check `UV_TOOL_DIR`.
```

## Context tradeoff

A/C/B2/E add context to every top-level `InstalledTools::tools()` error in `upgrade --all`.

B1 makes the invalid-name error self-explanatory through a path-aware domain error but leaves other top-level inventory I/O bare.

Preferred operation wording:

```text
Failed to inspect installed tools
```

`inspect` better describes the user-visible operation while `enumerate` exposes an implementation verb.

## Shared-behavior result

The sibling run establishes a real payoff for the shared B design: one lower-level path-aware error + `Hint` gives the same actionable recovery to `tool list`, `tool uninstall --all`, and `tool audit --all` without command-specific handling in each consumer.

That payoff is meaningful because all three commands currently fail on the same invalid child, and `uv tool uninstall --all` cannot itself be used as a recovery path for that child.

The tradeoff is scope: B2 turns the reported command bug into a shared tool-inventory diagnostic improvement and costs six files in a complete implementation. E is the strongest executed narrow alternative.

## Content boundary result

History changes the wording criteria:

- https://redirect.github.com/astral-sh/uv/issues/19630 shows a hint can be syntactically clear and operationally useless when it invokes a command that reads the same corrupt state;
- https://redirect.github.com/astral-sh/uv/issues/4867 shows unexpected tool-root children can originate from uv itself, so copy should avoid assigning blame;
- custom `UV_TOOL_DIR` means the root itself may be misconfigured, so destructive advice should leave room for that case;
- `teamleaderleo/fieldwork#660` keeps missing/malformed receipt cleanup separate because entrypoint ownership may be unavailable after receipt loss.

The copy work should therefore be reviewed with the same seriousness as the error variant: variant-specific, executable, reversible-first when origin is uncertain, and precise about the object the user will touch.
