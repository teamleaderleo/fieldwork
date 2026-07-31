from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from upstash_box import AsyncRun, Run
from upstash_box.errors import BoxError


class AsyncRequestBox:
    id = "box-async"

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls = 0
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def _request(self, method: str, path: str) -> object:
        assert method == "POST"
        assert path.endswith("/cancel")
        self.calls += 1
        self.started.set()
        await self.release.wait()
        if self.fail:
            raise BoxError("raw provider detail must not escape")
        return {}


class SyncRequestBox:
    id = "box-sync"

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls = 0
        self.started = threading.Event()
        self.release = threading.Event()
        self._calls_lock = threading.Lock()

    def _request(self, method: str, path: str) -> object:
        assert method == "POST"
        assert path.endswith("/cancel")
        with self._calls_lock:
            self.calls += 1
        self.started.set()
        assert self.release.wait(timeout=5)
        if self.fail:
            raise BoxError("raw provider detail must not escape")
        return {}


@pytest.mark.asyncio
async def test_async_callers_share_one_accepted_receipt() -> None:
    box = AsyncRequestBox()
    run = AsyncRun(box, "agent", "run-async")  # type: ignore[arg-type]

    first = asyncio.create_task(run.request_cancel())
    second = asyncio.create_task(run.request_cancel())
    await asyncio.wait_for(box.started.wait(), timeout=2)

    assert box.calls == 1
    assert run.status == "running"
    box.release.set()

    first_receipt, second_receipt = await asyncio.gather(first, second)
    assert first_receipt is second_receipt
    assert first_receipt.request_state == "accepted"
    assert first_receipt.outcome_state == "unknown"
    assert first_receipt.diagnostic is None

    with pytest.raises(FrozenInstanceError):
        first_receipt.request_state = "failed"  # type: ignore[misc]

    assert await run.request_cancel() is first_receipt
    assert box.calls == 1
    run._status = "completed"
    assert run.status == "completed"
    assert await run.request_cancel() is first_receipt
    run._status = "cancelled"
    assert run.status == "cancelled"
    assert await run.request_cancel() is first_receipt
    assert box.calls == 1


@pytest.mark.asyncio
async def test_cancelling_one_async_waiter_does_not_cancel_shared_request() -> None:
    box = AsyncRequestBox()
    run = AsyncRun(box, "command", "run-cancelled-waiter")  # type: ignore[arg-type]

    cancelled_waiter = asyncio.create_task(run.request_cancel())
    await asyncio.wait_for(box.started.wait(), timeout=2)
    cancelled_waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await cancelled_waiter

    surviving_waiter = asyncio.create_task(run.request_cancel())
    await asyncio.sleep(0)
    assert not surviving_waiter.done()
    assert box.calls == 1

    box.release.set()
    receipt = await surviving_waiter
    assert receipt.request_state == "accepted"
    assert receipt.outcome_state == "unknown"
    assert box.calls == 1


@pytest.mark.asyncio
async def test_async_failure_is_fixed_and_legacy_cancel_returns_none() -> None:
    box = AsyncRequestBox(fail=True)
    run = AsyncRun(box, "code", "run-async-failed")  # type: ignore[arg-type]

    legacy = asyncio.create_task(run.cancel())
    await asyncio.wait_for(box.started.wait(), timeout=2)
    box.release.set()

    assert await legacy is None
    receipt = await run.request_cancel()
    assert receipt.request_state == "failed"
    assert receipt.outcome_state == "unknown"
    assert receipt.diagnostic == "cancellation request failed"
    assert "raw provider detail" not in repr(receipt)
    assert run.status == "running"
    assert box.calls == 1


def test_sync_threads_share_one_accepted_receipt() -> None:
    box = SyncRequestBox()
    run = Run(box, "agent", "run-sync")  # type: ignore[arg-type]

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(run.request_cancel)
        assert box.started.wait(timeout=2)
        second = executor.submit(run.request_cancel)
        assert box.calls == 1
        assert run.status == "running"
        box.release.set()
        first_receipt = first.result(timeout=5)
        second_receipt = second.result(timeout=5)

    assert first_receipt is second_receipt
    assert first_receipt.request_state == "accepted"
    assert first_receipt.outcome_state == "unknown"
    assert run.request_cancel() is first_receipt
    run._status = "completed"
    assert run.status == "completed"
    assert run.request_cancel() is first_receipt
    run._status = "cancelled"
    assert run.status == "cancelled"
    assert run.request_cancel() is first_receipt
    assert box.calls == 1


def test_sync_failure_is_fixed_and_legacy_cancel_returns_none() -> None:
    box = SyncRequestBox(fail=True)
    run = Run(box, "command", "run-sync-failed")  # type: ignore[arg-type]

    result: dict[str, Any] = {}

    def invoke_legacy() -> None:
        result["value"] = run.cancel()

    thread = threading.Thread(target=invoke_legacy)
    thread.start()
    assert box.started.wait(timeout=2)
    box.release.set()
    thread.join(timeout=5)
    assert not thread.is_alive()

    receipt = run.request_cancel()
    assert result["value"] is None
    assert receipt.request_state == "failed"
    assert receipt.outcome_state == "unknown"
    assert receipt.diagnostic == "cancellation request failed"
    assert "raw provider detail" not in repr(receipt)
    assert run.status == "running"
    assert box.calls == 1
