#!/usr/bin/env python3
"""Model Tantivy prepare_commit worker-generation ownership after a late join error."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json


@dataclass
class Result:
    strategy: str
    prepare_result: str
    replacement_workers_started: int
    old_workers_still_live_after_error: list[str]
    admission_after_error: bool
    late_old_publication_accepted: bool
    mixed_generation_after_error: bool
    writer_retired: bool
    notes: list[str]


def current_order() -> Result:
    replacements = 0
    old_live = ["A", "B", "C"]
    notes = ["new generation installed before old joins"]

    old_live.remove("A")
    replacements += 1
    notes.append("old A joined; replacement A started")

    old_live.remove("B")
    notes.append("old B failed; remaining join handle for C dropped")

    return Result(
        strategy="current-order",
        prepare_result="error: worker B",
        replacement_workers_started=replacements,
        old_workers_still_live_after_error=old_live,
        admission_after_error=True,
        late_old_publication_accepted=True,
        mixed_generation_after_error=True,
        writer_retired=False,
        notes=notes,
    )


def admission_block_only() -> Result:
    result = current_order()
    result.strategy = "early-replacement-plus-admission-block"
    result.admission_after_error = False
    result.notes.append("writer marks preparation_failed and blocks add_document")
    result.notes.append("no publication fence was added for old worker C")
    return result


def join_before_replace() -> Result:
    return Result(
        strategy="join-before-replace",
        prepare_result="error: worker B",
        replacement_workers_started=0,
        old_workers_still_live_after_error=[],
        admission_after_error=False,
        late_old_publication_accepted=False,
        mixed_generation_after_error=False,
        writer_retired=True,
        notes=[
            "old workers are joined before new generation publication",
            "old A joined",
            "old B failed",
            "writer retired; old C cleanup remains owned before return",
        ],
    )


def generation_tagged() -> Result:
    result = current_order()
    result.strategy = "early-replacement-plus-generation-fence"
    result.admission_after_error = False
    result.late_old_publication_accepted = False
    result.notes.append("failed old generation is invalidated at publication boundary")
    result.notes.append("new admission stays blocked until reconciliation")
    return result


def run() -> dict[str, object]:
    results = [
        current_order(),
        admission_block_only(),
        join_before_replace(),
        generation_tagged(),
    ]

    assert results[0].mixed_generation_after_error
    assert results[0].admission_after_error
    assert results[0].late_old_publication_accepted

    assert not results[1].admission_after_error
    assert results[1].late_old_publication_accepted

    assert not results[2].mixed_generation_after_error
    assert not results[2].late_old_publication_accepted
    assert results[2].writer_retired

    assert results[3].mixed_generation_after_error
    assert not results[3].admission_after_error
    assert not results[3].late_old_publication_accepted

    return {
        "model": "tantivy-prepare-commit-generation-fence/v1",
        "claim_scope": "ordering and ownership only; not target execution",
        "results": [asdict(result) for result in results],
        "strongest_result": (
            "Blocking new admission after a failed preparation is insufficient by itself; "
            "late old-generation publication also needs cleanup completion or a publication fence."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
