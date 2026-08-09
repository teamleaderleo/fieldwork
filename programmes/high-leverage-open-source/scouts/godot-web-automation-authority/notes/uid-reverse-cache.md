# Godot UID reverse-cache candidate

## In simple words

Godot maintains a forward UID→path map and, in running games, a reverse path→UID cache. Two current replacement paths can leave stale reverse aliases: changing an ID path while reverse caching is active adds the new alias without erasing the old one, and loading an additional resource pack merges that pack's UID cache into the live runtime cache without resetting reverse state. A replacement pack can therefore update a UID's forward path while an older path still resolves back to the same UID.

The runtime semantics are worth characterizing, especially because packed-file replacement/removal and UID-cache merging are separate operations. Direct harmful call sites are currently sparse, so this is a lower-priority correctness/identity investigation behind Animation TRS and Web focus.

State: source-read + model-executed + target-test-prepared + exact runtime-pack fixture prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Stable comparison: `godotengine/godot@a13da4feb8d8aefc283c3763d33a2f170a18d541` (4.7.1 stable).
Retrieved: 2026-08-09.

## API contract

The ResourceUID class reference describes UIDs as the mechanism that keeps references intact when files are renamed or moved. `set_id()` is documented as updating the resource path of an existing UID. `path_to_uid(path)` returns the UID associated with a path, or the unchanged path when no UID is associated.

That makes replacement semantics observable even before deciding whether an old-path alias is allowed intentionally.

## Current behavior

`ResourceUID::set_id()` replaces `unique_ids[p_id].cs` and, when reverse caching is enabled, inserts `reverse_cache[new_path] = p_id`. It does not erase the previous path from `reverse_cache`.

`ResourceUID::update_cache()` appends entries whose `saved_to_cache` bit is false. A path change for an existing UID can therefore create a second record for the same UID in the editor cache instead of rewriting the original record.

`ResourceUID::load_from_cache()` iterates all records. For duplicate UID records, `unique_ids[id] = c` naturally leaves the latest path in the forward map, while `reverse_cache[c.cs] = id` retains each historical path unless replacement logic removes the prior alias.

`Main::setup()` enables the reverse cache for every non-editor run before loading `uid_cache.bin`. `ResourceLoader::get_resource_uid()` uses `ResourceUID::get_path_id()` outside the editor, so the reverse map is an active runtime identity surface.

## Runtime pack replacement boundary

`ProjectSettings::_load_resource_pack()` mounts the new pack first, then—when the project is already loaded—calls:

```cpp
ResourceUID::get_singleton()->load_from_cache(false);
```

The `false` retains existing UID and reverse-cache state while the newly visible pack's UID cache is merged.

Packed-file replacement has an independent policy. `PackedData::add_path()` overlays files when `replace_files` is enabled, while `PACK_FILE_REMOVAL` calls `remove_path()` to erase a path from the mounted packed-file namespace. `PCKPacker.add_file_removal()` exposes this operation specifically for patch packages.

Therefore file visibility and UID identity can be tested independently.

## Active exact runtime experiment

`playgrounds/EXP-20260809-godot-uid-pack-overlay/` now creates its own PCK files at runtime using `PCKPacker`, avoiding editor/exporter assumptions.

Base pack:

```text
res://uid_probe/old.txt
res://.godot/uid_cache.bin: UID 42424242 -> res://uid_probe/old.txt
```

Patch pack:

```text
remove res://uid_probe/old.txt
add res://uid_probe/new.txt
res://.godot/uid_cache.bin: UID 42424242 -> res://uid_probe/new.txt
```

The project loads base then patch with `ProjectSettings.load_resource_pack(..., true)` and records three independent views after each stage:

1. packed-file visibility (`FileAccess.file_exists`);
2. forward identity (`ResourceUID.uid_to_path`);
3. reverse identity (`ResourceUID.path_to_uid` for both paths).

Source-predicted patch receipt:

```text
old_exists=false
new_exists=true
uid_to_path=res://uid_probe/new.txt
path_to_uid(old)=uid://...
path_to_uid(new)=uid://...
```

If reproduced, the narrow finding is: **a path removed from the active packed-file namespace remains associated with the UID in the runtime reverse cache.** Whether that is harmful or intentional compatibility behavior is a separate decision.

## Model

A zero-dependency model mirroring the map updates was executed with one UID and two paths. It leaves the newest path in the forward map while retaining both old and new reverse aliases.

The model establishes the map consequence of the implementation. It does not establish a user-visible failure on a built Godot binary.

## Runtime caller sweep

`ResourceUID::path_to_uid()` has few runtime-side callers in current source. Most direct callers are editor/import helpers. `MultiplayerSpawner` is the meaningful runtime module caller, mainly when serializing/configuring its spawnable-scene list; its actual scene instantiation stores ensured paths and loads them directly.

This lowers the immediate consequence score. The pack experiment remains valuable for defining the identity contract, while promotion to an upstream bug should require one consequential caller or a clear project-visible invariant violation.

## Competing expectations

1. **Removed-path alias is stale:** once the packed path is removed and the UID points elsewhere, `path_to_uid(old)` should return the unchanged old path.
2. **UID aliases survive file relocation intentionally:** a removed path may remain a compatibility alias to the same UID.
3. **Pack overlays define identity independently of file visibility:** forward UID lookup tracks current content while reverse aliases preserve historical references.
4. **A later reconciliation path exists:** target execution may show behavior absent from the source paths already mapped.

The experiment distinguishes the state. Policy comes afterward.

## Secondary fork probe

Owned fork draft PR `teamleaderleo/godot#2` adds an API-level `tests/core/io/test_resource_uid.cpp` case for direct reverse-cache replacement semantics:

```text
add_id(uid, old)
set_id(uid, new)
get_id_path(uid) == new
get_path_id(new) == uid
get_path_id(old) == INVALID_ID
```

This remains useful as an invariant probe, while the PCK experiment is the production-path test.

## Candidate repair only if policy is clear

If target execution plus consequence analysis establish that historical aliases are wrong, replacement should reconcile the reverse map whenever a later UID record supersedes an existing one. If aliases are intentional, the behavior deserves explicit documentation and possibly an API distinction between current path and historical alias.

Avoid implementation until that semantic decision is resolved.

## Overlap

Open upstream search found no active PR for this reverse-cache replacement mechanism. Nearby issues cover duplicate UIDs, moved imported resources, and a debugger crash that once suspected stale UID cache state; none currently establish this pack-overlay behavior.

## Evidence boundary

Supported: map mechanism, API documentation, runtime pack merge path, packed-file removal semantics, and executed model.

Prepared: exact base-PCK + removal/replacement-PCK runtime fixture.

Unknown: target runtime result, intended alias policy, consequential runtime caller, and platform breadth.

Automated upstream contact: prohibited.
