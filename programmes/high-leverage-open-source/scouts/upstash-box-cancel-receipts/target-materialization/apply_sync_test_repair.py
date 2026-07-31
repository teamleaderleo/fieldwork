#!/usr/bin/env python3
"""Update the exact synchronous cancellation test for the receipt contract."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD = '''@respx.mock
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

NEW = '''@respx.mock
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_root", type=Path)
    args = parser.parse_args()
    path = (
        args.target_root.resolve()
        / "packages"
        / "python-sdk"
        / "tests"
        / "_sync"
        / "test_sync_client.py"
    )
    text = path.read_text(encoding="utf-8")
    count = text.count(OLD)
    if count != 1:
        raise RuntimeError(f"expected one sync cancellation test, found {count}")
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
