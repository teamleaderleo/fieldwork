#!/usr/bin/env python3
"""Model cgi-io's backup pipe ordering with and without a response reader."""

from __future__ import annotations

import errno
import fcntl
import json
import os
from pathlib import Path
import select
import signal
import time


READ_BLOCK = 4096
PRODUCER_BYTES = 2 * 1024 * 1024
OBSERVATION_SECONDS = 0.5


def proc_snapshot(pid: int) -> dict[str, str | int | None]:
    result: dict[str, str | int | None] = {"pid": pid, "state": None, "wchan": None}
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("State:"):
                result["state"] = line.split(":", 1)[1].strip()
                break
        result["wchan"] = Path(f"/proc/{pid}/wchan").read_text().strip()
    except FileNotFoundError:
        result["state"] = "exited"
    return result


def wait_until(pid: int, deadline: float) -> bool:
    while time.monotonic() < deadline:
        done, _ = os.waitpid(pid, os.WNOHANG)
        if done:
            return True
        time.sleep(0.01)
    return False


def terminate_owned(pid: int) -> None:
    """Terminate only a child created by this process, then reap it."""
    try:
        done, _ = os.waitpid(pid, os.WNOHANG)
        if done:
            return
    except ChildProcessError:
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    if wait_until(pid, time.monotonic() + 1.0):
        return

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


def cgi_worker(response_fd: int, status_fd: int) -> None:
    child_read, child_write = os.pipe()
    pipe_capacity = fcntl.fcntl(child_write, fcntl.F_GETPIPE_SZ)
    producer_pid = os.fork()

    if producer_pid == 0:
        os.close(child_read)
        os.close(status_fd)
        os.close(response_fd)
        remaining = PRODUCER_BYTES
        payload = b"x" * READ_BLOCK
        try:
            while remaining:
                written = os.write(child_write, payload[:remaining])
                remaining -= written
        except BrokenPipeError:
            pass
        finally:
            os.close(child_write)
        os._exit(0)

    os.close(child_write)
    os.write(
        status_fd,
        f"producer_pid={producer_pid}\npipe_capacity={pipe_capacity}\n".encode(),
    )
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

    splice_error = None
    while True:
        try:
            length = os.splice(child_read, response_fd, READ_BLOCK)
        except OSError as exc:
            if exc.errno == errno.EINTR:
                continue
            splice_error = exc.errno
            break
        if length <= 0:
            break

    os.write(status_fd, f"splice_errno={splice_error or 0}\n".encode())
    os.waitpid(producer_pid, 0)
    os.write(status_fd, b"waitpid_completed=1\n")
    os.close(child_read)
    os.close(response_fd)
    os.close(status_fd)


def parse_status(data: bytes) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in data.decode().splitlines():
        key, value = line.split("=", 1)
        result[key] = int(value)
    return result


def run_case(client_connected: bool) -> dict[str, object]:
    client_read, response_write = os.pipe()
    status_read, status_write = os.pipe()
    cgi_pid = os.fork()

    if cgi_pid == 0:
        os.close(client_read)
        os.close(status_read)
        try:
            cgi_worker(response_write, status_write)
        finally:
            os._exit(0)

    os.close(response_write)
    os.close(status_write)
    if not client_connected:
        os.close(client_read)

    status_data = bytearray()
    response_bytes = 0
    deadline = time.monotonic() + 3.0

    try:
        while time.monotonic() < deadline:
            reads = [status_read]
            if client_connected:
                reads.append(client_read)
            ready, _, _ = select.select(reads, [], [], 0.05)
            if status_read in ready:
                chunk = os.read(status_read, READ_BLOCK)
                if chunk:
                    status_data.extend(chunk)
            if client_connected and client_read in ready:
                chunk = os.read(client_read, 65536)
                if chunk:
                    response_bytes += len(chunk)

            status = parse_status(status_data)
            if client_connected and status.get("waitpid_completed") == 1:
                break
            if not client_connected and "splice_errno" in status:
                time.sleep(OBSERVATION_SECONDS)
                break

        status = parse_status(status_data)
        producer_pid = status.get("producer_pid")
        if client_connected and status.get("waitpid_completed") == 1:
            cgi_done = wait_until(cgi_pid, time.monotonic() + 1.0)
        else:
            cgi_done, _ = os.waitpid(cgi_pid, os.WNOHANG)
            cgi_done = bool(cgi_done)
        cgi_snapshot = proc_snapshot(cgi_pid) if not cgi_done else {"pid": cgi_pid, "state": "exited", "wchan": None}
        producer_snapshot = proc_snapshot(producer_pid) if producer_pid else None

        return {
            "client_connected": client_connected,
            "pipe_capacity_bytes": status.get("pipe_capacity"),
            "producer_bytes": PRODUCER_BYTES,
            "response_bytes": response_bytes,
            "splice_errno": status.get("splice_errno"),
            "waitpid_completed": status.get("waitpid_completed") == 1,
            "cgi": cgi_snapshot,
            "producer": producer_snapshot,
        }
    finally:
        status = parse_status(status_data)
        producer_pid = status.get("producer_pid")
        if producer_pid:
            try:
                os.kill(producer_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        terminate_owned(cgi_pid)
        os.close(status_read)
        if client_connected:
            os.close(client_read)


def main() -> int:
    connected = run_case(client_connected=True)
    disconnected = run_case(client_connected=False)
    result = {
        "model": "cgi-io main_backup splice-then-wait ordering",
        "connected_control": connected,
        "disconnected_case": disconnected,
        "expectations_met": (
            connected["waitpid_completed"] is True
            and connected["splice_errno"] == 0
            and disconnected["splice_errno"] == errno.EPIPE
            and disconnected["waitpid_completed"] is False
            and disconnected["cgi"]["state"] != "exited"
            and disconnected["producer"]["state"] != "exited"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
