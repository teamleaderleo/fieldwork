#!/usr/bin/env python3

INVALID_ID = -1


class ResourceUIDModel:
    def __init__(self):
        self.unique_ids = {}
        self.reverse_cache = {}

    def add_id(self, uid, path):
        self.unique_ids[uid] = path
        self.reverse_cache[path] = uid

    def set_id_current(self, uid, path):
        if self.unique_ids[uid] != path:
            self.unique_ids[uid] = path
            # Mirrors current ResourceUID::set_id(): add new reverse entry,
            # leaving the previous path untouched.
            self.reverse_cache[path] = uid

    def load_history_current(self, entries):
        self.unique_ids.clear()
        self.reverse_cache.clear()
        for uid, path in entries:
            # Mirrors current ResourceUID::load_from_cache().
            self.unique_ids[uid] = path
            self.reverse_cache[path] = uid

    def get_id_path(self, uid):
        return self.unique_ids.get(uid)

    def get_path_id(self, path):
        return self.reverse_cache.get(path, INVALID_ID)


def snapshot(model, uid):
    return {
        "forward": model.get_id_path(uid),
        "old_reverse": model.get_path_id("res://old.tres"),
        "new_reverse": model.get_path_id("res://new.tres"),
    }


def main():
    uid = 123
    model = ResourceUIDModel()
    model.add_id(uid, "res://old.tres")
    model.set_id_current(uid, "res://new.tres")
    print("after_set_id", snapshot(model, uid))

    model.load_history_current([
        (uid, "res://old.tres"),
        (uid, "res://new.tres"),
    ])
    print("after_reload_history", snapshot(model, uid))


if __name__ == "__main__":
    main()
