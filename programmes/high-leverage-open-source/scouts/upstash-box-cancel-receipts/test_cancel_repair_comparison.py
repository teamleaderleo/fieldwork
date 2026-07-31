#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from cancel_repair_comparison import (
    Candidate,
    RemoteCancelProbe,
    RunModel,
    wait_for_calls,
)


class CancellationRepairComparisonTests(unittest.IsolatedAsyncioTestCase):
    async def test_option_a_shares_request_but_still_claims_terminal_cancelled(self) -> None:
        remote = RemoteCancelProbe(succeeds=False)
        run = RunModel(Candidate.SHARED_TERMINAL, remote)

        first = self._asyncio_create_task(run.cancel())
        second = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 1)
        remote.release.set()
        receipts = await self._gather(first, second)

        self.assertEqual(1, remote.calls)
        self.assertEqual(receipts[0], receipts[1])
        self.assertEqual("failed", receipts[0].request_state)
        self.assertEqual("cancelled", run.status)

    async def test_option_b_preserves_unknown_intent_but_duplicates_requests(self) -> None:
        remote = RemoteCancelProbe(succeeds=False)
        run = RunModel(Candidate.PUBLIC_CANCELLING, remote)

        first = self._asyncio_create_task(run.cancel())
        second = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 2)
        remote.release.set()
        await self._gather(first, second)

        self.assertEqual(2, remote.calls)
        self.assertEqual("cancelling", run.status)

    async def test_option_c_shares_one_request_and_keeps_status_authoritative(self) -> None:
        remote = RemoteCancelProbe(succeeds=True)
        run = RunModel(Candidate.SEPARATE_RECEIPT, remote)

        first = self._asyncio_create_task(run.cancel())
        second = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 1)
        remote.release.set()
        receipts = await self._gather(first, second)

        self.assertEqual(1, remote.calls)
        self.assertIs(receipts[0], receipts[1])
        self.assertEqual("accepted", receipts[0].request_state)
        self.assertEqual("unknown", receipts[0].outcome_state)
        self.assertEqual("running", run.status)

    async def test_option_c_failure_is_fixed_prose_and_not_replayed(self) -> None:
        remote = RemoteCancelProbe(succeeds=False)
        run = RunModel(Candidate.SEPARATE_RECEIPT, remote)

        pending = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 1)
        remote.release.set()
        first = await pending
        later = await run.cancel()

        self.assertIs(first, later)
        self.assertEqual(1, remote.calls)
        self.assertEqual("failed", later.request_state)
        self.assertEqual("cancellation request failed", later.diagnostic)
        self.assertNotIn("provider", later.diagnostic or "")
        self.assertEqual("running", run.status)

    async def test_option_c_acceptance_requires_authoritative_terminal_update(self) -> None:
        remote = RemoteCancelProbe(succeeds=True)
        run = RunModel(Candidate.SEPARATE_RECEIPT, remote)

        pending = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 1)
        remote.release.set()
        await pending
        self.assertEqual("running", run.status)

        run.apply_authoritative_update("cancelled")
        self.assertEqual("cancelled", run.status)

    async def test_natural_completion_can_follow_failed_cancel_request(self) -> None:
        remote = RemoteCancelProbe(succeeds=False)
        run = RunModel(Candidate.SEPARATE_RECEIPT, remote)

        pending = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 1)
        remote.release.set()
        await pending

        run.apply_authoritative_update("completed")
        self.assertEqual("completed", run.status)
        self.assertEqual("failed", run.cancel_receipt.request_state)
        self.assertEqual("unknown", run.cancel_receipt.outcome_state)

    async def test_receipt_is_immutable(self) -> None:
        remote = RemoteCancelProbe(succeeds=True)
        run = RunModel(Candidate.SEPARATE_RECEIPT, remote)

        pending = self._asyncio_create_task(run.cancel())
        await wait_for_calls(remote, 1)
        remote.release.set()
        receipt = await pending

        with self.assertRaises(FrozenInstanceError):
            receipt.request_state = "failed"  # type: ignore[misc]

    @staticmethod
    def _asyncio_create_task(awaitable):
        import asyncio

        return asyncio.create_task(awaitable)

    @staticmethod
    async def _gather(*awaitables):
        import asyncio

        return await asyncio.gather(*awaitables)


if __name__ == "__main__":
    unittest.main(verbosity=2)
