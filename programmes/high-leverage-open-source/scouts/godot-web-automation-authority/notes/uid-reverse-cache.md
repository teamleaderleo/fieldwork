# Godot UID reverse-cache candidate

## In simple words

Godot writes UID→path changes into `uid_cache.bin` as append-only history. Non-editor runs enable a reverse path→UID cache and then reload that history. The current loader overwrites the forward UID map with the latest path but inserts every historical path into the reverse map. A moved resource can therefore leave both its old and new paths resolving to the same UID at runtime.

State: source-read + model-executed; target-native test being prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Stable comparison: `godotengine/godot@a13da4feb8d8aefc283c3763d33a2f170a18d541` (4.7.1 stable).
Retrieved: 2026-08-09.

## Current behavior

`ResourceUID::set_id()` replaces `unique_ids[p_id].cs` and, when reverse caching is enabled, inserts `reverse_cache[new_path] = p_id`. It does not erase the previous path from `reverse_cache`.

`ResourceUID::update_cache()` appends entries whose `saved_to_cache` bit is false. A path change for an existing UID therefore creates a second record for the same UID in the binary cache instead of rewriting the original record.

`ResourceUID::load_from_cache()` iterates all records. For duplicate UID records, `unique_ids[id] = c` naturally leaves the newest path in the forward map, while `reverse_cache[c.cs] = id` retains each historical path.

`Main::setup()` enables the reverse cache for every non-editor run before loading `uid_cache.bin`. `ResourceLoader::get_resource_uid()` uses `ResourceUID::get_path_id()` outside the editor, so the reverse map is an active runtime identity surface.

## Model

A zero-dependency model mirroring the map updates was executed with one UID and two paths.

Input history:

```text
123 -> res://old.tres
123 -> res://new.tres
```

Observed modeled state after the path change and after replaying append-only cache history:

```text
forward: 123 -> res://new.tres
reverse: res://old.tres -> 123
reverse: res://new.tres -> 123
```

The model establishes the map consequence of the implementation. It does not establish a user-visible failure on a built Godot binary.

## Consequence path

Outside the editor, `ResourceLoader::get_resource_uid(path)` returns the reverse-cache result. `ResourceUID::path_to_uid()` delegates to `ResourceLoader::get_resource_uid()`. Call sites include multiplayer spawning plus editor/import helpers. Runtime impact should be characterized with a moved-resource fixture before promotion.

## Competing hypotheses

1. **Stale reverse alias is observable:** after an editor move and restart/run, both old and new paths resolve to one UID through runtime APIs.
2. **Higher-level existence checks hide it:** callers never ask UID identity for the old path once the file is gone, so the stale alias has no consequential runtime effect.
3. **Cache compaction normally removes history:** another normal editor lifecycle step rewrites `uid_cache.bin` before runtime sees duplicate UID records.

## Target-native probe

Add a focused `tests/core/io/test_resource_uid.cpp` case for reverse-cache replacement semantics. The smallest API-level invariant is:

```text
add_id(uid, old)
set_id(uid, new)
get_id_path(uid) == new
get_path_id(new) == uid
get_path_id(old) == INVALID_ID
```

A second integration fixture should exercise append-only save/reload history if the API-level test confirms the stale reverse entry.

## Candidate repair

When changing an existing UID path, erase the prior reverse mapping before inserting the new one. During cache loading, when a duplicate UID record replaces an earlier record and reverse caching is enabled, erase the earlier path before adding the newer path.

Keep any repair narrow: append-only cache updates can remain; load-time reverse-map reconciliation is enough to preserve latest-path semantics.

## Overlap

Open upstream search found no active PR for this reverse-cache history mechanism. Open issue #120306 mentions a possibly stale `uid_cache.bin` while debugging a crash, but the reporter later withdrew confidence that UID state was causal. Treat it as adjacent context, not evidence for this candidate.

## Evidence boundary

Supported: mechanism and interface-level identity semantics from current source plus executed model.

Unknown: whether a normal moved-resource workflow produces an externally observable wrong UID in a built runtime; whether cache compaction eliminates the duplicate history before export/run; platform breadth.

Automated upstream contact: prohibited.
