#!/usr/bin/env python3
"""Deterministic Playwright library probe for retry-shaped isolation and artifacts.

This probe uses two fresh browser attempts. Attempt 0 is labelled failed and attempt 1
passed; the orchestration is deliberately outside Playwright Test so the result remains
a mechanism observation for the installed Playwright client.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import time
import zipfile

from playwright.sync_api import sync_playwright


def chromium_pids() -> list[int]:
    output = subprocess.run(
        ["ps", "-eo", "pid=,comm=,args="],
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    pids: list[int] = []
    for line in output.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 2:
            continue
        pid, command = parts[:2]
        args = parts[2] if len(parts) == 3 else ""
        if "chromium" in command.lower() or "/usr/lib/chromium/chromium" in args:
            try:
                pids.append(int(pid))
            except ValueError:
                pass
    return sorted(set(pids))


def wait_for_cleanup(new_pids: set[int], timeout: float = 8.0) -> list[int]:
    deadline = time.time() + timeout
    survivors: set[int] = set()
    while time.time() < deadline:
        survivors = new_pids & set(chromium_pids())
        if not survivors:
            return []
        time.sleep(0.1)
    return sorted(survivors)


def file_record(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": path.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def trace_record(path: Path) -> dict:
    record = file_record(path)
    with zipfile.ZipFile(path) as archive:
        names = sorted(archive.namelist())
    record.update({
        "entries": names,
        "entry_count": len(names),
        "has_trace": "trace.trace" in names,
        "has_network": "trace.network" in names,
    })
    return record


def ensure_ffmpeg(ffmpeg: Path | None) -> dict:
    expected = Path.home() / ".cache/ms-playwright/ffmpeg-1011/ffmpeg-linux"
    record = {
        "expected_path": str(expected),
        "supplied_path": str(ffmpeg) if ffmpeg else None,
        "created_symlink": False,
    }
    if expected.exists() or ffmpeg is None:
        return record
    if not ffmpeg.is_file():
        raise FileNotFoundError(ffmpeg)
    expected.parent.mkdir(parents=True, exist_ok=True)
    expected.symlink_to(ffmpeg)
    record["created_symlink"] = True
    return record


def run_attempt(root: Path, chromium: Path, attempt: int, fail: bool) -> dict:
    attempt_dir = root / f"attempt-{attempt}"
    attempt_dir.mkdir(parents=True)
    before = set(chromium_pids())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(chromium),
            headless=True,
            args=["--no-sandbox"],
        )
        launched = set(chromium_pids()) - before
        context = browser.new_context(record_video_dir=str(attempt_dir / "video-source"))
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        page.set_content("<!doctype html><title>probe</title><h1>retry probe</h1>")
        page.evaluate(f"window.__attempt = {attempt}")
        context.add_cookies([{
            "name": "attempt",
            "value": str(attempt),
            "url": "https://example.test/",
        }])

        screenshot = attempt_dir / "screenshot.png"
        page.screenshot(path=str(screenshot))
        trace = attempt_dir / "trace.zip"
        context.tracing.stop(path=str(trace))

        video_handle = page.video
        context.close()
        video = attempt_dir / "video.webm"
        video_error = None
        try:
            if video_handle is None:
                raise RuntimeError("page video handle is absent")
            video_handle.save_as(str(video))
        except Exception as error:  # Preserve exact failure for the result record.
            video_error = f"{type(error).__name__}: {error}"
        browser.close()

    return {
        "attempt": attempt,
        "simulated_status": "failed" if fail else "passed",
        "launched_chromium_pids": sorted(launched),
        "surviving_chromium_pids_after_close": wait_for_cleanup(launched),
        "artifacts": {
            "screenshot": file_record(screenshot),
            "trace": trace_record(trace),
            "video": file_record(video) if video.exists() else None,
            "video_error": video_error,
        },
    }


def run_context_isolation(chromium: Path) -> dict:
    before = set(chromium_pids())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(chromium),
            headless=True,
            args=["--no-sandbox"],
        )
        launched = set(chromium_pids()) - before
        first = browser.new_context()
        first_page = first.new_page()
        first_page.set_content("<title>first</title>")
        first_page.evaluate("window.__leak = 'attempt-0'")
        first.add_cookies([{
            "name": "leak",
            "value": "attempt-0",
            "url": "https://example.test/",
        }])
        first.close()

        second = browser.new_context()
        second_page = second.new_page()
        second_page.set_content("<title>second</title>")
        page_global = second_page.evaluate("window.__leak")
        cookies = second.cookies("https://example.test/")
        second.close()
        browser.close()

    survivors = wait_for_cleanup(launched)
    return {
        "new_context_page_global": page_global,
        "new_context_cookie_names": [cookie["name"] for cookie in cookies],
        "isolated": page_global is None and not cookies,
        "launched_chromium_pids": sorted(launched),
        "surviving_chromium_pids_after_close": survivors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chromium", type=Path, default=Path("/usr/bin/chromium"))
    parser.add_argument("--ffmpeg", type=Path, default=Path("/usr/bin/ffmpeg"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    baseline = set(chromium_pids())
    ffmpeg = ensure_ffmpeg(args.ffmpeg)

    result = {
        "probe": "playwright-retry-teardown-artifacts",
        "runtime": {
            "playwright_python": importlib.metadata.version("playwright"),
            "chromium": subprocess.run(
                [str(args.chromium), "--version"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip(),
            "python": platform.python_version(),
            "os": platform.platform(),
            "ffmpeg": subprocess.run(
                [str(args.ffmpeg), "-version"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.splitlines()[0],
        },
        "ffmpeg_adaptation": ffmpeg,
        "scope": "library-level mechanism probe; retry orchestration is two fresh attempts outside Playwright Test",
        "attempts": [
            run_attempt(args.output, args.chromium, 0, fail=True),
            run_attempt(args.output, args.chromium, 1, fail=False),
        ],
        "context_isolation": run_context_isolation(args.chromium),
        "baseline_chromium_pids": sorted(baseline),
    }
    time.sleep(1.0)
    result["new_chromium_pids_after_probe"] = sorted(set(chromium_pids()) - baseline)
    result_path = args.output / "result.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    print(result_path)


if __name__ == "__main__":
    main()
