from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:
        return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"
    except OSError:
        return False


def wait_for_markers(case: Path, process: subprocess.Popen[bytes]) -> None:
    markers = (case / "wrapper-ready", case / "child-ready")
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if all(marker.exists() for marker in markers):
            return
        if process.poll() is not None:
            raise RuntimeError(
                f"driver exited before readiness markers: rc={process.returncode}"
            )
        time.sleep(0.01)
    missing = [marker.name for marker in markers if not marker.exists()]
    raise RuntimeError(f"start timeout; missing {missing}")


def stop_pid(pid: int) -> None:
    if live(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


results: list[tuple[str, int, bool, bool]] = []
with tempfile.TemporaryDirectory(prefix="unit13-run-") as td:
    base = Path(td)
    for variant in ("baseline", "status", "group"):
        case = base / variant
        case.mkdir()
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "driver.py"), variant, str(case)]
        )
        wrapper_pid = child_pid = None
        try:
            wait_for_markers(case, process)
            wrapper_pid, child_pid = map(
                int, (case / "wrapper-ready").read_text().split()
            )
            os.kill(process.pid, signal.SIGINT)
            rc = process.wait(timeout=5)
            time.sleep(1.0)
            later = (case / "later-work").exists()
            alive = live(child_pid)
            results.append((variant, rc, later, alive))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            if child_pid is not None:
                stop_pid(child_pid)
            if wrapper_pid is not None:
                stop_pid(wrapper_pid)

for variant, rc, later, alive in results:
    print(
        f"variant={variant} rc={rc} "
        f"later_work={str(later).lower()} child_live={str(alive).lower()}"
    )

assert results == [
    ("baseline", 0, True, False),
    ("status", 130, True, False),
    ("group", 130, False, False),
]
