extends Node

const TEST_UID := 42424242
const OLD_PATH := "res://uid_probe/old.txt"
const NEW_PATH := "res://uid_probe/new.txt"
const CACHE_TARGET := "res://.godot/uid_cache.bin"
const BASE_PACK := "user://fieldwork_uid_base.pck"
const PATCH_PACK := "user://fieldwork_uid_patch.pck"
const BASE_CACHE_SOURCE := "user://fieldwork_uid_base_cache.bin"
const PATCH_CACHE_SOURCE := "user://fieldwork_uid_patch_cache.bin"


func _ready() -> void:
	var uid_text := ResourceUID.id_to_text(TEST_UID)
	print("UID_PACK_PROBE uid=%s" % uid_text)

	var err := _build_uid_cache(BASE_CACHE_SOURCE, OLD_PATH)
	if err != OK:
		_fail("build base UID cache", err)
		return
	err = _build_uid_cache(PATCH_CACHE_SOURCE, NEW_PATH)
	if err != OK:
		_fail("build patch UID cache", err)
		return

	err = _build_base_pack()
	if err != OK:
		_fail("build base pack", err)
		return
	err = _build_patch_pack()
	if err != OK:
		_fail("build patch pack", err)
		return

	_receipt("before", uid_text)

	if !ProjectSettings.load_resource_pack(BASE_PACK, true):
		push_error("UID_PACK_PROBE failed to load base pack")
		get_tree().quit(2)
		return
	_receipt("base", uid_text)

	if !ProjectSettings.load_resource_pack(PATCH_PACK, true):
		push_error("UID_PACK_PROBE failed to load patch pack")
		get_tree().quit(3)
		return
	_receipt("patch", uid_text)

	var old_exists := FileAccess.file_exists(OLD_PATH)
	var new_exists := FileAccess.file_exists(NEW_PATH)
	var forward_path := ResourceUID.uid_to_path(uid_text)
	var reverse_old := ResourceUID.path_to_uid(OLD_PATH)
	var reverse_new := ResourceUID.path_to_uid(NEW_PATH)
	var stale_removed_alias := !old_exists and new_exists and forward_path == NEW_PATH and reverse_old == uid_text and reverse_new == uid_text

	print("UID_PACK_RESULT stale_removed_alias=%s" % str(stale_removed_alias))
	get_tree().quit(0)


func _build_uid_cache(file_path: String, resource_path: String) -> Error:
	var file := FileAccess.open(file_path, FileAccess.WRITE)
	if file == null:
		return FileAccess.get_open_error()

	var path_bytes := resource_path.to_utf8_buffer()
	file.store_32(1)
	file.store_64(TEST_UID)
	file.store_32(path_bytes.size())
	file.store_buffer(path_bytes)
	file.close()
	return OK


func _build_base_pack() -> Error:
	var packer := PCKPacker.new()
	var err := packer.pck_start(BASE_PACK)
	if err != OK:
		return err

	err = packer.add_file_from_buffer(OLD_PATH, "base-old".to_utf8_buffer())
	if err != OK:
		return err
	err = packer.add_file(CACHE_TARGET, BASE_CACHE_SOURCE)
	if err != OK:
		return err
	return packer.flush()


func _build_patch_pack() -> Error:
	var packer := PCKPacker.new()
	var err := packer.pck_start(PATCH_PACK)
	if err != OK:
		return err

	err = packer.add_file_removal(OLD_PATH)
	if err != OK:
		return err
	err = packer.add_file_from_buffer(NEW_PATH, "patch-new".to_utf8_buffer())
	if err != OK:
		return err
	err = packer.add_file(CACHE_TARGET, PATCH_CACHE_SOURCE)
	if err != OK:
		return err
	return packer.flush()


func _receipt(stage: String, uid_text: String) -> void:
	print("UID_PACK_RECEIPT stage=%s old_exists=%s new_exists=%s uid_to_path=%s path_to_uid_old=%s path_to_uid_new=%s" % [
		stage,
		str(FileAccess.file_exists(OLD_PATH)),
		str(FileAccess.file_exists(NEW_PATH)),
		ResourceUID.uid_to_path(uid_text),
		ResourceUID.path_to_uid(OLD_PATH),
		ResourceUID.path_to_uid(NEW_PATH),
	])


func _fail(action: String, err: Error) -> void:
	push_error("UID_PACK_PROBE %s failed with error %d" % [action, err])
	get_tree().quit(10 + int(err))
