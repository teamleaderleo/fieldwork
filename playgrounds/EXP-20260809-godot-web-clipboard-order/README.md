# EXP-20260809-godot-web-clipboard-order

This probe logs browser clipboard event order beside Godot's synchronous paste path.

## Source question

On Web, `LineEdit` and `TextEdit` handle the `ui_paste` key action synchronously and read `DisplayServer.clipboard_get()`. The Web DisplayServer starts `navigator.clipboard.readText()` asynchronously but returns its current C++ cache immediately. A separate DOM `paste` listener updates that cache from `event.clipboardData`.

The Web key listener invokes Godot synchronously and calls `preventDefault()` on every handled DOM key event. Browser paste-event behavior after the canceled keydown therefore determines which refresh path is available and when.

## Run

Desktop control:

```sh
godot --path playgrounds/EXP-20260809-godot-web-clipboard-order/godot
```

Then export the same project to Web. Open browser devtools before testing.

1. Copy the literal text `FIELDWORK_A` in another application/page.
2. Focus LineEdit and paste once.
3. Copy the literal text `FIELDWORK_B` externally.
4. Replace/select the LineEdit contents and paste again.
5. Repeat in TextEdit.

The Web project installs capture-phase DOM listeners through `JavaScriptBridge.eval()`. Browser lines begin with `DOM_CLIP`; engine lines begin with `GODOT_CLIP`.

## What to compare

For each paste, record:

```text
DOM_CLIP kind=keydown
GODOT_CLIP kind=ui_paste_input clipboard=...
DOM_CLIP kind=paste text=...
GODOT_CLIP kind=line_changed/text_changed text=...
GODOT_CLIP kind=clipboard_deferred clipboard=...
GODOT_CLIP kind=clipboard_timer_50ms clipboard=...
GODOT_CLIP kind=clipboard_timer_250ms clipboard=...
DOM_CLIP kind=keyup
```

The exact order is the result; the list above is a hypothesis, not an expected transcript.

## Distinguishing outcomes

### Fresh DOM paste follows stale Godot paste

If `ui_paste_input` sees A while the following DOM `paste` carries B, the current text-control operation is consuming cache before the trusted fresh paste payload arrives.

### No DOM paste event

If keydown enters Godot but browser `paste` never fires, the event-driven cache refresh has been suppressed. Watch whether the 50/250 ms reads eventually become B through `navigator.clipboard.readText()` and whether permission failures leave A indefinitely.

### DOM paste precedes Godot paste

If the DOM paste carrying B appears first yet `clipboard_get()` still returns A, inspect C++ callback/cache propagation before changing input ordering.

### Text receives B while getter reports A

That implies an additional browser/native insertion path and invalidates the simple cached-getter explanation.

## Browser matrix

Capture Chromium and Firefox at minimum if available. Safari is high-value because async clipboard permission behavior differs substantially across browsers.

## Evidence boundary

The source proves that `clipboard_get()` cannot synchronously wait for `navigator.clipboard.readText()`. This experiment decides how trusted paste events, key cancellation, and the cached value interleave in real browsers.

Automated upstream contact is prohibited.
