#!/usr/bin/env python3
"""Dependency-free model of the cmux Computer Use hook-generation discriminator."""

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Record:
    driver_session_id: str
    logical_agent_session_id: str
    current_process_generations: frozenset[str]


@dataclass(frozen=True)
class Hook:
    logical_agent_session_id: str
    process_generation: str | None


def upstream_resolve(record: Record, hook: Hook) -> str | None:
    """Pinned eaa899c resolver order."""
    if record.logical_agent_session_id == hook.logical_agent_session_id:
        return record.driver_session_id
    if hook.process_generation in record.current_process_generations:
        return record.driver_session_id
    return None


def candidate_resolve(record: Record, hook: Hook) -> str | None:
    """Owned-fork candidate order."""
    if hook.process_generation is not None:
        if hook.process_generation not in record.current_process_generations:
            return None
        return record.driver_session_id
    if record.logical_agent_session_id != hook.logical_agent_session_id:
        return None
    return record.driver_session_id


def main() -> None:
    record_b = Record(
        driver_session_id="D(surface-S)",
        logical_agent_session_id="L",
        current_process_generations=frozenset({"B(pidB,startB)"}),
    )
    cases = {
        "current_b_same_logical_id": Hook("L", "B(pidB,startB)"),
        "current_b_hook_alias": Hook("hook-alias", "B(pidB,startB)"),
        "retired_a_same_logical_id": Hook("L", "A(pidA,startA)"),
        "generationless_same_logical_id": Hook("L", None),
    }

    observed = {
        name: {
            "upstream": upstream_resolve(record_b, hook),
            "candidate": candidate_resolve(record_b, hook),
        }
        for name, hook in cases.items()
    }

    assert observed["current_b_same_logical_id"] == {
        "upstream": record_b.driver_session_id,
        "candidate": record_b.driver_session_id,
    }
    assert observed["current_b_hook_alias"] == {
        "upstream": record_b.driver_session_id,
        "candidate": record_b.driver_session_id,
    }
    assert observed["retired_a_same_logical_id"] == {
        "upstream": record_b.driver_session_id,
        "candidate": None,
    }
    assert observed["generationless_same_logical_id"] == {
        "upstream": record_b.driver_session_id,
        "candidate": record_b.driver_session_id,
    }

    print(json.dumps(observed, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
