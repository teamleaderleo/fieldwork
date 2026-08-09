# Godot Web focus-query candidate

## In simple words

Godot Web receives real canvas focus/blur events and forwards focus notifications, but its `DisplayServerWeb::window_is_focused()` implementation always returns `true`. The public DisplayServer contract says the method returns whether the window is focused, and `Window::has_focus()` delegates directly to it for native windows.

The contradiction is especially crisp inside Godot itself: `Window::_event_callback(WINDOW_EVENT_FOCUS_OUT)` stores `focused = false` and emits `focus_exited`; a `focus_exited` handler that immediately calls `Window.has_focus()` on Web can still receive `true` from the DisplayServer query.

A source follow-up also shows that the obvious one-line repair, `canvas focused || IME focused`, is incomplete on mobile. Godot's Web display layer creates hidden `<input>`/`<textarea>` elements for the browser virtual keyboard and explicitly focuses them. Those are Godot-owned DOM focus too, but the native focus-notification suppression currently checks only the separate IME state. The right abstraction is therefore likely **Godot-owned DOM focus**, not canvas focus plus one special case.

State: source-strong + exact browser probe prepared; mobile virtual-keyboard case added to the promotion gate.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09/10.

Key paths:

- `platform/web/display_server_web.cpp`
- `platform/web/js/libs/library_godot_display.js`
- `platform/web/js/libs/library_godot_input.js`
- `platform/web/godot_js.h`
- `scene/main/window.cpp`
- `doc/classes/DisplayServer.xml`

## Current behavior

The Web JavaScript bridge already exposes `godot_js_display_canvas_is_focused()`, implemented as:

```text
document.activeElement === GodotConfig.canvas
```

The bridge also exposes `godot_js_is_ime_focused()`. Godot deliberately suppresses focus-in/focus-out window notifications caused by its hidden IME owning focus, so desktop text entry is already treated as retained Godot focus even when the canvas is temporarily not the active DOM element.

Canvas `focus` and `blur` events are otherwise forwarded into Godot's window callback.

Despite that live focus information, `DisplayServerWeb::window_is_focused()` returns `true` unconditionally.

The class reference contract says `window_is_focused(window_id)` returns true if that window is focused. `Window::has_focus()` calls this DisplayServer method whenever the Window has a real display-server window ID.

## Same-callback contradiction

`Window::_event_callback()` handles the focus events as follows:

```text
FOCUS_IN:
  focused = true
  emit focus_entered

FOCUS_OUT:
  focused = false
  emit focus_exited
```

For a native window, `Window.has_focus()` then bypasses this stored `focused` field and asks the DisplayServer. On Web that query returns `true`.

Therefore the source predicts this trace is possible in one synchronous focus-out callback:

```text
focus_exited signal is running
Window.has_focus() == true
```

Desktop display servers maintain actual focus state, making desktop a useful control.

## Godot-owned DOM focus is broader than canvas + IME

The Web display JavaScript also creates virtual-keyboard elements for touch devices:

- a hidden HTML `input`;
- a hidden HTML `textarea`;
- `show()` makes one active and calls `elem.focus()`.

This is distinct from the content-editable IME helper in `library_godot_input.js`.

The native Web notification callback currently suppresses focus transitions only when `godot_js_is_ime_focused()` is true:

```text
if IME focused and notification is FOCUS_IN/FOCUS_OUT:
    return
```

No equivalent virtual-keyboard ownership check surfaced in the source pass. Therefore a future focus query must not simply treat `document.activeElement === canvas` as the whole contract, and `canvas || IME` may still misclassify a Godot-owned mobile text-input element.

This also creates a nearby browser-execution question: when the Web virtual keyboard takes DOM focus, does Godot emit a spurious `focus_exited`, or is that transition hidden through another browser/native path not yet mapped?

## Consequence

A web application that gates input, pause overlays, keyboard capture, resume logic, or UI behavior with `Window.has_focus()` can observe a different state from the focus events it receives.

This is particularly relevant to an externally authoritative client: focus notifications should gate action collection, while the canonical action stream records whether input was accepted. A constant-true state query can make event-driven and poll-driven input policy disagree.

## Active browser experiment

`playgrounds/EXP-20260809-godot-web-focus-query/` contains a minimal Godot project that:

- connects `Window.focus_entered` and `focus_exited`;
- calls `Window.has_focus()` inside each callback;
- polls `has_focus()` continuously and logs changes;
- provides a `LineEdit` to exercise hidden-IME focus;
- emits machine-readable `FOCUS_PROBE` lines.

Source-predicted ordinary Web blur trace:

```text
FOCUS_PROBE ... kind=WINDOW_FOCUS_OUT has_focus=true
```

Desktop control should report:

```text
FOCUS_PROBE ... kind=WINDOW_FOCUS_OUT has_focus=false
```

The browser matrix should now distinguish at least:

1. canvas active;
2. ordinary HTML element outside Godot active;
3. browser/tab/window blur;
4. desktop Godot IME active;
5. touch/mobile Godot virtual-keyboard input or textarea active;
6. return to canvas.

## Competing expectations

1. **Godot-owned DOM focus:** focused while canvas, desktop IME, or Godot's virtual-keyboard element owns DOM focus. This best matches engine-level intent so far.
2. **Canvas focus only:** simple but wrong for Godot-owned text-input helpers.
3. **Browser document focus:** too broad; clicking another HTML control in the same page can leave the document focused while Godot interaction is not.
4. **Constant true is intentional:** if so, the public query requires a Web-specific documented limitation because current behavior conflicts with emitted focus state.

## Candidate implementation direction

If browser execution confirms the source prediction, prefer centralizing the policy in JavaScript as one query such as “is a Godot-owned focus target active?” rather than accumulating native checks for canvas, IME, virtual keyboard, and future helpers independently.

A narrow `canvas || IME` patch is no longer considered sufficient without proving the mobile virtual-keyboard case.

## Overlap

Open issue/PR searches at this refresh found no active Web `window_is_focused()` or `Window.has_focus()` repair. Nearby Web clipboard/focus reports do not describe this state-query contract.

## Evidence boundary

Supported: public API contract, constant-true Web implementation, live canvas-focus query, IME special-case, same-callback signal/query contradiction, and distinct Godot-owned virtual-keyboard DOM focus targets.

Prepared: desktop/Web/IME logging fixture; mobile virtual-keyboard case identified for extension.

Unknown: browser-observed trace, cross-browser/mobile details, whether the virtual-keyboard DOM transition already has another suppression path, and compatibility impact of changing the query.

Automated upstream contact: prohibited.
