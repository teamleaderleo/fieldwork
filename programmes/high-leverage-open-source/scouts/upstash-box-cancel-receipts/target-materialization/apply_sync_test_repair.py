#!/usr/bin/env python3
"""Apply exact target follow-ups discovered by full compatibility gates."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_SYNC_TEST = '''@respx.mock
def test_run_cancel_swallows_errors():
    box = make_sync_box(respx.mock)
    respx.post(RUN_URL).mock(
        return_value=sse_response(
            [
                {"event": "run_start", "data": {"run_id": "r1"}},
                {"event": "done", "data": {"output": "ok"}},
            ]
        )
    )
    run = box.agent.run(prompt="x")
    respx.post(f"{BASE}/runs/r1/cancel").mock(
        return_value=httpx.Response(500, json={"error": "no"})
    )
    run.cancel()
    assert run.status == "cancelled"
    box.close()
'''

NEW_SYNC_TEST = '''@respx.mock
def test_run_cancel_preserves_status_and_shared_failure_receipt():
    box = make_sync_box(respx.mock)
    respx.post(RUN_URL).mock(
        return_value=sse_response(
            [
                {"event": "run_start", "data": {"run_id": "r1"}},
                {"event": "done", "data": {"output": "ok"}},
            ]
        )
    )
    run = box.agent.run(prompt="x")
    route = respx.post(f"{BASE}/runs/r1/cancel").mock(
        return_value=httpx.Response(500, json={"error": "provider detail"})
    )

    assert run.cancel() is None
    receipt = run.request_cancel()

    assert run.status == "completed"
    assert receipt.request_state == "failed"
    assert receipt.outcome_state == "unknown"
    assert receipt.diagnostic == "cancellation request failed"
    assert "provider detail" not in repr(receipt)
    assert route.call_count == 1
    box.close()
'''

OLD_TYPING_IMPORT = (
    "from typing import Awaitable, Callable, Generic, Optional, TypeVar\n"
)
NEW_TYPING_IMPORT = (
    "from typing import Any, Callable, Coroutine, Generic, Optional, TypeVar\n"
)
OLD_RUN_SIGNATURE = (
    "    async def run(self, operation: Callable[[], Awaitable[T]]) -> T:\n"
)
NEW_RUN_SIGNATURE = (
    "    async def run(self, operation: Callable[[], Coroutine[Any, Any, T]]) -> T:\n"
)


def replace_once(path: Path, old: str, new: str, description: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one {description} in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_root", type=Path)
    args = parser.parse_args()
    python_sdk = args.target_root.resolve() / "packages" / "python-sdk"

    replace_once(
        python_sdk / "tests" / "_sync" / "test_sync_client.py",
        OLD_SYNC_TEST,
        NEW_SYNC_TEST,
        "sync cancellation test",
    )
    coordinator = python_sdk / "upstash_box" / "_cancellation.py"
    replace_once(
        coordinator,
        OLD_TYPING_IMPORT,
        NEW_TYPING_IMPORT,
        "cancellation typing import",
    )
    replace_once(
        coordinator,
        OLD_RUN_SIGNATURE,
        NEW_RUN_SIGNATURE,
        "async coordinator signature",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
