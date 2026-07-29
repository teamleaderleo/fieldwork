#!/usr/bin/env python3
"""Characterize HTTPX response close state after cancellation, failure, and concurrency."""

from __future__ import annotations

import asyncio
import json
import sys

import httpx


class ControlledCloseStream(httpx.AsyncByteStream):
    def __init__(self) -> None:
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.close_calls = 0
        self.cleaned = False

    async def __aiter__(self):
        if False:
            yield b""

    async def aclose(self) -> None:
        self.close_calls += 1
        self.entered.set()
        await self.release.wait()
        self.cleaned = True


class FailOnceCloseStream(httpx.AsyncByteStream):
    def __init__(self) -> None:
        self.close_calls = 0
        self.cleaned = False

    async def __aiter__(self):
        if False:
            yield b""

    async def aclose(self) -> None:
        self.close_calls += 1
        if self.close_calls == 1:
            raise RuntimeError("synthetic close failure")
        self.cleaned = True


async def cancellation_case() -> dict[str, object]:
    stream = ControlledCloseStream()
    response = httpx.Response(200, stream=stream)

    first = asyncio.create_task(response.aclose())
    await stream.entered.wait()
    first.cancel()
    try:
        await first
    except asyncio.CancelledError:
        pass

    before_retry = {
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    stream.release.set()
    await response.aclose()
    after_retry = {
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    assert before_retry == {
        "response_is_closed": True,
        "close_calls": 1,
        "stream_cleaned": False,
    }
    assert after_retry == before_retry
    return {"before_retry": before_retry, "after_retry": after_retry}


async def failure_case() -> dict[str, object]:
    stream = FailOnceCloseStream()
    response = httpx.Response(200, stream=stream)

    first_error = None
    try:
        await response.aclose()
    except Exception as error:
        first_error = f"{type(error).__name__}: {error}"

    before_retry = {
        "first_error": first_error,
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    await response.aclose()
    after_retry = {
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    assert before_retry == {
        "first_error": "RuntimeError: synthetic close failure",
        "response_is_closed": True,
        "close_calls": 1,
        "stream_cleaned": False,
    }
    assert after_retry == {
        "response_is_closed": True,
        "close_calls": 1,
        "stream_cleaned": False,
    }
    return {"before_retry": before_retry, "after_retry": after_retry}


async def concurrent_case() -> dict[str, object]:
    stream = ControlledCloseStream()
    response = httpx.Response(200, stream=stream)

    first = asyncio.create_task(response.aclose())
    await stream.entered.wait()
    await response.aclose()

    when_second_returned = {
        "first_done": first.done(),
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    stream.release.set()
    await first
    after_first_completed = {
        "first_done": first.done(),
        "response_is_closed": response.is_closed,
        "close_calls": stream.close_calls,
        "stream_cleaned": stream.cleaned,
    }

    assert when_second_returned == {
        "first_done": False,
        "response_is_closed": True,
        "close_calls": 1,
        "stream_cleaned": False,
    }
    assert after_first_completed == {
        "first_done": True,
        "response_is_closed": True,
        "close_calls": 1,
        "stream_cleaned": True,
    }
    return {
        "when_second_returned": when_second_returned,
        "after_first_completed": after_first_completed,
    }


async def main() -> None:
    result = {
        "python": sys.version.split()[0],
        "httpx": httpx.__version__,
        "cancellation": await cancellation_case(),
        "failure": await failure_case(),
        "concurrent": await concurrent_case(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
