# Stable shim inspiration and anti-patterns

## In simple words

`TRANSACTIONAL_LAYOUT.md` proposes stable public launchers so one per-tool active-generation pointer can switch every entrypoint together.

That idea has good precedents in version managers, but their tradeoffs are useful warnings. Shims can become stale, hide the real executable from `which`, add invocation overhead, depend on the manager executable, or silently fall back to a different system binary.

Our imaginary tool manager should keep the **stable logical command** and discard the surprising fallback behavior.

## Volta: one shim runtime, platform-specific publication

Current Volta source at `volta-cli/volta@5eedd5fb2f682baceb47a242289111fcd79435a5` has a dedicated shim layer.

Source:

- https://github.com/volta-cli/volta/blob/5eedd5fb2f682baceb47a242289111fcd79435a5/crates/volta-core/src/shim.rs

On Unix, creating a shim means symlinking the command name to a shared `volta-shim` executable.

On Windows, Volta writes a `.cmd` script:

```cmd
@echo off
volta run %~n0 %*
```

and a Git Bash script that similarly calls `volta run` using the invoked basename.

Useful lesson:

```text
public command name -> stable dispatcher -> current logical tool choice
```

can be implemented without public files pointing directly at one installed version.

### What I would change

Volta's Windows shim depends on the main `volta` command remaining callable. For our package-tool layer, I would prefer a tiny native launcher protocol that can resolve the active generation itself.

Reason:

```text
managed application should still launch if the main package-manager binary was moved or is being repaired
```

The launcher should know almost nothing: root identity, tool identity, entrypoint identity, active-generation lookup, and exec.

## mise: shims are convenient, but there are three sharp edges

Current mise docs at `jdx/mise@5c625afba01bcb9c91e9a26003e3a8fb07c2293c` describe its shims as small executables/symlinks to mise that intercept commands and load the selected context.

Source:

- https://github.com/jdx/mise/blob/5c625afba01bcb9c91e9a26003e3a8fb07c2293c/docs/dev-tools/shims.md
- https://github.com/jdx/mise/blob/5c625afba01bcb9c91e9a26003e3a8fb07c2293c/src/shims.rs

### Edge 1: shim sets need reconciliation

mise has `mise reshim`, and installation/update/removal normally causes reshim automatically. It also explains that package-manager-installed binaries can require shim refresh.

Our version cannot eliminate executable-set changes: a package upgrade may add or remove a console script.

But ordinary version upgrades where the entrypoint set is unchanged should never need public shim regeneration.

Desired rule:

```text
version changes -> active-generation pointer only
entrypoint-set changes -> reconcile stable launcher set
```

This narrows the public-filesystem mutation surface dramatically.

### Edge 2: `which` points at the shim

mise documents that shims obscure the actual executable path from ordinary `which`, and provides `mise which` for the resolved location.

Our CLI should embrace the distinction explicitly:

```text
$ which black
/home/leo/.local/bin/black

$ uv tool which black
/home/leo/.local/share/uv/tools/.uv/generations/T42/000015/env/bin/black
```

and perhaps:

```text
$ uv tool resolve black --json
{
  "public": "/home/leo/.local/bin/black",
  "tool": "black",
  "generation": 15,
  "target": ".../000015/env/bin/black"
}
```

The stable public path is a feature. The CLI gives a first-class way to see through it.

### Edge 3: silent fallback can violate managed-tool identity

mise currently documents a mode where an unresolved shim can fall back to the first same-named executable elsewhere on `PATH`. It explicitly warns that a command such as `python3` can therefore run an unrelated OS binary when the managed version cannot be resolved.

That is the opposite of the identity contract I want for our uv-like tool manager.

If `uv tool install black` owns the public `black` launcher, then:

```text
black
```

should either execute the active uv-managed `black` generation or fail clearly.

It should never silently become `/usr/bin/black` because local managed state is broken.

A managed launcher is an authority claim, not a fuzzy preference.

## asdf/pyenv-style reshim model: useful vocabulary, weaker fit for application tools

Classic version managers build a directory of shims from executables discovered in installed runtimes and regenerate it as available binaries change.

That works well when the core question is:

```text
which version of `python`, `ruby`, or `node` applies in this directory?
```

Our application-tool problem is narrower:

```text
which complete generation of this one explicitly installed tool currently owns `black`?
```

Because installation is explicit, we can record the entrypoint set in generation metadata and maintain ownership directly. We do not need to rediscover every executable in every environment on every reshim.

## Stable shim contract for our product

Each public launcher carries or resolves:

```text
root identity
tool identity
entrypoint identity
launcher schema
```

It does **not** carry:

```text
current package version
current generation number
final interpreter path
```

Those belong behind the active pointer.

Healthy invocation:

```text
public `black`
  ↓
launcher identity R1/T42/black
  ↓
active T42 = generation 15
  ↓
generation 15 launch manifest
  ↓
execute black target
```

## Failure behavior

### Tool root moved or replaced

Embedded path finds a directory with a different root ID:

```text
error: The `black` launcher no longer points to its uv tool root

hint: Run `uv tool repair black --dry-run` to preview re-exposing this launcher
```

No PATH fallback.

### Active pointer missing

```text
error: Tool `black` has no active generation

hint: Run `uv tool repair black --dry-run` to preview recovery from recorded install metadata
```

No PATH fallback.

### Active generation incomplete

```text
error: Tool `black` points to incomplete generation 15
  Caused by: expected entrypoint is missing: <path>

hint: Run `uv tool rollback black` to return to generation 14, or preview repair with `uv tool repair black --dry-run`
```

The availability of rollback can be checked before rendering the hint.

### Entrypoint retired by the active generation

Suppose the public launcher still exists briefly after an upgrade that removed `blackd`:

```text
error: Entrypoint `blackd` is no longer provided by tool `black`

hint: Run `uv tool repair black` to remove the stale uv-owned launcher
```

This is better than running old generation code behind the user's back.

## Performance budget

A stable launcher only earns acceptance if healthy invocation stays cheap.

Target hot path:

```text
0 network calls
0 package resolution
0 global inventory scan
0 mutation locks
1 root-id check (cacheable / compact)
1 active-generation read
0-1 launch-manifest reads
exec target
```

We could reduce this further with a compact active record that contains the entrypoint's generation-relative target directly.

The product test should benchmark shim overhead against direct environment execution, including Windows process-start cost.

## Launcher schema compatibility

Stable shims create a long-lived compatibility surface.

Keep it aggressively small and versioned:

```text
schema 1: root path + root ID + tool ID + entrypoint
```

New uv should continue launching old schema shims for a reasonable compatibility window and `doctor` can offer to refresh them.

If an old uv sees a newer launcher schema, it leaves the public file alone and reports it as newer managed state.

## Self-update interaction

A nice property of a standalone launcher protocol is that installed tools can keep running while the uv executable itself is replaced.

That suggests a clean authority split:

```text
uv command       -> manages catalog, generations, repair
stable launcher  -> resolves one already-published active generation
```

The launcher does not need to understand resolution, indexes, virtualenv creation, locks, or migration policy.

## VDFL decision

Steal from Volta:

- stable interception layer;
- one logical command can resolve current tool state at invocation time;
- platform-specific shim implementations behind one product contract.

Steal from mise:

- explicit `which`/resolution introspection;
- automatic reconciliation when executable sets change;
- documentation that treats shim behavior as a real product tradeoff.

Reject:

- silent system fallback for a broken managed launcher;
- requiring reshim for ordinary version changes;
- making the whole package manager part of every launch hot path;
- treating the shim path as sufficient observability for users.

Our command should be stable, owned, inspectable, and boring. The active generation behind it is allowed to change quickly.
