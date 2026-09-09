# Godot UID external-move startup candidate

## In simple words

Godot's UID system explicitly aims to preserve references when files move outside the editor, including file-manager, IDE, command-line, and version-control moves while the editor is closed. Script/shader `.uid` sidecars are designed to travel with those files.

Current startup ordering exposes a broader early-startup gap than the original autoload fixture suggested. Godot loads the centralized `.godot/uid_cache.bin`; when a UID already exists there but still maps to a pre-move path, `ResourceUID::get_id_path()` returns that stale path. Its editor scan fallback only runs when the UID itself is missing from the cache.

Two important startup consumers take that stale mapping before normal filesystem reconciliation can repair it:

- UID-backed **autoloads** are eagerly converted to paths by `ProjectSettings::fix_autoload_paths()` and then instantiated from the old path;
- a UID-backed **main scene** is converted directly with `ResourceUID::get_id_path(id)`, and an existing stale mapping bypasses the special missing-cache failure check before the engine later aborts loading the absent old scene.

The editor path is stronger than the original hypothesis too. The early UID scan deliberately skips UIDs that already exist in the cache, then the first editor scan creates autoloads before the later normal filesystem scan reaches the code that can `set_id(uid, current_path)`. A stale existing mapping can therefore break autoload creation during editor startup as well as direct runtime startup. Later scanning can repair the cache, but that repair happens after the autoload creation attempt.

State: source-strong across autoload + main-scene startup + documented-workflow + exact autoload integration fixture + owned-fork target-native workflow running; main-scene control queued for the next probe revision.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09/10.

Key paths:

- `core/io/resource_uid.cpp`
- `core/config/project_settings.cpp`
- `editor/file_system/editor_file_system.cpp`
- `editor/settings/editor_autoload_settings.cpp`
- `editor/settings/project_settings_editor.cpp`
- `main/main.cpp`
- `doc/classes/ResourceUID.xml`

Official workflow context: Godot's UID 4.4 rollout and 4.4 documentation describing external filesystem/VCS moves as a supported UID use case.

Owned-fork target-native carrier: https://github.com/teamleaderleo/godot/pull/3

## Intended move semantics

The current ResourceUID class reference says UIDs allow references between resources to remain intact when files are renamed or moved.

The 4.4 UID rollout goes further: it describes moving files outside Godot—using the OS file manager, an IDE, command line, or version-control changes while the editor is closed—as a workflow the universal UID system is intended to handle. For scripts/shaders, the `.uid` sidecar must travel with the resource and should be committed to version control.

This makes a stale-central-cache/external-move case materially different from an arbitrary corrupted-cache experiment.

## Shared stale-existing-entry branch

`ResourceUID::get_id_path()` has an editor-only recovery callback that can trigger `EditorFileSystem::scan_for_uid()`, but only when the requested UID is absent from the current cache.

If the UID already exists and maps to an old path, the lookup returns the old path immediately. The moved resource/sidecar is not consulted in this branch.

This is the key distinction: **existing-but-stale and missing UID entries have different startup recovery behavior.** The distinction matters anywhere an early startup consumer resolves a UID before normal editor discovery.

## Autoload startup ordering

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

`Main::start()` later copies the current autoload list and loads each already-resolved `AutoloadInfo.path` directly. Packed scenes are assigned/reloaded at that path; scripts use `ResourceLoader::load(info.path)`.

If the UID was resolved to an absent pre-move path during `fix_autoload_paths()`, the runtime has no obvious later opportunity to recover from the moved `.uid` sidecar before the autoload fails.

## Main-scene startup has the same stale-existing weakness

`Main::start()` handles a UID-backed `application/run/main_scene` separately:

```cpp
const String main_scene = GLOBAL_GET("application/run/main_scene");
if (main_scene.begins_with("uid://")) {
    ResourceUID::ID id = ResourceUID::get_singleton()->text_to_id(main_scene);
    if (!editor && !ResourceUID::get_singleton()->has_id(id) && !FileAccess::exists(ResourceUID::get_singleton()->get_cache_file())) {
        // abort: project must be imported first
    }
    game_path = ResourceUID::get_singleton()->get_id_path(id);
} else {
    game_path = main_scene;
}
```

The special runtime guard covers a missing UID when there is no UID cache file. It does **not** validate an existing mapping's target path.

For the external-move case:

```text
uid://U exists in uid_cache -> res://old/main.tscn
actual resource is now res://moved/main.tscn
old path is absent
```

`has_id(U)` is true, so the special error does not fire. `get_id_path(U)` returns the stale old path. Later `ResourceLoader::load(local_game_path)` fails and startup aborts with `Failed loading scene`.

This means the candidate is not merely about one autoload subsystem; it is a general stale-existing UID problem at early project dependency boundaries.

A main-scene control should be added to the owned target-native workflow after the first autoload run is harvested. It can use a moved `.tscn` carrying the same UID and a stale cache entry to test direct runtime failure and editor-scan repair without involving autoload semantics.

## Early editor UID scan also preserves stale existing mappings

`EditorFileSystem::scan_for_uid()` recursively reads resources and sidecars, but `_scan_for_uid_directory()` only calls `add_id(uid, path)` when `has_id(uid)` is false.

In other words, the startup fallback scan can fill missing mappings, but it intentionally does not replace an already-known UID whose path is stale.

That means the editor's early recovery mechanism does not repair the exact external-move case in this experiment.

## Editor first-scan ordering creates autoloads before stronger reconciliation

`EditorFileSystem::_first_scan_filesystem()` performs these relevant phases in order:

1. load the directory tree;
2. process scripts/global classes;
3. initialize GDExtensions;
4. call `ProjectSettingsEditor::init_autoloads()`;
5. initialize plugins;
6. only then begin the normal file scan.

`EditorAutoloadSettings::init_autoloads()` creates each cached autoload by calling `_create_autoload(ResourceUID::ensure_path(info.path))`.

For a stale existing UID, that `ensure_path()` still resolves to the absent old path. The autoload creation attempt therefore occurs before the later normal filesystem scan reaches its stronger UID reconciliation path.

The normal scan does contain code that replaces existing mappings:

```cpp
if (ResourceUID::get_singleton()->has_id(uid)) {
    ResourceUID::get_singleton()->set_id(uid, file);
} else {
    ResourceUID::get_singleton()->add_id(uid, file);
}
ResourceUID::get_singleton()->update_cache();
```

So the likely editor sequence is:

```text
load stale uid_cache
  -> resolve autoload UID to old path
  -> early UID scan sees UID already present and leaves it unchanged
  -> init_autoloads tries old path and fails
  -> later filesystem scan discovers moved sidecar/resource
  -> set_id repairs UID -> new path and persists cache
```

A repo-wide call search did not surface a filesystem-scan callback that automatically invokes `EditorAutoloadSettings::update_autoload()` after that repair. The visible `update_autoload()` path is used by the Project Settings UI and autoload editing operations. Target execution should therefore check whether the current editor session remains without the autoload even after the cache has been corrected.

## Active exact autoload experiment

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

The owned-fork Actions version tests three phases on the pinned engine:

1. direct headless runtime must expose the stale UID mapping and miss the autoload;
2. headless editor startup must show the failed autoload creation, then persist a repaired `uid_cache.bin` after filesystem discovery;
3. a subsequent direct runtime must load the moved autoload successfully from the repaired cache.

This is carried only in `teamleaderleo/godot` PR #3. Inherited Godot CI is suppressed with the owner-side repository variable; the narrow probe is the only intended target-native job.

## Distinguishing outcomes

### Runtime and editor cold-start gap reproduced

First direct runtime resolves UID to old path and misses the autoload. Editor startup also attempts the stale old path before its later scan repairs the cache. A subsequent runtime succeeds.

Together with the source-equivalent main-scene path, this would be a consequential external-move regression at early project dependency boundaries, with repair arriving one lifecycle phase too late.

### Runtime gap only

Direct runtime fails, but editor startup repairs the UID mapping before autoload creation through a source path not yet mapped. Stop the editor sub-hypothesis and identify that path.

### Runtime self-repairs

First direct runtime discovers the new `.uid` sidecar despite the stale existing cache entry. Stop the hypothesis and map the missing discovery path.

### Editor repairs cache but current session still lacks autoload

This is the strongest editor-specific outcome: cache is corrected during the session, yet the initial autoload creation failure is not retried automatically. Record whether opening Project Settings or restarting the editor restores it.

### Main scene behaves differently

If the future main-scene control self-repairs despite the direct `get_id_path()` source path, identify the loader/discovery path responsible. Do not assume autoload and main-scene runtime behavior are identical merely because they share the stale mapping.

## Candidate directions only after execution

Possible repair areas include:

1. validate cached UID paths before early startup consumers accept them;
2. if a cached path is missing in tools builds, trigger UID discovery even when the UID key exists;
3. let the early UID scan replace an existing mapping when its cached path no longer exists and a resource with the same UID is found;
4. preserve UID form for startup settings until actual resource load, allowing a missing cached path to invoke a broader lookup strategy;
5. centralize stale-path validation/recovery in `ResourceUID` so main scene, autoload, and other early consumers do not each need bespoke checks;
6. generate or consume a runtime-safe UID index whose path mappings are guaranteed current before game launch/export.

A runtime-wide recursive sidecar scan would have startup-cost implications, so avoid choosing a design before measuring the exact failure and existing editor/export guarantees.

## Overlap

Targeted current issue/PR searches for stale UID cache + external move + autoload/sidecar and UID-backed main-scene external moves found no matching repair in the connected search results.

## Evidence boundary

Supported: documented external-move goal; stale-existing-entry behavior in `get_id_path()`; eager startup autoload conversion; direct UID-backed main-scene `get_id_path()` resolution without stale-target validation; early editor UID scan refusing to replace existing IDs; autoload initialization before the stronger normal filesystem reconciliation path; later editor `set_id()` repair; direct autoload/main-scene loading from resolved paths.

Prepared/running: exact stale-cache + moved-script/sidecar autoload fixture and narrow owned-fork Actions probe in `teamleaderleo/godot#3`.

Prepared next: equivalent UID-backed moved-main-scene control after the current native run is harvested.

Unknown until execution: exact target-native runtime/editor outputs, whether current editor session retries autoload creation after cache repair, whether the main-scene control has any extra recovery path, platform breadth, and intended cold-runtime handling of externally moved development resources.

Automated upstream contact is prohibited.
