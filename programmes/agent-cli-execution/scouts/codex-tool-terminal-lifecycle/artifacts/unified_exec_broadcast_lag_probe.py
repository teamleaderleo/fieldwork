#!/usr/bin/env python3
"""Deterministic model of Codex unified-exec's bounded event broadcast.

Preserves the relevant mechanism at openai/codex@3725f02:
- an authoritative producer-side output capture;
- a bounded 64-item broadcast for event consumers;
- a delayed subscriber that ignores a lag notification and continues;
- a terminal event assembled from the subscriber transcript.

The probe intentionally omits Tokio scheduling, PTY details, and Codex protocol types.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import deque
from dataclasses import dataclass
from typing import Deque


class Lagged(Exception):
    def __init__(self, skipped: int) -> None:
        super().__init__(f"subscriber lagged by {skipped} chunks")
        self.skipped = skipped


@dataclass(frozen=True)
class Entry:
    seq: int
    data: bytes


class BoundedBroadcast:
    """Small deterministic model of tokio::sync::broadcast lag semantics."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._entries: Deque[Entry] = deque(maxlen=capacity)
        self._next_seq = 0

    def subscribe(self) -> "Subscriber":
        return Subscriber(self, self._next_seq)

    def send(self, data: bytes) -> None:
        self._entries.append(Entry(self._next_seq, data))
        self._next_seq += 1

    @property
    def oldest_seq(self) -> int:
        return self._entries[0].seq if self._entries else self._next_seq

    @property
    def next_seq(self) -> int:
        return self._next_seq

    def entry(self, seq: int) -> Entry | None:
        for entry in self._entries:
            if entry.seq == seq:
                return entry
        return None


class Subscriber:
    def __init__(self, bus: BoundedBroadcast, cursor: int) -> None:
        self.bus = bus
        self.cursor = cursor

    def recv(self) -> bytes | None:
        if self.cursor < self.bus.oldest_seq:
            skipped = self.bus.oldest_seq - self.cursor
            self.cursor = self.bus.oldest_seq
            raise Lagged(skipped)
        if self.cursor >= self.bus.next_seq:
            return None
        entry = self.bus.entry(self.cursor)
        if entry is None:
            raise RuntimeError(f"missing retained entry for sequence {self.cursor}")
        self.cursor += 1
        return entry.data


def digest(chunks: list[bytes]) -> str:
    h = hashlib.sha256()
    for chunk in chunks:
        h.update(chunk)
    return h.hexdigest()


def child_command(chunk_count: int) -> list[str]:
    program = (
        "import sys\n"
        f"for i in range({chunk_count}):\n"
        "    sys.stdout.write(f'chunk-{i:04d}\\n')\n"
        "    sys.stdout.flush()\n"
    )
    return [sys.executable, "-c", program]


def run_probe(chunk_count: int, capacity: int) -> dict[str, object]:
    proc = subprocess.Popen(
        child_command(chunk_count),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    assert proc.stderr is not None

    bus = BoundedBroadcast(capacity)
    subscriber = bus.subscribe()
    authoritative: list[bytes] = []

    # Delay the event consumer until the subprocess has finished. This makes the
    # lag deterministic while preserving a real subprocess producer.
    for line in proc.stdout:
        authoritative.append(line)
        bus.send(line)

    stderr = proc.stderr.read()
    return_code = proc.wait()

    event_transcript: list[bytes] = []
    lagged_chunks = 0
    while True:
        try:
            chunk = subscriber.recv()
        except Lagged as exc:
            # Mirrors async_watcher.rs: Err(RecvError::Lagged(_)) => continue.
            lagged_chunks += exc.skipped
            continue
        if chunk is None:
            break
        event_transcript.append(chunk)

    result = {
        "probe": "unified-exec-broadcast-lag-model",
        "subprocess_exit_code": return_code,
        "stderr_bytes": len(stderr),
        "configured_capacity_chunks": capacity,
        "authoritative_chunk_count": len(authoritative),
        "event_transcript_chunk_count": len(event_transcript),
        "lagged_chunk_count": lagged_chunks,
        "missing_chunk_count": len(authoritative) - len(event_transcript),
        "authoritative_sha256": digest(authoritative),
        "event_transcript_sha256": digest(event_transcript),
        "first_authoritative_chunk": authoritative[0].decode().strip() if authoritative else None,
        "first_event_chunk": event_transcript[0].decode().strip() if event_transcript else None,
        "last_event_chunk": event_transcript[-1].decode().strip() if event_transcript else None,
        "terminal_event_matches_authoritative_output": event_transcript == authoritative,
        "terminal_event_emitted_after_subscriber_drain": True,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", type=int, default=128)
    parser.add_argument("--capacity", type=int, default=64)
    args = parser.parse_args()
    if args.chunks < 1 or args.capacity < 1:
        parser.error("--chunks and --capacity must be positive")

    result = run_probe(args.chunks, args.capacity)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["missing_chunk_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
