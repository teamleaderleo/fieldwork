# uv tool diagnostic content prototypes

## In simple words

The implementation thunderdome answered several code-placement questions. This companion set tests the words users would actually see.

The prototypes are deliberately independent of final source selection. They compare concise versus contextual errors, exact-child versus root-only recovery, custom-root handling, and cases where a hint should stay absent. Public context: https://redirect.github.com/astral-sh/uv/issues/21058.

## Prototype 1 — concise shared domain error

Use when the lower-level tool inventory error retains the exact child path and the command can rely on that domain error as sufficient context.

```text
error: Invalid tool directory name: `/home/me/.local/share/uv/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

Why it works:

- names the exact filesystem object;
- states the exact invalid property: the directory **name**;
- gives a self-contained action that does not depend on inventory enumeration or receipt parsing;
- stays compact enough for `tool list`, `tool uninstall --all`, and `tool audit --all` too.

Question it leaves open: unrelated top-level inventory I/O gets no operation-level context in `tool upgrade --all`.

## Prototype 2 — operation context plus shared domain error

Use when `tool upgrade --all` should explain every top-level inventory failure, including receipt I/O.

```text
error: Failed to inspect installed tools
  Caused by: Invalid tool directory name: `/home/me/.local/share/uv/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

The extra header earns its line if sibling failure families also read better with it:

```text
error: Failed to inspect installed tools
  Caused by: failed to read from file `/home/me/.local/share/uv/tools/ruff/uv-receipt.toml`: Permission denied (os error 13)
```

This is the strongest content form for B2.

## Prototype 3 — custom-root escape hatch

Use when the exact child path is available and we want the copy to acknowledge that the configured root itself may be wrong.

```text
error: Invalid tool directory name: `/srv/shared/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted. If the configured tool directory is unexpected, check `UV_TOOL_DIR`
```

This protects a user who accidentally pointed `UV_TOOL_DIR` at an unrelated directory from reading the hint as permission to delete arbitrary contents.

Cost: the second sentence appears for users on the normal default path too. Keep it only if the custom-root confusion is plausible enough in real reports.

## Prototype 4 — scoped root-path recovery

Use when the repair stays command-local and lower-level `uv_tool::Error` remains unchanged.

```text
error: Failed to inspect installed tools
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Inspect the uv tool directory at `/home/me/.local/share/uv/tools`; move the invalid directory outside it, or remove it if it is unwanted
```

This is the executed E content family. It gives the root and invalid basename separately.

Ergonomic cost: the user has to join `/home/me/.local/share/uv/tools` with `tool backup` mentally. That is acceptable for a narrow fix, though weaker than an exact-child domain error.

## Prototype 5 — scoped discovery-command recovery

Use when review scope should stay tiny and the command prefers a stable discovery command over printing a path.

```text
error: Failed to inspect installed tools
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Run `uv tool dir` to locate the tool directory, then move the invalid directory outside it or remove it if it is unwanted
```

The thunderdome explicitly proved `uv tool dir` still works while inventory enumeration is broken.

Ergonomic cost: one extra command and one extra inference step.

## Prototype 6 — inspect-first, reversible recovery

Use when origin is especially uncertain and we want the first verb to preserve evidence.

```text
error: Invalid tool directory name: `/home/me/.local/share/uv/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Move this unexpected directory outside the uv tool directory, then retry the command
```

Follow-up behavior can confirm whether the remaining inventory is healthy. Removal becomes a later user choice.

Tradeoff: users who already know the directory is junk receive a two-step recovery.

## Prototype 7 — custom-root inspect-first

This version combines reversibility with an explicit custom-root check:

```text
error: Invalid tool directory name: `/srv/shared/python/tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Check that `/srv/shared/python` is the intended uv tool directory. If it is, move `tool backup` outside it or remove it if it is unwanted
```

This is the safest destructive-action copy in the set. It requires both root and child data in the rendered diagnostic.

Potential downside: it is more conversational than most current uv hints.

## Prototype 8 — receipt read I/O: context only

A variant-specific hint should stay absent here:

```text
error: Failed to inspect installed tools
  Caused by: failed to read from file `/opt/uv/tools/ruff/uv-receipt.toml`: Permission denied (os error 13)
```

Possible deployments include shared directories, containers, read-only mounts, network filesystems, and ordinary ownership mistakes. The OS error plus exact path gives the user evidence without inventing one universal repair.

## Prototype 9 — tool-root read I/O: context only

```text
error: Failed to inspect installed tools
  Caused by: failed to read directory `/opt/uv/tools`: Permission denied (os error 13)
```

A generic `chmod` hint would assume a local ownership model. A generic delete/recreate hint could destroy shared state. Silence is the stronger content choice until uv can distinguish a known recoverable condition.

## Prototype 10 — malformed receipt: diagnostic honesty

Current `tool list` wording can point to a recovery command that fails on the same malformed receipt; see https://redirect.github.com/astral-sh/uv/issues/19630.

Until uninstall recovery has a reliable entrypoint-ownership policy, prefer wording that describes the limitation:

```text
warning: Ignoring malformed tool `ruff`: failed to read `uv-receipt.toml`

hint: The tool receipt is required to recover its installed entrypoints. Inspect the tool state before removing it manually
```

This is intentionally conservative. `teamleaderleo/fieldwork#660` is separately investigating the entrypoint residue boundary after receipt loss.

A future product repair could support stronger copy once uv can remove only confidently owned entrypoints.

## Prototype 11 — missing environment with valid receipt

This is a case where current reinstall guidance has good recovery properties because identity and receipt data remain available:

```text
warning: Tool `ruff` environment not found

hint: Run `uv tool install ruff --reinstall` to recreate the tool environment
```

The key difference from malformed-receipt recovery is authority: uv still has the metadata needed to reconstruct the installation.

## Prototype 12 — broken environment/interpreter with valid receipt

Keep the original failure visible and make reinstall the second line:

```text
warning: Querying Python at `.../ruff/bin/python` failed: <interpreter error>

hint: Run `uv tool install ruff --reinstall` to recreate the tool environment
```

This is actionable because the repair path does not depend on the broken interpreter staying usable.

## Prototype 13 — entrypoint collision with ownership context

Public reports such as https://redirect.github.com/astral-sh/uv/issues/18854 show that a bare `use --force to overwrite` hint can omit the important fact that existing executables may come from another installation.

Content prototype:

```text
error: Executables already exist: black, blackd

hint: Use `--force` only if uv should replace the existing executables at these paths
```

A richer implementation could display the paths and, where ownership can be established, say whether they belong to another uv tool installation.

This is adjacent ergonomics work, not part of the #21058 repair.

## Prototype 14 — incomplete audit coverage

`teamleaderleo/fieldwork#626` is investigating a separate all-tools completeness problem. If the eventual policy treats skipped tools as incomplete coverage, the content should state the coverage loss explicitly:

```text
warning: Skipped `ruff`: tool lock is missing
warning: Skipped `black`: tool receipt is malformed

error: Tool audit was incomplete: 2 installed tools were not audited
```

or, under a partial-success result model:

```text
Audited 3 tools; skipped 2
```

Machine-readable output would need the same distinction. This prototype belongs to that campaign, but it reinforces the same rule as #21058: an aggregate command should never convert unknown coverage into an affirmative complete result.

## Content scorecard

| Prototype | Exact child | Extra command | Safe for wrong `UV_TOOL_DIR` | Shared across sibling commands | Recovery is self-contained | Review-copy length |
| --- | --- | --- | --- | --- | --- | --- |
| 1 concise shared | yes | no | medium | yes | yes | short |
| 2 operation + shared | yes | no | medium | shared lower layer; command context local | yes | medium |
| 3 custom-root guard | yes | no | high | yes | yes | long |
| 4 scoped root path | no | no | medium | no | mostly | medium |
| 5 discovery command | no | yes | medium | no | yes, two-step | medium |
| 6 reversible move-out | yes | no | medium | yes | yes | short |
| 7 root-check first | yes | no | high | yes | yes | medium |

## Current content finalists

### Shared behavior finalist

```text
error: Failed to inspect installed tools
  Caused by: Invalid tool directory name: `<exact child path>`
  Caused by: Not a valid package or extra name: "<basename>" ...

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

Optional custom-root sentence:

```text
If the configured tool directory is unexpected, check `UV_TOOL_DIR`
```

### Narrow behavior finalist

```text
error: Failed to inspect installed tools
  Caused by: Not a valid package or extra name: "<basename>" ...

hint: Inspect the uv tool directory at `<root>`; move the invalid directory outside it, or remove it if it is unwanted
```

The shared version wins on object identity and sibling-command reuse. The narrow version wins on review scope and keeps `uv-tool` unchanged.

## Next copy probes

1. Render the shared finalist with Unix and Windows `user_display()` paths.
2. Exercise a deliberately wrong `UV_TOOL_DIR` containing unrelated valid and invalid children; evaluate whether the custom-root sentence prevents unsafe interpretation.
3. Give the diagnostic to a reader who does not know uv's tool-directory layout and ask which path they would move.
4. Run the exact recovery action, retry `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all`, and record whether the state converges.
5. Compare `Failed to inspect installed tools` against no outer context using the receipt-I/O case, where the header has the clearest value.
