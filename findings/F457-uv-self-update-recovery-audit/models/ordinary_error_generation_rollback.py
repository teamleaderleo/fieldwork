"""Exhaustive state model for the bounded Windows generation rollback candidate.

This model is intentionally smaller than the filesystem implementation. It checks the
state-machine invariant that every ordinary returned error restores the exact pre-update
mapping for canonical uv, staged companion destinations, and the receipt.
"""

from __future__ import annotations

from itertools import product
from typing import Final

MISSING: Final = object()


def apply_update(
    initial: dict[str, str],
    staged_companions: dict[str, str],
    staged_receipt: str,
    *,
    fail_at: int | None,
    destructive_finalizer: bool,
) -> tuple[bool, dict[str, str]]:
    live = dict(initial)
    managed_paths = ["uv.exe", *sorted(staged_companions), "receipt"]
    snapshots: dict[str, object] = {
        path: live.get(path, MISSING) for path in managed_paths
    }

    step = 0
    try:
        for path, value in sorted(staged_companions.items()):
            step += 1
            if fail_at == step:
                raise RuntimeError(f"copy {path}")
            live[path] = value

        step += 1
        if fail_at == step:
            # Include a partial live mutation before the receipt writer reports failure.
            live["receipt"] = "partial-receipt"
            raise RuntimeError("receipt promotion")
        live["receipt"] = staged_receipt

        step += 1
        if destructive_finalizer:
            live.pop("uv.exe", None)
        if fail_at == step:
            raise RuntimeError("final executable replacement")
        live["uv.exe"] = "new-uv"
        return True, live
    except RuntimeError:
        for path, snapshot in snapshots.items():
            if snapshot is MISSING:
                live.pop(path, None)
            else:
                assert isinstance(snapshot, str)
                live[path] = snapshot
        return False, live


def test_every_ordinary_error_restores_exact_initial_generation() -> None:
    staged_companions = {
        "uvx.exe": "new-uvx",
        "uvw.exe": "new-uvw",
    }
    failure_points = range(1, len(staged_companions) + 3)
    checked = 0

    for uvx_exists, uvw_exists, receipt_exists in product([False, True], repeat=3):
        initial = {"uv.exe": "old-uv"}
        if uvx_exists:
            initial["uvx.exe"] = "old-uvx"
        if uvw_exists:
            initial["uvw.exe"] = "old-uvw"
        if receipt_exists:
            initial["receipt"] = "old-receipt"

        for fail_at in failure_points:
            completed, result = apply_update(
                initial,
                staged_companions,
                "new-receipt",
                fail_at=fail_at,
                destructive_finalizer=(fail_at == max(failure_points)),
            )
            assert not completed
            assert result == initial
            checked += 1

    assert checked == 32


def test_success_commits_complete_new_generation() -> None:
    completed, result = apply_update(
        {
            "uv.exe": "old-uv",
            "uvx.exe": "old-uvx",
            "receipt": "old-receipt",
        },
        {
            "uvx.exe": "new-uvx",
            "uvw.exe": "new-uvw",
        },
        "new-receipt",
        fail_at=None,
        destructive_finalizer=False,
    )
    assert completed
    assert result == {
        "uv.exe": "new-uv",
        "uvx.exe": "new-uvx",
        "uvw.exe": "new-uvw",
        "receipt": "new-receipt",
    }


if __name__ == "__main__":
    test_every_ordinary_error_restores_exact_initial_generation()
    test_success_commits_complete_new_generation()
    print("ordinary-error generation model: 32 rollback cases and success case passed")
