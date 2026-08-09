extends Node

const OBJECT_ORDER = ["alpha", "beta"]
const ACTIONS = [
	{"kind": "move", "id": "alpha", "dx": 2, "dy": 1},
	{"kind": "toggle", "id": "beta"},
	{"kind": "move", "id": "beta", "dx": -3, "dy": 4},
	{"kind": "move", "id": "alpha", "dx": 1, "dy": -5},
]
const SNAPSHOT_TICK = 2
const ThreadProbe = preload("res://thread_probe.gd")

var phase := "original"
var canonical_tick := 0
var action_index := 0
var rebuild_generation := 0
var objects: Dictionary = {
	"alpha": {"x": 0, "y": 0, "state": 0},
	"beta": {"x": 10, "y": -2, "state": 1},
}
var snapshot_objects: Dictionary = {}
var snapshot_action_index := 0
var replay_expected_hashes: Dictionary = {}
var replay_matched := 0
var presentation_root: Node2D
var thread_probe: Node


func _ready() -> void:
	thread_probe = ThreadProbe.new()
	thread_probe.name = "ThreadProbe"
	thread_probe.process_thread_group = Node.PROCESS_THREAD_GROUP_SUB_THREAD
	add_child(thread_probe)

	_build_presentation()
	get_tree().physics_frame.connect(_on_physics_frame)


func _on_physics_frame() -> void:
	if action_index >= ACTIONS.size():
		return

	# physics_frame is emitted before SceneTree processes physics nodes. Capture
	# the expected next sub-thread count now, then verify it from the deferred
	# receipt after SceneTree has joined the process-thread group.
	var expected_thread_probe_count := int(thread_probe.physics_count) + 1

	canonical_tick += 1
	_apply_action(ACTIONS[action_index])
	action_index += 1

	if phase == "original" and canonical_tick == 3:
		_rebuild_presentation()
	else:
		_sync_presentation()

	call_deferred("_emit_receipt", phase, canonical_tick, expected_thread_probe_count)


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


func _capture_snapshot() -> void:
	snapshot_objects = objects.duplicate(true)
	snapshot_action_index = action_index
	print("AUTH_SNAPSHOT tick=%d action_index=%d canonical=%s" % [
		canonical_tick,
		snapshot_action_index,
		_canonical_text(),
	])


func _begin_replay_from_snapshot() -> void:
	if snapshot_objects.is_empty():
		push_error("Replay requested without a canonical snapshot")
		get_tree().quit(6)
		return

	objects = snapshot_objects.duplicate(true)
	canonical_tick = SNAPSHOT_TICK
	action_index = snapshot_action_index
	phase = "replay"
	_rebuild_presentation()

	print("AUTH_RESTART from_tick=%d action_index=%d generation=%d canonical=%s" % [
		canonical_tick,
		action_index,
		rebuild_generation,
		_canonical_text(),
	])


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


func _emit_receipt(receipt_phase: String, receipt_tick: int, expected_thread_probe_count: int) -> void:
	if receipt_phase != phase or receipt_tick != canonical_tick:
		push_error("Deferred receipt crossed phase/tick: expected %s/%d, current %s/%d" % [
			receipt_phase,
			receipt_tick,
			phase,
			canonical_tick,
		])
		get_tree().quit(3)
		return

	var canonical := _canonical_text()
	var digest := canonical.sha256_text()
	var projection_ok := _projection_matches_canonical()
	var thread_probe_count := int(thread_probe.physics_count)
	var thread_probe_ok := thread_probe_count == expected_thread_probe_count
	var replay_hash_ok := true

	if receipt_phase == "original" and canonical_tick > SNAPSHOT_TICK:
		replay_expected_hashes[canonical_tick] = digest
	elif receipt_phase == "replay":
		replay_hash_ok = replay_expected_hashes.get(canonical_tick, "") == digest
		if replay_hash_ok:
			replay_matched += 1

	print("AUTH_RECEIPT phase=%s tick=%d hash=%s canonical=%s projection_ok=%s generation=%d thread_probe_count=%d expected_thread_probe_count=%d thread_probe_ok=%s replay_hash_ok=%s" % [
		receipt_phase,
		canonical_tick,
		digest,
		canonical,
		str(projection_ok),
		rebuild_generation,
		thread_probe_count,
		expected_thread_probe_count,
		str(thread_probe_ok),
		str(replay_hash_ok),
	])

	if !projection_ok:
		get_tree().quit(4)
		return

	if !thread_probe_ok:
		get_tree().quit(5)
		return

	if !replay_hash_ok:
		get_tree().quit(7)
		return

	if receipt_phase == "original" and canonical_tick == SNAPSHOT_TICK:
		_capture_snapshot()

	if canonical_tick == ACTIONS.size():
		if receipt_phase == "original":
			_begin_replay_from_snapshot()
		else:
			print("AUTH_REPLAY_RESULT matched=%d expected=%d final_hash=%s" % [
				replay_matched,
				ACTIONS.size() - SNAPSHOT_TICK,
				digest,
			])
			get_tree().quit(0)
