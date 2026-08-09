# Godot deeper scout pass — 2026-08-09

## Compressed result

The second pass sharpened the lane rather than multiplying candidates.

Current ranking:

1. **Animation TRS semantics** — strongest concrete correctness candidate.
2. **Web focus query** — strongest compact Web/API candidate.
3. **External-authority fixed-tick adapter** — strongest strategic/design result.
4. **ResourceUID pack-overlay semantics** — retain as characterization; direct runtime consequence currently weaker.
5. **Resource/reimport identity and broader Web lifecycle** — continue after the first three execution gates.

Target-native/browser execution remains the gating evidence. This pass intentionally strengthened fixtures and source contracts instead of claiming unexecuted fixes.

## 1. Animation TRS

The current source regression is the optimization introduced by `1a5d818ea97c40023e0b403a0390f5e24ea379a8`: three ordinary Node3D setters were replaced by one `set_transform()` path using:

```cpp
Basis(t->rot).scaled(t->scale)
```

The key semantic facts now line up cleanly:

- `scaled()` applies scale from the left (`S.R`).
- `scale_local()` applies scale from the right (`R.S`).
- Godot's own Basis decomposition comments explicitly assume `M = R.S`.
- Basis already has a Quaternion+scale constructor backed by `set_quaternion_scale()`.

The matrix experiment was expanded to six cases. Uniform scale and identity rotation are zero-difference controls. Rotated non-uniform scale diverges. Rotated negative non-uniform scale diverges even more strongly.

Current strongest candidate, after target execution:

```cpp
Transform3D transform(Basis(t->rot, t->scale), t->loc);
```

This is clearer than composing through a generic modifier and uses Godot's direct Quaternion+scale representation.

Upstream issue #121158 independently identifies the same regression/root cause. Current overlap search found no matching repair PR.

Execution gate: fork draft `teamleaderleo/godot#1` must fail on the baseline, controls must behave as predicted, and the candidate must pass the same test.

## 2. Web focus query

The source contradiction is stronger than the first pass recorded.

`Window::_event_callback(WINDOW_EVENT_FOCUS_OUT)`:

```text
focused = false
emit focus_exited
```

For a native Window, `Window.has_focus()` then delegates to the DisplayServer. Web's `window_is_focused()` returns true unconditionally.

Therefore a Web `focus_exited` handler can synchronously observe:

```text
focus_exited event
Window.has_focus() == true
```

The JS layer already knows whether the canvas is the active DOM element and separately knows whether Godot's hidden IME owns focus. Godot already suppresses false window-focus transitions caused by IME focus.

Leading candidate semantics after browser execution: **Godot-owned DOM focus = canvas focus OR Godot IME focus**.

Prepared experiment: `playgrounds/EXP-20260809-godot-web-focus-query/` logs focus signals, `Window.has_focus()` inside each callback, poll changes, and LineEdit/IME focus. Desktop is the control; Web is the target.

Current overlap search found no active `window_is_focused`/`Window.has_focus` Web repair.

## 3. External-authority adapter

The concurrency boundary improved.

SceneTree's process-group path submits `PROCESS_THREAD_GROUP_SUB_THREAD` groups to `WorkerThreadPool` and explicitly waits for group completion before `_process()` returns. The global MessageQueue flush in the physics tick happens after that return.

Therefore a main-thread receipt queued from `physics_frame` can observe completion of ordinary and sub-thread physics callbacks for the tick.

Important nuance: because the receipt is queued before node processing, later node-owned deferred calls can sit behind it in the global queue. The clean authority contract therefore excludes canonical mutation from presentation-owned deferred work.

`playgrounds/EXP-20260809-godot-authority-rebuild/` now includes a sub-thread sentinel. Its physics counter must equal the canonical tick at receipt time. The sentinel is excluded from the canonical hash; it tests ordering only.

This strengthens the design case for Godot as a replaceable projection over application-owned canonical state.

## 4. ResourceUID pack overlays

A production-path experiment now exists at `playgrounds/EXP-20260809-godot-uid-pack-overlay/`.

It manufactures two PCKs at runtime:

- base: old resource path + UID cache mapping UID→old;
- patch: explicit PCK removal of old path + new resource path + UID cache mapping the same UID→new.

It loads both through `ProjectSettings.load_resource_pack(..., true)` and records:

- old/new file existence;
- UID→path;
- old path→UID;
- new path→UID.

Source predicts the old packed path can be removed while the reverse UID cache still associates that removed path with the UID.

The direct runtime caller sweep reduced urgency. Most `path_to_uid()` callers are editor/import code; `MultiplayerSpawner` is the main runtime module caller and its use is largely configuration/serialization-facing. Treat the pack result as an identity-contract question until a consequential caller appears.

## Execution queue

1. Run fork Animation baseline/controls and candidate.
2. Run Web focus desktop control + Web canvas/browser/IME matrix.
3. Run authority-rebuild headless and rendered with sub-thread sentinel.
4. Run UID base-pack/removal-patch experiment headless and rendered.
5. Promote only executed, consequential findings to candidate implementation work.

Automated upstream contact remains prohibited.
