#!/usr/bin/env python3
"""Apply the selected cancellation-receipt repair to exact Upstash Box source.

This is an internal Fieldwork execution carrier. It fails closed unless every
expected source fragment occurs exactly once at the pinned target revision.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TARGET_HEAD = "b55d832d6e3ae0156e32d21ea3863e231dfff9cd"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one source fragment in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite unexpected target file: {path}")
    path.write_text(content, encoding="utf-8")


def apply(root: Path) -> None:
    sdk = root / "packages" / "sdk"
    python_sdk = root / "packages" / "python-sdk"

    replace_once(
        sdk / "src" / "types.ts",
        'export type RunStatus = "running" | "completed" | "failed" | "cancelled" | "detached";\n\n',
        '''export type RunStatus = "running" | "completed" | "failed" | "cancelled" | "detached";\n\n/** One local cancellation request observation. Remote run outcome remains unknown. */\nexport type RunCancellationReceipt = Readonly<{\n  requestState: "accepted" | "failed";\n  outcomeState: "unknown";\n  diagnostic?: "cancellation request failed";\n}>;\n\n''',
    )

    replace_once(
        sdk / "src" / "client.ts",
        "  type RunStatus,\n  type RunCost,\n",
        "  type RunStatus,\n  type RunCancellationReceipt,\n  type RunCost,\n",
    )
    replace_once(
        sdk / "src" / "client.ts",
        "  private _abortController?: AbortController;\n  private _startTime: number;\n",
        "  private _abortController?: AbortController;\n  private _cancelRequest?: Promise<RunCancellationReceipt>;\n  private _startTime: number;\n",
    )
    replace_once(
        sdk / "src" / "client.ts",
        '''  /**\n   * Cancel a running execution.\n   */\n  async cancel(): Promise<void> {\n    this._abortController?.abort();\n    await this._box\n      ._request("POST", `/v2/box/${this._box.id}/runs/${this._id}/cancel`)\n      .catch(() => {});\n    this._status = "cancelled";\n  }\n''',
        '''  /**\n   * Request cancellation and observe the shared local request result.\n   *\n   * The receipt deliberately does not claim that the remote run reached a\n   * terminal cancelled state. Later authoritative run updates remain the\n   * source of truth for `status`. Repeated callers share one request.\n   */\n  requestCancel(): Promise<RunCancellationReceipt> {\n    if (this._cancelRequest === undefined) {\n      this._abortController?.abort();\n      this._cancelRequest = Promise.resolve()\n        .then(() =>\n          this._box._request("POST", `/v2/box/${this._box.id}/runs/${this._id}/cancel`),\n        )\n        .then(\n          () =>\n            Object.freeze({\n              requestState: "accepted" as const,\n              outcomeState: "unknown" as const,\n            }),\n          () =>\n            Object.freeze({\n              requestState: "failed" as const,\n              outcomeState: "unknown" as const,\n              diagnostic: "cancellation request failed" as const,\n            }),\n        );\n    }\n    return this._cancelRequest;\n  }\n\n  /**\n   * Request cancellation while preserving the legacy void return contract.\n   */\n  async cancel(): Promise<void> {\n    await this.requestCancel();\n  }\n''',
    )

    replace_once(
        sdk / "src" / "index.ts",
        "  RunStatus,\n  RunCost,\n",
        "  RunStatus,\n  RunCancellationReceipt,\n  RunCost,\n",
    )

    replace_once(
        sdk / "src" / "__tests__" / "run.test.ts",
        '''  it("cancels a run", async () => {\n    const { box, fetchMock } = await createTestBox();\n    fetchMock.mockResolvedValueOnce(mockResponse({}));\n\n    const run = new Run(box, "agent", "run-1");\n    Run._update(run, { abortController: new AbortController() });\n\n    await run.cancel();\n    expect(run.status).toBe("cancelled");\n  });\n''',
        '''  it("requests cancellation without claiming the remote outcome", async () => {\n    const { box, fetchMock } = await createTestBox();\n    fetchMock.mockResolvedValueOnce(mockResponse({}));\n\n    const run = new Run(box, "agent", "run-1");\n    Run._update(run, { abortController: new AbortController() });\n\n    await expect(run.cancel()).resolves.toBeUndefined();\n    expect(run.status).toBe("running");\n    await expect(run.requestCancel()).resolves.toEqual({\n      requestState: "accepted",\n      outcomeState: "unknown",\n    });\n    // One Box.get request plus one shared cancellation request.\n    expect(fetchMock).toHaveBeenCalledTimes(2);\n  });\n''',
    )

    replace_once(
        python_sdk / "upstash_box" / "types.py",
        '''RunStatus = Literal["running", "completed", "failed", "cancelled", "detached"]\n\n\n@dataclass\nclass RunCost:\n''',
        '''RunStatus = Literal["running", "completed", "failed", "cancelled", "detached"]\n\n\n@dataclass(frozen=True)\nclass RunCancellationReceipt:\n    """One local cancellation request observation; remote outcome remains unknown."""\n\n    request_state: Literal["accepted", "failed"]\n    outcome_state: Literal["unknown"] = "unknown"\n    diagnostic: Optional[Literal["cancellation request failed"]] = None\n\n\n@dataclass\nclass RunCost:\n''',
    )

    write_new(
        python_sdk / "upstash_box" / "_cancellation.py",
        '''"""Runtime-specific at-most-once cancellation request coordination."""\n\nfrom __future__ import annotations\n\nimport asyncio\nimport threading\nfrom concurrent.futures import Future\nfrom typing import Awaitable, Callable, Generic, Optional, TypeVar\n\nT = TypeVar("T")\n\n\nclass AsyncCancellationCoordinator(Generic[T]):\n    """Share one task while isolating it from cancellation of any waiter."""\n\n    def __init__(self) -> None:\n        self._task: Optional[asyncio.Task[T]] = None\n\n    async def run(self, operation: Callable[[], Awaitable[T]]) -> T:\n        if self._task is None:\n            self._task = asyncio.create_task(operation())\n        return await asyncio.shield(self._task)\n\n\nclass SyncCancellationCoordinator(Generic[T]):\n    """Share one operation and result across concurrent synchronous callers."""\n\n    def __init__(self) -> None:\n        self._lock = threading.Lock()\n        self._future: Optional[Future[T]] = None\n\n    def run(self, operation: Callable[[], T]) -> T:\n        with self._lock:\n            owner = self._future is None\n            if owner:\n                self._future = Future()\n            future = self._future\n\n        assert future is not None\n        if owner:\n            try:\n                future.set_result(operation())\n            except BaseException as error:\n                future.set_exception(error)\n        return future.result()\n''',
    )

    replace_once(
        python_sdk / "upstash_box" / "_async" / "client.py",
        "from .. import _common as common\nfrom ..errors import BoxError\n",
        "from .. import _common as common\nfrom .._cancellation import AsyncCancellationCoordinator\nfrom ..errors import BoxError\n",
    )
    replace_once(
        python_sdk / "upstash_box" / "_async" / "client.py",
        "    RunCost,\n    RunLog,\n    RunStatus,\n",
        "    RunCancellationReceipt,\n    RunCost,\n    RunLog,\n    RunStatus,\n",
    )
    replace_once(
        python_sdk / "upstash_box" / "_async" / "client.py",
        "        self._compute_ms = 0.0\n        self._start_time = time.time() * 1000\n",
        "        self._compute_ms = 0.0\n        self._cancel_coordinator = AsyncCancellationCoordinator[RunCancellationReceipt]()\n        self._start_time = time.time() * 1000\n",
    )
    replace_once(
        python_sdk / "upstash_box" / "_async" / "client.py",
        '''    async def cancel(self) -> None:\n        try:\n            await self._box._request("POST", f"/v2/box/{self._box.id}/runs/{self._id}/cancel")\n        except Exception:\n            pass\n        self._status = "cancelled"\n''',
        '''    async def _request_cancel(self) -> RunCancellationReceipt:\n        try:\n            await self._box._request("POST", f"/v2/box/{self._box.id}/runs/{self._id}/cancel")\n        except Exception:\n            return RunCancellationReceipt(\n                request_state="failed",\n                diagnostic="cancellation request failed",\n            )\n        return RunCancellationReceipt(request_state="accepted")\n\n    async def request_cancel(self) -> RunCancellationReceipt:\n        """Return one shared request receipt without claiming a remote outcome."""\n        return await self._cancel_coordinator.run(self._request_cancel)\n\n    async def cancel(self) -> None:\n        """Request cancellation while preserving the legacy None return contract."""\n        await self.request_cancel()\n''',
    )

    replace_once(
        python_sdk / "scripts" / "generate_sync.py",
        '            "AsyncRun": "Run",\n',
        '            "AsyncRun": "Run",\n            "AsyncCancellationCoordinator": "SyncCancellationCoordinator",\n',
    )

    replace_once(
        python_sdk / "upstash_box" / "__init__.py",
        "    RunCost,\n    RunLog,\n    RunOptions,\n",
        "    RunCancellationReceipt,\n    RunCost,\n    RunLog,\n    RunOptions,\n",
    )
    replace_once(
        python_sdk / "upstash_box" / "__init__.py",
        '    "RunStatus",\n    "ScheduleStatus",\n',
        '    "RunStatus",\n    "RunCancellationReceipt",\n    "ScheduleStatus",\n',
    )

    replace_once(
        python_sdk / "PARITY.md",
        "| `Run`/`StreamRun`    | `Run`/`StreamRun` (+ `Async*`) |\n",
        "| `Run`/`StreamRun`    | `Run`/`StreamRun` (+ `Async*`) |\n| `RunCancellationReceipt` | same (frozen dataclass in Python) |\n",
    )
    replace_once(
        python_sdk / "PARITY.md",
        "- `Run.cancel()`: swallows endpoint errors, always sets `cancelled`.\n",
        "- `Run.cancel()`: preserves the void/None contract and delegates to the shared at-most-once cancellation request.\n- `Run.requestCancel()` / `request_cancel()`: returns an immutable accepted/failed request receipt while leaving authoritative run status unchanged.\n",
    )

    replace_once(
        python_sdk / "tests" / "_async" / "test_run.py",
        '''@respx.mock\nasync def test_run_cancel_sets_status_and_swallows_errors():\n    box = await make_async_box(respx.mock)\n    respx.post(RUN_URL).mock(\n        return_value=sse_response(\n            [\n                {"event": "run_start", "data": {"run_id": "r1"}},\n                {"event": "done", "data": {"output": "ok"}},\n            ]\n        )\n    )\n    run = await box.agent.run(prompt="x")\n    # Cancel endpoint returns an error — cancel() must not raise.\n    respx.post(f"{BASE}/runs/r1/cancel").mock(\n        return_value=httpx.Response(500, json={"error": "nope"})\n    )\n    await run.cancel()\n    assert run.status == "cancelled"\n    await box.aclose()\n''',
        '''@respx.mock\nasync def test_run_cancel_preserves_status_and_shared_failure_receipt():\n    box = await make_async_box(respx.mock)\n    respx.post(RUN_URL).mock(\n        return_value=sse_response(\n            [\n                {"event": "run_start", "data": {"run_id": "r1"}},\n                {"event": "done", "data": {"output": "ok"}},\n            ]\n        )\n    )\n    run = await box.agent.run(prompt="x")\n    route = respx.post(f"{BASE}/runs/r1/cancel").mock(\n        return_value=httpx.Response(500, json={"error": "provider detail"})\n    )\n\n    assert await run.cancel() is None\n    receipt = await run.request_cancel()\n\n    assert run.status == "completed"\n    assert receipt.request_state == "failed"\n    assert receipt.outcome_state == "unknown"\n    assert receipt.diagnostic == "cancellation request failed"\n    assert "provider detail" not in repr(receipt)\n    assert route.call_count == 1\n    await box.aclose()\n''',
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_root", type=Path)
    args = parser.parse_args()
    apply(args.target_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
