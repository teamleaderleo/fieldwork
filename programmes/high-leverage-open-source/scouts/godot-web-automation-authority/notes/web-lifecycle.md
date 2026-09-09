# Godot web lifecycle source map

## In simple words

Godot's web platform is explicit about several lifecycle limits. WebGL context loss is treated as terminal and asks the user to reload. Browser focus/blur events are forwarded into Godot, but `DisplayServerWeb::window_is_focused()` always returns true. Long animation-frame gaps are expected and the main loop resets its timing target after a long focus-loss gap. Explicit engine shutdown waits for asynchronous cleanup and a final persistent-filesystem sync before forcing the Emscripten runtime to exit.

These behaviors make an external-authority client viable if authoritative state does not depend on frame count, focus-query state, or recoverable GPU state.

State: source-read. No browser execution claimed.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

Key paths:

- `platform/web/web_main.cpp`
- `platform/web/display_server_web.cpp`
- `platform/web/js/libs/library_godot_display.js`
- `platform/web/js/libs/library_godot_os.js`

## Findings

### GPU context loss is terminal

`godot_js_display_setup_canvas()` registers `webglcontextlost`. On loss it alerts `WebGL context lost, please reload the page` and prevents the default event. The same setup code has no `webglcontextrestored` handler.

Current scout interpretation: treat GPU context loss as session termination for a web client. A resilient product can persist authoritative state outside renderer-owned objects and restart the presentation session.

### Event focus and queried focus differ

The JavaScript bridge registers canvas `focus` and `blur` events and forwards `WINDOW_EVENT_FOCUS_IN` / `WINDOW_EVENT_FOCUS_OUT` through `send_window_event_callback()`.

A separate window-level blur callback releases pressed input events.

`DisplayServerWeb::window_is_focused()` returns `true` unconditionally.

Current scout interpretation: use explicit focus events for lifecycle-sensitive behavior. Do not use `window_is_focused()` as authoritative web focus state without a separate probe showing the intended contract.

### Long browser gaps are expected

`web_main.cpp` notes that updates stop when the window loses focus. When the elapsed gap exceeds one second, the max-FPS target timestamp is reset to current time instead of accumulating the entire delay.

Current scout interpretation: frame cadence is presentation timing. External simulation/replay should use explicit ticks, timestamps, or action sequence numbers independent of animation-frame continuity.

### Explicit quit has an asynchronous persistence fence

`GodotOS.finish_async()` waits for any prior filesystem sync promise, runs registered asynchronous cleanup callbacks, performs a final `GodotFS.sync()`, then calls back on a later task. `web_main.cpp` switches to a cleanup loop and waits for that callback before `Main::cleanup()` and `emscripten_force_exit()`.

`GodotFS` mounts configured persistent paths through IDBFS, loads them at initialization, and explicitly unmounts/closes databases during deinit.

Current scout interpretation: an orderly Godot-requested quit has a useful persistence boundary. Browser tab destruction/page kill is a different boundary and should be tested separately; no pagehide/beforeunload persistence hook was found in this first source pass.

## First web integration probe

Build one generated web project whose canonical state is a small JSON receipt outside scene-node identity. Exercise:

1. apply action sequence 1..N and record authoritative hash;
2. trigger focus-out / long RAF gap, then resume;
3. compare action/hash continuity without integrating elapsed presentation frames;
4. explicitly request quit after writing one persistent receipt;
5. relaunch and verify the receipt;
6. separately kill/reload the page without orderly quit and classify what persistence was lost;
7. treat WebGL context loss as a forced presentation restart and verify that canonical state can rebuild the scene.

## Candidate questions

1. **Focus-query interface:** should `window_is_focused()` reflect canvas/document focus on web, or is the unconditional `true` value intentional because browser window focus cannot map cleanly to Godot windows?
2. **Page lifecycle persistence:** is there a supported way to flush IDBFS on page hide/visibility transitions, or must applications explicitly sync after important writes?
3. **Context loss:** terminal by current implementation; architecture/proposal-sized if transparent restoration is desired. Keep out of ordinary bug-fix scope unless a narrower invariant appears.

## Evidence boundary

Supported: implementation-level lifecycle behavior at the pinned revision.

Unknown: browser-specific event ordering, persistence under abrupt tab/process termination, threaded versus single-threaded web differences, user-visible behavior across Chromium/Firefox/Safari, and whether `window_is_focused()` has a documented compatibility rationale.

Automated upstream contact: prohibited.
