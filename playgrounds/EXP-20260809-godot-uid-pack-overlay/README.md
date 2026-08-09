# EXP-20260809-godot-uid-pack-overlay

This probe exercises `ResourceUID` through Godot's real runtime pack-overlay path.

It creates two PCK files at startup:

- a base pack containing `res://uid_probe/old.txt` plus a one-entry `.godot/uid_cache.bin` mapping the test UID to the old path;
- a patch pack that registers removal of the old path, adds `res://uid_probe/new.txt`, and carries a one-entry UID cache mapping the same UID to the new path.

Both packs are loaded with `ProjectSettings.load_resource_pack(..., true)`. Current `ProjectSettings::_load_resource_pack()` reloads UID cache entries with `ResourceUID::load_from_cache(false)` after a pack is mounted.

## Run

```sh
godot --headless --path playgrounds/EXP-20260809-godot-uid-pack-overlay/godot
```

A rendered run is a useful backend control:

```sh
godot --path playgrounds/EXP-20260809-godot-uid-pack-overlay/godot
```

## Source-predicted result

After the patch loads:

```text
old_exists=false
new_exists=true
uid_to_path=res://uid_probe/new.txt
path_to_uid_old=<test uid>
path_to_uid_new=<test uid>
UID_PACK_RESULT stale_removed_alias=true
```

The important comparison is that `old.txt` has been removed from the packed file namespace while `ResourceUID.path_to_uid(old.txt)` still reports the UID.

If `path_to_uid_old` instead returns the unchanged old path, some runtime reconciliation exists outside the source path already mapped and the candidate should stop.

## Why this is stronger than the first API probe

The earlier `add_id()`/`set_id()` test exposes a reverse-map replacement invariant directly, but ordinary editor path changes occur with the reverse cache disabled. This PCK experiment reproduces the production runtime merge path: non-editor reverse caching plus `load_from_cache(false)` after an additional pack is mounted.

## Follow-up if reproduced

Characterize both overlay directions before proposing a repair:

1. same UID moved to a new path while the old packed path is removed;
2. same path replaced by a different UID;
3. unrelated UIDs added by a patch;
4. pack loaded with `replace_files=false` as a negative control.

The desired policy for compatibility aliases should be stated explicitly before changing merge semantics.

Automated upstream contact is prohibited.
