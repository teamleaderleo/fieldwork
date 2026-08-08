## In simple words

Godot is worth a sustained scout. The first code path already gives us a strong, bounded question: when an `AnimationPlayer` applies position, rotation, and non-uniform scale together to a `Node3D`, the optimized combined path uses global/left-applied scale while the ordinary `Node3D` property path reconstructs local rotation-and-scale semantics. A mathematical model proves those operations diverge for a small fixture, and the owned Godot fork now carries a target-native regression test. The Godot test has been prepared but has not run yet, so the current result is a mechanism finding plus a target execution gate.

The broader scout should continue after this probe. The best longer-lived seams are externally authoritative state, resource/scene identity across import and reimport, web lifecycle, and headless deterministic automation. Chasing obvious open issues is less attractive because clean Godot regressions tend to acquire overlapping fixes quickly.

## State

- Fieldwork lane: #123
- Programme: #114
- Worker: `GPT-5.6 Sol / workstream F`
- State: `research-active`
- Upstream contact authorization: `false`
- Owned Fieldwork branch: `research/godot-web-automation-authority`
- Owned Godot fork: `teamleaderleo/godot`
- Probe branch: `fieldwork/godot/animation-trs-probe`
- Probe draft PR: `teamleaderleo/godot#1`
- Probe head: `92afcfd952bff5f2badb6bc7cbaae1623ae4a62f`

## Source pins

- Stable reference: Godot 4.7.1 stable, `a13da4feb8d8aefc283c3763d33a2f170a18d541`.
- Development/fork base: `4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
- Retrieval date: 2026-08-09.

The relevant `AnimationMixer::_blend_apply()` combined-TRS code is present at both pins.

## First code map: Node3D animation-state application

### Entrypoint and state

`AnimationPlayer::advance()` reaches the `AnimationMixer` processing and application path. Transform tracks share a `TrackCacheTransform` carrying blended location, quaternion rotation, scale, and `*_used` flags.

### Combined path

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

### Scale semantics

`Basis::scale()` documents and implements left multiplication by scale (`S * M`). `Basis::scaled()` delegates to that operation.

`Basis::scale_local()` documents and implements local/right multiplication (`M * S`). `Basis::scaled_local()` delegates to that operation.

`Node3D` stores Euler rotation and scale independently and, when its local transform is dirty, rebuilds the basis through `set_euler_scale()`. Its source comments and decomposition helpers treat the local transform as rotation followed by local scale (`R * S`).

### Consequence hypothesis

For rotation plus non-uniform scale, the combined AnimationMixer path (`S * R`) can produce a different local basis from the equivalent Node3D setters (`R * S`). Position is unaffected. Uniform scale and identity rotation are useful negative controls because left and right multiplication then coincide.

Evidence label: **Inferred from source**, strengthened by the model below. Target runtime confirmation remains open.

## EXP-20260809-godot-trs-scale-order

Retained at `playgrounds/EXP-20260809-godot-trs-scale-order/`.

Fixture:

- axis: `(1, 2, 3)` normalized;
- angle: `0.7` radians;
- scale: `(2, 1, 3)`.

Pure-Python standard-library model result:

- maximum absolute matrix-element difference between `S * R` and `R * S`: `0.5501172307043584`;
- Frobenius difference: `1.0471335212271937`.

Evidence label: **Model-executed**.

This establishes that the source operations are materially distinguishable for the selected fixture. It does not establish that an actual Godot binary has exercised the path.

## Target-native probe

Owned fork draft PR `teamleaderleo/godot#1` adds one test to `tests/scene/test_animation_player.cpp`.

The test:

1. creates a real `AnimationPlayer` and sibling `Node3D`;
2. builds position, rotation, and scale animation tracks targeting that node;
3. applies the same fixture through a second `Node3D` using the ordinary setters;
4. advances the animation;
5. compares the resulting transform against the setter-derived transform.

Exact fork head: `92afcfd952bff5f2badb6bc7cbaae1623ae4a62f`.

Evidence label: **Target-test-prepared**.

No PR workflow run appeared on the newly created fork at this refresh, so no compile or test result is claimed.

## Candidate improvement if target execution confirms the probe

The smallest source candidate is to use local scale in the combined path:

```cpp
Basis(t->rot).scaled_local(t->scale)
```

Boundary: source and model evidence make this candidate plausible. It remains generated candidate code until the target-native test fails on the baseline, passes with the candidate, and negative controls behave as expected.

## Negative controls to add after first execution

1. uniform scale plus rotation — combined and setter paths should agree;
2. non-uniform scale with identity rotation — combined and setter paths should agree;
3. rotation plus non-uniform scale — should distinguish current combined path;
4. position-only, rotation-only, and scale-only tracks — should preserve current individual-setter behavior;
5. optional imported-animation fixture only after the direct engine test establishes the lower boundary.

## Broader scout map and ranked branches

### 1. Animation/state application semantics — **retain; execute first**

Consequence: imported or authored animations can represent a different local transform when all TRS tracks are present, especially with rotation and non-uniform scale.

Owning boundary: `scene/animation/animation_mixer.cpp`, `scene/3d/node_3d.cpp`, `core/math/basis.*`.

Evidence needed: target-native failing test, negative controls, candidate pass.

### 2. External-authority adapter and deterministic headless fixture — **high priority after first probe**

Question: can a Godot scene consume externally authoritative state, emit bounded actions, restart, and replay without turning scene/resource identity into the canonical domain identity?

Likely boundaries: main loop/scene tree, resource identity, serialization, headless CLI, input dispatch, pause/focus/restart lifecycle.

Best evidence: a tiny generated state/receipt fixture first, followed by one owned testbed only if lifecycle behavior needs realistic use.

### 3. Resource and scene identity across import/reimport — **high priority source scout**

Recent Godot changes and open regressions show active complexity around editable children, local-to-scene resources, animation libraries, imported scenes, and serialization compatibility. Several obvious reported cases already have active fixes, so the better research question is a small identity matrix we own: external resource -> imported scene -> editable child/inherited scene -> reimport -> save/reopen, with explicit resource-path and UID receipts.

### 4. Web lifecycle and repeated run/teardown — **high value, heavier execution**

A current web-editor report attributes large repeated-session memory growth to an older Emscripten runtime. That specific report is useful context but should not become our hypothesis. Our own lane should measure startup/teardown, state restore, focus/resize, audio/GPU lifecycle, and repeated deterministic sessions against exact export toolchains.

### 5. Editor persisted-document identity — **compact secondary candidate**

A current master regression restores project-script help tabs as `Unknown Help Class` after editor restart. The first bad change was already narrowed to a ScriptEditor/DocumentList reorganization. This is a clean persisted-identity seam, though less central to the external-authority question than resource identity and headless execution.

### 6. `deprecated=no` full-test behavior — **time-box**

Current reports show several independent failures under a deprecated-free build. Characterize whether one shared configuration contract exists before spending implementation effort. Park if it decomposes into unrelated test maintenance.

## Overlap / stop ledger

Several initially attractive issue-shaped candidates already have overlapping upstream fixes, including recent `Node::duplicate`, threaded resource-load token cleanup, AnimationLibrary deserialization, scene-dock selection, and FileDialog behavior. These are useful context and stop signals, not contribution targets for this lane.

The pattern supports source-first discovery over open-issue harvesting.

## Current recommendation

**Continue the Godot scout.**

Immediate next transition:

1. execute the fork-native TRS regression probe on exact head `92afcfd952bff5f2badb6bc7cbaae1623ae4a62f`;
2. if baseline fails as predicted, add the negative-control matrix;
3. compare the one-line local-scale candidate against the same tests;
4. retain or stop the finding based on target execution;
5. then move to the external-authority/headless fixture and resource-identity matrix rather than opening another issue-shaped implementation branch.

Public upstream interaction: none.
