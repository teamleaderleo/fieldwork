#!/usr/bin/env python3
from pathlib import Path
import shutil
import struct

ROOT = Path(__file__).resolve().parent / "godot"
GODOT_DATA = ROOT / ".godot"
UID = 42424242
UID_TEXT = "uid://60nf3"
OLD_PATH = "res://old/autoload.gd"

if GODOT_DATA.exists():
    shutil.rmtree(GODOT_DATA)
GODOT_DATA.mkdir(parents=True, exist_ok=True)

path_bytes = OLD_PATH.encode("utf-8")
with (GODOT_DATA / "uid_cache.bin").open("wb") as f:
    f.write(struct.pack("<I", 1))
    f.write(struct.pack("<Q", UID))
    f.write(struct.pack("<I", len(path_bytes)))
    f.write(path_bytes)

print(f"prepared UID {UID} ({UID_TEXT}) with stale cache path {OLD_PATH}")
print("actual resource: res://moved/autoload.gd + res://moved/autoload.gd.uid")
