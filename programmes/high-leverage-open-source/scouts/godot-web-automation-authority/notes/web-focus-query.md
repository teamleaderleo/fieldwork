# Godot Web focus-query candidate

## In simple words

Godot Web receives real canvas focus/blur events and forwards focus notifications, but its `DisplayServerWeb::window_is_focused()` implementation always returns `true`. The public DisplayServer contract says the method returns whether the window is focused, and `Window::has_focus()` delegates directly to it for native windows.

The contradiction is especially crisp inside Godot itself: `Window::_event_callback(WINDOW_EVENT_FOCUS_OUT)` stores `focused = false` and emits `focus_exited`; a `focus_exited` handler that immediately calls `Window.has_focus()` on Web can still receive `true` from the DisplayServer query.

This is a compact interface-correctness candidate. Browser execution remains the promotion gate because Godot's hidden IME intentionally owns DOM focus during text entry and must continue counting as Godot-window focus.

State: source-read + exact browser probe prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

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

The bridge also exposes `godot_js_is_ime_focused()`. Godot deliberately suppresses focus-in/focus-out window notifications caused by its hidden IME owning focus, so text entry is already treated as retained Godot focus even when the canvas is temporarily not the active DOM element.

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

Source-predicted Web trace:

```text
FOCUS_PROBE ... kind=WINDOW_FOCUS_OUT has_focus=true
```

Desktop control should report:

```text
FOCUS_PROBE ... kind=WINDOW_FOCUS_OUT has_focus=false
```

The Web LineEdit path is a separate control. DOM focus moving from canvas to Godot's hidden IME should continue to count as Godot-window focus and should avoid a false application focus-out.

## Competing expectations

1. **Godot-owned DOM focus:** Web focus is true when either the canvas or Godot IME owns DOM focus. This currently best matches the existing event semantics.
2. **Canvas focus only:** simplest implementation, but likely wrong during IME text entry.
3. **Browser document focus:** broader than Godot interaction; clicking another HTML control in the same page may still leave the document focused while Godot should arguably be unfocused.
4. **Constant true is intentional:** if so, the public query requires a Web-specific documented limitation because current behavior conflicts with emitted focus state.

## Candidate implementation direction

If browser execution confirms the source prediction and the IME control behaves as expected, the narrow candidate is for Web `window_is_focused()` to reflect **Godot-owned DOM focus**, likely canvas focus OR Godot IME focus.

Avoid patching before capturing canvas → outside-page-content → browser/tab → canvas → LineEdit/IME transitions, ideally in Chromium, Firefox, and Safari where available.

## Overlap

Open issue/PR searches at this refresh found no active Web `window_is_focused()` or `Window.has_focus()` repair. Nearby Web clipboard/focus reports do not describe this state-query contract.

## Evidence boundary

Supported: public API contract, constant-true Web implementation, live canvas-focus query, IME special-case, and same-callback focus signal/query contradiction in source.

Prepared: desktop/Web/IME logging fixture.

Unknown: browser-observed trace, cross-browser details, and compatibility impact of changing the query.

Automated upstream contact: prohibited.
