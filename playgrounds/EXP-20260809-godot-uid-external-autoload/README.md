# EXP-20260809-godot-uid-external-autoload

This probe isolates a startup question in Godot's UID workflow: a resource and its `.uid` sidecar have been moved externally while the centralized `.godot/uid_cache.bin` still names the old path.

The fixture uses a UID-backed autoload because autoload paths are resolved very early during engine startup.

## Fixture

The UID pair is deliberately `1` / `uid://b`, which Godot's own ResourceUID unit test verifies as an encode/decode round trip.

Actual resource:

```text
res://moved/autoload.gd
res://moved/autoload.gd.uid -> uid://b
```

The old path is absent:

```text
res://old/autoload.gd
```

`project.godot` stores the autoload as:

```ini
[autoload]
Moved="*uid://b"
```

`prepare.py` deliberately writes a stale `.godot/uid_cache.bin`:

```text
UID 1 / uid://b -> res://old/autoload.gd
```

## Source sequence under test

At the pinned Godot revision, startup loads the centralized UID cache and then calls `ProjectSettings::fix_autoload_paths()`. That method eagerly replaces UID-backed autoload paths with `ResourceUID::ensure_path()`.

`ResourceUID::get_id_path()` can request an editor filesystem UID scan when a UID is missing from the cache. An existing stale UID entry does not take that path; it returns its cached path.

Later editor scan/import paths do call `ResourceUID::set_id(uid, current_path)` and update the cache when they encounter the actual file and sidecar. A direct game/runtime launch has no editor filesystem pass before autoload loading.

## Run sequence

Prepare the deliberately stale cache:

```sh
python3 playgrounds/EXP-20260809-godot-uid-external-autoload/prepare.py
python3 playgrounds/EXP-20260809-godot-uid-external-autoload/inspect_cache.py
```

First direct runtime launch:

```sh
godot --headless --path playgrounds/EXP-20260809-godot-uid-external-autoload/godot
```

Then run an editor/import discovery pass:

```sh
godot --headless --path playgrounds/EXP-20260809-godot-uid-external-autoload/godot --import
```

Inspect the cache again:

```sh
python3 playgrounds/EXP-20260809-godot-uid-external-autoload/inspect_cache.py
```

Then launch the game directly again:

```sh
godot --headless --path playgrounds/EXP-20260809-godot-uid-external-autoload/godot
```

If `--import` alone does not reach the correcting scan path, repeat the repair control with a normal editor start/quit. That is a harness distinction, separate from the startup claim.

## Source-predicted first-run result

The first game launch should still resolve:

```text
uid://b -> res://old/autoload.gd
```

while:

```text
res://moved/autoload.gd exists
res://old/autoload.gd does not exist
```

The moved autoload would therefore fail before `main.gd` can report `has_moved=true`.

A successful repair control should eventually update the centralized cache to the moved path, after which a fresh direct runtime launch should instantiate the autoload and print:

```text
MOVED_AUTOLOAD_ENTER path=res://moved/autoload.gd
MOVED_AUTOLOAD_READY path=res://moved/autoload.gd
AUTOLOAD_STARTUP_RESULT has_moved=true resolved_uid_path=res://moved/autoload.gd moved_file_exists=true old_file_exists=false
```

## Why this case is consequential

Godot's UID documentation says resource references survive rename/move operations. The 4.4 UID rollout explicitly describes moves performed outside the editor—file manager, IDE, command line, or version control while the editor is closed—as a workflow the sidecar UID design is intended to support.

A runtime startup dependency such as an autoload is a strong test because it needs UID resolution before editor discovery can repair a stale centralized cache.

## Competing outcomes

1. **Startup gap reproduced:** direct runtime trusts the stale existing UID entry and misses the moved autoload; editor discovery repairs the cache; a later runtime succeeds.
2. **Runtime self-repairs:** the first direct launch discovers the moved sidecar despite the existing stale cache entry. Stop the hypothesis and locate the discovery path.
3. **Editor repair also requires restart:** scan updates the centralized cache while the current editor's already-resolved autoload list remains stale. Record this as a second lifecycle boundary.
4. **Fixture invalid:** sidecar or autoload syntax differs from the assumed format. Repair the harness before drawing conclusions.

## Evidence boundary

Source evidence supports the ordering and stale-existing-entry branch. Official UID documentation supports external move resilience as an intended workflow. Target execution is still required to establish actual startup behavior.

Automated upstream contact is prohibited.
