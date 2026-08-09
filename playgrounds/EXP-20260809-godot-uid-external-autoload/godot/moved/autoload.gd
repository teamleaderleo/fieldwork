extends Node


func _enter_tree() -> void:
	print("MOVED_AUTOLOAD_ENTER path=%s" % get_script().resource_path)


func _ready() -> void:
	print("MOVED_AUTOLOAD_READY path=%s" % get_script().resource_path)
