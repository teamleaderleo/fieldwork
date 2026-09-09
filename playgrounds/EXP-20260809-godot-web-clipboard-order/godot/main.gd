extends Node

var sequence := 0
var line_edit: LineEdit
var text_edit: TextEdit


func _ready() -> void:
	var panel := VBoxContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel.add_theme_constant_override("separation", 10)
	get_window().add_child(panel)

	var instructions := Label.new()
	instructions.text = "Web clipboard ordering probe\nCopy A in another app, paste here, then copy B externally and paste again.\nKeep browser devtools open and compare DOM_CLIP with GODOT_CLIP lines."
	panel.add_child(instructions)

	line_edit = LineEdit.new()
	line_edit.placeholder_text = "LineEdit target"
	line_edit.text_changed.connect(_on_line_edit_changed)
	panel.add_child(line_edit)

	text_edit = TextEdit.new()
	text_edit.custom_minimum_size = Vector2(0, 220)
	text_edit.placeholder_text = "TextEdit target"
	text_edit.text_changed.connect(_on_text_edit_changed)
	panel.add_child(text_edit)

	_install_dom_trace()
	_log_clipboard("ready")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.is_action_pressed("ui_paste", true):
		_emit("ui_paste_input", {
			"keycode": event.keycode,
			"clipboard": DisplayServer.clipboard_get(),
			"line": line_edit.text,
			"text": text_edit.text,
		})
		call_deferred("_log_clipboard", "deferred")
		get_tree().create_timer(0.05).timeout.connect(_log_clipboard.bind("timer_50ms"), CONNECT_ONE_SHOT)
		get_tree().create_timer(0.25).timeout.connect(_log_clipboard.bind("timer_250ms"), CONNECT_ONE_SHOT)


func _on_line_edit_changed(new_text: String) -> void:
	_emit("line_changed", {"text": new_text, "clipboard": DisplayServer.clipboard_get()})


func _on_text_edit_changed() -> void:
	_emit("text_changed", {"text": text_edit.text, "clipboard": DisplayServer.clipboard_get()})


func _log_clipboard(label: String) -> void:
	_emit("clipboard_" + label, {
		"clipboard": DisplayServer.clipboard_get(),
		"line": line_edit.text if is_instance_valid(line_edit) else "",
		"text": text_edit.text if is_instance_valid(text_edit) else "",
	})


func _install_dom_trace() -> void:
	if !Engine.has_singleton("JavaScriptBridge"):
		_emit("dom_trace_unavailable", {})
		return

	var bridge := Engine.get_singleton("JavaScriptBridge")
	var code := """
(() => {
  if (window.__fieldworkClipboardProbeInstalled) return;
  window.__fieldworkClipboardProbeInstalled = true;
  const stamp = () => performance.now().toFixed(3);
  const safeText = (value) => JSON.stringify(value);

  window.addEventListener('focus', () => {
    console.log(`DOM_CLIP t=${stamp()} kind=window_focus active=${document.activeElement && document.activeElement.tagName}`);
  }, true);
  window.addEventListener('blur', () => {
    console.log(`DOM_CLIP t=${stamp()} kind=window_blur active=${document.activeElement && document.activeElement.tagName}`);
  }, true);

  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'v') {
      console.log(`DOM_CLIP t=${stamp()} kind=keydown defaultPrevented=${e.defaultPrevented}`);
      queueMicrotask(() => console.log(`DOM_CLIP t=${stamp()} kind=microtask_after_keydown defaultPrevented=${e.defaultPrevented}`));
    }
  }, true);

  window.addEventListener('paste', (e) => {
    const text = e.clipboardData ? e.clipboardData.getData('text') : '<no clipboardData>';
    console.log(`DOM_CLIP t=${stamp()} kind=paste defaultPrevented=${e.defaultPrevented} text=${safeText(text)}`);
    queueMicrotask(() => console.log(`DOM_CLIP t=${stamp()} kind=microtask_after_paste defaultPrevented=${e.defaultPrevented}`));
  }, true);

  window.addEventListener('keyup', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'v') {
      console.log(`DOM_CLIP t=${stamp()} kind=keyup defaultPrevented=${e.defaultPrevented}`);
    }
  }, true);

  if (navigator.clipboard && 'onclipboardchange' in navigator.clipboard) {
    console.log(`DOM_CLIP t=${stamp()} kind=clipboardchange_support supported=true`);
    navigator.clipboard.addEventListener('clipboardchange', async (e) => {
      const types = e.types ? Array.from(e.types) : [];
      console.log(`DOM_CLIP t=${stamp()} kind=clipboardchange types=${safeText(types)} changeId=${String(e.changeId ?? '')}`);
      const readStart = stamp();
      try {
        const text = await navigator.clipboard.readText();
        console.log(`DOM_CLIP t=${stamp()} kind=clipboardchange_read start=${readStart} text=${safeText(text)}`);
      } catch (err) {
        console.log(`DOM_CLIP t=${stamp()} kind=clipboardchange_read_error start=${readStart} error=${safeText(String(err))}`);
      }
    });
  } else {
    console.log(`DOM_CLIP t=${stamp()} kind=clipboardchange_support supported=false`);
  }
})();
"""
	bridge.call("eval", code, true)
	_emit("dom_trace_installed", {})


func _emit(kind: String, fields: Dictionary) -> void:
	sequence += 1
	var payload := "GODOT_CLIP seq=%d kind=%s" % [sequence, kind]
	for key in fields:
		payload += " %s=%s" % [key, JSON.stringify(fields[key])]
	print(payload)
