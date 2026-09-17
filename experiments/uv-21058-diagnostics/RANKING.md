# uv #21058 diagnostic ranking

## In simple words

The behavior repair is settled: `tool upgrade --all` should propagate top-level tool-inventory failures instead of turning them into an empty successful result.

The remaining engineering choice is scope. B2 gives one path-aware recovery diagnostic across the tool-inventory command family. E gives `tool upgrade --all` operation context and a safe root-path hint while leaving sibling commands and `uv-tool` unchanged. Both now have executed evidence.

Source generation: `astral-sh/uv@95637ecf70cbf3c8a8d11f424b9a654e8fefdf51`

Public issue: https://redirect.github.com/astral-sh/uv/issues/21058

Upstream regression: https://redirect.github.com/astral-sh/uv/pull/21059

Primary execution:

- shared contenders: focused run `31569454399`, sibling run `31570073281`;
- scoped E contender: focused run `31570915333`, success.

Content comparison lives in `CONTENT_PROTOTYPES.md`; recovery rules live in `HINT_BOUNDARIES.md`.

## Finalists

### 1. B2 — shared path-aware error + inventory context

Why it is alive:

- exact offending child path;
- same actionable recovery appears automatically in `tool list`, `tool upgrade --all`, `tool uninstall --all`, and `tool audit --all`;
- unrelated top-level `upgrade --all` inventory I/O receives operation context and no invalid-name hint;
- follows uv's documented `Hint` architecture;
- real sibling-command execution proved the cross-command payoff.

Preferred content form:

```text
error: Failed to inspect installed tools
  Caused by: Invalid tool directory name: `<exact child path>`
  Caused by: Not a valid package or extra name: "<basename>" ...

hint: Move this directory outside the uv tool directory, or remove it if it is unwanted
```

Optional custom-root guard:

```text
If the configured tool directory is unexpected, check `UV_TOOL_DIR`
```

Why it may be too large:

- complete repair footprint is six files including the existing regression and `Cargo.lock`;
- changes a lower-level error API and adds direct `uv-tool -> uv-errors` dependency metadata;
- expands the public issue into a shared tool-inventory diagnostic improvement.

Polish before treating it as a candidate:

- rename the lower-level variant to `InvalidToolDirectoryName`;
- display `Invalid tool directory name: <path>` with `user_display()`;
- remove generic rename recovery;
- use `Failed to inspect installed tools` for the outer header;
- remove the obsolete transparent `ToolName` variant if no producer remains;
- add the `Cargo.lock` direct-dependency entry;
- update the upstream-owned `tool_upgrade.rs` snapshot;
- decide whether sibling snapshot coverage belongs in the same repair.

### 2. E — scoped typed wrapper + central hint

Owned draft: `teamleaderleo/uv#94@f7ce7e1e854bf70415b3aecfd8612ffafbfafa20`.

Focused run `31570915333` / job `94032523828`: **success**.

Executed invalid-name output:

```text
error: Failed to inspect installed tools
  Caused by: Not a valid package or extra name: "tool backup". Names must start and end with a letter or digit and may only contain -, _, ., and alphanumeric characters.

hint: Inspect the uv tool directory at `/tmp/...`; move the invalid directory outside it, or remove it
exit: 2
```

Executed receipt-read I/O control:

```text
error: Failed to inspect installed tools
  Caused by: failed to read from file `/tmp/.../ruff/uv-receipt.toml`: Is a directory (os error 21)
exit: 2
```

Sibling commands remained intentionally unchanged and emitted no hint for the invalid-name state.

Why it is alive:

- keeps user-visible change scoped to `tool upgrade --all`;
- complete review footprint is three files including the existing regression;
- normal propagation preserves exit 2;
- central `Hint` rendering follows uv's diagnostics convention;
- gives every top-level inventory failure operation context;
- invalid-name recovery shows the configured root without touching `uv-tool`;
- the invalid-name hint stays absent from unrelated receipt-read I/O.

Tradeoff:

- no exact offending child path; the user combines the bad basename from the parser cause with the root path in the hint;
- sibling commands remain on the current bare invalid-name error;
- a command-specific wrapper type must be registered with the central collector.

`E2-scoped-command-owned-hint.patch` keeps the same behavior while placing the wrapper type beside `tool upgrade`; that is an ownership/layout comparison, not a different user experience.

## Proven fallbacks

### A — command-local + `uv tool dir`

A is the smallest executed option. It preserves exit 2, gives operation context, limits recovery advice to the invalid-name variant, and explicitly proved `uv tool dir` works while inventory enumeration is broken.

Complete review footprint: two files including the existing regression.

Use A if one-file production scope outweighs central hint plumbing.

### C — command-local + root path

C also passed the focused controls. It saves the extra discovery command but still owns local rendering and gains no exact-child or sibling-command payoff. E now provides the cleaner scoped form because it uses normal propagation and central `Hint` rendering.

## Demoted

### B1

B1 has the cleanest exact-path invalid-name output and the same sibling payoff as B2. It leaves unrelated top-level inventory I/O bare in `upgrade --all`. B2 better explains the full top-level failure set currently swallowed by `unwrap_or_default()`.

### D

D avoids the direct `uv-tool -> uv-errors` dependency by matching a concrete `uv_tool::Error` variant inside the central diagnostic walker. That cuts against the file's documented generic `Hint` collection convention. If shared behavior is selected, B2 is cleaner.

## Content conclusions that apply to every finalist

1. **Drop arbitrary rename advice.** Directory basename, receipt target, and environment identity can diverge after a rename.
2. **Prefer `inspect` over `enumerate` in user-facing operation context.** `inspect` describes the user-visible job while `enumerate` exposes an implementation verb.
3. **Use `user_display()` for paths.** Windows presentation is part of the user experience.
4. **Do not attach invalid-name recovery to I/O variants.** Exact path plus OS error is enough when deployment policy is unknown.
5. **Make recovery executable from the broken state.** https://redirect.github.com/astral-sh/uv/issues/19630 shows the cost of pointing users to a command that fails on the same corrupt receipt.
6. **Avoid origin claims.** https://redirect.github.com/astral-sh/uv/issues/4867 shows uv itself has historically produced unexpected tool-root children.
7. **Account for custom roots.** A wrong `UV_TOOL_DIR` can make unrelated directory contents look like broken tool state; destructive copy should leave room for that interpretation.

## Current decision question

The remaining choice is scope and object identity:

- **B2** if an invalid tool-directory name should become a first-class shared tool-inventory diagnostic, with the exact child path and one recovery story across sibling commands.
- **E** if the public issue should stay focused on `tool upgrade --all`, while still using uv's central error/hint machinery and giving safe root-level recovery.

Both preserve the original behavior insight and both pass invalid-name, empty-root, and unrelated top-level I/O controls.

## Next useful probes

1. Render polished B2 and E copy with Windows `user_display()` paths.
2. Exercise a deliberately wrong `UV_TOOL_DIR` containing unrelated content and evaluate the custom-root guard.
3. Execute the recommended move-out action, then retry the four inventory commands and record convergence.
4. Compare B2's exact-child gain against its six-file review footprint using the same final wording.
5. Keep malformed/missing receipt recovery separate until entrypoint ownership is settled by `teamleaderleo/fieldwork#660` and the public malformed-receipt behavior in https://redirect.github.com/astral-sh/uv/issues/19630 is reconciled.
