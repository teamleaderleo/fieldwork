#!/usr/bin/env python3
"""Neutral subprocess and terminal semantics case pack.

Runs deterministic local cases without invoking Gemini CLI or Codex. The output is
JSON so target-specific adapters can compare their event streams against the same
child behaviours.
"""
from __future__ import annotations

import argparse
import base64
import errno
import json
import os
import platform
import pty
import selectors
import signal
import struct
import subprocess
import sys
import termios
import time
from pathlib import Path
from typing import Any

SCRIPT = str(Path(__file__).resolve())


def emit(fd: int, data: bytes) -> None:
    os.write(fd, data)


def child(case: str) -> int:
    if case == "interleave":
        emit(1, b"O1\n")
        time.sleep(0.03)
        emit(2, b"E1\n")
        time.sleep(0.03)
        emit(1, b"O2\n")
        time.sleep(0.03)
        emit(2, b"E2\n")
        return 7

    if case == "terminal_identity":
        payload = {
            "stdin_tty": os.isatty(0),
            "stdout_tty": os.isatty(1),
            "stderr_tty": os.isatty(2),
            "term": os.environ.get("TERM"),
        }
        try:
            payload["winsize"] = list(os.get_terminal_size(1))
        except OSError:
            payload["winsize"] = None
        emit(1, (json.dumps(payload, sort_keys=True) + "\n").encode())
        return 0

    if case == "rewrite":
        emit(1, b"phase=one")
        time.sleep(0.02)
        emit(1, b"\rphase=two")
        time.sleep(0.02)
        emit(1, b"\x1b[2K\rphase=done\n")
        return 0

    if case == "invalid_utf8":
        emit(1, b"before:\xff\xfe:after\n")
        return 0

    if case == "final_marker":
        emit(1, b"prefix\n")
        emit(2, b"diagnostic\n")
        emit(1, b"FINAL-MARKER")
        return 0

    raise ValueError(f"unknown child case: {case}")


def terminate_process(
    proc: subprocess.Popen[bytes],
    *,
    process_group: bool,
    wait_timeout: float = 1.0,
) -> None:
    """Best-effort termination used only for harness cleanup paths."""
    if proc.poll() is not None:
        return
    try:
        if process_group:
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=wait_timeout)
    except subprocess.TimeoutExpired:
        pass


def close_streams(proc: subprocess.Popen[bytes]) -> None:
    for stream in (proc.stdout, proc.stderr):
        if stream is not None:
            stream.close()


def read_pipe_process(
    case: str,
    *,
    start_new_session: bool = False,
    timeout: float = 3.0,
) -> dict[str, Any]:
    started = time.monotonic()
    proc = subprocess.Popen(
        [sys.executable, SCRIPT, "--child", case],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=start_new_session,
        env={**os.environ, "TERM": "xterm-256color"},
    )
    assert proc.stdout is not None and proc.stderr is not None
    events: list[dict[str, Any]] = []
    stream_bytes = {"stdout": bytearray(), "stderr": bytearray()}
    direct_exit_at: float | None = None
    try:
        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ, "stdout")
            sel.register(proc.stderr, selectors.EVENT_READ, "stderr")
            while sel.get_map():
                if direct_exit_at is None and proc.poll() is not None:
                    direct_exit_at = time.monotonic() - started
                if time.monotonic() - started > timeout:
                    raise TimeoutError(f"pipe case {case} exceeded {timeout}s")
                ready = sel.select(0.02)
                if not ready:
                    continue
                for key, _ in ready:
                    chunk = os.read(key.fileobj.fileno(), 8192)
                    if chunk:
                        stream = key.data
                        stream_bytes[stream].extend(chunk)
                        events.append(
                            {
                                "stream": stream,
                                "at_ms": round((time.monotonic() - started) * 1000, 3),
                                "bytes_b64": base64.b64encode(chunk).decode(),
                                "text_lossy": chunk.decode("utf-8", "replace"),
                            }
                        )
                    else:
                        sel.unregister(key.fileobj)
        code = proc.wait(timeout=1)
        if direct_exit_at is None:
            direct_exit_at = time.monotonic() - started
        return {
            "pid": proc.pid,
            "exit_code": code,
            "direct_exit_ms": round(direct_exit_at * 1000, 3),
            "output_eof_ms": round((time.monotonic() - started) * 1000, 3),
            "events": events,
            "stdout_b64": base64.b64encode(stream_bytes["stdout"]).decode(),
            "stderr_b64": base64.b64encode(stream_bytes["stderr"]).decode(),
            "stdout_lossy": bytes(stream_bytes["stdout"]).decode("utf-8", "replace"),
            "stderr_lossy": bytes(stream_bytes["stderr"]).decode("utf-8", "replace"),
        }
    finally:
        terminate_process(proc, process_group=start_new_session)
        close_streams(proc)


def read_pty_process(
    case: str,
    cols: int = 72,
    rows: int = 19,
    timeout: float = 3.0,
) -> dict[str, Any]:
    import fcntl
    import select

    master, slave = pty.openpty()
    proc: subprocess.Popen[bytes] | None = None
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(slave, termios.TIOCSWINSZ, winsize)
    started = time.monotonic()
    raw = bytearray()
    events: list[dict[str, Any]] = []
    direct_exit_at: float | None = None
    try:
        proc = subprocess.Popen(
            [sys.executable, SCRIPT, "--child", case],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            start_new_session=True,
            close_fds=True,
            env={**os.environ, "TERM": "xterm-256color"},
        )
        os.close(slave)
        slave = -1
        while True:
            if direct_exit_at is None and proc.poll() is not None:
                direct_exit_at = time.monotonic() - started
            if time.monotonic() - started > timeout:
                raise TimeoutError(f"pty case {case} exceeded {timeout}s")
            try:
                ready, _, _ = select.select([master], [], [], 0.02)
                if not ready:
                    continue
                chunk = os.read(master, 8192)
                if not chunk:
                    break
                raw.extend(chunk)
                events.append(
                    {
                        "stream": "pty",
                        "at_ms": round((time.monotonic() - started) * 1000, 3),
                        "bytes_b64": base64.b64encode(chunk).decode(),
                        "text_lossy": chunk.decode("utf-8", "replace"),
                    }
                )
            except OSError as exc:
                if exc.errno == errno.EIO:
                    break
                raise
        code = proc.wait(timeout=1)
        if direct_exit_at is None:
            direct_exit_at = time.monotonic() - started
        return {
            "pid": proc.pid,
            "exit_code": code,
            "direct_exit_ms": round(direct_exit_at * 1000, 3),
            "output_eof_ms": round((time.monotonic() - started) * 1000, 3),
            "events": events,
            "pty_b64": base64.b64encode(raw).decode(),
            "pty_lossy": bytes(raw).decode("utf-8", "replace"),
            "configured_winsize": [cols, rows],
        }
    finally:
        if proc is not None:
            terminate_process(proc, process_group=True)
            close_streams(proc)
        if slave >= 0:
            os.close(slave)
        os.close(master)


def inherited_pipe_case(
    hold_seconds: float = 0.35,
    timeout: float = 4.0,
) -> dict[str, Any]:
    started = time.monotonic()
    proc = subprocess.Popen(
        [
            "bash",
            "-c",
            (
                f"(sleep {hold_seconds:.3f}; printf 'DESCENDANT-FINAL\\n') & "
                "printf 'DESCENDANT-PID=%s\\n' \"$!\"; exit 0"
            ),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    assert proc.stdout is not None and proc.stderr is not None
    events: list[dict[str, Any]] = []
    direct_exit_at: float | None = None
    try:
        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ, "stdout")
            sel.register(proc.stderr, selectors.EVENT_READ, "stderr")
            while sel.get_map():
                if direct_exit_at is None and proc.poll() is not None:
                    direct_exit_at = time.monotonic() - started
                if time.monotonic() - started > timeout:
                    raise TimeoutError("inherited pipe case exceeded timeout")
                for key, _ in sel.select(0.01):
                    chunk = os.read(key.fileobj.fileno(), 8192)
                    if chunk:
                        events.append(
                            {
                                "stream": key.data,
                                "at_ms": round((time.monotonic() - started) * 1000, 3),
                                "bytes_b64": base64.b64encode(chunk).decode(),
                                "text_lossy": chunk.decode("utf-8", "replace"),
                            }
                        )
                    else:
                        sel.unregister(key.fileobj)
        code = proc.wait(timeout=1)
        if direct_exit_at is None:
            direct_exit_at = time.monotonic() - started
        return {
            "pid": proc.pid,
            "exit_code": code,
            "direct_exit_ms": round(direct_exit_at * 1000, 3),
            "output_eof_ms": round((time.monotonic() - started) * 1000, 3),
            "hold_seconds": hold_seconds,
            "events": events,
            "output_lossy": "".join(event["text_lossy"] for event in events),
        }
    finally:
        terminate_process(proc, process_group=True)
        close_streams(proc)


def proc_state(pid: int) -> str | None:
    try:
        text = Path(f"/proc/{pid}/stat").read_text()
        tail = text.rsplit(") ", 1)[1]
        return tail.split()[0]
    except (OSError, IndexError):
        return None


def read_pid_lines(
    stream: Any,
    *,
    required: set[str],
    timeout: float,
) -> tuple[dict[str, int], str]:
    """Read newline-delimited KEY=PID records without blocking past timeout."""
    pids: dict[str, int] = {}
    raw = bytearray()
    pending = bytearray()
    deadline = time.monotonic() + timeout
    with selectors.DefaultSelector() as sel:
        sel.register(stream, selectors.EVENT_READ)
        while time.monotonic() < deadline and not required.issubset(pids):
            ready = sel.select(max(0.0, deadline - time.monotonic()))
            if not ready:
                break
            chunk = os.read(stream.fileno(), 8192)
            if not chunk:
                break
            raw.extend(chunk)
            pending.extend(chunk)
            while b"\n" in pending:
                line, _, pending = pending.partition(b"\n")
                text = line.decode("utf-8", "replace").strip()
                if "=" not in text:
                    continue
                key, value = text.split("=", 1)
                try:
                    pids[key] = int(value)
                except ValueError:
                    continue
    return pids, raw.decode("utf-8", "replace")


def cancel_tree_case() -> dict[str, Any]:
    script = r'''
trap 'printf "PARENT-TERM\n" >&2; sleep 0.15; exit 0' TERM
(
  trap 'printf "DESCENDANT-TERM\n" >&2; sleep 0.25; exit 0' TERM
  printf 'DESCENDANT-PID=%s\n' "$BASHPID"
  while :; do sleep 1; done
) &
descendant=$!
printf 'PARENT-PID=%s\n' "$BASHPID"
printf 'SPAWNED-DESCENDANT-PID=%s\n' "$descendant"
while :; do sleep 1; done
'''
    proc = subprocess.Popen(
        ["bash", "-c", script],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    assert proc.stdout is not None and proc.stderr is not None
    required = {"PARENT-PID", "SPAWNED-DESCENDANT-PID"}
    try:
        pids, _startup_stdout = read_pid_lines(
            proc.stdout,
            required=required,
            timeout=1.0,
        )
        if not required.issubset(pids):
            missing = ", ".join(sorted(required - pids.keys()))
            raise RuntimeError(f"process tree did not report required PIDs: {missing}")

        sent_at = time.monotonic()
        os.killpg(proc.pid, signal.SIGTERM)
        escalated = False
        try:
            code = proc.wait(timeout=0.1)
        except subprocess.TimeoutExpired:
            escalated = True
            os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait(timeout=1)
        stderr = proc.stderr.read().decode("utf-8", "replace")
        time.sleep(0.05)
        descendant = pids.get("SPAWNED-DESCENDANT-PID") or pids.get("DESCENDANT-PID")
        return {
            "pids": pids,
            "signal": "SIGTERM",
            "grace_ms": 100,
            "escalated_to_sigkill": escalated,
            "exit_code": code,
            "settled_ms": round((time.monotonic() - sent_at) * 1000, 3),
            "stderr": stderr,
            "descendant_proc_state": proc_state(descendant) if descendant else "missing",
        }
    finally:
        terminate_process(proc, process_group=True)
        close_streams(proc)


def run_all() -> dict[str, Any]:
    pipe_interleave = read_pipe_process("interleave")
    pty_interleave = read_pty_process("interleave")
    pipe_identity = read_pipe_process("terminal_identity")
    pty_identity = read_pty_process("terminal_identity")
    rewrite_pipe = read_pipe_process("rewrite")
    rewrite_pty = read_pty_process("rewrite")
    inherited = inherited_pipe_case()
    inherited_long = inherited_pipe_case(hold_seconds=2.25)
    invalid = read_pipe_process("invalid_utf8")
    final_marker = read_pipe_process("final_marker")
    cancelled = cancel_tree_case()

    return {
        "schema_version": 1,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "executable": sys.executable,
            "pid": os.getpid(),
        },
        "cases": {
            "pipe_interleave": pipe_interleave,
            "pty_interleave": pty_interleave,
            "pipe_terminal_identity": pipe_identity,
            "pty_terminal_identity": pty_identity,
            "pipe_terminal_rewrite": rewrite_pipe,
            "pty_terminal_rewrite": rewrite_pty,
            "inherited_pipe_after_direct_exit": inherited,
            "inherited_pipe_beyond_two_seconds": inherited_long,
            "invalid_utf8": invalid,
            "final_marker_before_exit": final_marker,
            "process_group_cancellation": cancelled,
        },
        "observations": {
            "pipe_stream_tags": [e["stream"] for e in pipe_interleave["events"]],
            "pty_is_single_stream": all(
                e["stream"] == "pty" for e in pty_interleave["events"]
            ),
            "inherited_pipe_lag_ms": round(
                inherited["output_eof_ms"] - inherited["direct_exit_ms"], 3
            ),
            "long_inherited_pipe_lag_ms": round(
                inherited_long["output_eof_ms"] - inherited_long["direct_exit_ms"],
                3,
            ),
            "final_marker_captured": "FINAL-MARKER"
            in final_marker["stdout_lossy"],
            "invalid_utf8_replacement_present": "\ufffd" in invalid["stdout_lossy"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if args.child:
        return child(args.child)
    result = run_all()
    json.dump(result, sys.stdout, indent=2 if args.pretty else None, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
