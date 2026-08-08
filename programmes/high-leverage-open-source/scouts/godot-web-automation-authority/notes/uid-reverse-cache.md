# Godot UID reverse-cache candidate

## In simple words

Godot maintains a forward UID→path map and, in running games, a reverse path→UID cache. Two current replacement paths can leave stale reverse aliases: changing an ID path while reverse caching is active adds the new alias without erasing the old one, and loading an additional resource pack merges that pack's UID cache into the live runtime cache without resetting reverse state. A replacement pack can therefore update a UID's forward path while an older path still resolves back to the same UID.

This is a promising runtime identity candidate for patch/DLC/resource-pack workflows. The map behavior is model-executed; a built Godot pack-load fixture remains the promotion gate.

State: source-read + model-executed + target-test-prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Stable comparison: `godotengine/godot@a13da4feb8d8aefc283c3763d33a2f170a18d541` (4.7.1 stable).
Retrieved: 2026-08-09.

## Current behavior

`ResourceUID::set_id()` replaces `unique_ids[p_id].cs` and, when reverse caching is enabled, inserts `reverse_cache[new_path] = p_id`. It does not erase the previous path from `reverse_cache`.

`ResourceUID::update_cache()` appends entries whose `saved_to_cache` bit is false. A path change for an existing UID can therefore create a second record for the same UID in the editor cache instead of rewriting the original record.

`ResourceUID::load_from_cache()` iterates all records. For duplicate UID records, `unique_ids[id] = c` naturally leaves the latest path in the forward map, while `reverse_cache[c.cs] = id` retains each historical path unless replacement logic removes the prior alias.

`Main::setup()` enables the reverse cache for every non-editor run before loading `uid_cache.bin`. `ResourceLoader::get_resource_uid()` uses `ResourceUID::get_path_id()` outside the editor, so the reverse map is an active runtime identity surface.

## Runtime pack replacement path

`ProjectSettings::_load_resource_pack()` has a stronger live-runtime consequence. When a project is already loaded, mounting another pack calls:

```cpp
ResourceUID::get_singleton()->load_from_cache(false);
```

The `false` means the existing UID/reverse caches are retained while the newly mounted pack's UID cache is merged.

Export-side filtered caches are generated from the exported path set: `_get_filtered_cache()` gathers each exported file's `EditorFileSystem` UID/path pair and encodes those entries through `ResourceUID::encode_binary_cache()`.

This produces a bounded replacement scenario:

```text
base pack:  UID 123 -> res://old.tres
running game enables reverse cache and loads base UID cache
patch pack: UID 123 -> res://new.tres
load_resource_pack(patch) mounts patch and load_from_cache(false)
```

Current map logic predicts:

```text
forward 123 -> res://new.tres
reverse res://old.tres -> 123
reverse res://new.tres -> 123
```

This path avoids relying on an editor cache containing append-only duplicate history. It is therefore the preferred target reproduction.

## Model

A zero-dependency model mirroring the map updates was executed with one UID and two paths.

Input history:

```text
123 -> res://old.tres
123 -> res://new.tres
```

Observed modeled state after the path change and after replaying replacement history:

```text
forward: 123 -> res://new.tres
reverse: res://old.tres -> 123
reverse: res://new.tres -> 123
```

The model establishes the map consequence of the implementation. It does not establish a user-visible failure on a built Godot binary.

## Consequence path

Outside the editor, `ResourceLoader::get_resource_uid(path)` returns the reverse-cache result. `ResourceUID::path_to_uid()` delegates to `ResourceLoader::get_resource_uid()`. Runtime call sites include multiplayer spawning.

The pack-load scenario gives the best consequence probe: after loading a patch that relocates a UID, ask both old and new paths for their UID, then exercise one caller that converts a scene/resource path to UID. Distinguish stale identity from ordinary file-existence/remap behavior.

## Competing hypotheses

1. **Stale reverse alias is observable:** after patch-pack load, both old and new paths resolve to one UID through runtime APIs.
2. **Pack replacement keeps the old path valid by design:** the base pack remains mounted and a path alias is intentional even when the forward UID path changes.
3. **Higher-level file/path semantics hide the alias:** callers only use paths that exist in the active overlay and stale reverse lookup cannot change behavior.
4. **Export patch generation prevents same-UID/different-path replacement:** a real patch workflow cannot produce the replacement cache assumed above.

The integration fixture must distinguish all four rather than assuming a defect from the map alone.

## Target-native probe

Owned fork draft PR `teamleaderleo/godot#2` adds an API-level `tests/core/io/test_resource_uid.cpp` case for reverse-cache replacement semantics:

```text
add_id(uid, old)
set_id(uid, new)
get_id_path(uid) == new
get_path_id(new) == uid
get_path_id(old) == INVALID_ID
```

This is useful as a narrow invariant but is not the decisive production reproduction because normal editor path changes occur with the runtime reverse cache disabled.

The stronger next fixture is a tiny base-pack + replacement-pack runtime test around `load_resource_pack()` and `load_from_cache(false)`.

## Candidate repair

If the pack fixture establishes stale aliases as wrong behavior, replacement should reconcile the reverse map whenever a later UID record supersedes an existing one:

- remember the prior forward path for the UID;
- erase that prior path from `reverse_cache` when reverse caching is enabled;
- install the new forward and reverse mapping.

The same rule can protect `set_id()` when reverse caching is active.

Keep the repair narrow. Append-only editor cache updates can remain; the invariant is one current reverse path per UID unless an explicit alias feature says otherwise.

## Overlap

Open upstream search found no active PR for this reverse-cache replacement mechanism. A nearby debugger-crash issue once mentioned stale `uid_cache.bin`, but its reporter later withdrew confidence that UID state was causal. Treat it as adjacent context, not evidence for this candidate.

## Evidence boundary

Supported: mechanism and interface-level identity semantics from current source plus executed model; live runtime pack merge path exists in current source; export caches encode selected UID/path pairs.

Unknown: whether a supported patch workflow can replace one UID's path exactly as modeled; whether retaining both path aliases is intentional overlay semantics; observable effect in a built runtime; platform breadth.

Automated upstream contact: prohibited.
