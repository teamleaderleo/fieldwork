# uv #21058 thunderdome results

Source generation: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream reproduction: https://redirect.github.com/astral-sh/uv/pull/21059

Focused owned-fork run: `31569454399` — success, all four contender jobs passed.

Second sibling-command run: `31570073281` — active at time of this note.

## Shared controls

All four contenders passed:

- invalid directory name -> exit 2, invalid-package-name cause, no `Nothing to upgrade`;
- empty tool directory -> `Nothing to upgrade`, exit 0;
- `ruff/uv-receipt.toml` created as a directory -> exit 2, no invalid-name recovery hint.

The receipt-path-as-directory fixture is a deterministic non-name top-level `InstalledTools::tools()` failure.

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

Notes:

- one production file;
- explicit exit 2 after local rendering;
- variant-specific hint boundary works;
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

Notes:

- exact offending child path;
- shared `Hint` implementation compiles;
- unrelated I/O receives operation context but no hint;
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

A/C/B2 add context to every top-level `InstalledTools::tools()` error.

B1 makes the invalid-name error self-explanatory through a path-aware domain error, but leaves other top-level inventory I/O bare.

Candidate context wording to compare:

```text
Failed to inspect installed tools
```

`inspect` is closer to existing uv user-facing diagnostic vocabulary than `enumerate`.

## Shared-behavior question

B1/B2 only earn their larger footprint if the exact-path `Hint` is useful across sibling inventory consumers (`tool list`, `tool uninstall --all`, `tool audit --all`). Run `31570073281` probes those commands against the same invalid directory and also verifies that `uv tool dir` remains usable under the broken state.
