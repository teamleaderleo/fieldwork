import asyncio

import httpx
import pytest
import respx
from helpers import TEST_BASE_URL, make_async_box

from upstash_box._async.client import AsyncRun

BASE = f"{TEST_BASE_URL}/v2/box/box-123"


@respx.mock
@pytest.mark.parametrize("status_code", [500, 503])
async def test_reports_cancelled_after_remote_request_failure(status_code: int) -> None:
    box = await make_async_box(respx.mock)
    route = respx.post(f"{BASE}/runs/run-1/cancel").mock(
        return_value=httpx.Response(status_code, json={"error": "cancel unavailable"})
    )
    run = AsyncRun(box, "agent", "run-1")

    await run.cancel()

    assert route.call_count == 1
    assert run.status == "cancelled"
    await box.aclose()


@respx.mock
async def test_concurrent_callers_send_duplicate_cancel_requests() -> None:
    box = await make_async_box(respx.mock)
    route = respx.post(f"{BASE}/runs/run-2/cancel").mock(
        return_value=httpx.Response(503, json={"error": "cancel unavailable"})
    )
    run = AsyncRun(box, "command", "run-2")

    await asyncio.gather(run.cancel(), run.cancel())

    assert route.call_count == 2
    assert run.status == "cancelled"
    await box.aclose()


@respx.mock
@pytest.mark.xfail(
    strict=True,
    reason="Current SDK converts a failed cancellation request into terminal cancelled state",
)
async def test_repair_control_preserves_nonterminal_status_after_request_failure() -> None:
    box = await make_async_box(respx.mock)
    respx.post(f"{BASE}/runs/run-3/cancel").mock(
        return_value=httpx.Response(500, json={"error": "cancel unavailable"})
    )
    run = AsyncRun(box, "agent", "run-3")

    await run.cancel()
    status = run.status
    await box.aclose()

    assert status == "running"


@respx.mock
@pytest.mark.xfail(
    strict=True,
    reason="Current SDK gives each concurrent caller independent cancellation ownership",
)
async def test_repair_control_concurrent_callers_share_one_request() -> None:
    box = await make_async_box(respx.mock)
    route = respx.post(f"{BASE}/runs/run-4/cancel").mock(return_value=httpx.Response(200, json={}))
    run = AsyncRun(box, "agent", "run-4")

    await asyncio.gather(run.cancel(), run.cancel())
    call_count = route.call_count
    await box.aclose()

    assert call_count == 1
