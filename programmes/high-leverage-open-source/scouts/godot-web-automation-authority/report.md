## In simple words

Godot is worth a sustained scout. Three compact correctness seams have emerged from the first source pass, and the larger adoption question looks promising.

1. `AnimationMixer` combines position, rotation, and non-uniform scale using left/global scale while ordinary `Node3D` setters rebuild local rotation-and-scale semantics. A mathematical model proves the operations diverge, and the owned fork carries a target-native regression test.
2. `ResourceUID` keeps an append-only UID cache. Runtime reverse lookup can replay historical paths for one UID, leaving an old path aliased to the current UID even though forward lookup points at the new path. A mechanism model proves the map behavior, and the owned fork carries a focused native test for reverse-cache replacement semantics.
3. Godot Web receives real focus/blur events, but `DisplayServerWeb::window_is_focused()` always returns true. The public API says the method reports actual focus, and `Window::has_focus()` delegates to it. This needs a browser matrix before implementation because canvas, document, and IME focus need an explicit expected contract.

The strategic result is encouraging: Godot's fixed-tick ordering can support an externally authoritative client. `physics_frame` is emitted before node physics processing, deferred calls flush afterward, and the scene can be treated as a replaceable projection if application-owned IDs, ticks, action sequences, and hashes remain outside Godot node/physics identity.

## State

- Fieldwork lane: #123
- Programme: #114
- Worker: `GPT-5.6 Sol / workstream F`
- State: `research-active`
- Upstream contact authorization: `false`
- Owned Fieldwork branch: `research/godot-web-automation-authority`
- Owned Godot fork: `teamleaderleo/godot`
- Fieldwork draft PR: #722
- Animation probe: `teamleaderleo/godot#1`, head `92afcfd952bff5f2badb6bc7cbaae1623ae4a62f`
- UID probe: `teamleaderleo/godot#2`, head `d188c162ce2c8a4834db62896b0567258dc5f7b2`

## Source pins

- Stable reference: Godot 4.7.1 stable, `a13da4feb8d8aefc283c3763d33a2f170a18d541`.
- Development/fork base: `4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
- Retrieval date: 2026-08-09.

A master refresh on 2026-08-09 still returned `4173760fdf6c2c722e82e08cb58e55f34c9efd80` as the latest commit available through the connected GitHub view, so the current source findings remain pinned to the active fork base.

---

# Finding A — combined AnimationPlayer TRS application

## Code map

`AnimationPlayer::advance()` reaches the `AnimationMixer` processing and application path. Transform tracks share a `TrackCacheTransform` carrying blended location, quaternion rotation, scale, and `*_used` flags.

For an ordinary `Node3D`, when location, rotation, and scale are all used, current code constructs:

```cpp
Transform3D(Basis(t->rot).scaled(t->scale), t->loc)
```

and passes it to `Node3D::set_transform()`.

When fewer than all three components are used, the same function calls the ordinary setters individually:

```cpp
set_position(...)
set_rotation(...)
set_scale(...)
```

`Basis::scale()` implements left multiplication by scale (`S * M`). `Basis::scaled()` delegates to that operation.

`Basis::scale_local()` implements local/right multiplication (`M * S`). `Basis::scaled_local()` delegates to that operation.

`Node3D` stores Euler rotation and scale independently and rebuilds its dirty local basis through `set_euler_scale()`, matching rotation followed by local scale (`R * S`).

## Consequence hypothesis

For rotation plus non-uniform scale, the combined AnimationMixer path (`S * R`) can produce a different local basis from the equivalent Node3D setters (`R * S`). Position is unaffected. Uniform scale and identity rotation are negative controls because left and right multiplication then coincide.

Evidence label: **Inferred from source**, strengthened by the model below. Target runtime confirmation remains open.

## EXP-20260809-godot-trs-scale-order

Retained at `playgrounds/EXP-20260809-godot-trs-scale-order/`.

Fixture:

- axis: `(1, 2, 3)` normalized;
- angle: `0.7` radians;
- scale: `(2, 1, 3)`.

Pure-Python model result:

- maximum absolute matrix-element difference between `S * R` and `R * S`: `0.5501172307043584`;
- Frobenius difference: `1.0471335212271937`.

Evidence label: **Model-executed**.

## Target-native probe

Owned fork draft PR `teamleaderleo/godot#1` adds a test to `tests/scene/test_animation_player.cpp` which:

1. creates a real `AnimationPlayer` and sibling `Node3D`;
2. builds position, rotation, and scale tracks targeting that node;
3. applies the same fixture through a second `Node3D` using ordinary setters;
4. advances the animation;
5. compares the resulting transform against the setter-derived transform.

Exact fork head: `92afcfd952bff5f2badb6bc7cbaae1623ae4a62f`.

Evidence label: **Target-test-prepared**.

No fork workflow run appeared at the latest refresh, so no compile or target-test result is claimed.

## Candidate improvement if execution confirms the probe

The smallest source candidate is:

```cpp
Basis(t->rot).scaled_local(t->scale)
```

Keep this generated candidate unpromoted until baseline failure, negative controls, and candidate pass are all target-executed.

---

# Finding B — ResourceUID reverse-cache history

Detailed note: `notes/uid-reverse-cache.md`.

## Current behavior

`ResourceUID::set_id()` updates the UID's forward path and marks the entry unsaved. `update_cache()` appends unsaved records instead of rewriting the cache file, so moving a resource can leave multiple cache records for one UID over time.

At runtime, `Main::setup()` enables the reverse path-to-UID cache for every non-editor run and then loads `uid_cache.bin`.

`load_from_cache()` iterates every record. Duplicate UID records naturally leave the newest path in `unique_ids[id]`, but each historical path is inserted into `reverse_cache[path] = id` unless an earlier mapping is explicitly removed. Current code does not remove the earlier reverse entry when replaying a duplicate UID.

Outside the editor, `ResourceLoader::get_resource_uid(path)` uses `ResourceUID::get_path_id(path)`. `ResourceUID::path_to_uid()` delegates to that lookup. Runtime callers include multiplayer spawning, so the reverse map is an active identity surface rather than dead cache metadata.

## Mechanism model

Retained at `playgrounds/EXP-20260809-godot-uid-reverse-cache/`.

Input history:

```text
123 -> res://old.tres
123 -> res://new.tres
```

Observed model state both after the equivalent path update and after replaying append-only cache history:

```text
forward: 123 -> res://new.tres
reverse: res://old.tres -> 123
reverse: res://new.tres -> 123
```

Evidence label: **Model-executed**, mechanism scope.

## Target-native probe

Owned fork draft PR `teamleaderleo/godot#2` adds a focused reverse-cache replacement test in `tests/core/io/test_resource_uid.cpp`.

Exact head: `d188c162ce2c8a4834db62896b0567258dc5f7b2`.

The prepared API-level test is useful but deliberately narrower than the production path. The decisive reproduction should also exercise duplicate UID records through cache save/reload or an equivalent isolated loader fixture, because the editor normally updates UID paths with reverse caching disabled and runtime later reconstructs the reverse cache from file history.

Evidence label: **Target-test-prepared**, with production-path refinement required.

## Candidate repair direction

If target execution confirms stale reverse aliases, preserve append-only cache writes but reconcile reverse entries on replacement:

- erase the previous reverse mapping before inserting a replacement path when reverse caching is active;
- during cache loading, if a later record replaces an existing UID, erase the previous path from the reverse map before adding the newer one.

Do not promote implementation before the cache-history fixture proves the user-visible boundary.

## Overlap

No active upstream PR matching the reverse-cache-history mechanism was found at this refresh. A nearby debugger-crash issue once suspected stale `uid_cache.bin`, but its reporter later withdrew confidence in UID causality; it is adjacent context only.

---

# Finding C — Web focus query disagrees with Web focus events

Detailed note: `notes/web-focus-query.md`.

## Current behavior

The Web JavaScript bridge already exposes live canvas focus through:

```text
document.activeElement === GodotConfig.canvas
```

Canvas `focus` and `blur` events are forwarded into Godot window events. The input layer also maintains a hidden IME element and deliberately treats that focus differently from an ordinary focus-out.

`DisplayServerWeb::window_is_focused()` nevertheless returns `true` unconditionally.

The public `DisplayServer.window_is_focused(window_id)` documentation says it returns true when that window is focused.

`Window::has_focus()` calls `DisplayServer::window_is_focused(window_id)` for a native window, so the high-level query inherits the Web constant-true result.

## Consequence

A Web application can receive a focus-out event while `Window.has_focus()` still reports true. That can affect input admission, pause overlays, keyboard capture, or resume logic. For an externally authoritative client this is especially useful to test because accepted input should be explicit in the action receipt.

## Browser gate

Before patching, run a tiny exported project that logs:

- `Window.has_focus()`;
- `DisplayServer.window_is_focused()`;
- focus-in/out window notifications;
- focus movement between the Godot canvas, a Godot text field/IME, ordinary HTML outside the canvas, browser chrome/tab, and back.

Run on Chromium, Firefox, and Safari where available.

The candidate implementation should follow the browser result: canvas focus, document focus, and IME focus are distinct and should be named explicitly.

Evidence label: **Source-read / interface mismatch**. Browser execution pending.

No active upstream focus-query repair was found at this refresh.

---

# Strategic map — Godot as an externally authoritative client

Detailed note: `notes/authoritative-state-boundary.md`.

## Physics tick boundary

At the pinned revision, `SceneTree::physics_process()` performs the relevant sequence:

```text
increment frame
flush transforms
MainLoop physics step
emit physics_frame
run picking
run node physics processing
flush unique deferred group calls
flush MessageQueue
run physics timers
run physics tweens
flush transforms
flush queued deletion
run idle callbacks
```

`physics_frame` is therefore a useful start-of-tick hook for an externally validated action batch.

Node physics/process ordering has explicit priority values plus tree-order tie-breaking. Lower process-priority values run earlier.

## Idle-frame boundary

`SceneTree::process()` polls multiplayer, emits `process_frame`, flushes deferred messages, runs node idle processing, flushes messages again, handles pending scene change, timers/tweens, transforms, queued deletion, and idle callbacks.

For canonical domain state, fixed physics ticks are the cleaner synchronization boundary. Idle frames are a presentation/input cadence.

## Proposed adapter

Canonical state should carry application-owned:

- object IDs;
- tick/sequence numbers;
- validated action IDs;
- state generation/hash;
- content identity where needed.

Godot nodes, instance IDs, generated names, default physics body identity, renderer objects, and frame cadence remain replaceable runtime state unless a narrower executed contract proves them suitable for authority.

A generated fixture should destroy and rebuild the entire Godot presentation tree mid-run, continue from the same canonical snapshot, and compare action/result receipts. Rendering-enabled and headless runs should yield the same canonical hash.

Current source conclusion: **Godot's main-loop ordering is compatible with this design.** Execution and ergonomics are the next questions.

---

# Web lifecycle map

Detailed note: `notes/web-lifecycle.md`.

## GPU context loss

Godot Web installs a `webglcontextlost` handler that tells the user to reload the page and prevents the default event. No matching restoration handler was found in the setup path.

Disposition: treat GPU context loss as terminal for the current presentation session. Transparent restoration looks architecture/proposal-sized until a narrower invariant appears.

## Long browser gaps

The Web main loop expects browser focus loss to interrupt updates. When the gap grows beyond one second it resets its frame target rather than accumulating the entire delay.

Disposition: canonical simulation/replay must use explicit tick/action sequencing rather than elapsed presentation frames.

## Orderly quit and persistence

Web shutdown waits for asynchronous cleanup and a final persistent-filesystem sync before forcing the Emscripten runtime to exit. IDBFS-backed paths are mounted/synchronized through the Web filesystem layer.

Disposition: orderly Godot-requested quit provides a useful persistence fence. Abrupt tab/process destruction is a separate test boundary; no pagehide/beforeunload persistence hook was found in the first source pass.

---

# Automation map

Detailed note: `notes/headless-automation.md`.

`--test` is intercepted before ordinary project startup. With a tests-enabled binary the entrypoint runs `test_setup()`, the test runner, then `test_cleanup()`.

The current test context is broad: it initializes core, servers, scene types, modules, dummy rendering, ThemeDB, and editor types in tools builds. Source contains a TODO for lighter test contexts.

This is still a good fit for AnimationPlayer and ResourceUID invariants. Use headless projects for save/load/restart and generated action-replay receipts, and browser execution for canvas/page/IDBFS/GPU lifecycle.

---

# Resource/scene import and remap map

`SceneState` recursively duplicates local-to-scene resources and preserves per-scene remap sharing through a cache. When a fallback local resource can be reused, it resets/copies storage properties while deliberately preserving the fallback resource path. Otherwise it creates a local-scene duplicate.

This area is active and subtle, but the obvious Editable Children/local-to-scene regression already has active upstream repair. Keep that specific case as an overlap stop.

The better owned question is an identity matrix:

```text
external resource UID/path
-> imported scene
-> editable child or inherited scene
-> local-to-scene resource
-> reimport
-> save/reopen
-> runtime load
```

Record both forward UID->path and reverse path->UID receipts plus resource-path/local-resource identity. This can distinguish UID-history errors from scene-remap/duplication errors.

---

# Ranked branches

## 1. Animation TRS semantics — execute first

Strongest bounded code candidate. Source, model, and target-native test already exist.

## 2. ResourceUID reverse-cache history — execute/refine in parallel

New unoccupied mechanism with runtime identity consequence and a small native test surface. Strengthen with cache-history execution before repair.

## 3. External-authority/headless fixture — highest strategic learning value

This answers whether Godot is useful to us even if every upstream candidate disappears. Build a tiny canonical-state/action-receipt adapter and prove presentation-tree rebuild plus headless/rendered equivalence.

## 4. Web focus query — browser characterization

Compact API mismatch with plausible input/lifecycle consequence. Browser semantics decide the repair.

## 5. Resource/scene identity across reimport — targeted matrix

Use generated fixtures and explicit UID/resource receipts. Avoid duplicating active Editable Children repair work.

## 6. Web lifecycle/persistence matrix

Measure orderly quit, abrupt reload, focus gaps, persistent receipts, and repeated sessions. Treat context loss as presentation restart.

## 7. Editor persisted-document identity — secondary

Interesting restart/identity seam, but less central than runtime identity and external authority.

## 8. `deprecated=no` test behavior — time-box

Continue only if characterization reveals one shared contract rather than unrelated test maintenance.

---

# Overlap / stop ledger

Several obvious issue-shaped candidates already have overlapping upstream fixes, including recent `Node::duplicate`, threaded resource-load token cleanup, AnimationLibrary deserialization, scene-dock selection, FileDialog behavior, and Editable Children/local-to-scene remapping.

WebGL transparent context restoration is currently too broad for an ordinary bug-fix lane.

The pattern continues to favor source-first discovery over open-issue harvesting.

---

# Current recommendation

**Continue the Godot scout.**

Immediate transitions:

1. execute owned fork Animation probe `teamleaderleo/godot#1`;
2. execute/refine UID probe `teamleaderleo/godot#2` with duplicate cache-history replay;
3. build the tiny external-authority headless receipt fixture;
4. run the Web focus browser matrix;
5. use those results to choose whether implementation energy goes to TRS, UID history, Web focus, or only the owned integration adapter;
6. keep recording negative results and occupied seams instead of manufacturing contribution work.

Evidence currently retained:

- source-read architecture maps;
- model-executed TRS and UID mechanisms;
- target-test-prepared Animation and UID probes;
- no target-native Godot execution yet;
- no public upstream interaction.

Public upstream interaction: none.
