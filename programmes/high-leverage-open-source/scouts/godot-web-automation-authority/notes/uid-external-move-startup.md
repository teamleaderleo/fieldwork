# Godot UID external-move startup candidate

## In simple words

Godot's UID system explicitly aims to preserve references when files move outside the editor, including file-manager, IDE, command-line, and version-control moves while the editor is closed. Script/shader `.uid` sidecars are designed to travel with those files.

Current startup ordering exposes a possible gap: Godot loads the centralized `.godot/uid_cache.bin`, then eagerly converts UID-backed autoloads to paths with `ProjectSettings::fix_autoload_paths()`. If the centralized cache already knows the UID but still points to the pre-move path, `ResourceUID::get_id_path()` returns that stale path. Its editor scan fallback only runs when the UID itself is missing from the cache.

Later editor filesystem/import work can discover the moved sidecar and call `set_id(uid, current_path)`, but a direct game launch has no editor scan before autoload loading. A UID-backed autoload is therefore a strong test of whether external-move resilience extends to cold runtime startup with a stale existing cache entry.

State: source-read + documented-workflow + exact integration fixture prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

Key paths:

- `core/io/resource_uid.cpp`
- `core/config/project_settings.cpp`
- `editor/file_system/editor_file_system.cpp`
- `main/main.cpp`
- `doc/classes/ResourceUID.xml`

Official workflow context: Godot's UID 4.4 rollout and 4.4 documentation describing external filesystem/VCS moves as a supported UID use case.

## Intended move semantics

The current ResourceUID class reference says UIDs allow references between resources to remain intact when files are renamed or moved.

The 4.4 UID rollout goes further: it describes moving files outside Godot—using the OS file manager, an IDE, command line, or version-control changes while the editor is closed—as a workflow the universal UID system is intended to handle. For scripts/shaders, the `.uid` sidecar must travel with the resource and should be committed to version control.

This makes a stale-central-cache/external-move case materially different from an arbitrary corrupted-cache experiment.

## Startup ordering

At startup, `Main::setup()` loads `uid_cache.bin`. It then calls:

```cpp
ProjectSettings::get_singleton()->fix_autoload_paths();
```

`fix_autoload_paths()` is simple and eager:

```cpp
for (KeyValue<StringName, AutoloadInfo> &kv : autoloads) {
    kv.value.path = ResourceUID::ensure_path(kv.value.path);
}
```

A UID-backed autoload is therefore converted into a concrete path before normal project startup.

## Stale-existing-entry branch

`ResourceUID::get_id_path()` has an editor-only recovery callback that can trigger `EditorFileSystem::scan_for_uid()`, but only when the requested UID is absent from the current cache.

If the UID already exists and maps to an old path, the lookup returns the old path immediately. The sidecar at the moved path is not consulted in this branch.

This is the key hypothesis: **existing-but-stale and missing UID entries have different startup recovery behavior.**

## Later editor reconciliation

The editor's first UID scan initially adds UIDs that are absent from the cache. Later filesystem/import scan paths are stronger: when they encounter a file whose UID is already known, they call `ResourceUID::set_id(uid, current_path)` and update the centralized cache.

That provides a plausible repair path after editor discovery. It does not help a direct game/runtime process that needs an autoload before such discovery exists.

## Game autoload loading

`Main::start()` copies the current autoload list and loads each already-resolved `AutoloadInfo.path` directly. Packed scenes are assigned/reloaded at that path; scripts use `ResourceLoader::load(info.path)`.

If the UID was resolved to an absent pre-move path during `fix_autoload_paths()`, the runtime has no obvious later opportunity to recover from the moved `.uid` sidecar before the autoload fails.

## Active exact experiment

`playgrounds/EXP-20260809-godot-uid-external-autoload/` uses Godot's tested UID pair `1` / `uid://b`.

Actual resource state:

```text
res://moved/autoload.gd
res://moved/autoload.gd.uid -> uid://b
```

Absent old path:

```text
res://old/autoload.gd
```

Project setting:

```ini
[autoload]
Moved="*uid://b"
```

`prepare.py` creates a deliberately stale centralized cache:

```text
UID 1 -> res://old/autoload.gd
```

The execution sequence is:

1. prepare and inspect stale cache;
2. direct headless game launch;
3. editor/import discovery pass;
4. inspect cache again;
5. fresh direct headless game launch.

The moved autoload prints its actual script resource path on enter/ready. The main scene prints whether `/root/Moved` exists, the current UID→path result, and physical existence of old/new paths.

## Distinguishing outcomes

### Startup gap reproduced

First direct runtime resolves UID to old path and misses the autoload, while an editor discovery pass updates the cache to the moved path and a later runtime succeeds.

This would be a consequential external-move regression at a cold-start dependency boundary.

### Runtime self-repairs

First direct runtime discovers the new `.uid` sidecar despite the stale existing cache entry. Stop the hypothesis and map the missing discovery path.

### Editor needs restart after repair

The filesystem scan updates `uid_cache.bin`, but the current editor process has already replaced the UID-backed autoload path with the old concrete path. A restart may be required before the corrected cache is used for autoload resolution. Record this separately if observed.

### Import-only control is insufficient

If `--import` does not reach the correcting filesystem path, use a normal editor startup/quit as the repair control. This is a harness distinction.

## Candidate directions only after execution

Possible repair areas include:

1. validate cached UID paths before eagerly replacing UID-backed startup settings;
2. if a cached path is missing in tools builds, trigger UID discovery even when the UID key exists;
3. preserve UID form for startup settings until actual resource load, allowing a missing cached path to invoke a broader lookup strategy;
4. generate or consume a runtime-safe UID index whose path mappings are guaranteed current before game launch/export.

A runtime-wide recursive sidecar scan would have startup-cost implications, so avoid choosing a design before measuring the actual failure and existing editor/export guarantees.

## Overlap

Targeted current issue/PR searches for stale UID cache + external move + autoload/sidecar found no matching active or historical repair in the connected search results.

## Evidence boundary

Supported: documented external-move goal; eager startup autoload conversion; stale-existing-entry behavior in `get_id_path()`; later editor `set_id()` reconciliation; direct autoload loading from resolved paths.

Prepared: exact stale-cache + moved-script/sidecar autoload fixture, cache preparer, and cache inspector.

Unknown: target runtime result; whether `--import` performs sufficient repair; whether a normal editor restart is required; platform breadth; intended cold-runtime handling of externally moved development resources.

Automated upstream contact is prohibited.
