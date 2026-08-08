#!/usr/bin/env python3

import hashlib


OBJECT_ORDER = ("alpha", "beta")
ACTIONS = (
    {"kind": "move", "id": "alpha", "dx": 2, "dy": 1},
    {"kind": "toggle", "id": "beta"},
    {"kind": "move", "id": "beta", "dx": -3, "dy": 4},
    {"kind": "move", "id": "alpha", "dx": 1, "dy": -5},
)


def canonical_text(tick, objects):
    parts = [f"tick={tick}"]
    for object_id in OBJECT_ORDER:
        obj = objects[object_id]
        parts.append(f"{object_id}:{obj['x']},{obj['y']},{obj['state']}")
    return "|".join(parts)


def apply_action(objects, action):
    obj = objects[action["id"]]
    if action["kind"] == "move":
        obj["x"] += action["dx"]
        obj["y"] += action["dy"]
    elif action["kind"] == "toggle":
        obj["state"] = 1 - obj["state"]
    else:
        raise ValueError(f"unknown action: {action['kind']}")


def main():
    objects = {
        "alpha": {"x": 0, "y": 0, "state": 0},
        "beta": {"x": 10, "y": -2, "state": 1},
    }

    for tick, action in enumerate(ACTIONS, start=1):
        apply_action(objects, action)
        text = canonical_text(tick, objects)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"AUTH_RECEIPT tick={tick} hash={digest} canonical={text}")


if __name__ == "__main__":
    main()
