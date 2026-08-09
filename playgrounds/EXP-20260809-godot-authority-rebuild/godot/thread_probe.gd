extends Node

var physics_count := 0


func _ready() -> void:
	set_physics_process(true)


func _physics_process(_delta: float) -> void:
	# Deliberately presentation-independent. The authority adapter reads this
	# only from its deferred receipt, after SceneTree has joined sub-thread
	# process groups for the tick.
	physics_count += 1
