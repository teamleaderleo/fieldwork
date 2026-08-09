# Godot Web clipboard/paste ordering candidate

## In simple words

Godot's Web clipboard path combines a synchronous engine API with an asynchronous browser API. `DisplayServer.clipboard_get()` starts `navigator.clipboard.readText()` but returns the currently cached C++ clipboard string immediately. `LineEdit` and `TextEdit` call that getter synchronously when their `ui_paste` key action runs.

Separately, the Web input bridge listens for the browser `paste` event and uses `event.clipboardData.getData("text")` to update the C++ clipboard cache synchronously from that event.

The Web key bridge forwards keydown into Godot and then always calls `preventDefault()` on the DOM key event. Keyboard-triggered paste event ordering therefore becomes critical: Godot can consume the cached clipboard before the browser's fresh clipboard event or asynchronous read has updated it.

This source chain is a strong explanation candidate for open upstream issue #119747, where the first Web paste succeeds but subsequent pastes reuse stale text. Browser execution is required before assigning the exact event-order variant.

State: source-read + browser-spec-read + exact event-order probe prepared.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

Key paths:

- `platform/web/js/libs/library_godot_display.js`
- `platform/web/js/libs/library_godot_input.js`
- `platform/web/display_server_web.cpp`
- `scene/gui/line_edit.cpp`
- `scene/gui/text_edit.cpp`
- `doc/classes/DisplayServer.xml`

Adjacent upstream report: issue #119747, open at this refresh.

## Engine-side synchronous contract

The public DisplayServer class reference says `clipboard_get()` returns the user's clipboard as a string if possible, and Web advertises `FEATURE_CLIPBOARD`.

`LineEdit::paste_text()` synchronously does:

```cpp
String paste_buffer = DisplayServer::get_singleton()->clipboard_get().strip_escapes();
```

Its key handler calls `paste_text()` when the key event matches `ui_paste`.

`TextEdit` follows the same pattern:

```text
ui_paste key action
  -> paste()
  -> _paste_internal()
  -> DisplayServer::clipboard_get()
```

## Web clipboard getter

The Web DisplayServer implementation calls the JavaScript clipboard getter and then immediately returns its cached `clipboard` string.

The JavaScript getter uses:

```js
navigator.clipboard.readText().then(function (result) {
    // callback into C++ later
})
```

The Promise cannot make the synchronous C++ return value become fresh during the same call. The direct `clipboard_get()` API therefore has cache semantics on Web even though its cross-platform signature appears synchronous.

## Web paste-event cache update

The Web input layer also installs a `window` paste listener:

```js
const text = evt.clipboardData.getData('text');
func(ptr);
```

That callback updates the C++ clipboard cache from the trusted browser paste event, where clipboard event data is synchronously available.

## Key-event ordering

The Web keyboard handler performs:

```text
DOM keydown
  -> C++ key callback
  -> Godot flushes buffered input
  -> LineEdit/TextEdit handles ui_paste
  -> synchronous clipboard_get returns current cache
  -> JS key handler calls preventDefault()
```

The W3C Clipboard API describes keyboard-triggered clipboard events as associated with the initiating key event and dispatched before keyup; historical normative text describes paste as the default action of the initiating keydown. The exact effect of canceling keydown on paste dispatch is browser-sensitive enough to keep as an execution question.

Two source-compatible failure modes exist:

1. **paste event still fires after Godot consumes ui_paste:** the current operation uses old cache; fresh `event.clipboardData` updates cache afterward, producing lagging paste state.
2. **preventDefault suppresses the browser paste event:** the event-driven fresh cache path is skipped; only the asynchronous `navigator.clipboard.readText()` can update cache after the synchronous engine paste has already completed. Permission/focus behavior can then leave the cache stale longer.

Neither mode can make the synchronous `clipboard_get()` return the just-requested async result.

## Upstream report fit

Issue #119747 reports:

- first paste works;
- copying different external text and pasting again keeps inserting the first text;
- explicitly calling `DisplayServer.clipboard_get()` from the Godot key handler did not refresh the value.

The last observation is directly predicted by the asynchronous getter: invoking it at paste time schedules a read but returns the cached value immediately.

The exact reason the first paste succeeds still needs browser trace evidence and should not be guessed from source alone.

## Active browser probe

`playgrounds/EXP-20260809-godot-web-clipboard-order/` logs:

- raw DOM `keydown` and `paste` events using `JavaScriptBridge`;
- Godot `ui_paste` input timing;
- `DisplayServer.clipboard_get()` value synchronously inside that input;
- clipboard value one and several deferred turns later;
- resulting LineEdit/TextEdit contents.

Run at least Chromium and Firefox; Safari is useful if available because clipboard permission/event behavior differs across engines.

## Candidate directions after execution

The cleanest Web paste path likely needs the browser's trusted `paste` event to carry the text used for that paste operation, instead of asking a synchronous engine control to pull fresh state from an asynchronous browser API.

Possible designs to evaluate after the trace:

1. deliver browser paste text as an explicit Godot paste/input event and let text controls consume that payload;
2. suppress the ordinary Godot `ui_paste` shortcut on Web and trigger paste insertion from the trusted DOM paste callback;
3. document `clipboard_get()` as cached/asynchronous on Web and add a separate async API, while still fixing text-control paste ordering independently.

Avoid selecting a patch until event traces show browser behavior.

## Overlap

Current PR search found no active repair matching `clipboard_get`/Web paste async ordering. Issue #119747 is open and labeled `platform:web` / `needs testing`.

## Evidence boundary

Supported: synchronous text-control call chain, Web cached getter, asynchronous browser read, trusted paste-event cache update, unconditional keydown `preventDefault()`, public clipboard API contract, and issue #119747 symptoms.

Unknown: exact DOM event sequence in each browser, first-paste success mechanism, permission behavior, and best compatibility-preserving fix.

Automated upstream contact: prohibited.
