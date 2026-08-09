#!/usr/bin/env python3
"""Probe sparse memfd extent granularity for Cloud Hypervisor issue 8582.

This is a no-network mechanism probe. It mirrors the relevant shape of
vmm/src/sparse.rs unit-test fixtures: write selected extents, explicitly punch
every gap, then enumerate the result with SEEK_DATA/SEEK_HOLE.

Run both modes:

    python3 cloud-hypervisor-sparse-page-granularity.py fixed4k
    python3 cloud-hypervisor-sparse-page-granularity.py host

`fixed4k` preserves the current upstream test assumption. `host` uses the
runtime host page size as the fixture quantum. A 16 KiB-page runner is needed
to distinguish the two modes experimentally.
"""

import ctypes
import os
import sys

FALLOC_FL_KEEP_SIZE = 0x01
FALLOC_FL_PUNCH_HOLE = 0x02

libc = ctypes.CDLL(None, use_errno=True)
libc.fallocate.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_longlong,
    ctypes.c_longlong,
]
libc.fallocate.restype = ctypes.c_int


def punch_hole(fd: int, offset: int, length: int) -> None:
    result = libc.fallocate(
        fd,
        FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE,
        offset,
        length,
    )
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def sparse_layout(fd: int, total: int, data: list[tuple[int, int, int]]) -> None:
    os.ftruncate(fd, total)
    for offset, length, byte in data:
        os.pwrite(fd, bytes([byte]) * length, offset)

    cursor = 0
    for offset, length, _ in sorted(data):
        if offset > cursor:
            punch_hole(fd, cursor, offset - cursor)
        cursor = offset + length
    if cursor < total:
        punch_hole(fd, cursor, total - cursor)


def collect_extents(fd: int, total: int) -> list[tuple[int, int]]:
    extents: list[tuple[int, int]] = []
    cursor = 0
    while cursor < total:
        try:
            data_offset = os.lseek(fd, cursor, os.SEEK_DATA)
        except OSError as error:
            if error.errno == 6:  # ENXIO: no more data.
                break
            raise

        hole_offset = min(os.lseek(fd, data_offset, os.SEEK_HOLE), total)
        extents.append((data_offset, hole_offset - data_offset))
        cursor = hole_offset
    return extents


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "fixed4k"
    if mode not in {"fixed4k", "host"}:
        raise SystemExit("usage: probe.py [fixed4k|host]")

    host_page_size = os.sysconf("SC_PAGE_SIZE")
    quantum = 4096 if mode == "fixed4k" else host_page_size
    total = quantum * 16
    data = [
        (quantum * 2, quantum, 0xAB),
        (quantum * 5, quantum * 2, 0xCD),
    ]
    requested = [(offset, length) for offset, length, _ in data]

    fd = os.memfd_create("fieldwork-ch-sparse", 0)
    try:
        sparse_layout(fd, total, data)
        actual = collect_extents(fd, total)
    finally:
        os.close(fd)

    print(f"host_page_size={host_page_size}")
    print(f"mode={mode} quantum={quantum}")
    print(f"requested={requested}")
    print(f"actual={actual}")
    print(f"match={actual == requested}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
