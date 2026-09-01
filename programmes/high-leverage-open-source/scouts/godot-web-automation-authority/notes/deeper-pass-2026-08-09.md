# Godot deeper scout pass — 2026-08-09

## Compressed result

The deeper pass converged on three concrete bug-shaped candidates, one consequential UID startup candidate, and one broader design result.

### Concrete candidate ranking

1. **Animation TRS semantics** — strongest engine correctness candidate.
2. **Web focus query** — strongest compact Web/API candidate.
3. **Web clipboard/paste ordering** — strong Web input candidate with an existing user-visible report.
4. **UID external-move autoload startup** — consequential identity/startup candidate tied to a documented external-move workflow.
5. **ResourceUID pack-overlay aliases** — retain as characterization; direct runtime consequence remains thinner.

### Strategic result

**External-authority fixed-tick adapter** remains the strongest architecture/replay result from the scout. Its ordering analysis now covers sub-thread process groups explicitly.

Target-native/browser execution remains the gating evidence. The pass strengthened fixtures and source contracts without claiming unexecuted fixes.

## 1. Animation TRS

The current source regression is the optimization introduced by `1a5d818ea97c40023e0b403a0390f5e24ea379a8`: three ordinary Node3D setters were replaced by one `set_transform()` path using:

```cpp
Basis(t->rot).scaled(t->scale)
```

The semantic facts line up cleanly:

- `scaled()` applies scale from the left (`S.R`).
- local scale applies from the right (`R.S`).
- Godot's own Basis decomposition comments assume `M = R.S`.
- Basis already has a Quaternion+scale constructor backed by `set_quaternion_scale()`.

The matrix experiment now has six cases. Uniform scale and identity rotation are zero-difference controls. Rotated non-uniform scale diverges. Rotated negative non-uniform scale diverges substantially more.

Current strongest candidate after target execution:

```cpp
Transform3D transform(Basis(t->rot, t->scale), t->loc);
```

The owned fork baseline test in `teamleaderleo/godot#1` now mirrors all six model cases.

Upstream issue #121158 independently identifies the same regression/root cause. Current overlap search found no matching repair PR.

Execution gate: baseline must fail only in the distinguishing cases, controls must behave as predicted, and the direct Quaternion+scale candidate must pass the same matrix.

## 2. Web focus query

The source contradiction is synchronous and user-facing.

`Window::_event_callback(WINDOW_EVENT_FOCUS_OUT)` sets its stored focus state false and emits `focus_exited`. For a native Window, `Window.has_focus()` then delegates to DisplayServer. Web's `window_is_focused()` returns true unconditionally.

A Web `focus_exited` handler can therefore observe:

```text
focus_exited event
Window.has_focus() == true
```

The JS layer already knows whether the canvas is the active DOM element and whether Godot's hidden IME owns focus. Godot suppresses false window-focus transitions caused by IME focus.

Leading candidate semantics after browser execution: **Godot-owned DOM focus = canvas focus OR Godot IME focus**.

Prepared experiment: `playgrounds/EXP-20260809-godot-web-focus-query/` logs focus signals, `Window.has_focus()` inside each callback, poll changes, and LineEdit/IME focus. Desktop is the control; Web is the target.

A related lifecycle question remains open: Input's internal application-focus flag drives the "ignore joypad while unfocused" option, while current Web source exposes window/canvas focus events and no obvious application-focus notification source. Keep this inside the focus lane until browser semantics are defined.

## 3. Web clipboard/paste ordering

The Web clipboard path combines a synchronous engine getter with an asynchronous browser API.

`LineEdit` and `TextEdit` handle `ui_paste` synchronously and consume `DisplayServer.clipboard_get()`. Web `clipboard_get()` starts `navigator.clipboard.readText()` but immediately returns the current cached C++ value.

A separate Web `paste` event listener can synchronously update that cache from `event.clipboardData`. The Web key bridge, however, enters Godot on keydown, flushes input during that call, and then calls `preventDefault()` on the DOM key event.

Current source therefore permits stale ordering variants where the text control consumes old cache before trusted fresh paste data or the asynchronous browser read arrives.

Open upstream issue #119747 reports exactly the high-level symptom: first Web paste succeeds, later external clipboard changes keep pasting old text; explicitly calling `DisplayServer.clipboard_get()` at paste time did not refresh the value.

Prepared experiment: `playgrounds/EXP-20260809-godot-web-clipboard-order/` logs capture-phase DOM keydown/paste/keyup, Godot `ui_paste`, synchronous clipboard values, later deferred/timed cache values, and resulting LineEdit/TextEdit contents.

Execution decides whether browser `paste` arrives after Godot's paste action, is suppressed by the canceled keydown, or exposes another insertion path.

## 4. UID external-move autoload startup

This is a stronger UID question than the pack-overlay alias because it touches an explicitly supported workflow and an early runtime dependency.

Godot's UID documentation says references survive file moves. The universal UID rollout explicitly describes outside-editor file-manager/IDE/CLI/VCS moves while the editor is closed as a target workflow, with script/shader `.uid` sidecars moving with the resource.

Current startup ordering:

1. load `.godot/uid_cache.bin`;
2. eagerly convert UID-backed autoloads to paths with `ProjectSettings::fix_autoload_paths()`;
3. later load those concrete autoload paths during game startup.

`ResourceUID::get_id_path()` can trigger editor UID discovery when a UID is missing. An existing stale UID entry returns its cached old path without taking that recovery branch.

Later editor filesystem/import phases do call `set_id(uid, current_path)` and update the cache. `--import` is a valid repair control because it enables editor mode and waits for the first filesystem scan before exit.

Prepared experiment: `playgrounds/EXP-20260809-godot-uid-external-autoload/` uses Godot's own tested UID pair `1` / `uid://b`, a correct moved script + sidecar, an absent old path, and a deliberately stale centralized cache. It compares first direct runtime, waited editor/import scan, cache contents, and second direct runtime.

Current overlap search found no matching issue/PR.

## 5. External-authority adapter

SceneTree submits `PROCESS_THREAD_GROUP_SUB_THREAD` groups to `WorkerThreadPool` and explicitly waits for them before the node-processing pass returns. The global MessageQueue flush in the physics tick happens afterward.

A main-thread receipt queued from `physics_frame` can therefore observe completion of ordinary and sub-thread physics callbacks for that tick.

Nuance: because the receipt is queued before node processing, later node-owned deferred calls may execute behind it in the same global queue. The clean canonical contract keeps domain mutation synchronous in the authority core and treats node-deferred work as presentation work.

`playgrounds/EXP-20260809-godot-authority-rebuild/` now combines four reference hashes, full presentation-subtree rebuild on tick 3, and a sub-thread physics sentinel whose counter must equal the canonical tick when the deferred receipt runs.

## 6. ResourceUID pack overlays

`playgrounds/EXP-20260809-godot-uid-pack-overlay/` manufactures a base PCK and a removal/replacement patch PCK at runtime. It compares packed-file visibility with UID→path and path→UID state.

Source predicts a removed old path can remain reverse-associated with the UID after the patch moves that UID to a new path. The direct runtime caller sweep reduced urgency: most reverse path→UID consumers are editor/import code, with MultiplayerSpawner as the main runtime module caller and largely configuration-facing.

Keep this as identity-contract characterization unless target execution or another caller raises consequence.

## Execution queue

1. Animation baseline six-case matrix + direct Quaternion/scale candidate.
2. Web focus desktop control + canvas/browser/IME matrix.
3. Web clipboard two-cycle DOM/Godot ordering matrix.
4. UID external-move autoload: stale direct runtime → waited import scan → fresh runtime.
5. Authority rebuild headless/rendered receipts + sub-thread sentinel.
6. UID pack-overlay base/removal-patch characterization.

Promote only executed, consequential findings to implementation work.

Automated upstream contact remains prohibited.
