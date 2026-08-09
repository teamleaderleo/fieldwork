extends Node

var root_window: Window
var sequence := 0
var last_polled_focus := false
var line_edit: LineEdit


func _ready() -> void:
	root_window = get_window()
	root_window.focus_entered.connect(_on_focus_entered)
	root_window.focus_exited.connect(_on_focus_exited)

	var panel := VBoxContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel.add_theme_constant_override("separation", 12)
	root_window.add_child(panel)

	var title := Label.new()
	title.text = "Fieldwork Web focus-query probe"
	panel.add_child(title)

	var instructions := Label.new()
	instructions.text = "1. Observe READY.\n2. Move browser/window focus away and return.\n3. Focus the LineEdit and type text.\n4. Compare EVENT has_focus with the event name."
	panel.add_child(instructions)

	line_edit = LineEdit.new()
	line_edit.placeholder_text = "Focus here to exercise Web IME focus"
	line_edit.focus_entered.connect(_on_line_edit_focus_entered)
	line_edit.focus_exited.connect(_on_line_edit_focus_exited)
	panel.add_child(line_edit)

	last_polled_focus = root_window.has_focus()
	_emit("READY", {"has_focus": last_polled_focus})


func _process(_delta: float) -> void:
	var current := root_window.has_focus()
	if current != last_polled_focus:
		last_polled_focus = current
		_emit("POLL_CHANGE", {"has_focus": current})


func _on_focus_entered() -> void:
	_emit("WINDOW_FOCUS_IN", {"has_focus": root_window.has_focus()})


func _on_focus_exited() -> void:
	_emit("WINDOW_FOCUS_OUT", {"has_focus": root_window.has_focus()})


func _on_line_edit_focus_entered() -> void:
	_emit("LINE_EDIT_FOCUS_IN", {"has_focus": root_window.has_focus()})


func _on_line_edit_focus_exited() -> void:
	_emit("LINE_EDIT_FOCUS_OUT", {"has_focus": root_window.has_focus()})


func _emit(kind: String, fields: Dictionary) -> void:
	sequence += 1
	var payload := "FOCUS_PROBE seq=%d kind=%s" % [sequence, kind]
	for key in fields:
		payload += " %s=%s" % [key, str(fields[key])]
	print(payload)
