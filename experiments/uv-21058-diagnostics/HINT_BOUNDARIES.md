# uv tool diagnostic hint boundaries

## In simple words

A useful hint should survive the same damaged state that caused the command to fail. It should identify the object the user can safely act on, recommend an action supported by the exact error variant, and stay quiet when uv does not know enough to prescribe recovery.

This note grew from the diagnostic work around https://redirect.github.com/astral-sh/uv/issues/21058. It is broader than that one command: it records copy and recovery rules that can be reused when tool inventory, receipts, environments, or entrypoints are damaged.

## Working rule

Treat every `hint:` line as part of the recovery path.

A hint is strong when all of these are true:

1. **The action is valid for this exact failure family.** A package-name parse failure, a receipt read failure, and a tool-root permission failure deserve different advice.
2. **The action remains usable while the affected state is broken.** A command that reads the same damaged receipt or enumerates the same broken inventory is a weak recovery dependency.
3. **The object is precise enough for the requested mutation.** If the advice says to move or remove a directory, show the directory or give a reliable way to locate it.
4. **The first action is reversible when origin is uncertain.** Moving unexpected state out of the managed directory preserves evidence and gives the user a rollback path.
5. **The wording does not guess who created the state.** Unexpected tool-root contents can come from uv, an interrupted operation, another tool, a backup, or manual edits.
6. **The advice cannot manufacture a more believable inconsistent state.** Arbitrary rename advice fails this test for invalid tool-directory names.
7. **Automation semantics stay clear.** Recovery text supplements the nonzero exit; it does not turn an unknown inventory into a successful empty result.
8. **Custom roots are part of the model.** `UV_TOOL_DIR` can point uv at a directory with unrelated contents, so destructive advice needs an escape hatch for a misconfigured root.

## Failure-family matrix

| Failure family | What uv knows at the boundary | Hint direction | Boundary |
| --- | --- | --- | --- |
| Invalid UTF-8 child name | child cannot become a package identity | separate policy question | current enumeration skips it; do not silently broaden the invalid-package-name proposal to this case |
| Invalid package directory name | exact child basename is invalid; path can be retained | move child outside tool root, or remove if unwanted | avoid arbitrary rename; consider `UV_TOOL_DIR` misconfiguration |
| Tool-root `read_dir` I/O | root cannot be inspected | usually context only | permissions, mount state, sharing policy, and transient I/O need different remedies |
| Non-`NotFound` receipt read I/O | exact receipt path and OS error | usually context only | a permission or filesystem error is already specific; generic deletion advice can be harmful |
| Missing receipt | package directory identity exists; authoritative entrypoint list is absent | recovery design still open | removing only the environment can leave published entrypoints; see `teamleaderleo/fieldwork#660` |
| Malformed receipt | receipt path exists but authoritative metadata cannot be parsed | recovery design still open | current `tool list` advice can send the user to an uninstall command that fails on the same receipt |
| Missing environment with valid receipt | tool identity and receipt remain available | reinstall is a strong hint | current command has enough information to reconstruct the environment |
| Broken environment/interpreter with valid receipt | tool identity and requested configuration remain available | reinstall is a strong hint | keep the underlying interpreter/environment cause visible |
| Entrypoint collision during install | conflicting executable paths are known | explain ownership before `--force` | `--force` is destructive when the existing executable belongs to another installation |

## Invalid directory-name boundary

The strongest shared form is path-aware because the recovery action touches a filesystem object:

```text
error: Invalid tool directory name: `/home/me/.local/share/uv/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

A custom-root guard can be added when the extra sentence earns its space:

```text
hint: Move this directory outside the uv tool directory, or remove it if it is unwanted. If the configured tool directory is unexpected, check `UV_TOOL_DIR`
```

The second sentence handles a different failure origin: uv may be inspecting the wrong root entirely. It should stay conditional because the default tool directory is common and `UV_TOOL_DIR` may be unset.

### Why `rename` was dropped

`InstalledTools::tools()` derives the enumerated `PackageName` from the directory basename. The receipt separately retains the requested requirements. Enumeration does not prove that an arbitrary newly valid basename agrees with the environment and receipt identity.

Turning `tool backup` into `ruff` can therefore replace an obvious invalid-name failure with a valid-looking directory whose receipt or environment belongs to something else. Move-out preserves the questionable state without assigning it a new tool identity.

## Recovery must be executable

https://redirect.github.com/astral-sh/uv/issues/19630 is the clean counterexample. `uv tool list` can tell the user to run `uv tool uninstall <name>` for a malformed receipt, while named uninstall reads that same malformed receipt and fails before recovery. The wording describes an action that the program cannot carry out under the reported condition.

That gives a useful content test:

```text
Can the user follow this hint immediately, from the exact state that produced it?
```

If the answer depends on repairing the same state first, the hint should say what is actually possible or stay silent.

## Avoid assigning blame

Historical tool-root state shows why wording such as "remove the directory you created" would be wrong.

https://redirect.github.com/astral-sh/uv/issues/4867 recorded uv itself creating `interpreter-v2` under the tools directory. The repair in https://redirect.github.com/astral-sh/uv/pull/4868 fixed the producer so tool listing stopped creating that unexpected child. The lesson is producer ownership, not a license to ignore arbitrary children.

https://redirect.github.com/astral-sh/uv/issues/6400 also shows a failed tool upgrade can leave later tool-list state malformed. Recovery copy should describe the state it sees and avoid claiming an origin it cannot establish.

Preferred nouns are therefore `unexpected directory`, `invalid tool directory name`, `malformed receipt`, and `broken environment`.

## Error context and hints do different jobs

Use error context to answer **what operation failed**:

```text
error: Failed to inspect installed tools
  Caused by: ...
```

Use a domain error to answer **which object is bad**:

```text
Caused by: Invalid tool directory name: `<path>`
```

Use a hint to answer **what the user can safely do next**:

```text
hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

Keeping those jobs separate makes the text easier to reuse. A shared domain error can improve `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all`, while a command-level context can remain specific to the operation.

## When silence is better

A missing hint is useful when uv already reports the exact failed path and OS error but cannot infer the user's deployment policy.

Examples:

```text
error: Failed to inspect installed tools
  Caused by: failed to read from file `/opt/uv/tools/ruff/uv-receipt.toml`: Permission denied (os error 13)
```

```text
error: Failed to inspect installed tools
  Caused by: failed to read directory `/mnt/shared/uv-tools`: Input/output error (os error 5)
```

Permissions, shared-group ownership, network filesystems, container mounts, and transient I/O each have different remedies. A generic `chmod`, delete, or reinstall hint would overclaim.

## Cross-command boundary

The shared B prototypes established that one path-aware lower-level error plus `Hint` naturally reaches every sibling that propagates `InstalledTools::tools()` errors. That is useful only for failure families whose recovery is genuinely common.

Do not use shared hint plumbing as a reason to attach one recovery instruction to every `uv_tool::Error` variant. The error type can implement `Hint` selectively and return no hints for variants without a known action.

## Content acceptance checks

Before selecting a final hint, test the copy against these states:

- default tool root with one unexpected invalid-name child;
- custom `UV_TOOL_DIR` with one unexpected invalid-name child;
- `UV_TOOL_DIR` accidentally aimed at an unrelated directory;
- valid tool plus malformed sibling;
- empty tool root;
- receipt read I/O;
- tool-root read I/O where a deterministic fixture is available;
- Windows path display through `Simplified::user_display()`;
- sibling commands that encounter the same lower-level error;
- the exact recovery command or filesystem action described by the hint.

The goal is a hint that remains true after the user follows it, not merely a sentence that sounds helpful beside the first reproduction.
