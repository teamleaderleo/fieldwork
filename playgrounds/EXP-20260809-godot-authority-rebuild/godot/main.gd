extends Node

const OBJECT_ORDER = ["alpha", "beta"]
const ACTIONS = [
	{"kind": "move", "id": "alpha", "dx": 2, "dy": 1},
	{"kind": "toggle", "id": "beta"},
	{"kind": "move", "id": "beta", "dx": -3, "dy": 4},
	{"kind": "move", "id": "alpha", "dx": 1, "dy": -5},
]

var canonical_tick := 0
var action_index := 0
var rebuild_generation := 0
var objects: Dictionary = {
	"alpha": {"x": 0, "y": 0, "state": 0},
	"beta": {"x": 10, "y": -2, "state": 1},
}
var presentation_root: Node2D


func _ready() -> void:
	_build_presentation()
	get_tree().physics_frame.connect(_on_physics_frame)


func _on_physics_frame() -> void:
	if action_index >= ACTIONS.size():
		return

	canonical_tick += 1
	_apply_action(ACTIONS[action_index])
	action_index += 1

	if canonical_tick == 3:
		_rebuild_presentation()
	else:
		_sync_presentation()

	# SceneTree flushes deferred calls after ordinary node physics processing.
	# The receipt therefore observes the canonical state after the presentation
	# nodes have had their physics callbacks for this tick.
	call_deferred("_emit_receipt", canonical_tick)


func _apply_action(action: Dictionary) -> void:
	var object_id: String = action["id"]
	var obj: Dictionary = objects[object_id]

	match action["kind"]:
		"move":
			obj["x"] += int(action["dx"])
			obj["y"] += int(action["dy"])
		"toggle":
			obj["state"] = 1 - int(obj["state"])
		_:
			push_error("Unknown action kind: %s" % action["kind"])
			get_tree().quit(2)
			return

	objects[object_id] = obj


func _build_presentation() -> void:
	presentation_root = Node2D.new()
	presentation_root.name = "Presentation_%d" % rebuild_generation
	add_child(presentation_root)

	for object_id in OBJECT_ORDER:
		var obj: Dictionary = objects[object_id]
		var marker := Node2D.new()
		marker.name = object_id
		marker.position = Vector2(int(obj["x"]), int(obj["y"]))
		marker.set_meta("app_id", object_id)
		marker.set_meta("state", int(obj["state"]))
		presentation_root.add_child(marker)


func _sync_presentation() -> void:
	for object_id in OBJECT_ORDER:
		var obj: Dictionary = objects[object_id]
		var marker := presentation_root.get_node(NodePath(object_id)) as Node2D
		marker.position = Vector2(int(obj["x"]), int(obj["y"]))
		marker.set_meta("state", int(obj["state"]))


func _rebuild_presentation() -> void:
	if is_instance_valid(presentation_root):
		remove_child(presentation_root)
		presentation_root.free()

	rebuild_generation += 1
	_build_presentation()


func _canonical_text() -> String:
	var text := "tick=%d" % canonical_tick
	for object_id in OBJECT_ORDER:
		var obj: Dictionary = objects[object_id]
		text += "|%s:%d,%d,%d" % [
			object_id,
			int(obj["x"]),
			int(obj["y"]),
			int(obj["state"]),
		]
	return text


func _projection_matches_canonical() -> bool:
	if !is_instance_valid(presentation_root):
		return false

	for object_id in OBJECT_ORDER:
		if !presentation_root.has_node(NodePath(object_id)):
			return false
		var obj: Dictionary = objects[object_id]
		var marker := presentation_root.get_node(NodePath(object_id)) as Node2D
		if marker.get_meta("app_id") != object_id:
			return false
		if marker.position != Vector2(int(obj["x"]), int(obj["y"])):
			return false
		if int(marker.get_meta("state")) != int(obj["state"]):
			return false

	return true


func _emit_receipt(receipt_tick: int) -> void:
	if receipt_tick != canonical_tick:
		push_error("Deferred receipt crossed canonical ticks: expected %d, current %d" % [receipt_tick, canonical_tick])
		get_tree().quit(3)
		return

	var canonical := _canonical_text()
	var digest := canonical.sha256_text()
	var projection_ok := _projection_matches_canonical()

	print("AUTH_RECEIPT tick=%d hash=%s canonical=%s projection_ok=%s generation=%d" % [
		canonical_tick,
		digest,
		canonical,
		str(projection_ok),
		rebuild_generation,
	])

	if !projection_ok:
		get_tree().quit(4)
		return

	if canonical_tick == ACTIONS.size():
		get_tree().quit(0)
