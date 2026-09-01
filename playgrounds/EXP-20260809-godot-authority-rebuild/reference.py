#!/usr/bin/env python3

import copy
import hashlib


OBJECT_ORDER = ("alpha", "beta")
ACTIONS = (
    {"kind": "move", "id": "alpha", "dx": 2, "dy": 1},
    {"kind": "toggle", "id": "beta"},
    {"kind": "move", "id": "beta", "dx": -3, "dy": 4},
    {"kind": "move", "id": "alpha", "dx": 1, "dy": -5},
)
SNAPSHOT_TICK = 2


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


def receipt(phase, tick, objects):
    text = canonical_text(tick, objects)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"AUTH_RECEIPT phase={phase} tick={tick} hash={digest} canonical={text}")
    return digest


def main():
    objects = {
        "alpha": {"x": 0, "y": 0, "state": 0},
        "beta": {"x": 10, "y": -2, "state": 1},
    }
    snapshot = None
    expected_replay = {}

    for tick, action in enumerate(ACTIONS, start=1):
        apply_action(objects, action)
        digest = receipt("original", tick, objects)
        if tick == SNAPSHOT_TICK:
            snapshot = copy.deepcopy(objects)
            print(f"AUTH_SNAPSHOT tick={tick} action_index={tick} canonical={canonical_text(tick, objects)}")
        elif tick > SNAPSHOT_TICK:
            expected_replay[tick] = digest

    if snapshot is None:
        raise RuntimeError("snapshot was not captured")

    objects = copy.deepcopy(snapshot)
    print(
        f"AUTH_RESTART from_tick={SNAPSHOT_TICK} action_index={SNAPSHOT_TICK} "
        f"canonical={canonical_text(SNAPSHOT_TICK, objects)}"
    )

    matched = 0
    for tick, action in enumerate(ACTIONS[SNAPSHOT_TICK:], start=SNAPSHOT_TICK + 1):
        apply_action(objects, action)
        digest = receipt("replay", tick, objects)
        if digest != expected_replay[tick]:
            raise AssertionError(
                f"replay receipt mismatch at tick {tick}: {digest} != {expected_replay[tick]}"
            )
        matched += 1

    print(
        f"AUTH_REPLAY_RESULT matched={matched} expected={len(ACTIONS) - SNAPSHOT_TICK} "
        f"final_hash={expected_replay[len(ACTIONS)]}"
    )


if __name__ == "__main__":
    main()
