# EXP-20260809-godot-web-focus-query

This probe compares Godot's focus event stream with `Window.has_focus()` on desktop and Web.

## Source observation

At Godot revision `4173760fdf6c2c722e82e08cb58e55f34c9efd80`, Web forwards DOM canvas focus/blur events into the Window event callback. `Window::_event_callback(WINDOW_EVENT_FOCUS_OUT)` stores `focused = false` and emits `focus_exited`. For a native Window, however, `Window::has_focus()` delegates to `DisplayServer::window_is_focused()`, and the Web implementation currently returns `true` unconditionally.

The Web bridge already exposes two lower-level focus facts: whether the canvas is the document active element and whether Godot's hidden IME element owns focus. Godot suppresses canvas focus transitions caused by IME focus, so any eventual implementation candidate should preserve that semantic distinction.

## Run

Desktop control:

```sh
godot --path playgrounds/EXP-20260809-godot-web-focus-query/godot
```

Export the same project to Web and open it directly in a browser. Record `FOCUS_PROBE` lines while:

1. the Godot canvas is active;
2. browser/window focus moves away;
3. focus returns;
4. the LineEdit is focused and receives text;
5. the LineEdit loses focus back to the canvas.

## Distinguishing trace

The source-predicted Web mismatch is:

```text
FOCUS_PROBE ... kind=WINDOW_FOCUS_OUT has_focus=true
```

The desktop control should report `has_focus=false` for the equivalent focus-out event.

The LineEdit/IME path is a separate control. Moving DOM focus from the canvas into Godot's hidden IME should remain Godot-window focus and should not be treated as an application focus loss.

## Candidate only after execution

If the browser trace confirms the mismatch and the IME control behaves as expected, the smallest candidate is for Web `window_is_focused()` to reflect Godot-owned DOM focus: canvas focus or Godot IME focus. Do not promote that candidate until the browser matrix has been captured.

Automated upstream contact is prohibited.
