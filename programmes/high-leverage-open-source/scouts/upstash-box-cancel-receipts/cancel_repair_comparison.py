#!/usr/bin/env python3
"""Executable comparison for Upstash Box cancellation receipt repairs.

This is a dependency-free semantic model. It does not import or modify Upstash
Box. Exact target-native materialization remains a later gate.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Literal

AuthoritativeRunStatus = Literal[
    "running", "completed", "failed", "cancelled", "detached"
]
RequestState = Literal["accepted", "failed"]


class Candidate(str, Enum):
    """Stable option IDs assigned before the comparison executes."""

    SHARED_TERMINAL = "A-shared-terminal"
    PUBLIC_CANCELLING = "B-public-cancelling"
    SEPARATE_RECEIPT = "C-separate-receipt"


@dataclass(frozen=True)
class CancellationReceipt:
    """Local observation of one at-most-once cancellation request."""

    request_state: RequestState
    outcome_state: Literal["unknown"] = "unknown"
    diagnostic: str | None = None


class RemoteCancelError(RuntimeError):
    pass


class RemoteCancelProbe:
    """Deterministic remote request probe with an explicit settlement barrier."""

    def __init__(self, *, succeeds: bool) -> None:
        self.succeeds = succeeds
        self.calls = 0
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def request(self) -> None:
        self.calls += 1
        self.started.set()
        await self.release.wait()
        if not self.succeeds:
            raise RemoteCancelError("untrusted provider failure detail")


class RunModel:
    """Compare the three candidate ownership/state contracts."""

    def __init__(self, candidate: Candidate, remote: RemoteCancelProbe) -> None:
        self.candidate = candidate
        self.remote = remote
        self.status: str = "running"
        self.cancel_receipt: CancellationReceipt | None = None
        self._cancel_task: asyncio.Task[CancellationReceipt] | None = None

    async def cancel(self) -> CancellationReceipt:
        if self.candidate in {
            Candidate.SHARED_TERMINAL,
            Candidate.SEPARATE_RECEIPT,
        }:
            if self._cancel_task is None:
                self._cancel_task = asyncio.create_task(self._request_cancel_once())
            return await asyncio.shield(self._cancel_task)

        # Candidate B fixes the state vocabulary only. Each caller still owns a
        # separate provider request, preserving the observed duplication defect.
        return await self._request_cancel_once()

    async def _request_cancel_once(self) -> CancellationReceipt:
        try:
            await self.remote.request()
        except RemoteCancelError:
            receipt = CancellationReceipt(
                request_state="failed",
                diagnostic="cancellation request failed",
            )
        else:
            receipt = CancellationReceipt(request_state="accepted")

        if self.candidate is Candidate.SHARED_TERMINAL:
            # Fixes duplicate ownership but retains the false terminal claim.
            self.status = "cancelled"
        elif self.candidate is Candidate.PUBLIC_CANCELLING:
            # Represents local intent in the public run-status field and widens
            # the existing authoritative status vocabulary.
            self.status = "cancelling"
        else:
            # The run status remains an authoritative server-observation field.
            # Local request state is published separately through the receipt.
            pass

        self.cancel_receipt = receipt
        return receipt

    def apply_authoritative_update(self, status: AuthoritativeRunStatus) -> None:
        self.status = status


async def wait_for_calls(remote: RemoteCancelProbe, expected: int) -> None:
    """Wait deterministically for the expected concurrent request count."""

    for _ in range(100):
        if remote.calls == expected:
            return
        await asyncio.sleep(0)
    raise AssertionError(f"expected {expected} calls, observed {remote.calls}")
