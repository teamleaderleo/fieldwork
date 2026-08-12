# uv #21058 thunderdome results

Source generation: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream reproduction: https://redirect.github.com/astral-sh/uv/pull/21059

Focused owned-fork run: `31569454399` — success, all four contender jobs passed.

Sibling-command run: `31570073281` — success, all four contender jobs passed.

## Shared controls

All four contenders passed:

- invalid directory name -> exit 2, invalid-package-name cause, no `Nothing to upgrade`;
- empty tool directory -> `Nothing to upgrade`, exit 0;
- `ruff/uv-receipt.toml` created as a directory -> exit 2, no invalid-name recovery hint.

The receipt-path-as-directory fixture is a deterministic non-name top-level `InstalledTools::tools()` failure.

All sibling jobs also confirmed `uv tool dir` remains usable when the tool root contains `tool backup`; it prints the configured root and exits 0.

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

Sibling commands under the same invalid directory remain unchanged:

```text
uv tool list
uv tool uninstall --all
uv --preview tool audit --all
```

each report only the generic invalid package-name error and exit 2.

Notes:

- one production file;
- explicit exit 2 after local rendering;
- variant-specific hint boundary works;
- `uv tool dir` recovery lookup is proven usable in the broken state;
- `rename` is superseded wording;
- `enumerate` is a wording placeholder; compare `inspect`.

## C — command-local + tool-root path

Owned carrier: `teamleaderleo/uv#92`

```text
error: Failed to enumerate installed tools
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Inspect the uv tool directory at `/tmp/...`; move, rename, or remove the invalid directory
exit: 2
```

Receipt-read I/O has the same operation context as A and no hint.

Sibling commands remain unchanged, as in A.

Notes:

- one production file;
- saves the extra `uv tool dir` lookup;
- user combines the bad basename from the cause with the root path from the hint;
- polished path output should use `user_display()`;
- `rename` is superseded.

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

Sibling commands gain the shared exact-path diagnostic. `uv tool list`, `uv tool uninstall --all`, and `uv --preview tool audit --all` each report:

```text
error: Invalid tool directory at `/tmp/.../tool backup`
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Move, rename, or remove the invalid tool directory at `/tmp/.../tool backup`
exit: 2
```

Notes:

- exact offending child path;
- shared `Hint` implementation compiles and improves all three sibling inventory commands consistently;
- unrelated I/O receives operation context but no hint in `upgrade --all`;
- complete footprint is five files after `Cargo.lock` records `uv-tool -> uv-errors`;
- prefer `Invalid tool directory name` over the first-pass `Invalid tool directory`;
- `rename` is superseded.

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

Sibling command output is the same shared exact-path diagnostic as B2 because that behavior comes from `uv_tool::Error` + central `Hint`, not the upgrade command's outer context.

Notes:

- shortest exact-path invalid-name diagnostic;
- upgrade production change remains literally `installed_tools.tools()?`;
- unrelated top-level inventory I/O remains bare;
- complete shared-hint footprint is still five files;
- prefer `Invalid tool directory name` and move-out/remove recovery.

## Recovery wording conclusion

Do not recommend arbitrary renaming.

The directory basename is used as the enumerated package identity, while the tool receipt separately retains the original requested requirement. Receipt deserialization does not validate the directory basename against that target. Renaming an invalid child to an arbitrary valid package name can therefore create a subtler identity mismatch.

Current preferred recovery:

```text
Move the invalid directory outside the uv tool directory, or remove it if it is unwanted.
```

## Context tradeoff

A/C/B2 add context to every top-level `InstalledTools::tools()` error in `upgrade --all`.

B1 makes the invalid-name error self-explanatory through a path-aware domain error, but leaves other top-level inventory I/O bare.

Candidate context wording to compare:

```text
Failed to inspect installed tools
```

`inspect` is closer to existing uv user-facing diagnostic vocabulary than `enumerate`.

## Shared-behavior result

The sibling run establishes a real payoff for the shared B design: one lower-level path-aware error + `Hint` gives the same actionable recovery to `tool list`, `tool uninstall --all`, and `tool audit --all` without command-specific handling in each consumer.

That payoff is meaningful because all three commands currently fail on the same invalid child, and `uv tool uninstall --all` cannot itself be used as a recovery path for that child.

The tradeoff is scope: B turns #21058 into a shared tool-inventory diagnostic improvement and costs five files in a complete implementation. A/C remain valid one-file fixes if upstream wants the reported command kept narrow.
