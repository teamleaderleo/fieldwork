extends Node


func _ready() -> void:
	var root := get_tree().root
	var has_moved := root.has_node("Moved")
	var resolved := ResourceUID.uid_to_path("uid://b")
	print("AUTOLOAD_STARTUP_RESULT has_moved=%s resolved_uid_path=%s moved_file_exists=%s old_file_exists=%s" % [
		str(has_moved),
		resolved,
		str(FileAccess.file_exists("res://moved/autoload.gd")),
		str(FileAccess.file_exists("res://old/autoload.gd")),
	])
	get_tree().quit(0 if has_moved else 2)
