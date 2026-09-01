#!/usr/bin/env python3
"""Dependency-free model of the cmux Computer Use generation fence."""

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class ProcessGeneration:
    pid: int
    start_seconds: int
    start_microseconds: int


@dataclass(frozen=True)
class Record:
    driver_session_id: str
    logical_agent_session_id: str
    current_process_generations: frozenset[ProcessGeneration]


@dataclass(frozen=True)
class Hook:
    logical_agent_session_id: str
    pid: int | None
    captured_generation: ProcessGeneration | None


@dataclass(frozen=True)
class AcceptedInvocation:
    logical_agent_session_id: str
    process_generation: ProcessGeneration | None


def upstream_resolve(record: Record, hook: Hook) -> str | None:
    """Current upstream order: logical session equality wins first."""
    if record.logical_agent_session_id == hook.logical_agent_session_id:
        return record.driver_session_id
    if hook.captured_generation in record.current_process_generations:
        return record.driver_session_id
    return None


def candidate_resolve(record: Record, hook: Hook) -> str | None:
    """Candidate: PID-bearing hooks require the frozen exact generation."""
    if hook.pid is not None:
        generation = hook.captured_generation
        if generation is None or generation.pid != hook.pid:
            return None
        if generation not in record.current_process_generations:
            return None
        return record.driver_session_id
    if hook.captured_generation is not None:
        return None
    if record.logical_agent_session_id != hook.logical_agent_session_id:
        return None
    return record.driver_session_id


def candidate_completion_fallback(
    accepted: AcceptedInvocation,
    completion: Hook,
) -> bool:
    if accepted.logical_agent_session_id != completion.logical_agent_session_id:
        return False
    if completion.pid is not None:
        return (
            accepted.process_generation is not None
            and completion.captured_generation is not None
            and completion.captured_generation.pid == completion.pid
            and completion.captured_generation == accepted.process_generation
        )
    return accepted.process_generation is None and completion.captured_generation is None


def main() -> None:
    a = ProcessGeneration(pid=100, start_seconds=10, start_microseconds=1)
    b = ProcessGeneration(pid=200, start_seconds=20, start_microseconds=2)
    recycled_b_pid = ProcessGeneration(
        pid=b.pid,
        start_seconds=b.start_seconds - 1,
        start_microseconds=b.start_microseconds,
    )
    record_b = Record(
        driver_session_id="D(surface-S)",
        logical_agent_session_id="L",
        current_process_generations=frozenset({b}),
    )
    cases = {
        "current_b_same_logical_id": Hook("L", b.pid, b),
        "current_b_hook_alias": Hook("hook-alias", b.pid, b),
        "retired_a_same_logical_id": Hook("L", a.pid, a),
        "recycled_pid_stale_start": Hook("L", b.pid, recycled_b_pid),
        "generationless_same_logical_id": Hook("L", None, None),
    }

    observed = {
        name: {
            "upstream": upstream_resolve(record_b, hook),
            "candidate": candidate_resolve(record_b, hook),
        }
        for name, hook in cases.items()
    }

    accepted_b = AcceptedInvocation("L", b)
    observed["completion_fallback"] = {
        "current_b": candidate_completion_fallback(accepted_b, Hook("L", b.pid, b)),
        "retired_a": candidate_completion_fallback(accepted_b, Hook("L", a.pid, a)),
        "recycled_pid_stale_start": candidate_completion_fallback(
            accepted_b, Hook("L", b.pid, recycled_b_pid)
        ),
        "generationless": candidate_completion_fallback(accepted_b, Hook("L", None, None)),
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
    assert observed["recycled_pid_stale_start"] == {
        "upstream": record_b.driver_session_id,
        "candidate": None,
    }
    assert observed["generationless_same_logical_id"] == {
        "upstream": record_b.driver_session_id,
        "candidate": record_b.driver_session_id,
    }
    assert observed["completion_fallback"] == {
        "current_b": True,
        "retired_a": False,
        "recycled_pid_stale_start": False,
        "generationless": False,
    }

    print(json.dumps(observed, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
