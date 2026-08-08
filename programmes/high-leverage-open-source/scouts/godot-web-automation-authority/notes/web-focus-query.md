# Godot Web focus-query candidate

## In simple words

Godot Web receives real canvas focus/blur events and forwards focus notifications, but its `DisplayServerWeb::window_is_focused()` implementation always returns `true`. The public DisplayServer contract says the method returns whether the window is focused, and `Window::has_focus()` delegates directly to it for native windows. A web game can therefore receive focus-out and still have `Window.has_focus()` report true.

This looks like a compact interface-correctness candidate. It still needs browser execution before implementation promotion because IME focus and browser/document focus semantics need a deliberate expected behavior.

State: source-read; browser probe required.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

Key paths:

- `platform/web/display_server_web.cpp`
- `platform/web/js/libs/library_godot_display.js`
- `platform/web/js/libs/library_godot_input.js`
- `scene/main/window.cpp`
- `doc/classes/DisplayServer.xml`

## Current behavior

The web JavaScript bridge already exposes `godot_js_display_canvas_is_focused()`, implemented as:

```text
document.activeElement === GodotConfig.canvas
```

It also forwards canvas `focus` and `blur` events into Godot window notifications. The C++ web display server uses those events for window callbacks and special-cases active IME focus so a text-input helper does not create a false window focus transition.

Despite that live focus information, `DisplayServerWeb::window_is_focused()` returns `true` unconditionally.

The class reference contract says `window_is_focused(window_id)` returns true if that window is focused.

`Window::has_focus()` calls `DisplayServer::window_is_focused(window_id)` whenever the Window has a real display-server window ID. Thus the high-level `Window.has_focus()` query inherits the web constant-true result.

## Consequence

A web application that gates input, pause overlays, keyboard capture, or resume logic with `Window.has_focus()` can see a different state from the focus-out notifications it receives.

This is especially relevant to externally authoritative clients: focus notifications should gate presentation/input collection, while the canonical action stream should record whether input was accepted. A stale `true` query can admit input or skip a pause UI after focus moved elsewhere in the page.

## Competing expectations

1. **Canvas focus is window focus:** `window_is_focused()` should reflect `godot_js_display_canvas_is_focused()`, while IME focus counts as retained Godot focus.
2. **Browser document focus is window focus:** canvas focus is too narrow; the correct query should use document/window focus state and treat interaction elsewhere on the same page separately.
3. **Constant true is intentional compatibility behavior:** focus is meant to be event-only on Web. If so, the public method needs a Web-specific documented limitation because the current contract reads as a state query.

## Browser probe

Minimal exported project:

- display `Window.has_focus()` and `DisplayServer.window_is_focused()` continuously;
- log `NOTIFICATION_WM_WINDOW_FOCUS_IN/OUT` or equivalent window events;
- provide one Godot text field to exercise IME/hidden input;
- provide one ordinary HTML input/button outside the canvas;
- click canvas → outside HTML → browser chrome/tab → canvas → Godot text field;
- repeat on Chromium, Firefox, and Safari where available.

Distinguish canvas focus, document focus, and IME focus explicitly.

## Candidate implementation direction

The existing JS bridge already has the canvas-focus query. A narrow repair may only require wiring `DisplayServerWeb::window_is_focused()` to live browser focus state, with IME treated consistently with the event callback. Do not patch until the browser matrix establishes the intended semantics.

## Overlap

Open issue/PR search found no active focus-query repair at this refresh. Nearby Web focus/clipboard bugs exist but do not describe this method contract.

## Evidence boundary

Supported: interface mismatch in source and documentation at the pinned revision.

Unknown: browser-observed behavior, expected IME semantics, whether applications depend on the current constant-true behavior, and cross-browser compatibility.

Automated upstream contact: prohibited.
