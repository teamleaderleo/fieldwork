# Reentrant async-close model receipt

## In simple words

The current HTTPX candidate lets concurrent callers wait for one close attempt. The state stores an event and failure bit, but no owner identity. When the delegated stream calls the same response's `aclose()` from the owning task, the inner call waits on an event that only the suspended outer call can set.

This dependency-free model copies the relevant control flow from source head `18256f10d1b306bdf87a1bab24b214c15839147b`. It demonstrates the cycle under AnyIO's asyncio backend. It does not execute the HTTPX package or Trio.

## Identity

- Date: 2026-08-01
- Claim scope: `mechanism`
- Source modeled: [`httpx/_models.py` at `18256f10...`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py#L1104-L1137)
- Python: `3.13.5`
- AnyIO: `4.13.0`
- Backend: `asyncio`
- Network: unused
- Upstream contact authorized: `false`

## Command

```sh
python /tmp/reentrant_probe.py
```

## Probe

```python
import anyio


class State:
    def __init__(self):
        self.event = anyio.Event()
        self.failed = False


class Response:
    def __init__(self):
        self.is_closed = False
        self._async_close_failed = False
        self._async_close_state = None
        self._async_close_started = False
        self.stream = None

    async def aclose(self):
        if self.is_closed:
            return
        if self._async_close_failed:
            raise RuntimeError("terminal observer failure")

        state = self._async_close_state
        if state is None:
            state = State()
            self._async_close_state = state
            self._async_close_started = True
            try:
                await self.stream.aclose()
            except BaseException:
                self._async_close_failed = True
                state.failed = True
                self._async_close_state = None
                state.event.set()
                raise
            else:
                self.is_closed = True
                self._async_close_state = None
                state.event.set()
                return

        await state.event.wait()
        if state.failed:
            raise RuntimeError("terminal observer failure")


class ReentrantStream:
    def __init__(self, response):
        self.response = response
        self.close_calls = 0

    async def aclose(self):
        self.close_calls += 1
        await self.response.aclose()


async def main():
    response = Response()
    stream = ReentrantStream(response)
    response.stream = stream
    try:
        with anyio.fail_after(0.1):
            await response.aclose()
    except TimeoutError:
        print(
            "TIMEOUT",
            stream.close_calls,
            response.is_closed,
            response._async_close_failed,
        )


anyio.run(main, backend="asyncio")
```

## Output

```text
3.13.5
anyio 4.13.0
TIMEOUT 1 False True
```

## Interpretation

1. The delegated stream was entered once.
2. The inner call joined the owner's event.
3. The owner could no longer reach either settlement branch.
4. The deadline cancellation escaped through the outer attempt and marked the response terminal-failed.

The timeout is the distinguishing observation. A repaired candidate should fail the same-owner inner call immediately or use another cycle-free ownership model while allowing unrelated tasks to join the owner attempt.

## Limits

- This is `model-executed`, not `target-executed`.
- Trio was unavailable in the local environment: `ModuleNotFoundError: No module named 'trio'`.
- The probe omits request context, exception classes, pickling, elapsed time, and external waiters.
- The target-native clearing test must run under both asyncio and Trio on the repaired source head.