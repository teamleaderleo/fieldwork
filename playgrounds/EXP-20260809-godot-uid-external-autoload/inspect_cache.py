#!/usr/bin/env python3
from pathlib import Path
import struct
import sys

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "godot/.godot/uid_cache.bin"

with path.open("rb") as f:
    count_raw = f.read(4)
    if len(count_raw) != 4:
        raise SystemExit(f"invalid cache header: {path}")
    count = struct.unpack("<I", count_raw)[0]
    print(f"UID_CACHE path={path} entries={count}")
    for index in range(count):
        uid = struct.unpack("<Q", f.read(8))[0]
        size = struct.unpack("<I", f.read(4))[0]
        resource_path = f.read(size).decode("utf-8")
        print(f"UID_CACHE_ENTRY index={index} uid={uid} path={resource_path}")
