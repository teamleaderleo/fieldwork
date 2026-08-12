# VDFL tool-manager CLI experience

## In simple words

This is what I would want our imaginary uv-like tool manager to feel like in ordinary use.

Most commands stay terse when the state is healthy. The extra machinery appears when it earns its keep: status can explain observed state, doctor produces typed findings, repair previews actions before applying them, upgrades have a single activation point, rollback is cheap, uninstall deactivates before cleanup, and machine output carries the same facts without scraping prose.

This is product-fiction backed by the state model in the neighboring files, not an upstream proposal.

## Healthy install

```text
$ uv tool install black
Resolved 8 packages
Installed black 25.1.0
Exposed: black, blackd
Generation: 1
```

The generation line is useful because it establishes vocabulary the user will later see in rollback/repair. It can stay hidden in a quieter default if normal output feels too technical.

Verbose mode:

```text
$ uv tool install black -v
Tool root: /home/leo/.local/share/uv/tools (claimed, schema 1)
Recorded desired spec: black
Prepared generation 1
Validated 2 entrypoints
Activated generation 1
Exposed: black, blackd
```

## Healthy list stays simple

```text
$ uv tool list
black 25.1.0
- black
- blackd

ruff 0.12.4
- ruff
```

`tool list` answers the ordinary question: what applications do I have?

It does not become a wall of health metadata merely because we have better internals.

## `tool status` answers what is actually there

```text
$ uv tool status
Tool directory: /home/leo/.local/share/uv/tools
Inventory: complete

black 25.1.0   generation 1   healthy
ruff  0.12.4   generation 7   healthy

2 tools, 3 entrypoints, 0 findings
```

A degraded state:

```text
$ uv tool status
Tool directory: /home/leo/.local/share/uv/tools
Inventory: complete with findings

black 25.1.0   generation 1   healthy
ruff  0.12.4   generation 7   degraded

! F3103 missing owned launcher
  expected: /home/leo/.local/bin/ruff

2 tools, 1 finding
```

`status` stays read-only and cheap: no index refresh, no upgrade resolution, no broad environment rebuild.

## `tool doctor` goes deeper

```text
$ uv tool doctor
Checking tool root...
Checking desired specs...
Checking active generations...
Checking receipts and locks...
Checking entrypoint ownership...
Checking interpreters...

black  healthy
ruff   degraded

F3103 missing owned launcher
  tool: ruff
  path: /home/leo/.local/bin/ruff
  recovery: recreate stable launcher
  confidence: certain
  safety: reversible

1 finding
```

Optional expensive verification:

```text
uv tool doctor --full
```

could hash expected generation members, validate more package metadata, or launch bounded interpreter probes.

The default doctor should finish quickly enough that people actually use it.

## Repair is a plan first

```text
$ uv tool repair --dry-run
Repair plan

1. F3103 ruff — recreate missing stable launcher
   path: /home/leo/.local/bin/ruff
   confidence: certain
   safety: reversible

No package resolution or environment rebuild required.
```

Apply:

```text
$ uv tool repair
Recreated launcher: /home/leo/.local/bin/ruff
Re-inspected tool state
All tools healthy
```

A repair plan can mix automatic and manual findings:

```text
$ uv tool repair --dry-run
Repair plan

1. F1001 unexpected invalid-name directory
   path: /home/leo/.local/share/uv/tools/tool backup
   action: move to uv quarantine
   confidence: certain
   safety: reversible

2. F1204 receipt unreadable
   path: /opt/shared/uv/black/uv-receipt.toml
   error: Permission denied
   automatic action: none

1 applicable repair; 1 unresolved finding
```

## Wrong custom root gets stopped early

```text
$ UV_TOOL_DIR=$HOME uv tool status
error: The configured tool directory is not initialized for uv
  Caused by: `UV_TOOL_DIR` points to `/home/leo`

hint: Check `UV_TOOL_DIR`, or initialize a dedicated tool directory if this location is intended for uv tools
```

Mutating commands go no further.

Read-only inspection could offer:

```text
uv tool doctor --unclaimed-root /home/leo
```

for deliberate forensic use, but it still would not classify arbitrary children as managed tools.

## Invalid child in a claimed root

```text
$ uv tool upgrade --all
error: Failed to inspect installed tools
  Caused by: Invalid tool directory name: `/home/leo/.local/share/uv/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Run `uv tool repair --dry-run` to preview a reversible recovery
```

Then:

```text
$ uv tool repair --dry-run
F1001 invalid tool directory name
  path: /home/leo/.local/share/uv/tools/tool backup
  action: quarantine unexpected directory
  destination: /home/leo/.local/share/uv/tools/.uv/quarantine/2026-08-12/tool backup
  confidence: certain
  safety: reversible
```

Apply:

```text
$ uv tool repair
Moved unexpected directory to uv quarantine
Inventory: complete
```

The original directory is preserved until the user chooses to discard it.

## Healthy upgrade

```text
$ uv tool upgrade black
Prepared black 25.2.0
Activated generation 2
Upgraded black 25.1.0 -> 25.2.0
```

The key promise is implicit:

```text
"Activated generation 2" means the new receipt, lock, environment and launch manifest were already complete.
```

More compact default:

```text
Upgraded black 25.1.0 -> 25.2.0
```

with generation detail under `-v`.

## Failed upgrade before activation

```text
$ uv tool upgrade black
error: Failed to prepare upgrade for `black`
  Caused by: <build/install error>

Current version 25.1.0 (generation 1) is unchanged.
```

That last line is only printed because the publication model can prove it.

This is the kind of reassurance worth designing internals around.

## Crash before activation

No special recovery flow should be necessary for the user:

```text
$ black --version
black, 25.1.0
```

Later:

```text
$ uv tool doctor
info: Found unreferenced complete generation 2 for `black`
  active generation: 1
  recovery: remove unreferenced generation, or inspect it
```

If the generation was merely staging/incomplete, doctor reports abandoned staging instead.

## Upgrade that drops an entrypoint

Old generation:

```text
black
blackd
```

New generation:

```text
black
```

After activation, before stale-launcher cleanup finishes:

```text
$ black
# runs new active generation
```

```text
$ blackd
error: Entrypoint `blackd` is no longer provided by tool `black`

hint: Run `uv tool repair black` to remove the stale uv-owned launcher
```

It never executes the previous generation simply because the old public name still exists.

## Upgrade that adds an entrypoint

Preflight all new public names before activation.

If clear:

```text
$ uv tool upgrade foo
Upgraded foo 1.0 -> 2.0
New entrypoint: foo-admin
```

If a foreign file already occupies it:

```text
$ uv tool upgrade foo
error: Cannot expose new entrypoint `foo-admin`
  Caused by: `/home/leo/.local/bin/foo-admin` already exists

existing owner: outside uv
requested owner: uv tool `foo`

Current version 1.0 (generation 8) is unchanged.
```

The candidate generation may exist off to the side, but activation stays on generation 8.

## `--force` becomes an explicit ownership decision

```text
$ uv tool install black --force
Plan:
  replace foreign executable: /home/leo/.local/bin/black
  install tool: black 25.1.0

Proceed? [y/N]
```

For scripts/CI:

```text
uv tool install black --force --yes
```

or a narrower capability:

```text
uv tool install black --replace-executable /home/leo/.local/bin/black
```

I like narrow authority better than one magical force flag, though the familiar `--force` can remain as shorthand.

## Rollback is boring and wonderful

```text
$ uv tool history black
* 3  black 25.2.1   active
  2  black 25.2.0
  1  black 25.1.0
```

```text
$ uv tool rollback black
Rolled back black 25.2.1 -> 25.2.0
Generation: 3 -> 2
```

No network, resolver, build, or reinstall.

Specific generation:

```text
uv tool rollback black --to 1
```

Rollback should refuse a generation that doctor marks incomplete/corrupt.

## Uninstall deactivates first

The logical commit point for uninstall is:

```text
active generation -> uninstalled tombstone
```

Then every stable launcher stops executing the tool together.

Conceptually:

```text
1. lock tool
2. verify exposure ownership
3. atomically publish uninstalled state
4. remove uv-owned public launchers
5. remove/retain generations according to history policy
6. remove desired spec
7. release lock
```

If cleanup fails after step 3, the application remains uninstalled from the executable-authority point of view.

Example:

```text
$ uv tool uninstall black
Uninstalled black
Removed: black, blackd
```

Cleanup failure:

```text
$ uv tool uninstall black
Uninstalled black
warning: Could not remove owned launcher `/home/leo/.local/bin/blackd`: Permission denied

hint: Run `uv tool repair` after correcting access to finish cleanup
```

`blackd` should detect the uninstalled/tombstoned tool if invoked, rather than launching an old generation.

## Foreign replacement during uninstall is preserved

Suppose uv originally created `/home/leo/.local/bin/black`, then another installer/user replaced it.

```text
$ uv tool uninstall black
Uninstalled black
warning: Preserved `/home/leo/.local/bin/black`: the current file is no longer the launcher uv published
```

This is a success with a cleanup finding, because deleting that foreign replacement would exceed uv's authority.

Machine output records the unresolved exposure finding.

## Audit has explicit coverage semantics

Clean complete audit:

```text
$ uv tool audit --all
Audited 5 tools
No known vulnerabilities found
exit: 0
```

Complete with findings:

```text
$ uv tool audit --all
Audited 5 tools
2 vulnerabilities found
exit: 1
```

Incomplete:

```text
$ uv tool audit --all
Audited 4 of 5 selected tools

error: Audit coverage is incomplete
  skipped ruff: active generation metadata is unreadable

exit: 2
```

JSON carries:

```json
{
  "schema": 1,
  "complete": false,
  "selected": 5,
  "audited": 4,
  "results": [],
  "findings": [
    {
      "code": "F4201",
      "kind": "audit_target_unreadable",
      "tool": "ruff"
    }
  ]
}
```

The empty `results` list cannot be mistaken for complete success because `complete` is a first-class field and exit 2 agrees.

## Machine output is a separate contract

```text
uv tool status --output json
uv tool doctor --output json
uv tool repair --dry-run --output json
uv tool history black --output json
```

Human wording can get prettier without breaking scripts.

Version machine schemas:

```json
{
  "schema": 1,
  "complete": true,
  "data": {},
  "findings": []
}
```

Unknown fields are additive; incompatible semantic changes bump schema.

## `tool which` sees through stable launchers

```text
$ which black
/home/leo/.local/bin/black
```

```text
$ uv tool which black
/home/leo/.local/share/uv/tools/.uv/generations/T42/000004/env/bin/black
```

Verbose:

```text
$ uv tool which black --verbose
Public launcher: /home/leo/.local/bin/black
Root: R1 (/home/leo/.local/share/uv/tools)
Tool: black (T42)
Generation: 4
Target: .../000004/env/bin/black
```

No silent fallback to `/usr/bin/black` if managed resolution fails.

## Export desired tools

```text
$ uv tool export
[tool.black]
requirement = "black>=25"

[tool.ruff]
requirement = "ruff==0.12.4"
python = ">=3.12"
```

Recreate elsewhere:

```text
uv tool sync tools.toml
```

Dry run:

```text
uv tool sync tools.toml --dry-run
```

This gives users a clean escape hatch from local manager-state loss.

## Garbage collection is explicit

```text
$ uv tool gc --dry-run
Would remove:
  black generation 1 (25.1.0)
  2 abandoned staging directories
  1 quarantined object older than retention policy

Would retain:
  black generation 4 (active)
  black generation 3 (rollback retention)
```

Quarantine GC should have a longer/default-conservative retention and clear path display.

## Shared roots need explicit policy

A custom root used by several users should declare that intent in its root marker.

Conceptually:

```toml
schema = 1
kind = "uv-tool-root"
scope = "shared-group"
group = "developers"
```

Then lock creation, generations, catalog files, and cleanup can enforce one permission policy deliberately.

I would avoid trying to infer safe multi-user semantics from whatever ownership bits happen to exist on the first `.lock` file.

For a simple first release, `scope = "user"` only is entirely respectable. Shared roots can arrive when we can test them properly across Unix ownership, containers/network filesystems, and Windows ACLs.

## Commands I would actually ship

Core:

```text
uv tool install
uv tool run / uvx
uv tool list
uv tool upgrade
uv tool uninstall
uv tool dir
```

State and recovery:

```text
uv tool status
uv tool doctor
uv tool repair
uv tool which
uv tool history
uv tool rollback
uv tool gc
uv tool export
uv tool sync
```

I would resist adding separate commands for every finding family. `doctor` discovers; `repair` plans/applies; finding codes carry specificity.

## Personality of the CLI

Healthy state:

```text
short, quick, pleasantly boring
```

Damaged state:

```text
precise object
precise uncertainty
stable finding code
safe next action
```

Recovery:

```text
preview first
preserve foreign/ambiguous state
make the commit point explicit
re-inspect afterward
```

That is the version of uv I would enjoy depending on for ten years.
