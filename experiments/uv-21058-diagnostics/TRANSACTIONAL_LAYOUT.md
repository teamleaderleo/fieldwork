# Cross-platform transactional tool layout

## In simple words

The generation/rollback idea in `VDFL_VISION.md` gets harder at the public executable boundary.

Current uv can publish a Unix entrypoint as a symlink directly to the executable inside a tool environment. On Windows it copies the generated entrypoint executable into the public tool bin directory. Those Windows executables are uv trampolines that embed the Python path in PE resources.

So a new immutable environment generation is only half the job. We need one publication model that keeps the **logical tool generation, every public entrypoint, the lock, and the receipt** coherent across both platforms.

My preferred answer for our imaginary product is a stable launcher layer. Public commands identify the logical tool and entrypoint; one per-tool atomic generation pointer chooses the executable generation. Upgrades switch that one pointer after a complete candidate generation is ready.

This is an internal design exercise, not an upstream proposal.

## Current uv boundary we have to beat

Read against `teamleaderleo/uv` current `main` on 2026-08-12.

`finalize_tool_install()` currently does roughly this:

```text
create / locate tool environment
      ↓
find entrypoints inside that environment
      ↓
check public target paths for collisions
      ↓
publish each public executable
      ↓
write tool lock
      ↓
write tool receipt
```

The important platform split is in `crates/uv/src/commands/tool/common.rs`:

```rust
#[cfg(unix)]
replace_symlink(src, &target)?;

#[cfg(windows)]
fs_err::copy(src, &target)?;
```

with a special self-replacement path on Windows.

The tool receipt is added only after public entrypoints are installed and the tool lock is written.

That ordering explains why a late receipt failure can coexist with already-changed environment or launcher state: publication has more than one durable owner and more than one commit point.

## Windows gives us provenance data

`uv-trampoline-builder` already defines a Windows `Launcher` containing:

```rust
pub struct Launcher {
    pub kind: LauncherKind,
    pub python_path: PathBuf,
    pub script_data: Option<Vec<u8>>,
}
```

The Python path is stored as a PE resource named `UV_PYTHON_PATH`, and `Launcher::try_from_path()` can read it back from an executable.

That is useful beyond launch itself. A tool manager can ask of an existing public `.exe`:

```text
is this one of our launchers?
which interpreter path does it target?
which launcher kind is it?
```

Our version would embed **logical ownership identity** too:

```text
UV_TOOL_ROOT_ID
UV_TOOL_ID
UV_ENTRYPOINT_ID
UV_LAUNCHER_SCHEMA
```

A copied public launcher can then prove which managed root/tool/entrypoint published it without depending on a possibly corrupt receipt.

This is especially attractive for receipt-loss recovery on Windows, where symlink target inspection is unavailable as the ordinary provenance mechanism.

## Candidate publication designs

### P0 — current style with better transaction receipts

Keep public entrypoints generation-specific.

```text
public black -> generation 12
public blackd -> generation 12
```

Upgrade builds generation 13, then replaces public entrypoints one by one, then records the new receipt.

Advantages:

- small conceptual delta;
- current Unix symlinks and Windows copied trampolines remain useful;
- retaining generation 12 means an old launcher stays executable during transition.

Weakness:

```text
black  -> generation 13
blackd -> generation 12
```

can exist during publication.

A transaction journal can detect and finish this state later, but it cannot make several unrelated public filesystem paths switch atomically.

Disposition: useful incremental design, weaker final model.

### P1 — public links target a stable `current` path

Unix can do:

```text
~/.local/bin/black
  -> <tool-root>/black/current/bin/black

<tool-root>/black/current
  -> generations/13
```

Then switching `current` changes every public symlink target transitively.

Advantages:

- one atomic directory-pointer switch can change all entrypoints;
- public symlinks rarely need rewriting;
- rollback is one pointer switch.

Windows problem:

Current copied trampolines embed an interpreter path. Copying a launcher produced inside `generations/13` gives it a generation-specific Python path. Windows symlink behavior also has privileges/platform constraints we should avoid making part of the product contract.

Disposition: excellent Unix implementation technique, incomplete cross-platform contract.

### P2 — stable uv-owned shims + per-tool active-generation pointer

This is my preferred model.

Public executable:

```text
~/.local/bin/black
```

is a stable uv-owned launcher whose durable identity is:

```text
root_id = R1
tool_id = T42
entrypoint = black
```

It does **not** permanently embed generation 13.

At invocation it resolves one small piece of current state:

```text
T42 -> generation 13
```

and dispatches the corresponding entrypoint from that complete generation.

Conceptually:

```text
black launcher ─┐
blackd launcher ├──▶ tool T42 active generation = 13
ruff-lsp ...    │
                └──▶ generation 13 manifest maps entrypoint -> executable
```

Switching one atomic per-tool pointer changes every entrypoint for that tool together.

Rollback changes the same pointer back to 12.

## What the stable launcher should resolve

Avoid turning every command invocation into a heavyweight package-manager operation.

The hot-path data should be tiny and local.

One possible layout:

```text
<tool-root>/.uv/active/T42
    contains: 000013\n
<tool-root>/.uv/generations/T42/000013/launch.toml
```

or one compact binary/JSON record:

```json
{
  "schema": 1,
  "generation": 13,
  "entrypoints": {
    "black": "env/bin/black",
    "blackd": "env/bin/blackd"
  }
}
```

The launcher algorithm:

```text
read root/tool identity from embedded launcher metadata
      ↓
read active generation pointer
      ↓
read/derive executable for this entrypoint
      ↓
exec/spawn it preserving argv, stdio, cwd and exit code
```

The pointer format should be small enough that invocation can use one or two local reads with no lock in the healthy path.

## Make the generation pointer self-validating

A pointer to a missing generation would be a nasty new failure class.

So publication should obey:

```text
generation directory exists
+ generation manifest validates
+ interpreter exists
+ every required entrypoint exists
+ receipt/lock/spec generation metadata agrees
        ↓
only then publish active pointer
```

The launcher can still fail clearly if disk corruption occurs later:

```text
error: Tool `black` points to an incomplete generation 13
  Caused by: expected executable is missing: <path>

hint: Run `uv tool repair black --dry-run` to preview recovery
```

## Generation contents

I would co-locate the things that describe one executable generation:

```text
<root>/.uv/generations/T42/000013/
├── env/
├── receipt.toml
├── uv.lock
├── launch.toml
└── complete
```

`complete` is written last or represented by an atomic final directory rename.

The independent desired `ToolSpec` remains outside the generation:

```text
<root>/.uv/catalog/T42/spec.toml
```

because desired state must survive throwing a broken generation away.

## Publication algorithm

```text
1. acquire tool T42 mutation lock
2. read active generation = 12
3. resolve/build candidate under staging/tx-ID
4. write receipt + lock + launch manifest into staging
5. validate candidate by launching its expected entrypoints in a bounded smoke mode where feasible
6. publish staging as immutable generation 13
7. atomically change active/T42 from 12 -> 13
8. release lock
9. garbage-collect old generations later
```

The only user-visible commit point is step 7.

A failure before step 7 leaves generation 12 active.

A process death after step 7 leaves generation 13 active and complete. Cleanup is secondary.

That is the transaction boundary I want.

## Entry-point set changes become easier

Suppose generation 12 exposes:

```text
black
blackd
```

and generation 13 drops `blackd`.

Stable launcher ownership lets us separate **activation** from **public-name garbage collection**.

Before pointer switch:

- create any newly required stable launchers;
- verify existing launchers are still uv-owned.

Switch 12 -> 13.

After switch:

- `black` resolves generation 13;
- stale `blackd` launcher sees that entrypoint is absent from active generation and can produce a precise retired-entrypoint error for a short grace interval;
- cleanup removes `blackd` only if the public file still carries the same root/tool/entrypoint ownership metadata.

This is safer than deleting the old public entrypoint before the replacement generation is committed.

A temporary friendly failure is also better than silently executing stale generation 12 code after generation 13 became authoritative.

## Should a stable shim call uv itself?

I would avoid requiring the full `uv` executable on every tool invocation.

Two approaches:

### Tiny native shim

Embed the generation resolver in the launcher itself.

Pros:

- tool keeps launching even if the main uv binary moves;
- minimal startup process chain;
- Windows already has native trampoline machinery to build on.

Cons:

- launcher protocol becomes a persistent compatibility contract;
- upgrades must support older shim schemas for a while.

### Central dispatcher executable

Every public command points at one `uv-tool-launcher` binary and passes identity through argv0/metadata.

Pros:

- one implementation to update;
- tiny public wrappers possible;
- richer diagnostics centrally.

Cons:

- dispatcher becomes shared critical state;
- replacing it safely is another publication problem;
- argv0/symlink semantics vary.

My preference: **tiny versioned launcher protocol, deliberately boring.** The launcher only resolves a generation and executes a path. Health/repair logic stays in uv.

## Windows implementation direction

Current uv already carries architecture-specific native trampoline binaries and writes PE resources into them. For our product I would extend that format so the launcher resource contains logical identity instead of only the final interpreter path.

Illustrative resources:

```text
UV_TRAMPOLINE_KIND = tool-entrypoint
UV_TOOL_ROOT_ID = R1
UV_TOOL_ID = T42
UV_ENTRYPOINT = black
UV_LAUNCHER_SCHEMA = 2
```

The launcher discovers the tool root through a stable per-user locator or an embedded root path + root ID check, then resolves the current generation.

Embedding both `root_path` and `root_id` is attractive:

```text
path tells us where to look
id proves it is still the same managed root
```

If the directory was moved, repair can rewrite/re-expose the launcher. If the path now contains a different root ID, the launcher refuses to execute foreign state.

## Unix implementation direction

Unix has more choices.

The simplest cross-platform-consistent answer is to use the same logical launcher concept everywhere, even though symlinks could do more.

A lighter Unix implementation could use:

```text
public black -> <root>/.uv/launchers/T42/black
```

where that stable script/binary reads `active/T42`.

This avoids public symlinks pointing directly into mutable/versioned environment directories.

Consistency wins here: the product contract is one logical launcher model; the platform implementation can optimize internally.

## Public executable provenance becomes recoverable

With embedded identity, `uv tool doctor` can inspect every executable it believes it owns.

Expected record:

```text
catalog says:
  T42 owns ~/.local/bin/black as entrypoint `black`

actual launcher says:
  root R1 / tool T42 / entrypoint black / schema 2
```

Results:

```text
match
    -> healthy exposure

file missing
    -> confidently recreate stable launcher

foreign file
    -> preserve; report ownership conflict

uv launcher for different tool
    -> report internal ownership conflict

old launcher schema
    -> rewrite launcher if backward-compatible
```

This gives us a solid repair path after receipt loss because entrypoint ownership has independent evidence.

## Exposure catalog and launcher metadata cross-check each other

I would keep both.

Catalog:

```text
what uv intended to expose
```

Launcher metadata:

```text
what this public file claims to be
```

Filesystem file identity/hash:

```text
whether it is still the same file uv published
```

No single one has to carry all authority.

This helps detect stale copied launchers, user replacements, cross-tool collisions, and partial publication.

## What about scripts without native launchers?

A Python console script installed in the environment can remain generation-local. The public stable shim is the only durable exposure.

For special arbitrary executable files from a package, the generation manifest records the target relative path.

The public layer stays consistent regardless of what the package produced internally.

## Concurrency

Two upgrades of the same tool serialize on `T42`.

Different tools may build concurrently.

Exposure-name conflicts require a short global exposure-catalog lock only around reservation/publication of names such as `black`.

Conceptually:

```text
build T42 gen13 ──────────────┐
                              ├─ acquire exposure reservation if set changes
build T99 gen8 ───────────────┘

per-tool active pointer switch remains independent
```

Avoid holding a global tools lock while network resolution/building occurs.

This is a place where our imaginary redesign could improve concurrency as well as correctness.

## Crash table

| Failure point | Visible state | Next action |
| --- | --- | --- |
| resolution fails | gen12 active | report error |
| build gen13 fails | gen12 active + staging residue | remove/quarantine staging later |
| generation validation fails | gen12 active + rejected gen13 | retain brief forensic record or delete staging |
| process dies before active switch | gen12 active + complete unreferenced gen13 | doctor offers cleanup or resume |
| active pointer switch completes | gen13 active | success boundary reached |
| process dies after active switch | gen13 active + gen12 retained | cleanup later |
| stale public launcher cleanup fails | gen13 active; stale owned name may remain | doctor/repair reconciles exposure catalog |
| foreign file occupies new entrypoint | gen12 stays active | no generation switch; ask user to resolve ownership/force |

The active generation never depends on completing post-switch deletion.

## Upgrade output becomes wonderfully simple

Success:

```text
Upgraded ruff 0.12.3 -> 0.12.4
Generation: 14 -> 15
```

Failure before commit:

```text
error: Failed to prepare upgrade for `ruff`
  Caused by: ...

Current generation 14 is unchanged.
```

A sentence like `Current generation 14 is unchanged` is powerful because the transaction model makes it literally true.

Rollback:

```text
$ uv tool rollback ruff
Rolled back ruff 0.12.4 -> 0.12.3
Generation: 15 -> 14
```

No package resolution required.

## Relationship to the diagnostic thunderdome

The original invalid-directory problem asks how to talk about damaged inventory.

This design tries to reduce how often ambiguous damage occurs in the first place:

- reserved `.uv/` namespace keeps internal state out of package-name enumeration;
- root marker distinguishes owned state from a wrong custom root;
- catalog keeps desired intent outside mutable environments;
- immutable generations avoid in-place half-upgrades;
- one active pointer defines executable authority;
- stable launcher metadata preserves public-entrypoint ownership;
- findings can propose repairs from redundant evidence.

The diagnostic system then has better facts to report.

## Revised VDFL preference

After reading current Unix/Windows publication code, I would upgrade the earlier proposal from “maybe stable launchers” to:

> **Stable logical launchers are part of the product model. Tool generations are immutable; one per-tool active-generation pointer is the executable authority.**

Unix symlinks and Windows PE trampolines become platform implementations of that model rather than separate behavioral contracts.

The extra launcher indirection earns its keep through atomic activation, rollback, provenance, receipt-loss recovery, and fewer public-file mutations during ordinary upgrades.
